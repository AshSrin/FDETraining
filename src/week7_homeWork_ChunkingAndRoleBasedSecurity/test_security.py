"""Exercise E — negative tests and revocation, with saved evidence.

All retrieval runs as the restricted reader role (k8s_rag_reader) with RLS. The admin login is used
only to revoke/restore a membership and to fingerprint the stored embeddings.

Required by the homework:
  E1  an authorized user retrieves a restricted document
  E2  an unauthorized user cannot retrieve that same document
  E3  revoking group membership removes access immediately, without re-embedding/re-ingesting
  E4  an unknown identity cannot read protected chunks
  E5  restoring the membership brings authorized access back
Extra hardening checks (X*): missing identity, cross-tenant, multi-group user, privilege boundaries.

Outputs: evidence/exercise_e_security_tests.txt (full transcript) and .md (summary table).
Exit code 1 if any check fails. Meena's membership is always restored (finally block).
"""
from datetime import datetime
from pathlib import Path
import sys
import time
from common import connect, embed, TENANT
from search import run_search

ROOT = Path(__file__).resolve().parent
DOC = 'SEC-rbac-good-practices'                      # restricted: SECURITY_ENGINEERING only
QUESTION = 'What are recommended Kubernetes RBAC practices?'
REVOKE_USER, REVOKE_GROUP = 'meena', 'SECURITY_ENGINEERING'

transcript, results = [], []


def log(line=''):
    print(line)
    transcript.append(line)


def check(test_id, label, passed, detail):
    results.append((test_id, label, passed, detail))
    log(f"{'PASS' if passed else 'FAIL'}  {test_id}  {label}\n      -> {detail}")


# ------------------------------------------------------------------ database helpers
def reader(sql_text, params=(), user=None, tenant=TENANT, set_identity=True, before=None):
    """Run a query as the restricted reader role with a transaction-local identity."""
    with connect() as db, db.transaction():
        if set_identity:
            db.execute("SELECT set_config('app.user_id', %s, true), set_config('app.tenant_id', %s, true)",
                       (user, tenant))
        if before:
            db.execute(before)
        return db.execute(sql_text, params).fetchall()


def reader_error(sql_text, params=(), user='priya', before=None):
    """Return the error message if the reader query is rejected, else None."""
    try:
        reader(sql_text, params, user=user, before=before)
        return None
    except Exception as exc:
        return f'{type(exc).__name__}: {str(exc).splitlines()[0]}'


def doc_chunk_count(user, doc=DOC, tenant=TENANT):
    return reader('SELECT count(*) FROM k8srag.chunks WHERE document_id = %s', (doc,), user, tenant)[0][0]


def visible_documents(user, tenant=TENANT, set_identity=True):
    return [r[0] for r in reader('SELECT document_id FROM k8srag.documents ORDER BY 1',
                                 user=user, tenant=tenant, set_identity=set_identity)]


def search_docs(user, vector, k=20):
    rows = run_search(user, QUESTION, k, vector, max_distance=None)   # raw top-k, no relevance cutoff
    return [(r[0], r[2], float(r[6])) for r in rows]


def fingerprint():
    """Hash of every stored chunk id + embedding: proves nothing was re-embedded or re-ingested."""
    with connect(admin=True) as db:
        return db.execute("""SELECT count(*), max(chunk_id),
                                    md5(string_agg(chunk_id::text || ':' || md5(embedding::text), ',' ORDER BY chunk_id))
                             FROM k8srag.chunks""").fetchone()


def membership(user, group):
    with connect(admin=True) as db:
        return bool(db.execute('SELECT 1 FROM k8srag.user_groups WHERE user_id=%s AND group_name=%s',
                               (user, group)).fetchone())


def set_membership(user, group, present):
    with connect(admin=True) as db:
        if present:
            db.execute('INSERT INTO k8srag.user_groups(user_id, group_name) VALUES (%s,%s) ON CONFLICT DO NOTHING',
                       (user, group))
        else:
            db.execute('DELETE FROM k8srag.user_groups WHERE user_id=%s AND group_name=%s', (user, group))
        db.commit()
    log(f"ADMIN {'RESTORE' if present else 'REVOKE'}: {user} {'+' if present else '-'} {group}  "
        f"(committed {datetime.now().strftime('%H:%M:%S.%f')[:-3]})")


def top(rows, n=3):
    return ', '.join(f'{d}#{c} d={dist:.4f}' for d, c, dist in rows[:n]) or '(no results)'


# ------------------------------------------------------------------ tests
def main():
    log(f'Exercise E security tests — {datetime.now():%Y-%m-%d %H:%M:%S}')
    log(f'Tenant={TENANT}  restricted document={DOC}  question={QUESTION!r}')
    log('Retrieval role: k8s_rag_reader (RLS).  Admin used only for revoke/restore and fingerprints.\n')
    vector = embed([QUESTION])[0]

    if not membership(REVOKE_USER, REVOKE_GROUP):
        log(f'NOTE: {REVOKE_USER} was missing {REVOKE_GROUP} before the run; restoring baseline first.')
        set_membership(REVOKE_USER, REVOKE_GROUP, True)

    # E1 — authorized user retrieves the restricted document
    meena_before = search_docs('meena', vector)
    n_meena = doc_chunk_count('meena')
    check('E1', f'Meena (SECURITY_ENGINEERING) retrieves restricted {DOC}',
          bool(meena_before) and meena_before[0][0] == DOC and n_meena > 0,
          f'top results: {top(meena_before)}; {n_meena} chunks of {DOC} visible')

    # E2 — unauthorized users cannot retrieve the same document
    for user in ('arjun', 'priya'):
        rows = search_docs(user, vector)
        leaked = [r for r in rows if r[0] == DOC]
        n = doc_chunk_count(user)
        check('E2', f'{user.title()} cannot retrieve {DOC} (not in SECURITY_ENGINEERING)',
              not leaked and n == 0 and DOC not in visible_documents(user),
              f'{DOC} in top-20: {len(leaked)}; direct chunk count: {n}; document row visible: '
              f'{DOC in visible_documents(user)}; best they get instead: {top(rows, 1)}')

    # E3 — revoke membership: immediate, no re-embedding / re-ingest
    fp_before = fingerprint()
    log(f'\nFingerprint before revoke: chunks={fp_before[0]} max_id={fp_before[1]} md5={fp_before[2]}')
    try:
        set_membership(REVOKE_USER, REVOKE_GROUP, False)
        t0 = time.perf_counter()
        n_after = doc_chunk_count('meena')
        elapsed_ms = (time.perf_counter() - t0) * 1000
        rows_after = search_docs('meena', vector)
        sec_after = [d for d in visible_documents('meena') if d.startswith('SEC-')]
        shared_after = [d for d in visible_documents('meena') if d.startswith('SHARED-')]
        fp_after = fingerprint()
        log(f'Fingerprint after revoke:  chunks={fp_after[0]} max_id={fp_after[1]} md5={fp_after[2]}')
        check('E3', 'Revoking SECURITY_ENGINEERING removes Meena\'s access on the very next query',
              n_after == 0 and not sec_after and all(r[0] != DOC for r in rows_after),
              f'{DOC} chunks visible: {n_meena} -> {n_after} (next query, {elapsed_ms:.0f} ms); '
              f'SEC-* documents visible: {len(sec_after)}; top results now: {top(rows_after)}')
        check('E3', 'Revocation needed no re-embedding or re-ingesting',
              fp_before == fp_after,
              'chunk count, max chunk_id and embedding hash identical before/after revoke')
        check('E3', 'Revocation is scoped: Meena keeps ALL_EMPLOYEES shared documents',
              len(shared_after) == 5, f'SHARED-* documents still visible: {len(shared_after)}')
    finally:
        log('')
        set_membership(REVOKE_USER, REVOKE_GROUP, True)   # always restore, even if a check failed

    # E5 — restoring membership brings access back (same ranking as before)
    meena_restored = search_docs('meena', vector)
    check('E5', 'Restoring SECURITY_ENGINEERING returns Meena\'s authorized access',
          doc_chunk_count('meena') == n_meena and meena_restored[:5] == meena_before[:5],
          f'{DOC} chunks visible: {doc_chunk_count("meena")}; top results: {top(meena_restored)} '
          f'(identical to E1: {meena_restored[:5] == meena_before[:5]})')

    # E4 — unknown identity
    for user in ('intruder', 'Meena ', 'admin'):
        total = reader('SELECT count(*) FROM k8srag.chunks', user=user)[0][0]
        if user == 'Meena ':   # case/space variants are NOT normalised by the database
            check('E4', "Look-alike identity 'Meena ' (capital + trailing space) is unknown to the database",
                  total == 0, f'chunks visible: {total}')
            continue
        check('E4', f'Unknown identity {user!r} cannot read protected chunks',
              total == 0 and doc_chunk_count(user) == 0 and not visible_documents(user),
              f'chunks visible: {total}; {DOC} chunks: {doc_chunk_count(user)}; documents visible: 0')
    rows = run_search('intruder', QUESTION, 5, vector, max_distance=None)
    check('E4', 'search.py path: unknown identity gets zero results', not rows, f'results returned: {len(rows)}')

    # X — extra hardening
    log('')
    n = reader('SELECT count(*) FROM k8srag.chunks', set_identity=False)[0][0]
    check('X1', 'No identity set at all -> fail closed', n == 0, f'chunks visible: {n}')
    n = doc_chunk_count('meena', tenant='OTHER_ORG')
    check('X2', 'Valid user with the wrong tenant (OTHER_ORG) sees nothing',
          n == 0 and not visible_documents('meena', tenant='OTHER_ORG'), f'{DOC} chunks visible: {n}')
    divya = visible_documents('divya')
    check('X3', 'Divya (APP + SECURITY) reads both departments + shared, but not Platform',
          DOC in divya and 'APP-deployment' in divya and not any(d.startswith('PLAT-') for d in divya),
          f"APP={sum(d.startswith('APP-') for d in divya)} SEC={sum(d.startswith('SEC-') for d in divya)} "
          f"SHARED={sum(d.startswith('SHARED-') for d in divya)} PLAT={sum(d.startswith('PLAT-') for d in divya)}")
    for test_id, label, sql_text, before in [
        ('X4', 'Reader cannot read the ACL table', 'SELECT * FROM k8srag.document_acl', None),
        ('X4', 'Reader cannot read identity tables', 'SELECT * FROM k8srag.user_groups', None),
        ('X5', 'Reader cannot grant itself a group',
         "INSERT INTO k8srag.user_groups VALUES ('arjun','SECURITY_ENGINEERING')", None),
        ('X5', 'Reader cannot modify stored chunks', 'DELETE FROM k8srag.chunks', None),
        ('X6', 'Reader cannot switch RLS off (SET row_security = off)',
         'SELECT count(*) FROM k8srag.chunks', 'SET LOCAL row_security = off'),
    ]:
        err = reader_error(sql_text, before=before)
        check(test_id, label, err is not None, err or 'query unexpectedly succeeded')

    write_evidence()
    failed = [r for r in results if not r[2]]
    log(f'\n{len(results) - len(failed)}/{len(results)} checks passed.')
    log('Identities are simulated with --user for this local demo; production identities must come '
        'from a trusted, authenticated backend.')
    (ROOT / 'evidence' / 'exercise_e_security_tests.txt').write_text('\n'.join(transcript) + '\n')
    if failed:
        sys.exit(1)


def write_evidence():
    out = ROOT / 'evidence'
    out.mkdir(exist_ok=True)
    md = ['# Exercise E — negative tests and revocation', '',
          f'Run {datetime.now():%Y-%m-%d %H:%M:%S} · tenant `{TENANT}` · restricted document `{DOC}` · '
          f'question *{QUESTION}*', '',
          'All retrieval runs as `k8s_rag_reader` under PostgreSQL RLS. Full transcript: '
          '`exercise_e_security_tests.txt`.', '',
          '| ID | Check | Result | Evidence |', '|---|---|---|---|']
    for test_id, label, passed, detail in results:
        md.append(f"| {test_id} | {label} | {'✅ PASS' if passed else '❌ FAIL'} | "
                  f"{detail.replace('|', '/')} |")
    (out / 'exercise_e_security_tests.md').write_text('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
