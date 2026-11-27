"""Exercise C/D — permission-aware retrieval. Access control is enforced INSIDE PostgreSQL.

DEMO ONLY: --user simulates an identity that a trusted backend would normally take from a verified
login. This script connects as the restricted reader role (never admin) and sets the identity
transaction-locally; RLS then filters chunks and documents before any row leaves the database.
Unknown identities are passed through on purpose so the database (not Python) denies them.

Relevance cutoff: chunks with cosine distance above MAX_COSINE_DISTANCE are dropped in the same SQL
query. When nothing passes, the caller gets one neutral message that is identical whether the
relevant content is restricted or simply does not exist, so restricted documents are not revealed.
"""
import argparse
from common import connect, embed, TENANT, MAX_DISTANCE

KNOWN_USERS = ('priya', 'arjun', 'meena', 'divya')
NO_ANSWER = 'No relevant information found in the documents you have access to.'

SEARCH_SQL = """
SELECT c.document_id, d.title, c.chunk_no, c.heading_path, d.source_url, d.classification,
       round((c.embedding <=> %(q)s::vector)::numeric, 4) AS cosine_distance,
       left(c.chunk_text, 160) AS preview
FROM k8srag.chunks c
JOIN k8srag.documents d USING (document_id)
WHERE %(max_d)s::float8 IS NULL OR (c.embedding <=> %(q)s::vector) <= %(max_d)s::float8
ORDER BY c.embedding <=> %(q)s::vector
LIMIT %(k)s
"""


def run_search(user_id, question, k=5, vector=None, max_distance=MAX_DISTANCE):
    """Top-k chunks this identity is authorized to read (RLS) and that are within max_distance.
    max_distance=None disables the relevance cutoff (used for raw evidence in run_matrix.py)."""
    vector = vector if vector is not None else embed([question])[0]
    with connect() as db:                      # restricted reader role, never admin
        with db.transaction():                 # identity lives only for this transaction
            db.execute('SELECT set_config(%s, %s, true)', ('app.user_id', user_id.strip().lower()))
            db.execute('SELECT set_config(%s, %s, true)', ('app.tenant_id', TENANT))
            return db.execute(SEARCH_SQL, {'q': vector, 'k': k, 'max_d': max_distance}).fetchall()


def print_results(user_id, question, rows, max_distance=MAX_DISTANCE):
    cutoff = 'off' if max_distance is None else f'<= {max_distance}'
    print(f'IDENTITY={user_id} | QUESTION={question!r} | cutoff {cutoff} | results={len(rows)}')
    for rank, (doc, title, no, heading, url, cls, dist, _preview) in enumerate(rows, 1):
        print(f'  {rank}. d={dist}  {doc} #{no} ({cls})  {heading}\n       {url}')
    if not rows:
        print(f'  {NO_ANSWER}')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Permission-aware retrieval (demo identity simulation).')
    p.add_argument('--user', required=True, help=f"demo identity, e.g. {', '.join(KNOWN_USERS)}")
    p.add_argument('--question', required=True)
    p.add_argument('--k', type=int, default=5)
    p.add_argument('--max-distance', type=float, default=MAX_DISTANCE,
                   help=f'relevance cutoff (default {MAX_DISTANCE})')
    p.add_argument('--no-cutoff', action='store_true', help='return the top-k regardless of distance')
    a = p.parse_args()
    if a.user.lower() not in KNOWN_USERS:
        print(f'WARNING: {a.user!r} is not a demo user — querying anyway so PostgreSQL decides.')
    max_d = None if a.no_cutoff else a.max_distance
    print_results(a.user, a.question, run_search(a.user, a.question, a.k, max_distance=max_d), max_d)
