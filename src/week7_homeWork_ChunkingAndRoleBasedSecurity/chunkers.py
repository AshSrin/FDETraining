"""Exercise A — four chunking strategies applied to the same cleaned Markdown.

Every chunker takes (text, title) and returns a list of Chunk objects. Sizes are in characters
(BGE-small truncates at 512 tokens, roughly 2,000 characters of English, so every strategy keeps
chunks below that).
"""
from dataclasses import dataclass
import re

CHUNK_SIZE = 800        # target characters per chunk (≈200 tokens)
CHUNK_OVERLAP = 100     # characters repeated between neighbouring chunks (fixed / recursive / markdown)
MIN_SECTION = 200       # markdown: sections smaller than this are merged into the next section
SEMANTIC_PERCENTILE = 90
SEMANTIC_MIN, SEMANTIC_MAX = 200, 1500
RECURSIVE_SEPARATORS = ['\n\n', '\n', '. ', ' ', '']


@dataclass
class Chunk:
    text: str                 # text that is stored and embedded
    heading_path: str = ''    # "Title > Section > Subsection" when the strategy knows it


# --------------------------------------------------------------------------- 1. fixed-size
def fixed_size(text, title='', size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Slide a window of `size` characters forward by (size - overlap). Ignores structure."""
    step = size - overlap
    return [Chunk(text[i:i + size].strip()) for i in range(0, len(text), step)
            if text[i:i + size].strip() and (i == 0 or i + overlap < len(text))]


# --------------------------------------------------------------------------- 2. recursive
def _merge(splits, sep, size, overlap):
    """Greedily pack splits into chunks <= size, carrying trailing splits forward as overlap."""
    docs, current, total = [], [], 0
    for s in splits:
        add = len(s) + (len(sep) if current else 0)
        if current and total + add > size:
            docs.append(sep.join(current))
            while current and (total > overlap or total + add > size):
                total -= len(current[0]) + (len(sep) if len(current) > 1 else 0)
                current.pop(0)
            add = len(s) + (len(sep) if current else 0)
        current.append(s)
        total += add
    if current:
        docs.append(sep.join(current))
    return [d.strip() for d in docs if d.strip()]


def _recursive_split(text, separators, size, overlap):
    sep = next((s for s in separators if s == '' or s in text), '')
    if sep == '':
        step = max(size - overlap, 1)
        return [text[i:i + size] for i in range(0, len(text), step)]
    remaining = separators[separators.index(sep) + 1:]
    out, small = [], []
    for piece in text.split(sep):
        if len(piece) <= size:
            small.append(piece)
            continue
        if small:
            out.extend(_merge(small, sep, size, overlap))
            small = []
        out.extend(_recursive_split(piece, remaining, size, overlap))
    if small:
        out.extend(_merge(small, sep, size, overlap))
    return out


MIN_FRAGMENT = 50  # pieces shorter than this (e.g. a lone "```") are glued onto the previous piece


def recursive_texts(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    out = []
    for t in (t.strip() for t in _recursive_split(text, RECURSIVE_SEPARATORS, size, overlap)):
        if not t:
            continue
        if out and len(t) < MIN_FRAGMENT:
            out[-1] = f'{out[-1]}\n{t}'
        else:
            out.append(t)
    return out


def recursive(text, title='', size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split on paragraphs, then lines, then sentences, then words — only as far as needed."""
    return [Chunk(t) for t in recursive_texts(text, size, overlap)]


# --------------------------------------------------------------------------- 3. markdown-aware
_HEADING = re.compile(r'^(#{1,6})\s+(.+?)\s*#*\s*$')


def markdown_sections(text, title=''):
    """Yield (heading_path, heading_line, body) per heading. Headings inside code fences are ignored."""
    sections, stack, heading_line, body, in_fence = [], [], '', [], False

    def flush():
        if heading_line or ''.join(body).strip():
            sections.append((' > '.join(h for _, h in stack) or title, heading_line, '\n'.join(body).strip()))

    for line in text.splitlines():
        if line.lstrip().startswith(('```', '~~~')):
            in_fence = not in_fence
        m = None if in_fence else _HEADING.match(line)
        if m:
            flush()
            level = len(m.group(1))
            stack = [(lvl, h) for lvl, h in stack if lvl < level] + [(level, m.group(2))]
            heading_line, body = line, []
        else:
            body.append(line)
    flush()
    return sections


def markdown_aware(text, title='', size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, min_section=MIN_SECTION):
    """One chunk per heading section, prefixed with its heading path. Small sections are merged
    forward (a parent's short intro joins its first subsection); large sections are split
    recursively, and every piece keeps the heading path."""
    merged, carry = [], ''
    for path, heading_line, body in markdown_sections(text, title):
        block = f'{carry}\n\n{heading_line}\n\n{body}'.strip() if carry else body
        if len(block) < min_section:
            carry = f'{carry}\n\n{heading_line}\n\n{body}'.strip() if carry else f'{heading_line}\n\n{body}'.strip()
            continue
        merged.append((path, block))
        carry = ''
    if carry:  # trailing small section: attach to the previous one
        if merged:
            merged[-1] = (merged[-1][0], f'{merged[-1][1]}\n\n{carry}')
        else:
            merged.append((title, carry))

    chunks = []
    for path, body in merged:
        prefix = f'{path}\n\n'
        if len(prefix) + len(body) <= size:
            chunks.append(Chunk(prefix + body, path))
        else:
            for piece in recursive_texts(body, size - len(prefix), overlap):
                chunks.append(Chunk(prefix + piece, path))
    return chunks


# --------------------------------------------------------------------------- 4. semantic
_SENTENCE_END = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9`*\[_(])')


def semantic_units(text):
    """Split into sentence-level units; code fences stay whole. Returns [(separator_before, unit)]."""
    units, in_fence, fence, para = [], False, [], []

    def flush_para():
        if para:
            sentences = _SENTENCE_END.split(' '.join(l.strip() for l in para))
            for i, s in enumerate(sentences):
                units.append(('\n\n' if i == 0 else ' ', s))
            para.clear()

    for line in text.splitlines():
        if line.lstrip().startswith(('```', '~~~')):
            if not in_fence:
                flush_para()
                in_fence, fence = True, [line]
            else:
                fence.append(line)
                units.append(('\n\n', '\n'.join(fence)))
                in_fence, fence = False, []
            continue
        if in_fence:
            fence.append(line)
        elif not line.strip():
            flush_para()
        elif _HEADING.match(line) or re.match(r'^\s*([*+-]|\d+\.)\s', line):
            flush_para()  # headings and list items are their own units
            units.append(('\n\n' if _HEADING.match(line) else '\n', line.strip()))
        else:
            para.append(line)
    flush_para()
    if fence:
        units.append(('\n\n', '\n'.join(fence)))
    return [(sep, u) for sep, u in units if u.strip()]


def semantic(text, title='', embed_fn=None, percentile=SEMANTIC_PERCENTILE,
             min_chars=SEMANTIC_MIN, max_chars=SEMANTIC_MAX):
    """Embed each unit; start a new chunk where the cosine distance between neighbouring units is in
    the top (100 - percentile)% for this document. min/max character guards stop tiny or oversized
    chunks."""
    import numpy as np
    if embed_fn is None:
        from common import embed as embed_fn
    units = [(sep if i == 0 else '\n', piece)          # oversized units (long code blocks) are pre-split
             for sep, u in semantic_units(text)
             for i, piece in enumerate([u] if len(u) <= max_chars else recursive_texts(u, max_chars, 0))]
    if len(units) < 2:
        return [Chunk(text.strip())]
    vectors = np.array(embed_fn([u[:2000] for _, u in units]), dtype=float)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    distances = 1 - np.sum(vectors[:-1] * vectors[1:], axis=1)
    threshold = np.percentile(distances, percentile)

    chunks, current = [], units[0][1]
    for (sep, unit), dist in zip(units[1:], distances):
        topic_shift = dist > threshold and len(current) >= min_chars
        too_big = len(current) + len(sep) + len(unit) > max_chars
        if topic_shift or too_big:
            chunks.append(Chunk(current.strip()))
            current = unit
        else:
            current += sep + unit
    chunks.append(Chunk(current.strip()))
    return [c for c in chunks if c.text]


STRATEGIES = {
    'fixed_size': fixed_size,
    'recursive': recursive,
    'markdown_aware': markdown_aware,
    'semantic': semantic,
}
