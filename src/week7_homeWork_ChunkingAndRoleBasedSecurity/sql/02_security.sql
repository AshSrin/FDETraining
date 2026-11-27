-- Exercise C — identities, group membership and Row-Level Security.
-- Run as the database owner/admin (bootstrap.py). Idempotent: safe to re-run.
-- Role creation and GRANTs live in bootstrap.py because the reader role name/password come from .env.

-- Demo identities (application users, NOT PostgreSQL login roles).
CREATE TABLE IF NOT EXISTS k8srag.users (
    user_id      text PRIMARY KEY,
    display_name text NOT NULL,
    tenant_id    text NOT NULL
);

-- Group membership: the single source of truth for what a user may read.
CREATE TABLE IF NOT EXISTS k8srag.user_groups (
    user_id    text NOT NULL REFERENCES k8srag.users(user_id) ON DELETE CASCADE,
    group_name text NOT NULL REFERENCES k8srag.groups(group_name),
    PRIMARY KEY (user_id, group_name)
);
CREATE INDEX IF NOT EXISTS user_groups_group_idx ON k8srag.user_groups(group_name);

-- Authorization check used by the RLS policies.
--  * Identity comes from transaction-local settings app.user_id / app.tenant_id, set by the
--    trusted backend (search.py simulates it).
--  * SECURITY DEFINER lets the check read users/user_groups/document_acl while the reader role has
--    no privileges on those tables.
--  * It deliberately does not query k8srag.documents or k8srag.chunks (both are RLS-protected),
--    so the policy can never recurse into itself.
--  * Missing/empty/unknown identity => no matching rows => false (fail closed).
CREATE OR REPLACE FUNCTION k8srag.may_read(p_document_id text)
RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, k8srag
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM k8srag.document_acl a
        JOIN k8srag.user_groups ug ON ug.group_name = a.group_name
        JOIN k8srag.users u        ON u.user_id = ug.user_id
        WHERE a.document_id = p_document_id
          AND u.user_id   = nullif(current_setting('app.user_id', true), '')
          AND u.tenant_id = nullif(current_setting('app.tenant_id', true), '')
    );
$$;
REVOKE ALL ON FUNCTION k8srag.may_read(text) FROM PUBLIC;

-- Row-Level Security on every table that holds document content or metadata.
-- FORCE applies the policies to the table owner too (superusers still bypass RLS — admin use only).
ALTER TABLE k8srag.chunks    ENABLE ROW LEVEL SECURITY;
ALTER TABLE k8srag.chunks    FORCE  ROW LEVEL SECURITY;
ALTER TABLE k8srag.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE k8srag.documents FORCE  ROW LEVEL SECURITY;

DROP POLICY IF EXISTS chunks_authorized ON k8srag.chunks;
CREATE POLICY chunks_authorized ON k8srag.chunks
    FOR SELECT
    USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')
           AND k8srag.may_read(document_id));

DROP POLICY IF EXISTS documents_authorized ON k8srag.documents;
CREATE POLICY documents_authorized ON k8srag.documents
    FOR SELECT
    USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')
           AND k8srag.may_read(document_id));
-- No INSERT/UPDATE/DELETE policies: with RLS enabled, non-superusers cannot write at all.
