"""Exercise D — same question, different results.

For each test question:
  1. Admin ground truth (no RLS): the top-k chunks over the whole corpus, with a column per user
     showing whether that user can see it (✅) or is blocked (⛔).
  2. Each user's own top-k via search.py (restricted reader role + RLS).
Every result a user receives is re-checked against the declared policy (data/users.json groups vs
the document's ACL). Any result that is not authorized is reported as a VIOLATION and the script
exits non-zero.

Outputs: evidence/exercise_d_matrix.md and evidence/exercise_d_matrix.json
"""
import argparse
import json
import sys
from pathlib import Path
from common import connect, embed, TENANT, MAX_DISTANCE
from retrieval_check import QUESTIONS, admin_search
from search import run_search, NO_ANSWER

ROOT = Path(__file__).resolve().parent
AREAS = ['Application Engineering', 'Platform Engineering', 'Security Engineering', 'Shared knowledge']


def load_policy():
    users = json.loads((ROOT / 'data' / 'users.json').read_text())
    user_groups = {u['user_id']: set(u['groups']) for u in users}
    names = {u['user_id']: u['display_name'] for u in users}
    with connect(admin=True) as db:
        doc_groups = {}
        for doc, group in db.execute('SELECT document_id, group_name FROM k8srag.document_acl'):
            doc_groups.setdefault(doc, set()).add(group)
    return user_groups, names, doc_groups


def main(k):
    user_groups, names, doc_groups = load_policy()
    users = list(user_groups)

    def authorized(user, doc):
        return bool(user_groups[user] & doc_groups.get(doc, set()))

    vectors = embed(QUESTIONS)
    report, violations, total = [], [], 0
    for question, area, vector in zip(QUESTIONS, AREAS, vectors):
        truth = admin_search(question, k, vector)
        entry = {'question': question, 'area': area, 'ground_truth': [], 'users': {}}
        for rank, (doc, title, no, heading, url, cls, groups, dist) in enumerate(truth, 1):
            entry['ground_truth'].append({
                'rank': rank, 'document_id': doc, 'title': title, 'chunk_no': no, 'heading': heading,
                'source_url': url, 'groups': groups, 'cosine_distance': float(dist),
                'visible_to': {u: authorized(u, doc) for u in users}})
        for u in users:
            rows = run_search(u, question, k, vector, max_distance=None)  # raw top-k for evidence
            results = []
            for rank, (doc, title, no, heading, url, cls, dist, _preview) in enumerate(rows, 1):
                ok = authorized(u, doc)
                total += 1
                if not ok:
                    violations.append((u, question, doc))
                results.append({'rank': rank, 'document_id': doc, 'title': title, 'chunk_no': no,
                                'heading': heading, 'source_url': url, 'classification': cls,
                                'cosine_distance': float(dist), 'authorized': ok,
                                'within_cutoff': float(dist) <= MAX_DISTANCE})
            entry['users'][u] = results
        report.append(entry)
        print(f'\nQ: {question}  [{area}]')
        for u in users:
            top = entry['users'][u][0] if entry['users'][u] else None
            label = f"{top['document_id']} d={top['cosine_distance']}" if top else '(no results)'
            passed = sum(r['within_cutoff'] for r in entry['users'][u])
            print(f'  {names[u]:6} top-1: {label:38} passed cutoff: {passed}/{k}')

    out = ROOT / 'evidence'
    out.mkdir(exist_ok=True)
    summary = {'tenant': TENANT, 'k': k, 'max_distance': MAX_DISTANCE, 'results_checked': total,
               'unauthorized_results': len(violations), 'violations': violations}
    (out / 'exercise_d_matrix.json').write_text(json.dumps({'summary': summary, 'questions': report}, indent=2))
    (out / 'exercise_d_matrix.md').write_text(render(report, users, names, user_groups, summary))
    print(f'\nChecked {total} user results: {len(violations)} unauthorized.')
    print(f'Wrote {out / "exercise_d_matrix.md"}')
    if violations:
        print('VIOLATIONS:', violations)
        sys.exit(1)


def render(report, users, names, user_groups, summary):
    tick = lambda b: '✅' if b else '⛔'
    keep = lambda b: 'kept' if b else 'dropped'
    md = ['# Exercise D — same question, different results', '',
          f"Tenant `{summary['tenant']}` · top-{summary['k']} by cosine distance (lower = closer) · "
          'user results come from `search.py` (restricted reader role, PostgreSQL RLS).', '',
          '| User | Groups |', '|---|---|']
    md += [f"| {names[u]} | {', '.join(sorted(user_groups[u]))} |" for u in users]
    md += ['', f"**Result: {summary['results_checked']} results returned to users, "
           f"{summary['unauthorized_results']} unauthorized.**", '',
           '## Summary — top-1 result per user', '',
           '| Question | Area | ' + ' | '.join(names[u] for u in users) + ' |',
           '|---|---|' + '---|' * len(users)]
    for e in report:
        cells = []
        for u in users:
            r = e['users'][u]
            cells.append(f"`{r[0]['document_id']}` {r[0]['cosine_distance']}" if r else '—')
        md.append(f"| {e['question']} | {e['area']} | " + ' | '.join(cells) + ' |')

    md += ['', f"## After the relevance cutoff (cosine distance <= {summary['max_distance']})", '',
           'Chunks that would be passed to an answer generator. Raw top-k above is the evidence; '
           f'when 0 chunks pass, the user gets: *"{NO_ANSWER}"* (same message whether the relevant '
           'content is restricted or absent).', '',
           '| Question | ' + ' | '.join(names[u] for u in users) + ' |', '|---|' + '---|' * len(users)]
    for e in report:
        cells = []
        for u in users:
            n = sum(r['within_cutoff'] for r in e['users'][u])
            cells.append(f"{n}/{summary['k']}" if n else 'no answer')
        md.append(f"| {e['question']} | " + ' | '.join(cells) + ' |')

    for e in report:
        md += ['', f"## {e['question']}", '', f"Primary knowledge area: **{e['area']}**", '',
               '### Ground truth (admin, no access control)', '',
               '| Rank | Document | Heading | Groups | Distance | ' + ' | '.join(names[u] for u in users) + ' |',
               '|---|---|---|---|---|' + '---|' * len(users)]
        for g in e['ground_truth']:
            md.append(f"| {g['rank']} | [`{g['document_id']}`]({g['source_url']}) #{g['chunk_no']} | "
                      f"{g['heading']} | {g['groups']} | {g['cosine_distance']} | "
                      + ' | '.join(tick(g['visible_to'][u]) for u in users) + ' |')
        for u in users:
            md += ['', f"### {names[u]} ({', '.join(sorted(user_groups[u]))})", '',
                   '| Rank | Document | Heading | Distance | Source | Authorized | Cutoff |', '|---|---|---|---|---|---|---|']
            for r in e['users'][u]:
                md.append(f"| {r['rank']} | `{r['document_id']}` #{r['chunk_no']} | {r['heading']} | "
                          f"{r['cosine_distance']} | {r['source_url']} | {tick(r['authorized'])} | "
                          f"{keep(r['within_cutoff'])} |")
            if not e['users'][u]:
                md.append('| — | no authorized chunks | | | | | |')
    return '\n'.join(md) + '\n'


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--k', type=int, default=5)
    main(p.parse_args().k)
