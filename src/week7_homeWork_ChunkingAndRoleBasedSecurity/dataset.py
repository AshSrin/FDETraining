"""Load the 30 selected Kubernetes documents with attributable metadata and access policy."""
from pathlib import Path
import csv
import re
from cleaning import clean_markdown

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'k8s_docs'
LICENSE = 'CC BY 4.0 (kubernetes/website)'

# Fictional access policy for this exercise: source area -> ID prefix and permitted group.
CATEGORIES = {
    'Application Engineering': ('APP', 'APPLICATION_ENGINEERING', 'restricted'),
    'Platform Engineering': ('PLAT', 'PLATFORM_ENGINEERING', 'restricted'),
    'Security Engineering': ('SEC', 'SECURITY_ENGINEERING', 'restricted'),
    'Shared knowledge': ('SHARED', 'ALL_EMPLOYEES', 'shared'),
}
EXPECTED_COUNTS = {'APP': 10, 'PLAT': 10, 'SEC': 5, 'SHARED': 5}


def source_commit():
    m = re.search(r'commit ([0-9a-f]{40})', (DATA / 'SOURCE.md').read_text())
    if not m:
        raise RuntimeError('Pinned commit not found in data/k8s_docs/SOURCE.md')
    return m.group(1)


def load_documents():
    commit = source_commit()
    docs = []
    with (DATA / 'index.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            prefix, group, visibility = CATEGORIES[row['access_category']]
            source_path = row['source_path']                       # content/en/docs/concepts/...
            local = DATA / source_path.removeprefix('content/en/docs/')
            raw = local.read_text(encoding='utf-8')
            meta, text, leftovers = clean_markdown(raw)
            docs.append({
                'document_id': f"{prefix}-{Path(row['filename']).stem}",
                'title': meta['title'] or row['title'],
                'description': meta['description'],
                'access_category': row['access_category'],
                'classification': visibility,
                'permitted_groups': [group],
                'filename': row['filename'],
                'source_path': source_path,
                'github_url': f'https://github.com/kubernetes/website/blob/{commit}/{source_path}',
                'source_url': row['docs_url'],
                'license': LICENSE,
                'raw': raw,
                'text': text,
                'leftover_shortcodes': leftovers,
            })
    counts = {p: sum(d['document_id'].startswith(p + '-') for d in docs) for p in EXPECTED_COUNTS}
    if counts != EXPECTED_COUNTS:
        raise ValueError(f'Unexpected document split {counts}; expected {EXPECTED_COUNTS}')
    ids = [d['document_id'] for d in docs]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate document IDs')
    return docs


if __name__ == '__main__':
    for d in load_documents():
        print(f"{d['document_id']:32} {d['permitted_groups'][0]:24} raw={len(d['raw']):6} "
              f"clean={len(d['text']):6} leftover_shortcodes={d['leftover_shortcodes']}  {d['title']}")
