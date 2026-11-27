-- Exercise B — storage schema for attributable chunks and embeddings.
-- Run as the database owner/admin (bootstrap.py). Idempotent: safe to re-run.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS k8srag;
REVOKE ALL ON SCHEMA k8srag FROM PUBLIC;

-- Security groups that documents can be shared with (fictional access policy).
CREATE TABLE IF NOT EXISTS k8srag.groups (
    group_name  text PRIMARY KEY,
    description text NOT NULL
);

-- One row per source Markdown file, with everything needed to cite it.
CREATE TABLE IF NOT EXISTS k8srag.documents (
    document_id     text PRIMARY KEY,                -- e.g. APP-deployment
    tenant_id       text NOT NULL,
    title           text NOT NULL,
    description     text NOT NULL DEFAULT '',
    access_category text NOT NULL,                   -- Application / Platform / Security Engineering, Shared knowledge
    classification  text NOT NULL CHECK (classification IN ('restricted', 'shared')),
    filename        text NOT NULL,
    source_path     text NOT NULL,                   -- content/en/docs/concepts/...
    source_url      text NOT NULL,                   -- https://kubernetes.io/docs/...
    github_url      text NOT NULL,                   -- commit-pinned GitHub link
    license         text NOT NULL,
    chunk_strategy  text NOT NULL,
    ingested_at     timestamptz NOT NULL DEFAULT now()
);

-- Group permissions per document (document-level ACL).
CREATE TABLE IF NOT EXISTS k8srag.document_acl (
    document_id text NOT NULL REFERENCES k8srag.documents(document_id) ON DELETE CASCADE,
    group_name  text NOT NULL REFERENCES k8srag.groups(group_name),
    PRIMARY KEY (document_id, group_name)
);

-- Retrieval units: text, position, heading and 384-d BGE-small embedding.
CREATE TABLE IF NOT EXISTS k8srag.chunks (
    chunk_id     bigserial PRIMARY KEY,
    document_id  text NOT NULL REFERENCES k8srag.documents(document_id) ON DELETE CASCADE,
    tenant_id    text NOT NULL,
    chunk_no     integer NOT NULL CHECK (chunk_no >= 0),
    heading_path text NOT NULL,                      -- e.g. "Deployments > Updating a Deployment"
    chunk_text   text NOT NULL,
    char_count   integer GENERATED ALWAYS AS (char_length(chunk_text)) STORED,
    embedding    vector(384) NOT NULL,
    UNIQUE (document_id, chunk_no)
);
CREATE INDEX IF NOT EXISTS chunks_document_id_idx ON k8srag.chunks(document_id);
CREATE INDEX IF NOT EXISTS document_acl_group_idx ON k8srag.document_acl(group_name);
-- No HNSW/IVFFlat index on purpose: ~1.1k rows makes an exact scan instant, and an approximate
-- index combined with Row-Level Security can return fewer than k rows (filtering happens after
-- the index picks its candidates). See README "Known limitations".
