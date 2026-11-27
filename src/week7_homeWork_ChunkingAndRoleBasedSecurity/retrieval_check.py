"""Exercise B — cosine-distance retrieval returning ranked, attributable results.

ADMIN VIEW, NO ACCESS CONTROL: this proves storage + ranking work and serves as the
"ground truth" ranking that Exercise D compares each user's RLS-filtered results against.
End-user retrieval goes through search.py (Exercise C), never through this script.
"""
import argparse
from pathlib import Path
from common import connect, embed

ROOT = Path(__file__).resolve().parent
QUESTIONS = [
    'How does a Kubernetes Deployment manage application replicas?',
    'What are PersistentVolumes and PersistentVolumeClaims?',
    'What are recommended Kubernetes RBAC practices?',
    'What are the main Kubernetes components?',
]

RETRIEVAL_SQL = """
SELECT c.document_id, d.title, c.chunk_no, c.heading_path, d.source_url, d.classification,
       array_to_string(ARRAY(SELECT group_name FROM k8srag.document_acl a
                             WHERE a.document_id = d.document_id ORDER BY 1), ',') AS groups,
       round((c.embedding <=> %(q)s::vector)::numeric, 4) AS cosine_distance
FROM k8srag.chunks c
JOIN k8srag.documents d USING (document_id)
ORDER BY c.embedding <=> %(q)s::vector
LIMIT %(k)s
"""


def admin_search(question, k=5, vector=None):
    vector = vector if vector is not None else embed([question])[0]
    with connect(admin=True) as db:
        return db.execute(RETRIEVAL_SQL, {'q': vector, 'k': k}).fetchall()


def main(k):
    lines = ['# Exercise B — admin cosine retrieval (no access control)', '',
             'Ground-truth ranking over all stored chunks. Lower cosine distance = more similar.', '']
    for q in QUESTIONS:
        rows = admin_search(q, k)
        print(f'\nQ: {q}')
        lines += [f'## {q}', '', '| Rank | Document | Chunk | Heading | Groups | Distance | Source |',
                  '|---|---|---|---|---|---|---|']
        for rank, (doc, title, no, heading, url, cls, groups, dist) in enumerate(rows, 1):
            print(f'  {rank}. {dist}  {doc} #{no}  [{groups}]  {heading}\n      {url}')
            lines.append(f'| {rank} | `{doc}` {title} | {no} | {heading} | {groups} | {dist} | {url} |')
        lines.append('')
    out = ROOT / 'evidence' / 'exercise_b_retrieval.md'
    out.parent.mkdir(exist_ok=True)
    out.write_text('\n'.join(lines))
    print(f'\nWrote {out}')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--k', type=int, default=5)
    main(p.parse_args().k)
