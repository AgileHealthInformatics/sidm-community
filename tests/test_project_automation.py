import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from project_model import (REGISTER, LINKS, create_project, read_page, save_projects,
                           validate_projects, write_page)
from project_automation import (API, BEGIN, END, discussion_body, marker,
                               project_pull_request, sync_discussions)

class FakeAPI:
    def __init__(self, nodes=None):
        self.nodes=copy.deepcopy(nodes or []); self.created=[]; self.updated=[]
        self.categories=[{'id':'CAT','name':'General'}]
    def discussion_context(self):
        return {'id':'REPO','discussionCategories':{'nodes':self.categories}}
    def discussions(self): return copy.deepcopy(self.nodes)
    def create_discussion(self,repo_id,cat,title,body):
        self.created.append((repo_id,cat,title,body))
        node={'id':'D'+str(len(self.nodes)+1),'number':len(self.nodes)+1,
              'url':'https://github.com/owner/repo/discussions/'+str(len(self.nodes)+1),
              'title':title,'body':body,'author':{'__typename':'Bot','login':'github-actions[bot]'}}
        self.nodes.append(copy.deepcopy(node)); return node
    def update_discussion(self,node,title,body):
        self.updated.append(node['id'])
        for n in self.nodes:
            if n['id']==node['id']: n.update(title=title,body=body);return copy.deepcopy(n)

class Projects(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);save_projects(self.root,{})
        self.pid,self.project=create_project(self.root,'123','Data & definitions','What differs?','Two sources','Practitioners',True)
    def save(self, project): save_projects(self.root,{self.pid:project})
    def sync(self,api,**kw):
        return sync_discussions(self.root,api,enabled=True,category='General',site_url='https://owner.github.io/repo',**kw)
    def test_unique_page_and_register(self):
        data=validate_projects(self.root)
        self.assertEqual(data[self.pid]['permalink'],'/enquiries/enq-123/')
        meta,_=read_page(self.root/self.project['page_path'])
        self.assertEqual(meta['title'],'Data & definitions')
        self.assertEqual(meta['project_ids'],[self.pid])
    def test_duplicate_creation_does_not_overwrite(self):
        before=(self.root/REGISTER).read_text()
        with self.assertRaises(ValueError):create_project(self.root,'123','Other','Q','S','A',True)
        self.assertEqual(before,(self.root/REGISTER).read_text())
    def test_form_content_cannot_execute_liquid_or_html(self):
        _,p=create_project(self.root,'124','Example','{{ site.secret }} <script>x</script>','{% include evil %}','People',False)
        _,body=read_page(self.root/p['page_path'])
        self.assertNotIn('{{',body); self.assertNotIn('{%',body);self.assertNotIn('<script>',body)
        self.assertIn('&lt;script&gt;',body)
    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError):create_project(self.root,'../bad','T','Q','S','A',True)
        with self.assertRaises(ValueError):create_project(self.root,'125','x'*141,'Q','S','A',True)
    def test_unknown_resource_project_rejected(self):
        meta,body=read_page(self.root/self.project['page_path']);meta['project_ids']=['ENQ-missing']
        write_page(self.root/self.project['page_path'],meta,body)
        with self.assertRaisesRegex(ValueError,'unknown'):validate_projects(self.root)
    def test_duplicate_association_rejected(self):
        meta,body=read_page(self.root/self.project['page_path']);meta['project_ids']*=2
        write_page(self.root/self.project['page_path'],meta,body)
        with self.assertRaises(ValueError):validate_projects(self.root)
    def test_multiple_project_membership(self):
        pid2,_=create_project(self.root,'124','Second','Q','S','A',False)
        meta,_=read_page(self.root/self.project['page_path'])
        meta.pop('project_id');meta.update(resource_id='RES-1',permalink='/resources/shared/',project_ids=[self.pid,pid2])
        write_page(self.root/'docs/resources/shared.md',meta,'Shared resource')
        self.assertEqual(len(validate_projects(self.root)),2)
    def test_only_landing_page_can_claim_project_id(self):
        meta,body=read_page(self.root/self.project['page_path'])
        write_page(self.root/'docs/resources/duplicate.md',meta,body)
        with self.assertRaises(ValueError):validate_projects(self.root)
    def test_invalid_number_rejected(self):
        p=copy.deepcopy(self.project);p['discussion_number']=True;self.save(p)
        with self.assertRaises(ValueError):validate_projects(self.root)
    def test_invalid_path_rejected(self):
        p=copy.deepcopy(self.project);p['page_path']='docs/enquiries/../../secret';self.save(p)
        with self.assertRaises(ValueError):validate_projects(self.root)
    def test_disabled_sync_never_calls_api(self):
        class Fail:
            def discussion_context(self):raise AssertionError('must not call API')
        links=sync_discussions(self.root,Fail(),enabled=False)
        self.assertEqual(links[self.pid]['state'],'automation-disabled')
    def test_unrequested_project_creates_nothing(self):
        p=copy.deepcopy(self.project);p['discussion_requested']=False;self.save(p)
        api=FakeAPI();self.sync(api);self.assertEqual(api.created,[])
    def test_first_run_and_rerun_are_idempotent(self):
        api=FakeAPI();a=self.sync(api);b=self.sync(api)
        self.assertEqual(a,b);self.assertEqual(len(api.created),1);self.assertEqual(api.updated,[])
        self.assertEqual(json.loads((self.root/LINKS).read_text()),a)
    def test_graphql_bot_login_without_suffix_is_recognised(self):
        api=FakeAPI();self.sync(api);api.nodes[0]['author']['login']='github-actions'
        self.sync(api);self.assertEqual(len(api.created),1)
    def test_paused_project_retains_existing_link(self):
        api=FakeAPI();self.sync(api);p=copy.deepcopy(self.project);p['discussion_requested']=False;self.save(p)
        self.assertEqual(self.sync(api)[self.pid]['state'],'linked');self.assertEqual(len(api.created),1)
    def test_recovery_after_mapping_is_lost(self):
        api=FakeAPI();first=self.sync(api);(self.root/LINKS).unlink()
        recovered=self.sync(api);self.assertEqual(recovered,first);self.assertEqual(len(api.created),1)
    def test_duplicate_markers_fail_closed(self):
        api=FakeAPI();self.sync(api);node=copy.deepcopy(api.nodes[0]);node['id']='D2';node['number']=2;api.nodes.append(node)
        with self.assertRaisesRegex(ValueError,'multiple matching'):self.sync(api)
        self.assertEqual(len(api.created),1)
    def test_untrusted_marker_does_not_claim_project(self):
        api=FakeAPI();self.sync(api);api.nodes[0]['author']={'login':'someone-else'}
        self.sync(api);self.assertEqual(len(api.created),2)
    def test_explicit_existing_thread_is_adopted_without_edit(self):
        api=FakeAPI();self.sync(api);api.nodes[0]['author']={'login':'human'};api.nodes[0]['body']='Human-owned thread'
        p=copy.deepcopy(self.project);p['discussion_number']=1;self.save(p)
        self.assertEqual(self.sync(api)[self.pid]['number'],1);self.assertEqual(api.updated,[])
    def test_missing_explicit_thread_is_not_replaced(self):
        p=copy.deepcopy(self.project);p['discussion_number']=77;self.save(p);api=FakeAPI()
        with self.assertRaises(ValueError):self.sync(api)
        self.assertEqual(api.created,[])
    def test_changed_scope_updates_generated_block_only(self):
        api=FakeAPI();self.sync(api);api.nodes[0]['body']+='\n\nHuman annotation after block'
        p=copy.deepcopy(self.project);p['scope']='Changed scope';self.save(p);self.sync(api)
        self.assertIn('Changed scope',api.nodes[0]['body']);self.assertTrue(api.nodes[0]['body'].endswith('Human annotation after block'))
        self.assertEqual(len(api.updated),1)
    def test_changed_domain_updates_backlink(self):
        api=FakeAPI();self.sync(api)
        sync_discussions(self.root,api,True,'General','https://new.example.org')
        self.assertIn('https://new.example.org/enquiries/enq-123/',api.nodes[0]['body'])
    def test_damaged_block_is_not_overwritten(self):
        api=FakeAPI();self.sync(api);api.nodes[0]['body']=marker(self.pid)+'\nHuman rewrite'
        with self.assertRaisesRegex(ValueError,'markers'):self.sync(api)
        self.assertEqual(api.updated,[])
    def test_archived_project_does_not_create_thread(self):
        p=copy.deepcopy(self.project);p['status']='archived';self.save(p);api=FakeAPI()
        self.sync(api);self.assertFalse(api.created)
    def test_archived_existing_thread_keeps_link(self):
        api=FakeAPI();self.sync(api);p=copy.deepcopy(self.project);p['status']='archived';self.save(p)
        self.assertEqual(self.sync(api)[self.pid]['state'],'linked');self.assertFalse(api.updated)
    def test_missing_category_has_actionable_error(self):
        api=FakeAPI();api.categories=[]
        with self.assertRaisesRegex(ValueError,'PROJECT_DISCUSSION_CATEGORY'):self.sync(api)
        self.assertEqual(api.created,[])
    def test_site_url_must_be_valid(self):
        with self.assertRaises(ValueError):sync_discussions(self.root,FakeAPI(),True,'General','javascript:alert(1)')
    def test_discussion_input_is_escaped(self):
        p=copy.deepcopy(self.project);p['question']='@everyone <!-- forged --> [bad](url)'
        body=discussion_body(self.pid,p,'https://example.org')
        self.assertNotIn('@everyone',body);self.assertNotIn('<!-- forged -->',body)
    def test_api_paginates_all_discussions(self):
        api=object.__new__(API);api.repo='a/b';seen=[]
        def graph(q,v):
            seen.append(v['after'])
            return {'repository':{'discussions':{'nodes':[{'number':1 if v['after'] is None else 2}],
                'pageInfo':{'hasNextPage':v['after'] is None,'endCursor':'cursor'}}}}
        api.graphql=graph
        self.assertEqual([n['number'] for n in api.discussions()],[1,2]);self.assertEqual(seen,[None,'cursor'])
    def test_new_project_pr_uses_base_tree_and_never_updates_main(self):
        class Creator:
            repo='a/b'
            def __init__(self):self.calls=[]
            def rest(self,method,path,data=None):
                self.calls.append((method,path,data))
                if path.startswith('/pulls?'):return []
                if path=='':return {'default_branch':'main'}
                if path=='/git/ref/heads/main':return {'object':{'sha':'HEAD'}}
                if path=='/git/commits/HEAD':return {'tree':{'sha':'BASE_TREE'}}
                if path=='/git/trees':
                    assert data['base_tree']=='BASE_TREE'
                    assert len(data['tree'])==2
                    return {'sha':'NEW_TREE'}
                if path=='/git/commits':return {'sha':'NEW_COMMIT'}
                if path.startswith('/git/matching-refs/heads/'):return []
                if path=='/git/refs':
                    assert data['ref']=='refs/heads/automation/project-999'
                    return {}
                if path=='/pulls':return {'html_url':'https://github.com/a/b/pull/1'}
                raise AssertionError((method,path))
        api=Creator()
        env={'GITHUB_RUN_ID':'999','PROJECT_TITLE':'New','PROJECT_QUESTION':'Question',
             'PROJECT_SCOPE':'Scope','PROJECT_AUDIENCE':'People','PROJECT_READY':'true'}
        with patch.dict(os.environ,env), patch('subprocess.check_output',return_value='HEAD'), patch('subprocess.run'):
            project_pull_request(self.root,api)
        self.assertTrue(all(method!='PATCH' for method,_,_ in api.calls))
        self.assertIn('ENQ-999',validate_projects(self.root))
    def test_stale_checkout_cannot_write(self):
        class Stale:
            repo='a/b'
            def rest(self,method,path,data=None):
                assert method=='GET'
                if path.startswith('/pulls?'):return []
                if path=='':return {'default_branch':'main'}
                return {'object':{'sha':'NEW_HEAD'}}
        with patch.dict(os.environ,{'GITHUB_RUN_ID':'999'}),patch('subprocess.check_output',return_value='OLD_HEAD'):
            with self.assertRaisesRegex(RuntimeError,'changed after checkout'):
                project_pull_request(self.root,Stale())
    def test_existing_pull_request_rerun_is_noop(self):
        class Existing:
            repo='a/b'
            def rest(self,method,path,data=None):
                assert method=='GET' and path.startswith('/pulls?')
                return [{'html_url':'https://github.com/a/b/pull/1'}]
        with patch.dict(os.environ,{'GITHUB_RUN_ID':'99'},clear=False):
            project_pull_request(self.root,Existing())

if __name__=='__main__':unittest.main()
