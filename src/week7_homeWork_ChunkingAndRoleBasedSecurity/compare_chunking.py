"""Exercise A — run all four chunkers on the same 30 cleaned documents and write evidence.

Outputs:
  evidence/chunking_comparison.md   human-readable comparison (copied into README)
  evidence/chunking_stats.json      raw numbers

Besides size statistics it runs a small in-memory retrieval check (no database, no RLS) with the
four Exercise D questions, so the recommendation rests on retrieval behaviour, not only on shape.
"""
from pathlib import Path
import json
import re
import statistics
import time
import numpy as np
from chunkers import STRATEGIES, CHUNK_SIZE, CHUNK_OVERLAP, SEMANTIC_PERCENTILE, MIN_SECTION
from common import embed, MODEL
from dataset import load_documents

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'evidence'
EXAMPLE_DOC = 'APP-deployment'
QUESTIONS = [
    ('How does a Kubernetes Deployment manage application replicas?', 'APP-deployment'),
    ('What are PersistentVolumes and PersistentVolumeClaims?', 'PLAT-persistent-volumes'),
    ('What are recommended Kubernetes RBAC practices?', 'SEC-rbac-good-practices'),
    ('What are the main Kubernetes components?', 'SHARED-components'),
]
SETTINGS = {
    'fixed_size': f'{CHUNK_SIZE} chars, {CHUNK_OVERLAP} overlap',
    'recursive': f'{CHUNK_SIZE} chars, {CHUNK_OVERLAP} overlap; ¶ → line → sentence → word',
    'markdown_aware': f'split on #–######; ≤{CHUNK_SIZE} chars, {CHUNK_OVERLAP} overlap inside long sections; '
                      f'sections <{MIN_SECTION} merged forward',
    'semantic': f'sentence units, break at p{SEMANTIC_PERCENTILE} cosine distance; 200–1500 chars',
}
OVERLAP = {'fixed_size': CHUNK_OVERLAP, 'recursive': f'≤{CHUNK_OVERLAP}',
           'markdown_aware': f'≤{CHUNK_OVERLAP} (only inside long sections)', 'semantic': 0}

CLEAN_END = re.compile(r'([.!?:;)\]`|*_]|```)\s*$')


def has_heading(chunk, strategy):
    if strategy == 'markdown_aware' and chunk.heading_path:
        return True
    return bool(re.search(r'^#{1,6} ', chunk.text, flags=re.M))


def starts_at_heading(chunk, strategy):
    return (strategy == 'markdown_aware' and bool(chunk.heading_path)) or chunk.text.startswith('#')


def broken_fence(text):
    return text.count('```') % 2 == 1


def mid_sentence_start(text):
    return text[:1].islower()


def clean_end(text):
    last = text.rstrip().splitlines()[-1] if text.strip() else ''
    return bool(CLEAN_END.search(last)) or bool(re.match(r'^\s*([*+-]|\d+\.)\s', last))


def boundary(a, b, width=110):
    tail = a.text[-width:].replace('\n', '⏎')
    head = b.text[:width].replace('\n', '⏎')
    return f'…{tail}  ‖  {head}…'


def pick_examples(chunks, strategy):
    good = poor = fallback = None
    for a, b in zip(chunks, chunks[1:]):
        bad = broken_fence(a.text) or not clean_end(a.text) or mid_sentence_start(b.text)
        if bad and poor is None:
            poor = boundary(a, b)
        if not bad and fallback is None:
            fallback = boundary(a, b)
        if not bad and starts_at_heading(b, strategy) and good is None:
            good = boundary(a, b)
    return good or fallback or '(none found)', poor or '(none found)'


def retrieval_check(chunks_by_doc):
    """Cosine top-5 over all chunks of one strategy (unrestricted; RLS is tested later)."""
    flat = [(doc_id, c) for doc_id, cs in chunks_by_doc.items() for c in cs]
    matrix = np.array(embed([c.text for _, c in flat]), dtype=float)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    qvecs = np.array(embed([q for q, _ in QUESTIONS]), dtype=float)
    qvecs /= np.linalg.norm(qvecs, axis=1, keepdims=True)
    results = []
    for (question, expected), qv in zip(QUESTIONS, qvecs):
        dist = 1 - matrix @ qv
        top = np.argsort(dist)[:5]
        top_docs = [flat[i][0] for i in top]
        rank = next((r + 1 for r, d in enumerate(top_docs) if d == expected), None)
        results.append({
            'question': question, 'expected': expected, 'top5_docs': top_docs,
            'top1_distance': round(float(dist[top[0]]), 4),
            'expected_rank': rank, 'expected_in_top5': sum(d == expected for d in top_docs),
            'top1_preview': flat[top[0]][1].text[:160].replace('\n', ' '),
        })
    return results


def main():
    docs = load_documents()
    OUT.mkdir(exist_ok=True)
    report = {}
    for name, chunker in STRATEGIES.items():
        started = time.monotonic()
        chunks_by_doc = {d['document_id']: chunker(d['text'], d['title']) for d in docs}
        elapsed = time.monotonic() - started
        all_chunks = [c for cs in chunks_by_doc.values() for c in cs]
        sizes = [len(c.text) for c in all_chunks]
        n = len(all_chunks)
        good, poor = pick_examples(chunks_by_doc[EXAMPLE_DOC], name)
        smallest = min(all_chunks, key=lambda c: len(c.text))
        print(f'{name}: {n} chunks in {elapsed:.1f}s — running retrieval check')
        report[name] = {
            'settings': SETTINGS[name],
            'overlap': OVERLAP[name],
            'total_chunks': n,
            'avg_chars': round(statistics.mean(sizes)),
            'median_chars': round(statistics.median(sizes)),
            'min_chars': min(sizes),
            'max_chars': max(sizes),
            'pct_under_200': round(100 * sum(s < 200 for s in sizes) / n, 1),
            'pct_with_heading': round(100 * sum(has_heading(c, name) for c in all_chunks) / n, 1),
            'pct_start_at_heading': round(100 * sum(starts_at_heading(c, name) for c in all_chunks) / n, 1),
            'pct_mid_sentence_start': round(100 * sum(mid_sentence_start(c.text) for c in all_chunks) / n, 1),
            'pct_clean_end': round(100 * sum(clean_end(c.text) for c in all_chunks) / n, 1),
            'pct_broken_code_fence': round(100 * sum(broken_fence(c.text) for c in all_chunks) / n, 1),
            'chunk_seconds': round(elapsed, 1),
            'good_boundary': good,
            'poor_boundary': poor,
            'smallest_chunk': smallest.text[:200].replace('\n', '⏎'),
            'retrieval': retrieval_check(chunks_by_doc),
        }
    (OUT / 'chunking_stats.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
    (OUT / 'chunking_comparison.md').write_text(render(report, len(docs)))
    print(f'Wrote {OUT / "chunking_comparison.md"}')
    write_html(report, len(docs))


def render(r, n_docs):
    names = list(r)
    rows = [
        ('Settings', 'settings'), ('Overlap (chars)', 'overlap'), ('Total chunks', 'total_chunks'),
        ('Average size (chars)', 'avg_chars'), ('Median size', 'median_chars'),
        ('Minimum size', 'min_chars'), ('Maximum size', 'max_chars'),
        ('% chunks < 200 chars', 'pct_under_200'),
        ('% chunks carrying a section heading', 'pct_with_heading'),
        ('% chunks starting at a heading', 'pct_start_at_heading'),
        ('% chunks starting mid-sentence', 'pct_mid_sentence_start'),
        ('% chunks ending at a clean boundary', 'pct_clean_end'),
        ('% chunks with a split code block', 'pct_broken_code_fence'),
        ('Chunking time (s)', 'chunk_seconds'),
    ]
    md = [f'# Chunking comparison — {n_docs} Kubernetes documents',
          '', f'Generated by `compare_chunking.py`. Sizes are characters of cleaned Markdown. '
          f'Embedding model: `{MODEL}`.', '',
          '| Metric | ' + ' | '.join(names) + ' |', '|---|' + '---|' * len(names)]
    for label, key in rows:
        md.append(f'| {label} | ' + ' | '.join(str(r[n][key]) for n in names) + ' |')

    md += ['', '## Retrieval check (unrestricted, in-memory, top-5 cosine)', '',
           'Rank of the first chunk from the expected document, and how many of the top-5 chunks '
           'come from it. Lower top-1 distance = closer match.', '',
           '| Question | Expected doc | ' + ' | '.join(names) + ' |', '|---|---|' + '---|' * len(names)]
    for i, (q, expected) in enumerate(QUESTIONS):
        cells = []
        for n in names:
            x = r[n]['retrieval'][i]
            cells.append(f"rank {x['expected_rank'] or '—'}, {x['expected_in_top5']}/5, d={x['top1_distance']}")
        md.append(f'| {q} | `{expected}` | ' + ' | '.join(cells) + ' |')

    md += ['', f'## Boundary examples (`{EXAMPLE_DOC}`)', '',
           '`‖` marks where one chunk ends and the next begins; `⏎` is a newline.', '']
    for n in names:
        md += [f'### {n}', '', f'- **Good:** `{r[n]["good_boundary"]}`',
               f'- **Poor:** `{r[n]["poor_boundary"]}`',
               f'- **Smallest chunk in corpus:** `{r[n]["smallest_chunk"]}`', '']
    return '\n'.join(md)


HTML_OUT = ROOT / 'data' / 'chunking_comparison.html'
HIGHER_BETTER = {'pct_with_heading', 'pct_start_at_heading', 'pct_clean_end'}
LOWER_BETTER = {'pct_under_200', 'pct_mid_sentence_start', 'pct_broken_code_fence'}
RECOMMENDED = 'markdown_aware'


def render_html(r, n_docs):
    from html import escape as e
    names = list(r)
    rows = [
        ('Settings', 'settings'), ('Overlap (chars)', 'overlap'), ('Total chunks', 'total_chunks'),
        ('Average size (chars)', 'avg_chars'), ('Median size', 'median_chars'),
        ('Minimum size', 'min_chars'), ('Maximum size', 'max_chars'),
        ('% chunks &lt; 200 chars', 'pct_under_200'),
        ('% chunks carrying a section heading', 'pct_with_heading'),
        ('% chunks starting at a heading', 'pct_start_at_heading'),
        ('% chunks starting mid-sentence', 'pct_mid_sentence_start'),
        ('% chunks ending at a clean boundary', 'pct_clean_end'),
        ('% chunks with a split code block', 'pct_broken_code_fence'),
        ('Chunking time (s)', 'chunk_seconds'),
    ]
    head = ''.join(f'<th class="{"rec" if n == RECOMMENDED else ""}">{e(n)}</th>' for n in names)

    metric_rows = []
    for label, key in rows:
        values = [r[n][key] for n in names]
        best = (max(values) if key in HIGHER_BETTER else min(values) if key in LOWER_BETTER else None)
        cells = ''.join(
            f'<td class="{"best" if best is not None and v == best else ""} {"rec" if n == RECOMMENDED else ""}">'
            f'{e(str(v))}</td>' for n, v in zip(names, values))
        metric_rows.append(f'<tr><th scope="row">{label}</th>{cells}</tr>')

    retrieval_rows = []
    for i, (q, expected) in enumerate(QUESTIONS):
        hits = [r[n]['retrieval'][i]['expected_in_top5'] for n in names]
        cells = ''
        for n, h in zip(names, hits):
            x = r[n]['retrieval'][i]
            cells += (f'<td class="{"best" if h == max(hits) else ""} {"rec" if n == RECOMMENDED else ""}">'
                      f'<b>{h}/5</b><span class="sub">rank {x["expected_rank"] or "—"} · d={x["top1_distance"]}</span></td>')
        retrieval_rows.append(f'<tr><th scope="row">{e(q)}<span class="sub"><code>{e(expected)}</code></span></th>{cells}</tr>')

    examples = ''.join(
        f'<section class="card"><h3>{e(n)}{" <span class=pill>recommended</span>" if n == RECOMMENDED else ""}</h3>'
        f'<p class="lbl good-l">Good boundary</p><pre>{e(r[n]["good_boundary"])}</pre>'
        f'<p class="lbl poor-l">Poor boundary</p><pre>{e(r[n]["poor_boundary"])}</pre>'
        f'<p class="lbl">Smallest chunk in corpus</p><pre>{e(r[n]["smallest_chunk"])}</pre></section>'
        for n in names)

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chunking Comparison</title>
<style>
:root {{ --bg:#f7f8fa; --panel:#fff; --text:#1d2330; --muted:#5d6678; --line:#dde1e8;
        --accent:#0a7d55; --accent-bg:#e6f4ee; --best:#d9f2e5; --poor:#b3412e; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#14171c; --panel:#1c2028; --text:#e6e9ef; --muted:#9aa3b2;
        --line:#2e3440; --accent:#4cc596; --accent-bg:#183129; --best:#1f4434; --poor:#ef8a76; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
main {{ max-width:1100px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:1.7rem; margin:0 0 4px; }} h2 {{ margin:40px 0 8px; font-size:1.25rem; }} h3 {{ margin:0 0 8px; font-size:1.05rem; }}
.meta, .sub, .note {{ color:var(--muted); }} .sub {{ display:block; font-size:.8rem; font-weight:400; }}
.wrap {{ overflow-x:auto; background:var(--panel); border:1px solid var(--line); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; min-width:640px; }}
th, td {{ padding:9px 12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
thead th {{ font-size:.85rem; text-transform:uppercase; letter-spacing:.03em; color:var(--muted); }}
tbody tr:last-child > * {{ border-bottom:0; }}
td {{ font-variant-numeric:tabular-nums; }}
.rec {{ background:var(--accent-bg); }} thead th.rec {{ color:var(--accent); }}
td.best {{ background:var(--best); font-weight:600; }}
.callout {{ background:var(--accent-bg); border-left:4px solid var(--accent); padding:14px 18px; border-radius:6px; margin:20px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr)); gap:14px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px; min-width:0; }}
pre {{ white-space:pre-wrap; word-break:break-word; background:var(--bg); border:1px solid var(--line);
       border-radius:6px; padding:8px 10px; font-size:.8rem; margin:0 0 10px; }}
.lbl {{ margin:6px 0 4px; font-size:.78rem; font-weight:600; text-transform:uppercase; color:var(--muted); }}
.good-l {{ color:var(--accent); }} .poor-l {{ color:var(--poor); }}
.pill {{ font-size:.7rem; background:var(--accent); color:var(--panel); padding:2px 8px; border-radius:99px; vertical-align:middle; }}
code {{ font-size:.85em; }}
</style></head><body><main>
<h1>Chunking comparison</h1>
<p class="meta">{n_docs} Kubernetes documents (kubernetes/website, CC BY 4.0) · embedding model <code>{e(MODEL)}</code>
· generated by <code>compare_chunking.py</code>. Sizes are characters of cleaned Markdown.</p>

<div class="callout"><b>Recommendation: markdown-aware chunking.</b> It is the only strategy where every chunk carries
its section heading path and none start mid-sentence, it is as fast as fixed-size, and it ties or leads on retrieval.
Semantic chunking has similarly clean boundaries but needs an embedding pass at chunking time and can separate a heading
from the text it introduces (see its poor boundary below).</div>

<h2>Size and boundary metrics</h2>
<p class="note">Highlighted cells are the best value for metrics with a clear direction.</p>
<div class="wrap"><table><thead><tr><th>Metric</th>{head}</tr></thead><tbody>{"".join(metric_rows)}</tbody></table></div>

<h2>Retrieval check</h2>
<p class="note">Unrestricted, in-memory top-5 cosine search (no RLS). Bold = how many of the top-5 chunks come from the
expected document; rank = position of its first chunk; d = top-1 cosine distance (lower is closer).</p>
<div class="wrap"><table><thead><tr><th>Question / expected document</th>{head}</tr></thead><tbody>{"".join(retrieval_rows)}</tbody></table></div>

<h2>Boundary examples <span class="sub">from <code>{EXAMPLE_DOC}</code> · ‖ marks a chunk boundary, ⏎ a newline</span></h2>
<div class="grid">{examples}</div>
</main></body></html>
'''


def write_html(report, n_docs):
    HTML_OUT.write_text(render_html(report, n_docs), encoding='utf-8')
    print(f'Wrote {HTML_OUT}')


if __name__ == '__main__':
    import sys
    if '--html-only' in sys.argv:   # rebuild the HTML from the saved stats without re-embedding
        write_html(json.loads((OUT / 'chunking_stats.json').read_text()), len(load_documents()))
    else:
        main()
