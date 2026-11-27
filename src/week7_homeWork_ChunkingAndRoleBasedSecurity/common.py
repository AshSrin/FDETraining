"""Shared configuration, database connections and embeddings."""
from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
# Fictional technology organisation from the business scenario. Stamped on every document, chunk
# and user; RLS only returns rows whose tenant matches the caller's app.tenant_id.
TENANT = os.getenv('TENANT_ID', 'TECHORG_ENGINEERING')
# Relevance cutoff (cosine distance). Calibrated on the Exercise D matrix: on-topic authorized chunks
# scored 0.153–0.216, off-topic fallbacks 0.251+. Chunks above it are never passed on.
MAX_DISTANCE = float(os.getenv('MAX_COSINE_DISTANCE', '0.23'))
MODEL = os.getenv('EMBED_MODEL', 'BAAI/bge-small-en-v1.5')
EMBED_DIM = 384
DBNAME = os.getenv('DATABASE_NAME', 'k8s_raglab')
SERVER_URL = os.environ.get('POSTGRES_SERVER_URL', '')
READER_ROLE = os.environ.get('READER_ROLE', 'k8s_rag_reader')
READER_PASSWORD = os.environ.get('READER_PASSWORD', '')


def connection_string(*, admin=False, server=False):
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    if not SERVER_URL:
        raise RuntimeError('Set POSTGRES_SERVER_URL in .env (see .env.example)')
    settings = conninfo_to_dict(SERVER_URL)
    if not server:
        settings['dbname'] = DBNAME
    if not admin and not server:  # retrieval always uses the restricted, RLS-bound role
        settings['user'] = READER_ROLE
        settings['password'] = READER_PASSWORD
    return make_conninfo(**settings)


def connect(*, admin=False, server=False, autocommit=False, register=True):
    from psycopg import connect as pg_connect
    from pgvector.psycopg import register_vector
    db = pg_connect(connection_string(admin=admin, server=server), autocommit=autocommit)
    if not server and register:
        register_vector(db)
    return db


@lru_cache(maxsize=1)
def get_model():
    from fastembed import TextEmbedding
    print(f'Loading local embedding model: {MODEL} (first run downloads weights)')
    return TextEmbedding(model_name=MODEL)


def embed(texts):
    vectors = [v.tolist() for v in get_model().embed(list(texts), batch_size=32)]
    if any(len(v) != EMBED_DIM for v in vectors):
        raise RuntimeError(f'Expected {EMBED_DIM}-dimensional embeddings from {MODEL}')
    return vectors
