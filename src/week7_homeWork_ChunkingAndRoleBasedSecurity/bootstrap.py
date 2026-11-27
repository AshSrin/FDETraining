"""Create the database (if missing), schema, security groups, reader role, RLS and demo users.

  sql/01_schema.sql    Exercise B — documents, chunks, groups, document ACLs
  sql/02_security.sql  Exercise C — users, memberships, may_read(), RLS policies

Never drops data. Re-running resets the four demo users' memberships to data/users.json
(this also undoes any manual revocation).
"""
import json
from psycopg import sql
from common import connect, DBNAME, ROOT, READER_ROLE, READER_PASSWORD, TENANT

GROUPS = {
    'APPLICATION_ENGINEERING': 'Application Engineering — Kubernetes workloads (concepts/workloads)',
    'PLATFORM_ENGINEERING': 'Platform Engineering — Kubernetes storage (concepts/storage)',
    'SECURITY_ENGINEERING': 'Security Engineering — Kubernetes security (concepts/security)',
    'ALL_EMPLOYEES': 'Organisation-wide shared knowledge (concepts/overview)',
}
SQL_FILES = ['01_schema.sql', '02_security.sql']


def ident(name):
    return sql.Identifier(name)


def setup_reader_role(db):
    """Least-privilege login used for ALL end-user retrieval."""
    exists = db.execute('SELECT 1 FROM pg_roles WHERE rolname=%s', (READER_ROLE,)).fetchone()
    verb = 'ALTER' if exists else 'CREATE'
    db.execute(sql.SQL(verb + ' ROLE {} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD {}')
               .format(ident(READER_ROLE), sql.Literal(READER_PASSWORD)))
    r = ident(READER_ROLE)
    db.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(ident(DBNAME), r))
    db.execute(sql.SQL('GRANT USAGE ON SCHEMA k8srag TO {}').format(r))
    db.execute(sql.SQL('GRANT SELECT ON k8srag.chunks, k8srag.documents TO {}').format(r))   # RLS-filtered
    db.execute(sql.SQL('GRANT EXECUTE ON FUNCTION k8srag.may_read(text) TO {}').format(r))
    # Identity and permission tables are never readable or writable by the reader.
    db.execute(sql.SQL('REVOKE ALL ON k8srag.users, k8srag.user_groups, k8srag.document_acl, k8srag.groups '
                       'FROM {}').format(r))
    db.execute(sql.SQL('REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON k8srag.chunks, k8srag.documents '
                       'FROM {}').format(r))
    print(f'Reader role ready: {READER_ROLE} (SELECT on chunks/documents only, subject to RLS)')


def load_users(db):
    users = json.loads((ROOT / 'data' / 'users.json').read_text())
    for u in users:
        db.execute("""INSERT INTO k8srag.users(user_id, display_name, tenant_id) VALUES (%s,%s,%s)
                      ON CONFLICT (user_id) DO UPDATE
                      SET display_name=excluded.display_name, tenant_id=excluded.tenant_id""",
                   (u['user_id'], u['display_name'], TENANT))
        db.execute('DELETE FROM k8srag.user_groups WHERE user_id=%s', (u['user_id'],))
        for group in u['groups']:
            db.execute('INSERT INTO k8srag.user_groups(user_id, group_name) VALUES (%s,%s)',
                       (u['user_id'], group))
        print(f"  {u['display_name']:6} -> {', '.join(u['groups'])}")


def main():
    if not READER_PASSWORD:
        raise RuntimeError('READER_PASSWORD is missing in .env')
    with connect(server=True, autocommit=True) as db:
        if db.execute('SELECT 1 FROM pg_database WHERE datname=%s', (DBNAME,)).fetchone():
            print(f'Using existing database: {DBNAME}')
        else:
            db.execute(sql.SQL('CREATE DATABASE {}').format(ident(DBNAME)))
            print(f'Created database: {DBNAME}')

    with connect(admin=True, register=False) as db:
        for name in SQL_FILES:
            db.execute((ROOT / 'sql' / name).read_text())
            print(f'Applied sql/{name}')
        for group, description in GROUPS.items():
            db.execute("""INSERT INTO k8srag.groups(group_name, description) VALUES (%s, %s)
                          ON CONFLICT (group_name) DO UPDATE SET description = excluded.description""",
                       (group, description))
        print(f'Groups: {", ".join(GROUPS)}')
        setup_reader_role(db)
        print('Users:')
        load_users(db)
    print('Next: python ingest.py (if not yet ingested), then python search.py --user priya --question "..."')


if __name__ == '__main__':
    main()
