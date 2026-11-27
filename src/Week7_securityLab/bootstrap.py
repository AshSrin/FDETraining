"""One-time safe setup: create database if missing, schema, RLS, reader, Indian demo users."""
import json
from pathlib import Path
from psycopg import sql
from common import connect, DBNAME, READER_ROLE, READER_PASSWORD, TENANT
ROOT=Path(__file__).resolve().parent

def main():
    if not READER_PASSWORD: raise RuntimeError('READER_PASSWORD is missing in .env')
    with connect(server=True, autocommit=True) as db:
        exists=db.execute('SELECT 1 FROM pg_database WHERE datname=%s',(DBNAME,)).fetchone()
        if not exists:
            db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(DBNAME)))
            print(f'Created PostgreSQL database: {DBNAME}')
        else: print(f'Using existing PostgreSQL database: {DBNAME}')
    with connect(admin=True, register=False) as db:
        # DDL of an existing schema is non-destructive to existing documents.
        db.execute((ROOT/'sql/schema.sql').read_text())
        role_exists=db.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(READER_ROLE,)).fetchone()
        if not role_exists:
            db.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(READER_ROLE),sql.Literal(READER_PASSWORD)))
        else:
            db.execute(sql.SQL('ALTER ROLE {} WITH LOGIN PASSWORD {}').format(sql.Identifier(READER_ROLE),sql.Literal(READER_PASSWORD)))
        db.execute(sql.SQL('GRANT CONNECT ON DATABASE {} TO {}').format(sql.Identifier(DBNAME),sql.Identifier(READER_ROLE)))
        db.execute(sql.SQL('GRANT USAGE ON SCHEMA raglab TO {}').format(sql.Identifier(READER_ROLE)))
        db.execute(sql.SQL('GRANT SELECT ON raglab.chunks TO {}').format(sql.Identifier(READER_ROLE)))
        db.execute(sql.SQL('GRANT EXECUTE ON FUNCTION raglab.may_read(text,text) TO {}').format(sql.Identifier(READER_ROLE)))
        # Explicitly prevent reading underlying ACL and identity tables via the restricted login.
        db.execute(sql.SQL('REVOKE ALL ON raglab.documents, raglab.document_acl, raglab.users, raglab.user_groups FROM {}').format(sql.Identifier(READER_ROLE)))
        users=json.loads((ROOT/'data/users.json').read_text())
        for u in users:
            db.execute("""INSERT INTO raglab.users(user_id,display_name,tenant_id)
                          VALUES (%s,%s,%s) ON CONFLICT(user_id) DO UPDATE
                          SET display_name=excluded.display_name,tenant_id=excluded.tenant_id""",
                       (u['user_id'],u['display_name'],TENANT))
            db.execute('DELETE FROM raglab.user_groups WHERE user_id=%s',(u['user_id'],))
            for group in u['groups']:
                db.execute('INSERT INTO raglab.user_groups(user_id,group_name) VALUES(%s,%s)',(u['user_id'],group))
    print('Next: python ingest.py')

if __name__=='__main__': main()
