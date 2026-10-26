"""Shared, dependency-free front matter reader. Run scripts from repository root."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def pages():
    for path in sorted((ROOT / 'docs').rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        if not text.startswith('---\n'):
            raise ValueError(f'{path}: missing front matter')
        try:
            header, body = text[4:].split('\n---\n', 1)
            meta = json.loads(header)
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f'{path}: front matter must be JSON between --- delimiters') from exc
        yield path, meta, body
