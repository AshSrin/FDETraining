-- Run as database owner / admin, not as rag_reader.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS raglab;
REVOKE ALL ON SCHEMA raglab FROM PUBLIC;

CREATE TABLE IF NOT EXISTS raglab.users (
    user_id text PRIMARY KEY,
    display_name text NOT NULL,
    tenant_id text NOT NULL
);
CREATE TABLE IF NOT EXISTS raglab.user_groups (
    user_id text NOT NULL REFERENCES raglab.users(user_id) ON DELETE CASCADE,
    group_name text NOT NULL,
    PRIMARY KEY (user_id, group_name)
);
CREATE TABLE IF NOT EXISTS raglab.documents (
    document_id text PRIMARY KEY,
    tenant_id text NOT NULL,
    department text NOT NULL,
    title text NOT NULL,
    visibility text NOT NULL,
    version integer NOT NULL,
    source_path text NOT NULL
);
CREATE TABLE IF NOT EXISTS raglab.document_acl (
    document_id text NOT NULL REFERENCES raglab.documents(document_id) ON DELETE CASCADE,
    group_name text NOT NULL,
    PRIMARY KEY (document_id, group_name)
);
CREATE TABLE IF NOT EXISTS raglab.chunks (
    chunk_id bigserial PRIMARY KEY,
    document_id text NOT NULL REFERENCES raglab.documents(document_id) ON DELETE CASCADE,
    tenant_id text NOT NULL,
    chunk_no integer NOT NULL,
    chunk_text text NOT NULL,
    embedding vector(384) NOT NULL,
    UNIQUE(document_id, chunk_no)
);
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON raglab.chunks(document_id);
CREATE INDEX IF NOT EXISTS documents_tenant_idx ON raglab.documents(tenant_id);

-- SECURITY DEFINER: permissions checked against ACLs, without granting
-- rag_reader any direct SELECT on the user/group/ACL tables.
CREATE OR REPLACE FUNCTION raglab.may_read(p_document_id text, p_tenant text)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, raglab
AS $$
 SELECT EXISTS (
   SELECT 1 FROM raglab.documents d
   JOIN raglab.document_acl a ON a.document_id=d.document_id
   JOIN raglab.user_groups ug ON ug.group_name=a.group_name
   JOIN raglab.users u ON u.user_id=ug.user_id
   WHERE d.document_id=p_document_id
     AND d.tenant_id=p_tenant AND u.tenant_id=d.tenant_id
     AND u.user_id=nullif(current_setting('app.user_id', true),'')
     AND d.tenant_id=nullif(current_setting('app.tenant_id',true),'')
 );
$$;
REVOKE ALL ON FUNCTION raglab.may_read(text,text) FROM PUBLIC;

ALTER TABLE raglab.chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE raglab.chunks FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS authorized_chunks ON raglab.chunks;
CREATE POLICY authorized_chunks ON raglab.chunks FOR SELECT
USING (
  tenant_id = nullif(current_setting('app.tenant_id',true),'')
  AND raglab.may_read(document_id,tenant_id)
);
