"""Create project PRs and synchronise GitHub Discussions. No third-party dependencies."""
import argparse
import base64
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from project_model import REGISTER, LINKS, create_project, validate_projects

class API:
    def __init__(self):
        self.token = os.environ['GH_TOKEN']
        self.repo = os.environ['GITHUB_REPOSITORY']
        self.api = os.environ.get('GITHUB_API_URL', 'https://api.github.com').rstrip('/')
        self.graph = os.environ.get('GITHUB_GRAPHQL_URL', 'https://api.github.com/graphql')
        self.server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com').rstrip('/')

    def request(self, method, path, data=None):
        url = path if path.startswith('https://') else self.api + path
        headers = {'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                   'Content-Type': 'application/json', 'User-Agent': 'SIDM-project-automation'}
        payload = None if data is None else json.dumps(data).encode()
        try:
            with urlopen(Request(url, data=payload, headers=headers, method=method), timeout=45) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except HTTPError as exc:
            # Do not expose credentials or raw request bodies in workflow logs.
            raise RuntimeError(f'GitHub API returned HTTP {exc.code} for {method} {urlsplit(url).path}. Check permissions and repository settings.') from None
        except URLError:
            raise RuntimeError('GitHub API connection failed. Rerun to recover; no mutation is automatically retried.') from None

    def rest(self, method, suffix, data=None):
        return self.request(method, '/repos/' + self.repo + suffix, data)

    def graphql(self, query, variables):
        response = self.request('POST', self.graph, {'query': query, 'variables': variables})
        if response.get('errors'):
            messages = '; '.join(str(e.get('message', 'GraphQL error')) for e in response['errors'])
            raise RuntimeError(messages)
        return response['data']

    def discussion_context(self):
        owner, name = self.repo.split('/')
        data = self.graphql('''query($owner:String!,$name:String!){repository(owner:$owner,name:$name){
          id hasDiscussionsEnabled discussionCategories(first:100){nodes{id name}}}}''', {'owner': owner, 'name': name})
        repo = data['repository']
        if not repo or not repo['hasDiscussionsEnabled']:
            raise RuntimeError('Enable repository Discussions before enabling project discussion automation.')
        return repo

    def discussions(self):
        owner, name = self.repo.split('/')
        result = []; cursor = None
        while True:
            data = self.graphql('''query($owner:String!,$name:String!,$after:String){repository(owner:$owner,name:$name){
              discussions(first:100,after:$after,orderBy:{field:CREATED_AT,direction:ASC}){
              nodes{id number url title body author{__typename login}} pageInfo{hasNextPage endCursor}}}}''',
              {'owner': owner, 'name': name, 'after': cursor})['repository']['discussions']
            result.extend(data['nodes'])
            if not data['pageInfo']['hasNextPage']: return result
            cursor = data['pageInfo']['endCursor']

    def create_discussion(self, repo_id, category_id, title, body):
        return self.graphql('''mutation($input:CreateDiscussionInput!){createDiscussion(input:$input){
          discussion{id number url title body author{__typename login}}}}''', {'input': {
          'repositoryId': repo_id, 'categoryId': category_id, 'title': title, 'body': body}})['createDiscussion']['discussion']

    def update_discussion(self, node, title, body):
        return self.graphql('''mutation($input:UpdateDiscussionInput!){updateDiscussion(input:$input){
          discussion{id number url title body author{__typename login}}}}''', {'input': {
          'discussionId': node['id'], 'title': title, 'body': body}})['updateDiscussion']['discussion']


def summary(message):
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
            stream.write(message + '\n\n')


def project_pull_request(root, api):
    run_id = os.environ['GITHUB_RUN_ID']
    branch = 'automation/project-' + run_id
    owner = api.repo.split('/')[0]
    existing = api.rest('GET', '/pulls?state=all&head=' + quote(owner + ':' + branch, safe='') + '&per_page=100')
    if existing:
        summary('Project request already exists: ' + existing[0]['html_url'])
        return
    repository = api.rest('GET', '')
    default = repository['default_branch']
    # Checkout and API base must agree; never commit stale content over a newer main.
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    tip = api.rest('GET', '/git/ref/heads/' + quote(default, safe=''))['object']['sha']
    if head != tip:
        raise RuntimeError('Default branch changed after checkout. Rerun against its current state.')
    fields = {key: os.environ['PROJECT_' + key.upper()] for key in ['title', 'question', 'scope', 'audience']}
    pid, project = create_project(root, run_id, **fields, ready=os.environ.get('PROJECT_READY') == 'true')
    subprocess.run(['python', 'scripts/validate_content.py'], cwd=root, check=True)
    commit = api.rest('GET', '/git/commits/' + head)
    entries = []
    for rel in [REGISTER.as_posix(), project['page_path']]:
        entries.append({'path': rel, 'mode': '100644', 'type': 'blob', 'content': (root / rel).read_text(encoding='utf-8')})
    tree = api.rest('POST', '/git/trees', {'base_tree': commit['tree']['sha'], 'tree': entries})
    new = api.rest('POST', '/git/commits', {'message': 'Propose project ' + pid, 'tree': tree['sha'], 'parents': [head]})
    # On partial failure a retry may find the branch but not yet the PR. Never force it.
    branches = api.rest('GET', '/git/matching-refs/heads/' + branch)
    exact = [b for b in branches if b['ref'] == 'refs/heads/' + branch]
    if not exact:
        api.rest('POST', '/git/refs', {'ref': 'refs/heads/' + branch, 'sha': new['sha']})
    else:
        # Existing branch is preserved; a previous run may already have written the full proposal.
        for rel in [REGISTER.as_posix(), project['page_path']]:
            stored = api.rest('GET', '/contents/' + quote(rel, safe='/') + '?ref=' + quote(branch, safe=''))
            if base64.b64decode(stored['content']).decode() != (root / rel).read_text(encoding='utf-8'):
                raise RuntimeError('Existing automation branch differs. Inspect it before retrying; it was not overwritten.')
    pr = api.rest('POST', '/pulls', {'title': '[' + pid + '] ' + fields['title'].strip(), 'head': branch, 'base': default,
        'body': 'Creates the project landing page and register entry. Review the scope and proposal wording before merging.\n\n'
                + ('Discussion creation is requested after merge when PROJECT_DISCUSSIONS_ENABLED is true and the site is published.'
                   if project['discussion_requested'] else 'Discussion creation is not requested yet.')
                + '\n\nThis does not approve an operational SIDM programme. If GitHub shows an Approve workflows to run banner, approve CI and wait for Build and validate before merging.'})
    summary('Project prepared for review: ' + pr['html_url'])


def is_actions_bot(author):
    return bool(author and author.get("__typename") == "Bot" and author.get("login") in {"github-actions", "github-actions[bot]"})

def marker(pid):
    return '<!-- sidm-project:' + pid + ' -->'

BEGIN = '<!-- sidm-generated:start -->'
END = '<!-- sidm-generated:end -->'

def safe_markdown(text):
    # Inputs cannot close hidden markers, execute HTML or ping users/teams in generated posts.
    import html
    escaped = html.escape(text).replace('@', '@\u200b')
    return re.sub(r'([\\`*_{}\[\]()#!|])', r'\\\1', escaped)


def discussion_body(pid, p, site_url):
    return '\n\n'.join([marker(pid), BEGIN, '## Project proposal: ' + safe_markdown(pid),
        '**This thread concerns a proposal, not an approved SIDM or BCS work programme.**',
        '[Read the project page](' + site_url.rstrip('/') + p['permalink'] + ')',
        '### Question\n' + safe_markdown(p['question']), '### Scope\n' + safe_markdown(p['scope']),
        '### Intended audience\n' + safe_markdown(p['audience']),
        'Discuss the scope, evidence and approach here. Reviewed findings belong on the project pages. '
        'The project page may appear after the current Pages deployment finishes. '
        'The section between the sidm-generated markers is refreshed from the repository; comments and text outside it are preserved.', END])


def sync_discussions(root, api=None, enabled=False, category='', site_url=''):
    projects = validate_projects(root)
    links = {pid: {'state': 'not-established'} for pid in projects}
    if not enabled:
        for pid,p in projects.items():
            if p['discussion_requested']: links[pid]['state'] = 'automation-disabled'
    elif projects:
        parsed = urlsplit(site_url)
        if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment or any(c in site_url for c in '\n\r <>'):
            raise ValueError('A valid HTTPS Pages base URL is required')
        context = api.discussion_context()
        nodes = api.discussions()
        matches = [x for x in context['discussionCategories']['nodes'] if x['name'] == category]
        for pid,p in projects.items():
            explicit = p.get('discussion_number')
            if explicit:
                found = [x for x in nodes if x['number'] == explicit]
                if len(found) != 1: raise ValueError(f'{pid}: configured discussion number was not found')
                node = found[0]  # Explicitly adopted human-created threads are linked, never edited.
            else:
                found = [x for x in nodes if marker(pid) in x['body'] and is_actions_bot(x.get('author'))]
                if len(found) > 1: raise ValueError(f'{pid}: multiple matching discussions; resolve or set discussion_number explicitly')
                if not found and (not p['discussion_requested'] or p['status'] == 'archived'): continue
                body = discussion_body(pid,p,site_url)
                title = '[' + pid + '] ' + p['title']
                if not found:
                    if len(matches) != 1: raise ValueError('Set PROJECT_DISCUSSION_CATEGORY to an existing category name (exact spelling)')
                    node = api.create_discussion(context['id'], matches[0]['id'], title, body)
                    nodes.append(node)  # Subsequent work in this run sees the mutation immediately.
                else:
                    node = found[0]
                    if p['discussion_requested'] and p['status'] != 'archived':
                        old = node['body']
                        if old.count(BEGIN) != 1 or old.count(END) != 1 or old.index(BEGIN) > old.index(END):
                            raise ValueError(f'{pid}: generated block markers were changed; repair or adopt the discussion explicitly')
                        generated = body[body.index(BEGIN):body.index(END)+len(END)]
                        updated = old[:old.index(BEGIN)] + generated + old[old.index(END)+len(END):]
                        if updated != old or node['title'] != title:
                            node = api.update_discussion(node,title,updated)
            links[pid] = {'state': 'linked', 'number': node['number'], 'url': node['url']}
    target = root / LINKS
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(links, indent=2) + '\n', encoding='utf-8')
    return links


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command', choices=['create','validate','sync'])
    parser.add_argument('--root', type=Path, default=Path('.'))
    args=parser.parse_args(); root=args.root.resolve()
    if args.command=='validate':
        summary(f'PASS: {len(validate_projects(root))} project records and all content associations validated.')
    elif args.command=='create':
        project_pull_request(root, API())
    else:
        enabled=os.environ.get('PROJECT_DISCUSSIONS_ENABLED')=='true'
        links=sync_discussions(root, API() if enabled else None, enabled,
            os.environ.get('PROJECT_DISCUSSION_CATEGORY',''), os.environ.get('SITE_URL',''))
        summary('Discussion links generated: ' + str(sum(x['state']=='linked' for x in links.values())))

if __name__=='__main__':
    try: main()
    except (ValueError, RuntimeError, KeyError) as exc: raise SystemExit(str(exc))
