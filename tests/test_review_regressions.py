"""Reproductions of the independent functional review, with isolated data."""
import copy
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from workbench.browser_control import BrowserControl, text_matches, equivalent_plans
from workbench.config import Config
from workbench.engine import Engine
from workbench.model import Budget, RunError
from workbench.server import Application
from workbench.store import Store, WorkspaceConflict, digest

EMPTY={"projects":[],"chats":[],"workflows":[]}


class PersistenceRegression(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(Path(self.temp.name))
    def tearDown(self):
        self.store.close();self.temp.cleanup()

    def test_two_stale_clients_preserve_both_projects_and_disjoint_edits(self):
        first={**EMPTY,"projects":[{"id":"a","name":"A","instructions":"original"}]}
        second={**EMPTY,"projects":[{"id":"b","name":"B"}],"workflows":[{"id":"w","title":"Saved"}]}
        self.store.merge_workspace(EMPTY,first)
        merged=self.store.merge_workspace(EMPTY,second)
        self.assertEqual({p['id'] for p in merged['projects']},{'a','b'})
        a,b=copy.deepcopy(merged),copy.deepcopy(merged)
        a['projects'][0]['instructions']='new instructions';b['projects'][0]['name']='Renamed'
        self.store.merge_workspace(merged,a);result=self.store.merge_workspace(merged,b)
        self.assertEqual(result['projects'][0],{'id':'a','name':'Renamed','instructions':'new instructions'})
        self.assertEqual(result['workflows'][0]['id'],'w')

    def test_same_field_conflict_is_atomic_and_cannot_resurrect_deletion(self):
        base={**EMPTY,'projects':[{'id':'a','name':'A'}]};self.store.save_workspace(base)
        one={**EMPTY,'projects':[{'id':'a','name':'First'}]}
        two={**EMPTY,'projects':[{'id':'a','name':'Second'}],'workflows':[{'id':'w'}]}
        self.store.merge_workspace(base,one)
        with self.assertRaises(WorkspaceConflict):self.store.merge_workspace(base,two)
        self.assertEqual(self.store.workspace(),one)
        self.store.merge_workspace(one,EMPTY)
        with self.assertRaises(WorkspaceConflict):self.store.merge_workspace(base,two)
        self.assertEqual(self.store.workspace(),EMPTY)

    def test_same_chat_context_contains_real_results_but_new_chat_is_clean(self):
        self.store.save_workspace({**EMPTY,'chats':[{'id':'chat','projectId':'a'},{'id':'fresh','projectId':'a'}]})
        r=self.store.new_run('Clean source data',{});r.update(chat_id='chat',project_id='a',status='completed',result=['Missing One','Missing Two','Evan']);self.store.save_run(r)
        self.assertEqual(self.store.chat_context('chat','a')[0]['result'],r['result'])
        self.assertEqual(self.store.chat_context('fresh','a'),[])
        with self.assertRaises(ValueError):self.store.chat_context('chat','b')

    def test_maps_are_scoped_and_before_after_hashes_match(self):
        a,b=self.store.scoped('a'),self.store.scoped('b')
        a.remember_app({'connected':True,'origin':'https://example.test','elements':[{'name':'Private A'}]})
        self.assertEqual(b.applications(),[]);self.assertEqual(self.store.applications(),[])
        self.assertEqual(a.applications()[0]['elements'],[{'name':'Private A'}])
        app=Application(Config(data_dir=Path(self.temp.name), free_confirmed=True))
        try:
            app.store.save_workspace({**EMPTY,'projects':[{'id':'a','name':'A'}]})
            app.store.scoped('b').accept({'id':'other'},'fixture',[{}],[{'passed':True}],{})
            with patch.object(app.model,'ready',return_value=None),patch.object(app.pool,'submit'):
                r=app.start('Task',{},'task',project_id='a')
            self.assertEqual(r['registry_before'],digest(app.store.scoped('a').registry()))
            self.assertEqual(r['registry_scope'],{'project_id':'a','includes_shared':True})
        finally:app.pool.shutdown();app.browser.close();app.store.close()


class BrowserRegression(unittest.TestCase):
    def test_both_plan_invocation_paths_count_executed_actions(self):
        from unittest.mock import Mock
        plan={'origin':'https://example.test','steps':[{'action':'fill','target':{'name':'Name','tag':'input'},'value':'Alex'}],'expected_text':['Alex']}
        manifest={'id':'plan_fixture','title':'Fixture','description':'Synthetic plan execution fixture','kind':'browser_plan','permissions':['compute'],'input_schema':{'type':'object'},'output_schema':{'type':'object'}}
        for action in ('call','browser_plan'):
            with self.subTest(action=action),tempfile.TemporaryDirectory() as directory:
                store=Store(Path(directory));store.accept(manifest,'fixture',[{}],[{'passed':True}],{'source':'test_fixture'})
                model=Mock();model.ready.return_value=None;model.ask.side_effect=[{'action':action,'id':'plan_fixture','input':{}},{'action':'finish'}]
                sandbox=Mock();sandbox.status.return_value=True;sandbox.run.return_value=plan
                browser=Mock();browser.cached={'connected':True,'origin':plan['origin']};browser.observation.return_value=browser.cached
                browser.run_plan.return_value={'steps':1,'observed':True}
                run=store.new_run('Use the plan',{})
                try:
                    Engine(Config(),model,sandbox,store,browser).execute(run)
                    self.assertEqual(run['status'],'needs_review',run.get('error'))
                    browser.run_plan.assert_called_once()
                finally:store.close()

    def test_format_retry_is_once_per_run_and_never_retries_quota(self):
        from unittest.mock import Mock
        from workbench.model import ModelFormatError
        model=Mock();model.ask.side_effect=[ModelFormatError('invalid'),{'action':'finish'},ModelFormatError('invalid again')]
        engine=Engine(Config(),model,None,None);budget=Budget()
        self.assertEqual(engine.ask('Planning','system',{},budget),{'action':'finish'})
        with self.assertRaises(ModelFormatError):engine.ask('Planning','system',{},budget)
        self.assertEqual(model.ask.call_count,3)
        model.ask.reset_mock();model.ask.side_effect=RunError('quota exhausted')
        with self.assertRaises(RunError):engine.ask('Planning','system',{},Budget())
        self.assertEqual(model.ask.call_count,1)

    def test_redirect_never_reaches_other_origin_in_real_browser(self):
        hits=[]
        class Other(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                hits.append(self.path);self.send_response(200);self.end_headers();self.wfile.write(b'probe')
        other=ThreadingHTTPServer(('127.0.0.1',0),Other)
        class Allowed(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                if self.path=='/redirect':
                    self.send_response(302);self.send_header('Location',f'http://127.0.0.1:{other.server_port}/probe');self.end_headers()
                else:
                    self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(b'<html><body><h1>Allowed</h1><img src="/redirect"></body></html>')
        allowed=ThreadingHTTPServer(('127.0.0.1',0),Allowed)
        for server in (allowed,other):threading.Thread(target=server.serve_forever,daemon=True).start()
        browser=BrowserControl()
        try:
            browser.connect(f'http://127.0.0.1:{allowed.server_port}/',headless=True)
            self.assertEqual(hits,[])
            self.assertIn('Allowed',browser.cached['text'])
            with self.assertRaises(RunError):browser.request('act',{'action':'navigate','value':f'http://127.0.0.1:{allowed.server_port}/redirect'})
            self.assertEqual(hits,[])
        finally:
            browser.close()
            for server in (allowed,other):server.shutdown();server.server_close()

    def test_count_and_full_record_are_verified(self):
        self.assertFalse(text_matches(['1 registered'],'11 registered'))
        self.assertFalse(text_matches(['Ann'],'Anna'))
        self.assertTrue(text_matches(['1 registered','Ann'],'1 registered\nAnn'))
        browser=BrowserControl();before={'count':0,'records':[]}
        row={'name':'Alex','email':'alex@example.test','workshop':'Building agents','checked':True}
        try:
            with patch.object(browser,'request'):
                for wrong in ({**row,'workshop':'Storytelling'},{**row,'checked':False},{**row,'email':'wrong@example.test'}):
                    browser.cached={'registration_state':{'count':1,'records':[wrong]}}
                    with self.assertRaises(RunError):browser.verify_registrations([row],before,Budget(),lambda *a,**k:None)
                browser.cached={'registration_state':{'count':11,'records':[row]}}
                with self.assertRaises(RunError):browser.verify_registrations([row],before,Budget(),lambda *a,**k:None)
                browser.cached={'registration_state':{'count':1,'records':[row]}}
                self.assertEqual(browser.verify_registrations([row],before,Budget(),lambda *a,**k:None)['count'],1)
        finally:browser.close()

    def test_equivalent_setter_order_and_extra_checks_but_no_changed_value(self):
        snapshot={'origin':'https://workspace.demo','elements':[{'name':'Name','tag':'input'},{'name':'Email','tag':'input'},{'name':'Add participant','tag':'button'}]}
        a={'action':'fill','target':{'name':'Name','tag':'input'},'value':'Alex'}
        b={'action':'fill','target':{'name':'Email','tag':'input'},'value':'alex@example.test'}
        click={'action':'click','target':{'name':'Add participant','tag':'button'}}
        plan={'origin':snapshot['origin'],'steps':[a,b,click],'expected_text':['Alex']}
        equivalent={**plan,'steps':[b,a,click],'expected_text':['Alex','alex@example.test']}
        self.assertTrue(equivalent_plans(equivalent,plan,snapshot))
        self.assertFalse(equivalent_plans({**equivalent,'steps':[b,{**a,'value':'Wrong'},click]},plan,snapshot))
        self.assertFalse(equivalent_plans({**equivalent,'expected_text':['alex@example.test']},plan,snapshot))

    def test_finish_without_browser_action_cannot_complete(self):
        class Model:
            def ready(self):return None
            def ask(self,system,payload,budget):budget.reserve();return {'action':'finish','message':'Done','result':{'pretend':True}}
        class Sandbox:
            def status(self):return True
        browser=BrowserControl();browser.cached={'connected':True,'origin':'https://example.test'}
        with tempfile.TemporaryDirectory() as directory:
            store=Store(Path(directory));run=store.new_run('Change the site',{})
            try:
                Engine(Config(),Model(),Sandbox(),store,browser).execute(run)
                self.assertEqual(run['status'],'failed');self.assertIn('no browser action',run['error'])
            finally:store.close();browser.close()

    def test_missing_previous_result_requests_input_without_model_call(self):
        class Sandbox:
            def status(self):return True
        with tempfile.TemporaryDirectory() as directory:
            store=Store(Path(directory));run=store.new_run('List names from your previous result',{})
            try:
                from unittest.mock import Mock
                model=Mock();model.ready.return_value=None
                Engine(Config(),model,Sandbox(),store).execute(run)
                self.assertEqual(run['status'],'needs_input');model.ask.assert_not_called()
            finally:store.close()
