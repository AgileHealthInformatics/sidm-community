"""Project register, page generation and validation (Python standard library only)."""
import html
import json
import re
from datetime import date, timedelta
from pathlib import Path

REGISTER = Path('docs/_data/projects.json')
LINKS = Path('docs/_data/project_discussions.json')
ID = re.compile(r'ENQ-[A-Za-z0-9-]+\Z')

def read_page(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'Missing JSON front matter: {path}')
    head, body = text[4:].split('\n---\n', 1)
    return json.loads(head), body

def write_page(path, metadata, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\n' + json.dumps(metadata, indent=2, ensure_ascii=False) + '\n---\n\n' + body.strip() + '\n', encoding='utf-8')

def load_projects(root):
    value = json.loads((root / REGISTER).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Project register must be an object keyed by project identifier')
    return value

def save_projects(root, value):
    path = root / REGISTER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def validate_projects(root):
    projects = load_projects(root)
    pages = {}
    for path in (root / 'docs').rglob('*.md'):
        m, _ = read_page(path)
        pages[path.relative_to(root).as_posix()] = m
        refs = m.get('project_ids', [])
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
            raise ValueError(f'{path}: project_ids must be a list of strings')
        if len(refs) != len(set(refs)) or any(x not in projects for x in refs):
            raise ValueError(f'{path}: duplicate or unknown project identifier')
        if m.get('project_id'):
            pid = m['project_id']
            if pid not in projects or projects[pid].get('page_path') != path.relative_to(root).as_posix():
                raise ValueError(f'{path}: project_id is only valid on its registered landing page')
    urls = set()
    for pid, p in projects.items():
        if not ID.fullmatch(pid) or not isinstance(p, dict):
            raise ValueError('Invalid project identifier or record')
        for key in ['title', 'summary', 'question', 'scope', 'audience', 'page_path', 'permalink']:
            if not isinstance(p.get(key), str) or not p[key].strip():
                raise ValueError(f'{pid}: missing {key}')
        if not p['page_path'].startswith('docs/enquiries/') or '..' in Path(p['page_path']).parts:
            raise ValueError(f'{pid}: invalid page_path')
        url = p['permalink']
        if not re.fullmatch(r'/enquiries/[a-z0-9-]+/', url) or url in urls:
            raise ValueError(f'{pid}: invalid or duplicate permalink')
        urls.add(url)
        if type(p.get('discussion_requested')) is not bool:
            raise ValueError(f'{pid}: discussion_requested must be boolean')
        if p.get('status') not in ['proposed', 'active', 'archived']:
            raise ValueError(f'{pid}: invalid project status')
        n = p.get('discussion_number')
        if n is not None and (type(n) is not int or n <= 0):
            raise ValueError(f'{pid}: discussion_number must be a positive integer or null')
        page = pages.get(p['page_path'])
        if not page or page.get('project_id') != pid or page.get('permalink') != url or pid not in page.get('project_ids', []):
            raise ValueError(f'{pid}: landing page does not match the register')
    return projects

def plain_text(value, name, limit):
    value = value.strip()
    if not value or len(value) > limit or any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise ValueError(f'{name} is empty, too long or contains control characters')
    return value

def html_text(value):
    # Neutralise Liquid delimiters as well as HTML. Form values are data, never templates.
    return html.escape(value).replace('{', '&#123;').replace('}', '&#125;').replace('\n', '<br>')

def create_project(root, run_id, title, question, scope, audience, ready):
    if not re.fullmatch(r'[0-9]+', str(run_id)):
        raise ValueError('Run identifier must be numeric')
    fields = {name: plain_text(value, name, limit) for name, value, limit in [
        ('title', title, 140), ('question', question, 3000), ('scope', scope, 5000), ('audience', audience, 2000)]}
    pid = 'ENQ-' + str(run_id)
    projects = load_projects(root)
    if pid in projects:
        raise ValueError(f'{pid} already exists; inspect the existing project instead of overwriting it')
    slug = 'enq-' + str(run_id)
    url = '/enquiries/' + slug + '/'
    path = 'docs/enquiries/' + slug + '/index.md'
    if (root / path).exists():
        raise ValueError('Project page already exists')
    today = date.today()
    project = {**fields, 'summary': fields['question'], 'status': 'proposed', 'page_path': path,
               'permalink': url, 'discussion_requested': bool(ready), 'discussion_number': None}
    projects[pid] = project
    metadata = {'layout': 'page', 'title': fields['title'],
        'description': 'Project proposal for discussion; no approved work programme is implied.',
        'resource_id': pid, 'section': 'enquiries', 'status': 'working-draft',
        'owner': 'Project owner to be agreed', 'contributors': [], 'last_updated': today.isoformat(),
        'last_reviewed': None, 'next_review': (today + timedelta(days=90)).isoformat(),
        'topics': [], 'source_versions': [], 'ai_assistance': 'Page scaffold generated automatically; proposal text supplied through the project form.',
        'permalink': url, 'project_id': pid, 'project_ids': [pid]}
    body = '\n\n'.join('<h2>' + name + '</h2>\n<p>' + html_text(fields[key]) + '</p>'
                        for name, key in [('Question', 'question'), ('Scope', 'scope'), ('Intended audience', 'audience')])
    body += '\n\n## Status and next steps\n\nThis is a proposal. Ownership, sources, methods and an operating programme remain to be agreed. Creating a discussion does not constitute SIDM or BCS endorsement.\n'
    save_projects(root, projects)
    write_page(root / path, metadata, body)
    validate_projects(root)
    return pid, project
