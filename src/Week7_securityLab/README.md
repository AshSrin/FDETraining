# Testleaf FDE — Enterprise RAG Security Lab
## Step-by-Step Setup Guide (Windows & macOS)

**Objective:** Create a PostgreSQL database, ingest 200 synthetic enterprise documents, generate embeddings, and demonstrate secure retrieval using five Indian employee identities.

### Step 1 — Prerequisites

Install the following:

- Python **3.12**
- PostgreSQL 15 or later with pgvector, or Docker Desktop
- VS Code
- Internet connection for the initial embedding model download

### Step 2 — Extract the Lab

1. Extract `Security_Lab.zip`.
2. Open the extracted `Security_Lab` folder in VS Code.
3. Open the integrated terminal.

### Step 3 — Start PostgreSQL

**Option A: Using Docker (Windows or macOS)**

If you do not have PostgreSQL with pgvector running:

```bash
docker compose up -d
```

This starts PostgreSQL on port `5433` using the provided Docker configuration.

**Option B: Existing PostgreSQL**

If PostgreSQL with pgvector is already running, skip Docker and continue to Step 4.

### Step 4 — Configure the Database Connection

Open the included `.env` file:

```dotenv
POSTGRES_SERVER_URL=postgresql://<admin_user>:<admin_password>@127.0.0.1:5433/postgres
DATABASE_NAME=raglab
READER_ROLE=security_lab_reader
READER_PASSWORD=<choose_a_local_password>
EMBED_MODEL=BAAI/bge-small-en-v1.5
```

Update the PostgreSQL username, password, host or port if your existing server uses different settings.

**Note:** You do not need to create the `raglab` database manually. The bootstrap script creates it if it does not exist.

### Step 5 — Create the Python Virtual Environment

**macOS Terminal**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python --version
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Expected: `Python 3.12.x`

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

### Step 6 — Install Python Dependencies

**Windows and macOS**

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Wait for installation to complete successfully.

### Step 7 — Initialize the Database

**Windows and macOS**

```bash
python bootstrap.py
```

This script:

- Creates database `raglab` if missing.
- Creates schema `raglab` and enables pgvector.
- Creates the required tables and access permissions.
- Configures PostgreSQL Row-Level Security.
- Creates five demo employee identities.

### Step 8 — Ingest 200 Documents

**Windows and macOS**

```bash
python ingest.py
```

This script:

1. Reads 200 synthetic documents from HR, Finance, Procurement and Operations.
2. Splits documents into chunks.
3. Generates 384-dimensional embeddings.
4. Stores documents and chunks in PostgreSQL.
5. Assigns document-level access permissions.

The first execution downloads the embedding model.

### Step 9 — Verify Ingestion in DBeaver

Connect to:

- Host: `127.0.0.1`
- Port: `5433` (or your configured port)
- Database: `raglab`
- Username/password: As configured in `.env`

Execute:

```sql
SELECT department, COUNT(*)
FROM raglab.documents
GROUP BY department
ORDER BY department;

SELECT COUNT(*) FROM raglab.chunks;

SELECT user_id, display_name
FROM raglab.users
ORDER BY user_id;

SELECT vector_dims(embedding)
FROM raglab.chunks
LIMIT 1;
```

Expected: 200 documents, five employee identities, 384 embedding dimensions, and the generated chunks.

### Step 10 — Execute Secure Retrieval

**Windows and macOS**

**Priya — HR**

```bash
python search.py --user priya --question "employee onboarding checklist"
```

**Arjun — Finance**

```bash
python search.py --user arjun --question "employee onboarding checklist"
```

**Meena — Procurement**

```bash
python search.py --user meena --question "vendor purchase order approval"
```

**Rahul — Operations**

```bash
python search.py --user rahul --question "operational incident management"
```

**Divya — Finance and Procurement**

```bash
python search.py --user divya --question "vendor purchase order budget approval"
```

Compare the retrieved document IDs and cosine distances. Different users may receive different results based on their permissions.

### Step 11 — Run Enterprise Security Tests

**Windows and macOS**

```bash
python test_security.py
```

Verify the following:

- Users can retrieve documents they are authorized to read.
- Users cannot retrieve restricted documents.
- All-employee documents remain accessible.
- Unknown identities are denied.
- Revoking group membership removes access.
- Restoring membership restores access.
- Direct access to the restricted ACL table is rejected.

A successful run displays `PASS` for each security check.

### Step 12 — Classroom Discussion

Discuss the following questions:

1. Why can Priya retrieve HR documents that Arjun cannot?
2. Why can Arjun access an HR document marked `all_employees`?
3. Does cosine similarity override document permissions?
4. What happens when a user's group membership is revoked?
5. Why must permissions be enforced before retrieved chunks reach an LLM?

**Key takeaway:** Enterprise RAG combines semantic retrieval with identity, document permissions and database-enforced security.

---

### Important Notes

- Use **Python 3.12** with the supplied lab dependencies.
- Do not start a second Docker PostgreSQL instance if port `5433` is occupied.
- `bootstrap.py` creates missing database objects; it does not drop the database or schema.
- Rerunning `ingest.py` can replace existing chunks and ACLs for matching documents.
- The included `.env` credentials are for local classroom use only.
- The `--user` option simulates identities. Production applications require verified authentication and must not expose database credentials to learners.
- HNSW indexing is not required for this security lab.