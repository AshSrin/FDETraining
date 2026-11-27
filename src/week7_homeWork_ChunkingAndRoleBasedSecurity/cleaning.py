"""Turn raw Kubernetes Hugo Markdown into clean Markdown suitable for chunking and embedding.

The raw files in data/k8s_docs/ are never modified (attribution). Cleaning happens in memory:
front matter is removed (title/description kept as metadata), Hugo shortcodes are converted
into plain-text equivalents or removed, and HTML comments / heading anchors are dropped.
"""
import re

HEADING_LABELS = {
    'whatsnext': "What's next",
    'prerequisites': 'Before you begin',
    'objectives': 'Objectives',
    'cleanup': 'Clean up',
    'synopsis': 'Synopsis',
    'options': 'Options',
}

# A Hugo shortcode: {{< name attrs >}} or {{% name attrs %}}; may span several lines.
_SC = r'\{\{[<%]\s*{name}\b(?P<attrs>[^}]*?)\s*[>%]\}\}'


def _attr(attrs, key):
    m = re.search(rf'{key}\s*=\s*"([^"]*)"', attrs or '')
    return m.group(1).strip() if m else ''


def _sub(name, repl, text):
    return re.sub(_SC.replace("{name}", re.escape(name)), repl, text)


def split_front_matter(raw):
    """Return (metadata, body). Only the top-level title/description keys are parsed."""
    meta = {'title': '', 'description': ''}
    if not raw.startswith('---'):
        return meta, raw
    end = raw.find('\n---', 3)
    if end == -1:
        return meta, raw
    front, body = raw[3:end], raw[end + 4:]
    lines = front.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'^(title|description):\s*(.*)$', line)  # top-level keys only (no indent)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value in ('>', '>-', '|', '|-'):  # folded / literal block: collect indented lines
            block = []
            for nxt in lines[i + 1:]:
                if nxt.startswith((' ', '\t')) or not nxt.strip():
                    block.append(nxt.strip())
                else:
                    break
            value = ' '.join(b for b in block if b)
        meta[key] = value.strip('"\'')
    return meta, body


def clean_markdown(raw):
    """Return (metadata, cleaned_markdown, leftover_shortcode_count)."""
    meta, text = split_front_matter(raw)

    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)

    text = _sub('glossary_tooltip',
                lambda m: _attr(m['attrs'], 'text') or _attr(m['attrs'], 'term_id').replace('-', ' '), text)
    text = _sub('glossary_definition',
                lambda m: ' '.join(filter(None, [_attr(m['attrs'], 'prepend'),
                                                 f"(glossary definition: {_attr(m['attrs'], 'term_id')})"])), text)

    # Heading shortcodes: "## {{% heading "whatsnext" %}}" or a bare "{{% heading ... %}}" line.
    def heading(m):
        key = re.search(r'"(\w+)"', m['attrs'] or '')
        return HEADING_LABELS.get(key.group(1) if key else '', 'Section')
    text = re.sub(r'^(#+\s*)?' + _SC.replace("{name}", "heading"),
                  lambda m: (m.group(1) or '## ') + heading(m), text, flags=re.M)

    for admonition in ('note', 'caution', 'warning'):
        text = _sub(admonition, f'**{admonition.title()}:** ', text)
        text = _sub('/' + admonition, '', text)

    def feature_state(m):
        version, state = _attr(m['attrs'], 'for_k8s_version'), _attr(m['attrs'], 'state')
        gate = _attr(m['attrs'], 'feature_gate_name')
        if version or state:
            return f'_Feature state: Kubernetes {version} [{state}]_'.replace('  ', ' ')
        return f'_Feature gate: {gate}_' if gate else ''
    text = _sub('feature-state', feature_state, text)

    text = _sub('skew', '1.x', text)
    text = _sub('param', 'latest', text)
    text = _sub('api-reference', lambda m: f"API reference ({_attr(m['attrs'], 'page')})", text)
    text = _sub('code_sample', lambda m: f"[code sample: {_attr(m['attrs'], 'file')}]", text)
    text = _sub('example', '', text)
    text = _sub('/example', lambda m: '', text)
    text = _sub('figure', lambda m: f"[Figure: {_attr(m['attrs'], 'caption') or _attr(m['attrs'], 'alt')}]", text)
    text = _sub('table', lambda m: f"Table: {_attr(m['attrs'], 'caption')}", text)
    text = _sub('/table', '', text)
    text = _sub('tabs', '', text)
    text = _sub('/tabs', '', text)
    text = _sub('tab', lambda m: f"**{_attr(m['attrs'], 'name')}**", text)
    text = _sub('/tab', '', text)
    text = _sub('thirdparty-content', '', text)

    leftovers = len(re.findall(r'\{\{[<%].*?[>%]\}\}', text, flags=re.S))
    text = re.sub(r'\{\{[<%].*?[>%]\}\}', '', text, flags=re.S)  # anything unknown

    text = re.sub(r'^(#{1,6} .*?)\s*\{#[\w-]+\}\s*$', r'\1', text, flags=re.M)  # heading anchors
    text = re.sub(r'[ \t]+$', '', text, flags=re.M)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    title = meta['title'] or 'Untitled'
    return meta, f'# {title}\n\n{text}\n', leftovers
