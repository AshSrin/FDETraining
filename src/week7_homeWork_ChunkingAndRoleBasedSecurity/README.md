# Enterprise RAG: Chunking & Role-Based Security

**Testleaf FDE Program, Week 7 homework.** This is an enterprise knowledge assistant for a technology organisation (`TECHORG_ENGINEERING`) with three restricted engineering teams and shared organisation-wide knowledge. It ingests 30 real Kubernetes documentation pages and compares four chunking strategies. Embeddings are stored in PostgreSQL with pgvector. Access is enforced with **PostgreSQL Row-Level Security**, so a chunk the caller is not authorized to see never leaves the database.

```
question ──► embed (BGE-small, local) ──► search.py ──► PostgreSQL (k8s_rag_reader login)
                                           │ SET app.user_id / app.tenant_id (transaction-local)
                                           ▼
                         RLS policy on chunks + documents ──► may_read(document_id)
                                           │      (document_acl ⋈ user_groups ⋈ users)
                                           ▼
                    only authorized AND relevant (cosine distance ≤ 0.23) chunks returned
```

> **Retrieval only.** No generative LLM is called. The chunks returned by `search.py` are exactly what would be passed to an LLM as context, so all enforcement happens before that point.

---

## Contents
1. [Project layout](#1-project-layout)
2. [Installation and execution](#2-installation-and-execution)
3. [Dataset, licence and selected files](#3-dataset-licence-and-selected-files)
4. [Exercise A: chunking comparison](#4-exercise-a-chunking-comparison)
5. [Exercise B: embeddings and pgvector storage](#5-exercise-b-embeddings-and-pgvector-storage)
6. [Exercise C: role-based access, RLS and trust boundary](#6-exercise-c-role-based-access-rls-and-trust-boundary)
7. [Exercise D: same question, different results](#7-exercise-d-same-question-different-results)
8. [Exercise E: negative tests and revocation](#8-exercise-e-negative-tests-and-revocation)
9. [Known limitations and proposed improvements](#9-known-limitations-and-proposed-improvements)
10. [Final reflection](#10-final-reflection)

---

## 1. Project layout

| Path | Purpose |
|---|---|
| `data/k8s_docs/` | 30 unmodified Kubernetes Markdown files, plus `index.csv`, `manifest.jsonl` and `SOURCE.md` (source commit and licence) |
| `data/users.json` | The four demo identities and their group memberships |
| `cleaning.py` | Converts Hugo front matter and shortcodes into clean Markdown, in memory only (the raw files are never changed) |
| `dataset.py` | Loads the 30 documents with IDs, titles, URLs, licence, classification and permitted groups |
| `chunkers.py` | **Exercise A**: fixed-size, recursive, markdown-aware and semantic chunkers |
| `compare_chunking.py` | **Exercise A**: runs all four chunkers and writes the comparison evidence |
| `sql/01_schema.sql` | **Exercise B**: tables for documents, chunks (`vector(384)`), groups and ACLs |
| `sql/02_security.sql` | **Exercise C**: users, memberships, `may_read()` and the RLS policies |
| `bootstrap.py` | Creates the database, schema, groups, reader role and users |
| `ingest.py` | **Exercise B**: chunks, embeds and stores everything in one transaction |
| `retrieval_check.py` | **Exercise B**: admin "ground truth" cosine ranking, with no access control |
| `search.py` | **Exercise C/D**: permission-aware search that always runs as the restricted reader |
| `run_matrix.py` | **Exercise D**: 4 questions × 4 users, with an independent authorization check |
| `test_security.py` | **Exercise E**: negative tests, revocation and restore, plus hardening checks |
| `evidence/` | Generated evidence (Markdown, JSON and the test transcript) |
| `data/chunking_comparison.html` | Visual version of the chunking comparison |

---

## 2. Installation and execution

**Prerequisites:**
- Python 3.12
- Docker Desktop, or any PostgreSQL 15+ with the `pgvector` extension
- An internet connection on the first run, to download the embedding model (about 130 MB)

```bash
cd src/week7_homeWork_ChunkingAndRoleBasedSecurity

# 1. Database (skip if PostgreSQL + pgvector is already running on 5432)
docker compose up -d

# 2. Python environment
python3.12 -m venv .venv
source .venv/bin/activate              # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Configuration: copy the template and fill in YOUR local values (never commit .env)
cp .env.example .env
```

| `.env` key | Meaning |
|---|---|
| `POSTGRES_SERVER_URL` | **Admin** login on an existing database (usually `postgres`). Used only by bootstrap, ingest and the revoke/restore steps of the tests. |
| `DATABASE_NAME` | Created automatically (`k8s_raglab`) |
| `READER_ROLE` / `READER_PASSWORD` | Restricted login used for all retrieval. Created by `bootstrap.py`. |
| `EMBED_MODEL` | `BAAI/bge-small-en-v1.5` |
| `TENANT_ID` | `TECHORG_ENGINEERING` |
| `MAX_COSINE_DISTANCE` | Relevance cutoff, `0.23` |

**Run order:**

```bash
python compare_chunking.py        # Exercise A (~4 min; --html-only rebuilds the HTML from saved stats)
python bootstrap.py               # database, schema, groups, reader role, RLS, users
python ingest.py                  # Exercise B: 30 docs -> 1,137 chunks -> pgvector (~35 s)
python retrieval_check.py         # Exercise B: admin ground-truth ranking
python search.py --user priya --question "How does a Kubernetes Deployment manage application replicas?"
python run_matrix.py              # Exercise D
python test_security.py           # Exercise E (exit code 1 if any check fails)
```

All scripts are safe to re-run. Re-running `bootstrap.py` resets the demo memberships to `data/users.json`.

**Inspect the data in DBeaver:** connect to database `k8s_raglab` and open schema `k8srag`. As the admin you see every row, because superusers bypass RLS. To see what a user sees, connect as `k8s_rag_reader` and run:

```sql
BEGIN;
SELECT set_config('app.user_id','arjun',true), set_config('app.tenant_id','TECHORG_ENGINEERING',true);
SELECT document_id FROM k8srag.documents ORDER BY 1;   -- PLAT-* and SHARED-* only
COMMIT;
```

---

## 3. Dataset, licence and selected files

- **Source:** [github.com/kubernetes/website](https://github.com/kubernetes/website), directory `content/en/docs`, pinned to commit `61712ddb619690242534e6e86bb5646c88f16c2e` (2026-11-26).
- **Licence:** Kubernetes documentation © The Kubernetes Authors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The files are stored unmodified. Cleaning happens only in memory at ingest time.
- **Access policy:** the department restrictions are a **fictional** access policy created for this exercise only.

Each document stores: `document_id`, `title`, `description`, `filename`, `source_path`, a `source_url` on kubernetes.io, a `github_url` pinned to the commit, `license`, `classification` (`restricted` or `shared`) and its permitted group.

**Cleaning** (`cleaning.py`):
- Front matter is removed; the title and description are kept as metadata.
- Notes, cautions and warnings become `**Note:**` (and so on).
- `glossary_tooltip` shortcodes become their display text.
- `code_sample` shortcodes become `[code sample: file]`.
- `heading "whatsnext"` becomes `## What's next`.
- `feature-state` shortcodes become readable text.
- HTML comments and `{#anchors}` are removed.

**0 shortcodes remain** across the 30 files.

| ID | Title | Path (under `content/en/docs/`) | Group | URL | Chunks |
|---|---|---|---|---|---|
| `APP-pod-lifecycle` | Pod Lifecycle | `concepts/workloads/pods/pod-lifecycle.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) | 87 |
| `APP-init-containers` | Init Containers | `concepts/workloads/pods/init-containers.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) | 29 |
| `APP-sidecar-containers` | Sidecar Containers | `concepts/workloads/pods/sidecar-containers.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/) | 16 |
| `APP-probes` | Liveness, Readiness, and Startup Probes | `concepts/workloads/pods/probes.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/pods/probes/) | 44 |
| `APP-deployment` | Deployments | `concepts/workloads/controllers/deployment.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) | 112 |
| `APP-replicaset` | ReplicaSet | `concepts/workloads/controllers/replicaset.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) | 35 |
| `APP-statefulset` | StatefulSets | `concepts/workloads/controllers/statefulset.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) | 51 |
| `APP-daemonset` | DaemonSet | `concepts/workloads/controllers/daemonset.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) | 30 |
| `APP-job` | Jobs | `concepts/workloads/controllers/job.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/controllers/job/) | 124 |
| `APP-cron-jobs` | CronJob | `concepts/workloads/controllers/cron-jobs.md` | APPLICATION_ENGINEERING | [link](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) | 26 |
| `PLAT-volumes` | Volumes | `concepts/storage/volumes.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/volumes/) | 57 |
| `PLAT-persistent-volumes` | Persistent Volumes | `concepts/storage/persistent-volumes.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) | 106 |
| `PLAT-storage-classes` | Storage Classes | `concepts/storage/storage-classes.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/storage-classes/) | 46 |
| `PLAT-dynamic-provisioning` | Dynamic Volume Provisioning | `concepts/storage/dynamic-provisioning.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/) | 11 |
| `PLAT-ephemeral-volumes` | Ephemeral Volumes | `concepts/storage/ephemeral-volumes.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/ephemeral-volumes/) | 23 |
| `PLAT-projected-volumes` | Projected Volumes | `concepts/storage/projected-volumes.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/projected-volumes/) | 23 |
| `PLAT-volume-snapshots` | Volume Snapshots | `concepts/storage/volume-snapshots.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/volume-snapshots/) | 24 |
| `PLAT-ephemeral-storage` | Local ephemeral storage | `concepts/storage/ephemeral-storage.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/ephemeral-storage/) | 21 |
| `PLAT-storage-capacity` | Storage Capacity | `concepts/storage/storage-capacity.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/storage-capacity/) | 8 |
| `PLAT-volume-attributes-classes` | Volume Attributes Classes | `concepts/storage/volume-attributes-classes.md` | PLATFORM_ENGINEERING | [link](https://kubernetes.io/docs/concepts/storage/volume-attributes-classes/) | 9 |
| `SEC-service-accounts` | Service Accounts | `concepts/security/service-accounts.md` | SECURITY_ENGINEERING | [link](https://kubernetes.io/docs/concepts/security/service-accounts/) | 39 |
| `SEC-pod-security-standards` | Pod Security Standards | `concepts/security/pod-security-standards.md` | SECURITY_ENGINEERING | [link](https://kubernetes.io/docs/concepts/security/pod-security-standards/) | 42 |
| `SEC-rbac-good-practices` | Role Based Access Control Good Practices | `concepts/security/rbac-good-practices.md` | SECURITY_ENGINEERING | [link](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) | 29 |
| `SEC-secrets-good-practices` | Good practices for Kubernetes Secrets | `concepts/security/secrets-good-practices.md` | SECURITY_ENGINEERING | [link](https://kubernetes.io/docs/concepts/security/secrets-good-practices/) | 11 |
| `SEC-security-checklist` | Security Checklist | `concepts/security/security-checklist.md` | SECURITY_ENGINEERING | [link](https://kubernetes.io/docs/concepts/security/security-checklist/) | 42 |
| `SHARED-components` | Kubernetes Components | `concepts/overview/components.md` | ALL_EMPLOYEES | [link](https://kubernetes.io/docs/concepts/overview/components/) | 5 |
| `SHARED-kubernetes-api` | The Kubernetes API | `concepts/overview/kubernetes-api.md` | ALL_EMPLOYEES | [link](https://kubernetes.io/docs/concepts/overview/kubernetes-api/) | 32 |
| `SHARED-kubectl` | The kubectl command-line tool | `concepts/overview/kubectl.md` | ALL_EMPLOYEES | [link](https://kubernetes.io/docs/concepts/overview/kubectl/) | 11 |
| `SHARED-namespaces` | Namespaces | `concepts/overview/working-with-objects/namespaces.md` | ALL_EMPLOYEES | [link](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) | 14 |
| `SHARED-labels` | Labels and Selectors | `concepts/overview/working-with-objects/labels.md` | ALL_EMPLOYEES | [link](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) | 30 |

**Totals:**
- Application Engineering: 10 files
- Platform Engineering: 10 files
- Security Engineering: 5 files
- Shared knowledge: 5 files
- **30 documents, 1,137 chunks** (markdown-aware)

---

## 4. Exercise A: chunking comparison

All four strategies ran on the same 30 cleaned documents. Sizes are in characters; BGE-small truncates input at about 2,000 characters. The full report with boundary examples is in [`evidence/chunking_comparison.md`](evidence/chunking_comparison.md), and a visual version is in [`data/chunking_comparison.html`](data/chunking_comparison.html).

| Metric | Fixed-size | Recursive | **Markdown-aware** | Semantic |
|---|---|---|---|---|
| Settings | 800 chars | 800 chars; split on ¶ → line → sentence → word | split on headings; ≤800 chars; sections <200 chars merged forward | sentence units; break at the 90th-percentile cosine distance; 200–1500 chars |
| Overlap | 100 | ≤100 | ≤100 (long sections only) | 0 |
| Total chunks | 829 | 942 | **1137** | 610 |
| Avg / median size | 785 / 800 | 625 / 669 | 560 / 608 | 929 / 966 |
| Min / max size | 123 / 800 | 87 / 827 | 76 / 800 | 82 / 1501 |
| % chunks carrying their section heading | 54.4 | 55.8 | **100.0** | 55.4 |
| % chunks starting at a heading | 4.0 | 28.5 | **100.0** | 21.1 |
| % chunks starting mid-sentence | 78.2 | 2.7 | **0.0** | 4.4 |
| % chunks ending at a clean boundary | 19.3 | 76.9 | **92.4** | 90.5 |
| % chunks splitting a code block | 13.8 | 2.9 | 2.5 | **1.6** |
| Chunking time | instant | instant | instant | 115 s (embeds every sentence) |

**Retrieval check.** This is an in-memory top-5 search with no access control. Each cell shows how many of the top-5 chunks come from the expected document. The expected document ranked #1 for all four strategies.

| Question | Fixed | Recursive | Markdown-aware | Semantic |
|---|---|---|---|---|
| Deployment replicas → `APP-deployment` | 2/5 | 2/5 | 2/5 | 1/5 |
| PV and PVC → `PLAT-persistent-volumes` | 3/5 | 4/5 | 4/5 | 4/5 |
| RBAC practices → `SEC-rbac-good-practices` | 3/5 | 4/5 | 4/5 | 3/5 |
| Main components → `SHARED-components` | 2/5 | 1/5 | **4/5** | 3/5 |

**Boundary examples from `APP-deployment`** (`‖` marks a chunk boundary):
- **Good (markdown-aware):** `…if your use case is not covered below. ‖ Deployments > Use Case⏎⏎The following are typical use cases…` The new chunk begins exactly at a section and carries its heading path.
- **Poor (fixed-size):** `…to see if it succeeds or not.⏎* [Declare the new ‖ in the background. Check the status…` This cuts mid-link, and 78% of fixed chunks start mid-sentence.
- **Poor (recursive):** a `kubectl describe` output block split across two chunks, so neither half makes sense alone.
- **Poor (semantic):** `## Updating a Deployment` is left at the end of one chunk, while its body text starts the next chunk.

**Recommendation: markdown-aware chunking for technical documentation.**
- Kubernetes docs are already organised by their authors into headed sections that each cover one concept. Splitting on those headings matches the authors' own topic boundaries at no cost.
- Every chunk carries its heading path (e.g. `Deployments > Writing a Deployment Spec > Replicas`). That path is embedded with the text, which improves retrieval, and it is stored as a citation.
- It never starts mid-sentence, ties or leads on retrieval, and is as fast as fixed-size chunking.
- Cost: it produces more and smaller chunks; 3.6% are under 200 characters (short "What's next" link lists).

---

## 5. Exercise B: embeddings and pgvector storage

- **Model:** `BAAI/bge-small-en-v1.5`, run locally through `fastembed` (ONNX, CPU). It produces 384 dimensions, which `common.embed()` checks.
- **Database:** PostgreSQL 17 + pgvector 0.8, database `k8s_raglab`, schema `k8srag`.
- **Distance:** cosine distance, using the pgvector `<=>` operator (0 means identical; lower is closer).

```
groups(group_name PK, description)
documents(document_id PK, tenant_id, title, description, access_category,
          classification CHECK IN ('restricted','shared'), filename, source_path,
          source_url, github_url, license, chunk_strategy, ingested_at)
document_acl(document_id FK→documents, group_name FK→groups, PK(document_id, group_name))
chunks(chunk_id PK, document_id FK→documents, tenant_id, chunk_no, heading_path,
       chunk_text, char_count GENERATED, embedding vector(384), UNIQUE(document_id, chunk_no))
users(user_id PK, display_name, tenant_id)                                -- sql/02_security.sql
user_groups(user_id FK→users, group_name FK→groups, PK(user_id, group_name))
```

**Ranked, attributable retrieval query** (`search.py`):

```sql
SELECT c.document_id, d.title, c.chunk_no, c.heading_path, d.source_url, d.classification,
       round((c.embedding <=> :q)::numeric, 4) AS cosine_distance
FROM   k8srag.chunks c JOIN k8srag.documents d USING (document_id)
WHERE  (c.embedding <=> :q) <= :max_distance          -- relevance cutoff (0.23)
ORDER  BY c.embedding <=> :q
LIMIT  :k;
```

Admin ground truth for all four questions is in [`evidence/exercise_b_retrieval.md`](evidence/exercise_b_retrieval.md). The expected document ranks #1 for every question, for example `PLAT-persistent-volumes #70 "Persistent Volumes > PersistentVolumeClaims"` at d = 0.1661.

**No ANN index (HNSW or IVFFlat), on purpose.** With 1,137 rows an exact scan takes milliseconds and always returns the true top-k *after* RLS filtering. An approximate index picks its candidates before RLS filters them, so it can silently return fewer than k rows (see §9).

---

## 6. Exercise C: role-based access, RLS and trust boundary

### Group memberships (`data/users.json`)

| Employee | Groups | May retrieve | Verified visible documents |
|---|---|---|---|
| Priya | APPLICATION_ENGINEERING, ALL_EMPLOYEES | Application + shared | APP 10 + SHARED 5 |
| Arjun | PLATFORM_ENGINEERING, ALL_EMPLOYEES | Platform + shared | PLAT 10 + SHARED 5 |
| Meena | SECURITY_ENGINEERING, ALL_EMPLOYEES | Security + shared | SEC 5 + SHARED 5 |
| Divya | APPLICATION_ENGINEERING, SECURITY_ENGINEERING, ALL_EMPLOYEES | Both departments + shared | APP 10 + SEC 5 + SHARED 5 |

### RLS policy (`sql/02_security.sql`)

```sql
ALTER TABLE k8srag.chunks    ENABLE ROW LEVEL SECURITY;  ALTER TABLE k8srag.chunks    FORCE ROW LEVEL SECURITY;
ALTER TABLE k8srag.documents ENABLE ROW LEVEL SECURITY;  ALTER TABLE k8srag.documents FORCE ROW LEVEL SECURITY;

CREATE POLICY chunks_authorized ON k8srag.chunks FOR SELECT
USING (tenant_id = nullif(current_setting('app.tenant_id', true), '')
       AND k8srag.may_read(document_id));          -- same policy on k8srag.documents
```

`k8srag.may_read(document_id)` is a `SECURITY DEFINER` SQL function. It returns true only if a chain `document_acl → user_groups → users` exists for the caller's `app.user_id` within their `app.tenant_id`.
- **Fail closed:** if the identity is missing, empty, unknown or has the wrong tenant, there are no matching rows, so the result is `false` and zero rows come back.
- **No recursion:** the function never reads the RLS-protected tables, so a policy can never call itself in a loop.
- **No writes:** there are no INSERT, UPDATE or DELETE policies, so non-superusers cannot write to RLS tables at all.
- **Permissions are data:** granting or revoking access means changing a `user_groups` or `document_acl` row. Chunks and embeddings are never touched.

### Database roles

| Role | Used by | Privileges |
|---|---|---|
| Admin / owner (`POSTGRES_SERVER_URL`) | `bootstrap.py`, `ingest.py`, revoke/restore in `test_security.py` | Full DDL/DML. Never used to answer user questions. |
| `k8s_rag_reader` (LOGIN, `NOSUPERUSER NOBYPASSRLS`) | `search.py`, `run_matrix.py`, every retrieval in `test_security.py` | `SELECT` on `chunks` and `documents` (RLS-filtered); `EXECUTE` on `may_read`. **No** access to `users`, `user_groups`, `document_acl` or `groups`. No write privileges. |

### Trust boundary

- **Trusted:** PostgreSQL (data, RLS and ACLs), the admin pipeline, and the backend that holds the reader credentials and sets `app.user_id`. In this demo, `search.py` plays the backend.
- **Untrusted:** end users, their questions, and anything downstream of retrieval, including an LLM.
- **The boundary is the database query.** Authorization is evaluated inside PostgreSQL on every row before results leave the database. It is not a label check and not a filter applied after retrieval. Nothing in Python decides access; unknown users are passed through on purpose so that PostgreSQL denies them.
- **Identity is set per transaction** (`set_config(..., true)`), so it cannot leak into the next request on a pooled connection.
- **Demo vs production:** `--user` simulates an identity for this local demo. Anyone with the reader password could call `set_config('app.user_id', …)` and impersonate someone, so the reader credentials must live only in a trusted backend. In production, that backend derives `app.user_id` from a verified login (an SSO or JWT token), and users never connect to the database directly.

---

## 7. Exercise D: same question, different results

`run_matrix.py` runs each question for all four users and does three things:
1. Produces the admin ground-truth top-5, with ✅ or ⛔ per user.
2. Records each user's own RLS-filtered top-5: document ID, chunk number, heading, cosine distance and source link.
3. Re-checks every returned result against the declared policy, independently of RLS.

**Result: 80 results returned to users, 0 unauthorized.** Full tables are in [`evidence/exercise_d_matrix.md`](evidence/exercise_d_matrix.md).

**Top-1 result per user** (document, cosine distance):

| Question (area) | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|
| Deployment replicas (App) | [`APP-deployment`](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) **0.172** | `SHARED-kubernetes-api` 0.251 | `SHARED-kubernetes-api` 0.251 | [`APP-deployment`](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) **0.172** |
| PV and PVC (Platform) | [`APP-statefulset`](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) 0.176 | [`PLAT-persistent-volumes`](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) **0.166** | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) 0.220 | [`APP-statefulset`](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) 0.176 |
| RBAC practices (Security) | `SHARED-kubernetes-api` 0.279 | `PLAT-storage-classes` 0.276 | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) **0.168** | [`SEC-rbac-good-practices`](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) **0.168** |
| Main components (Shared) | [`SHARED-components`](https://kubernetes.io/docs/concepts/overview/components/) **0.153** | same | same | same |

**Ground truth for the PV/PVC question** (admin view, no access control):

| Rank | Chunk | Distance | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|---|---|
| 1 | `PLAT-persistent-volumes #70` Persistent Volumes > PersistentVolumeClaims | 0.1661 | ⛔ | ✅ | ⛔ | ⛔ |
| 2 | `PLAT-persistent-volumes #1` Persistent Volumes > Introduction | 0.1761 | ⛔ | ✅ | ⛔ | ⛔ |
| 3 | `APP-statefulset #17` StatefulSets > Pod Identity > Stable Storage | 0.1762 | ✅ | ⛔ | ⛔ | ✅ |
| 4 | `PLAT-persistent-volumes #3` Persistent Volumes > Introduction | 0.1797 | ⛔ | ✅ | ⛔ | ⛔ |
| 5 | `PLAT-persistent-volumes #29` … > Reserving a PersistentVolume | 0.1816 | ⛔ | ✅ | ⛔ | ⛔ |

**Relevance cutoff (0.23).** Results on the user's own topic scored 0.153–0.216, and off-topic fallbacks scored 0.251 or more. `search.py` therefore drops chunks with a distance above 0.23 inside the same SQL query. When nothing passes, it returns one neutral message: *"No relevant information found in the documents you have access to."* The message is the same whether the content is restricted or absent, so the response never reveals that a restricted document exists. Without the cutoff, Arjun's top "RBAC" answer is *Storage Classes > Ceph **RBD*** (0.276), a surface-level word match rather than a real answer.

| Chunks passed on (of 5) | Priya | Arjun | Meena | Divya |
|---|---|---|---|---|
| Deployment replicas | 5 | no answer | no answer | 5 |
| PV and PVC | 2 | 5 | 1 | 3 |
| RBAC practices | no answer | no answer | 5 | 5 |
| Main components | 5 | 5 | 5 | 5 |

---

## 8. Exercise E: negative tests and revocation

`python test_security.py` passed **19/19 checks**. The transcript is in [`evidence/exercise_e_security_tests.txt`](evidence/exercise_e_security_tests.txt) and the summary in [`evidence/exercise_e_security_tests.md`](evidence/exercise_e_security_tests.md). The restricted document under test is `SEC-rbac-good-practices`, which belongs to SECURITY_ENGINEERING only.

| ID | Requirement | Evidence |
|---|---|---|
| E1 | Authorized user retrieves a restricted doc | Meena: rank 1 `SEC-rbac-good-practices #0` d = 0.1681; 29 chunks visible |
| E2 | Unauthorized user cannot | Arjun and Priya: 0 hits in their top-20, a direct chunk count of 0, and the document row is invisible |
| E3 | Revocation is immediate, with no re-embedding or re-ingest | `DELETE` of meena/SECURITY_ENGINEERING → visible chunks **29 → 0 on the next query (15 ms)**. The embedding fingerprint (1,137 chunks, md5 `2926ec27…`) is **identical** before and after. The 5 shared documents stay visible. |
| E4 | Unknown identity is denied | `intruder`, `admin` and the look-alike `'Meena '` all see 0 chunks, including through `search.py` |
| E5 | Restore brings access back | 29 chunks visible again; the top-3 ranking is identical to E1 |
| X1 | No identity set | 0 chunks (fails closed) |
| X2 | Valid user, wrong tenant `OTHER_ORG` | 0 chunks |
| X3 | Divya (multiple groups) | APP 10, SEC 5, SHARED 5, PLAT 0 |
| X4 | Reader reads `document_acl` / `user_groups` | `permission denied` |
| X5 | Reader grants itself a group / deletes chunks | `permission denied` |
| X6 | Reader runs `SET row_security = off` | Refused: *"query would be affected by row-level security policy"* |

```
ADMIN REVOKE: meena - SECURITY_ENGINEERING  (committed 11:05:27.731)
PASS  E3  Revoking SECURITY_ENGINEERING removes Meena's access on the very next query
      -> SEC-rbac-good-practices chunks visible: 29 -> 0 (next query, 15 ms); SEC-* documents visible: 0
PASS  E3  Revocation needed no re-embedding or re-ingesting
ADMIN RESTORE: meena + SECURITY_ENGINEERING  (committed 11:05:27.805)
PASS  E5  Restoring SECURITY_ENGINEERING returns Meena's authorized access
```

The restore runs in a `finally` block, so a failed run never leaves Meena locked out.

---

## 9. Known limitations and proposed improvements

| Limitation | Proposed improvement |
|---|---|
| The reader login can set any `app.user_id`, so identity is trusted, not verified, inside the database | Keep reader credentials only in the backend. Derive identity from a verified JWT or SSO token. Optionally have the database verify a signed claim, or map users to per-user roles with `SET ROLE`. |
| The admin is a superuser and bypasses RLS | Use a dedicated non-superuser owner role for ingest and a separate role for ACL management, both with audit logging |
| No ANN index; an exact scan won't scale to millions of chunks | HNSW with pgvector 0.8 iterative scans (`hnsw.iterative_scan`) so RLS filtering still fills top-k; or partition by tenant or group |
| `may_read()` runs once per row | Cache memberships per transaction, or put an `allowed_groups text[]` column on chunks with a GIN index and policy `allowed_groups && current_groups()` |
| Relevance cutoff 0.23 was calibrated on 4 questions | Build a larger labelled question set, tune the threshold per domain, add a cross-encoder reranker |
| Cleaning loses some content (`glossary_definition` text, code-sample files, tables) | Resolve glossary terms from `content/en/docs/reference/glossary`, inline referenced YAML samples |
| Markdown-aware chunking still produces 3.6% tiny chunks (link lists) | Drop or merge navigation-only sections ("What's next"); add document title and description to every chunk's embedding text |
| Documents carry one ACL group each | Support multiple groups per document, `deny` entries, and document versions |
| BGE query instruction prefix not used | Test the BGE v1.5 query prefix ("Represent this sentence for searching relevant passages: ") |
| Retrieval only, with no answer generation | Add an LLM step that receives only the post-RLS, post-cutoff chunks and must cite `source_url` and `heading_path` |

---

## 10. Final reflection

### Q1. Is semantic chunking always better than recursive or structure-aware chunking?

**No.** On this corpus it was competitive on boundaries but not better overall:
- It scored 90.5% clean endings, against 92.4% for markdown-aware, and had the fewest split code blocks (1.6%).
- It was the slowest by far: 115 s to embed every sentence, against instant for the other three.
- It had the lowest hit count on the Deployment question: 1/5, against 2/5 for the others.
- It produced the clearest heading error: `## Updating a Deployment` ended one chunk while its body began the next.

Semantic chunking guesses topic boundaries from neighbouring-sentence similarity. Technical documentation already *declares* its boundaries with headings, and structure-aware chunking uses them for free. It also keeps the heading path for citation: 100% of its chunks carry it, against about 55% for the others. Semantic chunking makes sense for unstructured text such as transcripts or emails, where no structure exists to exploit.

### Q2. If the most semantically relevant document is restricted, what should the retriever return?

It should return **only the best results the user is authorized to see, and nothing that reveals the restricted document exists**. Arjun asking about Deployments shows how this works here:
1. The best match, `APP-deployment` (0.172), is filtered out by RLS inside the query, so it never leaves the database.
2. The retriever does not say "1 restricted result hidden" or show the title, a snippet or a count. Even that would leak the document's existence.
3. The next authorized results (0.251 or more) are weak. The relevance cutoff removes them, and Arjun gets the neutral *"No relevant information found in the documents you have access to."*

If he needs the content, the right path is an access request through the owning team, not a smarter retriever.

### Q3. Why must permissions be enforced by the retrieval system instead of asking an LLM to respect them?

- **An LLM is not a security boundary.** Anything placed in its context window can be repeated, summarised or paraphrased. Prompt injection ("ignore previous instructions"), cleverly worded questions or plain model error can all leak restricted text. An instruction in the prompt is a request, not a control.
- **Once the data is in the context window, it has already left the trust boundary.** It may be logged, cached, sent to a third-party API or shown in a trace. The only safe restricted chunk is one that was never retrieved.
- **Database enforcement is deterministic and testable.** RLS denied 100% of unauthorized rows in 80 Exercise D results and 19 Exercise E checks. Revocation takes effect on the next query, and attempts to bypass it (`SET row_security = off`, reading the ACL tables, granting yourself a group) are refused by PostgreSQL itself. None of that can be guaranteed or audited for a model's behaviour.
- **One place to get it right.** Every consumer of the retriever (chat UI, API, batch jobs, a future agent) inherits the same policy, with no need to re-implement it in every prompt.

---

*Kubernetes documentation © The Kubernetes Authors, CC BY 4.0. The department access restrictions are fictional and exist only for this exercise.*
