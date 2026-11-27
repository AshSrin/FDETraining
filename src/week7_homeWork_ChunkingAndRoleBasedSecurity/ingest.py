"""Exercise B — chunk, embed and store the 30 Kubernetes documents with metadata and ACLs.

Uses the strategy recommended in Exercise A (markdown_aware). Runs as admin in one transaction;
re-running replaces each document's ACL and chunks, so it is safe to repeat.
"""
import argparse
import time
from chunkers import STRATEGIES
from common import connect, embed, TENANT
from dataset import load_documents

DEFAULT_STRATEGY = 'markdown_aware'


def main(strategy=DEFAULT_STRATEGY):
    chunker = STRATEGIES[strategy]
    docs = load_documents()
    rows = []
    for d in docs:
        for no, chunk in enumerate(chunker(d['text'], d['title'])):
            rows.append((d['document_id'], no, chunk.heading_path or d['title'], chunk.text))
    print(f'{len(docs)} documents -> {len(rows)} chunks using {strategy}')

    started = time.monotonic()
    vectors = []
    for i in range(0, len(rows), 64):
        vectors.extend(embed([r[3] for r in rows[i:i + 64]]))
        print(f'  embedded {len(vectors)}/{len(rows)}', end='\r')
    print(f'\nEmbedding took {time.monotonic() - started:.1f}s')

    with connect(admin=True) as db, db.transaction():
        for d in docs:
            db.execute("""
                INSERT INTO k8srag.documents (document_id, tenant_id, title, description, access_category,
                    classification, filename, source_path, source_url, github_url, license, chunk_strategy)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (document_id) DO UPDATE SET
                    tenant_id=excluded.tenant_id, title=excluded.title, description=excluded.description,
                    access_category=excluded.access_category, classification=excluded.classification,
                    filename=excluded.filename, source_path=excluded.source_path,
                    source_url=excluded.source_url, github_url=excluded.github_url,
                    license=excluded.license, chunk_strategy=excluded.chunk_strategy, ingested_at=now()""",
                (d['document_id'], TENANT, d['title'], d['description'], d['access_category'],
                 d['classification'], d['filename'], d['source_path'], d['source_url'],
                 d['github_url'], d['license'], strategy))
            db.execute('DELETE FROM k8srag.document_acl WHERE document_id=%s', (d['document_id'],))
            for group in d['permitted_groups']:
                db.execute('INSERT INTO k8srag.document_acl(document_id, group_name) VALUES (%s,%s)',
                           (d['document_id'], group))
            db.execute('DELETE FROM k8srag.chunks WHERE document_id=%s', (d['document_id'],))
        with db.cursor() as cur:
            cur.executemany("""INSERT INTO k8srag.chunks
                               (document_id, tenant_id, chunk_no, heading_path, chunk_text, embedding)
                               VALUES (%s,%s,%s,%s,%s,%s)""",
                            [(doc_id, TENANT, no, path, text, vec)
                             for (doc_id, no, path, text), vec in zip(rows, vectors)])

    with connect(admin=True) as db:
        n_docs, n_chunks, n_acl = db.execute("""SELECT (SELECT count(*) FROM k8srag.documents),
                                                       (SELECT count(*) FROM k8srag.chunks),
                                                       (SELECT count(*) FROM k8srag.document_acl)""").fetchone()
    print(f'Stored: {n_docs} documents, {n_chunks} chunks, {n_acl} ACL rows')
    print('Next: python retrieval_check.py')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--strategy', default=DEFAULT_STRATEGY, choices=list(STRATEGIES))
    main(p.parse_args().strategy)
