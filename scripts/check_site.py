"""Check generated HTML internal links, fragments and asset references."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import sys
class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.refs=[]; self.ids=set(); self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag=='a' and attrs.get('name'): self.ids.add(attrs['name'])
        for key in ['href','src']:
            if attrs.get(key): self.refs.append(attrs[key])
p=argparse.ArgumentParser(); p.add_argument('directory');p.add_argument('--baseurl',default='');a=p.parse_args()
root=Path(a.directory).resolve();base=a.baseurl.rstrip('/');docs={}
for path in root.rglob('*.html'): docs[path]=Document(path.read_text(encoding='utf-8'))
errors=[]
if not (root/'index.html').is_file(): errors.append('Missing generated index.html')
for path,doc in docs.items():
    for ref in doc.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc: continue
        link=unquote(u.path)
        if not link: target=path
        elif link.startswith('/'):
            if base and not (link==base or link.startswith(base+'/')):
                errors.append(f'{path}: link outside base path: {ref}');continue
            target=root / (link[len(base):] if base else link).lstrip('/')
        else: target=path.parent/link
        target=target.resolve()
        if not target.is_relative_to(root): errors.append(f'{path}: escaping link {ref}');continue
        if target.is_dir(): target=target/'index.html'
        if not target.exists(): errors.append(f'{path}: missing target {ref}');continue
        if u.fragment and target in docs and unquote(u.fragment) not in docs[target].ids:
            errors.append(f'{path}: missing fragment {ref}')
if errors: print('\n'.join(errors));sys.exit(1)
print(f'PASS: internal links, fragments and assets across {len(docs)} generated HTML pages.')
