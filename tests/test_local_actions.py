"""Infrastructure fixtures, not agent-created demo capabilities."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from workbench.config import Config
from workbench.engine import Engine
from workbench.files import FileVault
from workbench.local_actions import LocalActions, action_detail, checked_record
from workbench.model import Budget, RunError
from workbench.sandbox import Sandbox
from workbench.server import Application
from workbench.store import Store, digest
from workbench.usage import summarize

MANIFEST = {"id": "group_capacity", "title": "Check group capacity", "description": "Keep a group together if enough places remain.", "permissions": ["compute"], "kind": "task", "input_schema": {"type": "object", "properties": {"names": {"type": "array", "items": {"type": "string"}}, "capacity": {"type": "integer", "minimum": 0}}, "required": ["names", "capacity"]}, "output_schema": {"type": "object", "properties": {"assigned": {"type": "array", "items": {"type": "string"}}, "waiting": {"type": "array", "items": {"type": "string"}}}, "required": ["assigned", "waiting"]}}
CODE = 'def run(d):\n    fits=len(d["names"])<=d["capacity"]\n    return {"assigned":d["names"] if fits else [],"waiting":[] if fits else d["names"]}'
CASES = [{"name":"Fits", "input":{"names":["Alex","Sam"],"capacity":2}, "expected":{"assigned":["Alex","Sam"],"waiting":[]}}, {"name":"Keep together", "input":{"names":["Alex","Sam"],"capacity":1}, "expected":{"assigned":[],"waiting":["Alex","Sam"]}}]

class LocalActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = Sandbox()
        if not cls.sandbox.status():
            raise RuntimeError("Real Docker is required to verify Blackout.")

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=Store(Path(self.temp.name))
        self.local=LocalActions(self.store,self.sandbox,FileVault(Path(self.temp.name)))
        run=self.store.new_run('Infrastructure fixture',{})
        engine=Engine(Config(),None,self.sandbox,self.store)
        self.record,_=engine.install(run,copy.deepcopy(MANIFEST),CODE,CASES,Budget(),source='test_fixture')
        self.body={"id":MANIFEST['id'],"version":self.record['version'],"code_hash":self.record['code_hash'],"input":{"names":["New person","Other person","Third person"],"capacity":2}}

    def tearDown(self):
        self.store.close();self.temp.cleanup()

    def test_real_blackout_without_provider_preserves_code_and_constraints(self):
        before=digest(self.store.registry())
        run=self.local.prepare(self.body,ai_paused=True)
        result=self.local.execute(run)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['result'],{'assigned':[],'waiting':self.body['input']['names']})
        self.assertEqual(result['model_calls'],0)
        self.assertEqual(result['model_usage'],[])
        self.assertEqual(result['permissions'],['compute'])
        self.assertEqual(before,result['registry_after'])
        self.assertEqual(result['registry_before'],before)
        self.assertEqual(summarize(result)['estimated_usd'],0)
        _,path=self.local.vault.get(result['artifacts'][0]['id'])
        self.assertTrue(path.exists())
        detail=action_detail(self.store,MANIFEST['id'])
        self.assertEqual(detail['input_source']['kind'],'previous_run')
        self.assertEqual(detail['input'],self.body['input'])

    def test_invalid_and_unsupported_inputs_never_reach_sandbox(self):
        self.local.sandbox=Mock()
        for value in ({'names':[],'capacity':-1},{'names':[],'capacity':1,'group_policy':'invented'}):
            with self.assertRaises(RunError):self.local.prepare({**self.body,'input':value})
        self.local.sandbox.run.assert_not_called()

    def test_inactive_changed_and_other_project_actions_rejected(self):
        with self.assertRaisesRegex(RunError,'changed'):self.local.prepare({**self.body,'version':99})
        with self.assertRaisesRegex(RunError,'changed'):self.local.prepare({**self.body,'code_hash':'bad'})
        self.store.deactivate(MANIFEST['id'])
        with self.assertRaisesRegex(RunError,'inactive'):self.local.prepare(self.body)
        self.store.scoped('other').accept({**MANIFEST, 'id':'other_group_capacity'},CODE,CASES,self.record['tests'],{'source':'test_fixture'})
        with self.assertRaisesRegex(RunError,'outside'):self.local.prepare({**self.body,'id':'other_group_capacity'})

    def test_execution_rechecks_active_version(self):
        run=self.local.prepare(self.body)
        self.store.deactivate(MANIFEST['id'])
        self.local.sandbox=Mock()
        result=self.local.execute(run)
        self.assertEqual(result['status'],'failed')
        self.local.sandbox.run.assert_not_called()

    def test_output_must_match_interface(self):
        self.local.sandbox=Mock();self.local.sandbox.run.return_value={'assigned':'wrong'}
        result=self.local.execute(self.local.prepare(self.body))
        self.assertEqual(result['status'],'failed')
        self.assertNotIn('artifacts',result)

    def test_blackout_persists_and_blocks_chat_before_provider_access(self):
        import threading
        app=Application.__new__(Application)
        app.store=self.store;app.lock=threading.Lock();app.future=None
        app.model=Mock();app.model.ready.side_effect=AssertionError('Provider must not be queried')
        app.set_blackout(True)
        other=Store(Path(self.temp.name))
        try:self.assertTrue(other.setting('ai_paused'))
        finally:other.close()
        with self.assertRaisesRegex(ValueError,'Blackout'):app.start('new task',{},'task')
        app.model.ready.assert_not_called()
        app.set_blackout(False)
        self.assertFalse(self.store.setting('ai_paused'))

    def test_tampered_code_and_incomplete_test_report_never_execute(self):
        for mutate, message in (
            (lambda r: r.update(code=CODE + "\n# untested change"), "fingerprint"),
            (lambda r: r.update(tests=r["tests"][:-1]), "test report"),
            (lambda r: r["tests"][0].update(passed=False), "test report"),
            (lambda r: r.update(cases=[]), "test report"),
        ):
            record=copy.deepcopy(self.record);mutate(record)
            store=Mock();store.get.return_value=record
            with self.subTest(message=message), self.assertRaisesRegex(RunError,message):
                checked_record(store,MANIFEST["id"],self.record["version"],self.record["code_hash"])

    def test_nested_unsupported_group_field_is_not_silently_dropped(self):
        from workbench.local_actions import strict_inputs
        schema={"type":"object","properties":{"participants":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"}}}}}}
        with self.assertRaisesRegex(RunError,"group_id"):
            strict_inputs({"participants":[{"name":"Alex","group_id":"team"}]},schema)

    def test_blackout_also_blocks_scheduled_tasks_and_corrections(self):
        import threading
        app=Application.__new__(Application)
        app.store=self.store;app.lock=threading.Lock();app.future=None
        app.model=Mock();app.model.ready.side_effect=AssertionError("Provider must not be queried")
        app.set_blackout(True)
        with self.assertRaisesRegex(ValueError,"Blackout"):
            app.start_scheduled("new task",{},kind="task")
        with self.assertRaisesRegex(ValueError,"Blackout"):
            app.start("fix this",{},"correction")
        app.model.ready.assert_not_called()

    def test_blackout_cannot_change_while_a_task_is_running(self):
        import threading
        app=Application.__new__(Application)
        app.store=self.store;app.lock=threading.Lock();app.future=Mock()
        app.future.done.return_value=False
        with self.assertRaisesRegex(ValueError,"finish"):
            app.set_blackout(True)
        self.assertFalse(self.store.setting("ai_paused",False))

    def test_app_context_binding_is_validated_and_saved(self):
        binding={"origin":"https://event.workspace.demo","revision":1,"state_hash":"a"*64}
        prepared=self.local.prepare({**self.body,"app_context":binding})
        self.assertEqual(self.store.run(prepared["id"])["app_context"],binding)
        for invalid in ({},[],{**binding,"state_hash":"short"},{**binding,"unexpected":True}):
            with self.subTest(invalid=invalid),self.assertRaisesRegex(RunError,"snapshot"):
                self.local.prepare({**self.body,"app_context":invalid})

    def test_application_local_route_never_requires_a_provider(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        app=Application.__new__(Application)
        app.store=self.store;app.lock=threading.Lock();app.future=None
        app.model=Mock();app.model.ready.side_effect=AssertionError("Provider must not be queried")
        app.model.ask.side_effect=AssertionError("Provider must not be called")
        app.local_actions=self.local
        self.store.set_setting("ai_paused",True)
        with ThreadPoolExecutor(max_workers=1) as app.pool:
            app.start_local(self.body)
            result=app.future.result(timeout=15)
        self.assertEqual(result["status"],"completed")
        self.assertTrue(result["ai_paused"])
        app.model.ready.assert_not_called();app.model.ask.assert_not_called()

    def test_stop_does_not_publish_preview(self):
        run=self.local.prepare(self.body);run['cancel_requested']=True
        self.local.sandbox=Mock()
        self.assertEqual(self.local.execute(run)['status'],'stopped')
        self.local.sandbox.run.assert_not_called()

class ApplyChecks(unittest.TestCase):
    def setUp(self):
        self.current={'revision':2,'participants':[{'id':'a','name':'Alex','email':'alex@example.test','first_choice':'design','second_choice':'agents','group_id':'team'},{'id':'b','name':'Sam','email':'sam@example.test','first_choice':'design','second_choice':'agents','group_id':'team'}], 'rooms':[{'id':'room','name':'Room','capacity':2,'open':True}], 'workshops':[{'id':'design','name':'Design','room':'room','time':'10:00'},{'id':'agents','name':'Agents','room':'room','time':'10:00'}],'assignments':[],'waitlist':[]}
        self.run={'kind':'local_action','status':'completed','input':{k:self.current[k] for k in ('participants','rooms','workshops')},'result':{'assignments':[{'participant_id':'a','workshop_id':'design'},{'participant_id':'b','workshop_id':'design'}],'waitlist':[]}}

    def test_stale_preview_rejected(self):
        from workbench.action_app import preflight
        preflight(self.run,self.current)
        changed=copy.deepcopy(self.current);changed['rooms'][0]['capacity']=1
        with self.assertRaisesRegex(RunError,'differ'):preflight(self.run,changed)

    def test_replanner_preview_rejects_newer_reservations(self):
        from workbench.action_app import preflight
        self.run["input"]["assignments"]=copy.deepcopy(self.current["assignments"])
        self.run["input"]["waitlist"]=copy.deepcopy(self.current["waitlist"])
        changed=copy.deepcopy(self.current)
        changed["assignments"]=[{"participant_id":"a","workshop_id":"agents"},{"participant_id":"b","workshop_id":"agents"}]
        changed["revision"]+=1
        with self.assertRaisesRegex(RunError,"differ|changed|stale"):
            preflight(self.run,changed)

    def test_capacity_and_missing_people_rejected_before_app_mutation(self):
        from workbench.action_app import preflight
        changed=copy.deepcopy(self.current);changed["rooms"][0]["capacity"]=1
        self.run["input"]={k:copy.deepcopy(changed[k]) for k in ("participants","rooms","workshops")}
        with self.assertRaisesRegex(RunError,"capacity"):
            preflight(self.run,changed)
        self.run["input"]={k:copy.deepcopy(self.current[k]) for k in ("participants","rooms","workshops")}
        self.run["result"]["assignments"].pop()
        with self.assertRaisesRegex(RunError,"everyone"):
            preflight(self.run,self.current)

    def test_app_snapshot_binding_detects_revision_and_non_input_changes(self):
        from workbench.action_app import preflight, ORIGIN
        self.run["app_context"]={"origin":ORIGIN,"revision":self.current["revision"],"state_hash":digest(self.current)}
        preflight(self.run,self.current)
        changed=copy.deepcopy(self.current);changed["revision"]+=1
        with self.assertRaisesRegex(RunError,"changed"):
            preflight(self.run,changed)
        changed=copy.deepcopy(self.current);changed["waitlist"]=["a","b"]
        with self.assertRaisesRegex(RunError,"changed"):
            preflight(self.run,changed)

    def test_group_split_rejected_independently(self):
        from workbench.action_app import preflight
        self.run['result']['assignments'][1]['workshop_id']='agents'
        with self.assertRaisesRegex(RunError,'split'):preflight(self.run,self.current)
        self.run['result']['assignments'].pop();self.run['result']['waitlist']=['b']
        with self.assertRaisesRegex(RunError,'split'):preflight(self.run,self.current)

    def test_roster_preview_rejects_hidden_invalid_or_duplicate_csv_rows(self):
        from workbench.action_app import preflight
        import csv,io
        people=copy.deepcopy(self.current['participants'])
        for p in people:p.update(first_choice='design',second_choice='agents')
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(people[0]));writer.writeheader();writer.writerows(people)
        valid=out.getvalue()
        self.run['result']={'cleaned_csv':valid,'participants':people}
        preflight(self.run,self.current)
        duplicate=valid+valid.splitlines()[1]+'\n'
        invalid=valid+'bad,,bad@example.test,design,agents,team\n'
        for text in (duplicate,invalid):
            self.run['result']['cleaned_csv']=text
            with self.subTest(csv=text),self.assertRaises(RunError):
                preflight(self.run,self.current)

    def test_rich_allocation_projection_keeps_ids_and_rejects_reported_errors(self):
        from workbench.action_app import preflight
        expected=copy.deepcopy(self.run['result'])
        for assignment in self.run['result']['assignments']:
            assignment.update(rank=1,group_id='team',room='room')
        self.run['result']['errors']=[]
        self.assertEqual(preflight(self.run,self.current),expected)
        self.run['result']['assignments']=[]
        self.run['result']['waitlist']=[{'participant_id':p['id'],'group_id':'team','reason':'No shared place available'} for p in self.current['participants']]
        self.assertEqual(preflight(self.run,self.current),{'assignments':[],'waitlist':['a','b']})
        self.run['result']['errors']=['An input rule could not be satisfied']
        with self.assertRaisesRegex(RunError,'successful'):
            preflight(self.run,self.current)
        self.run['result']['errors']=[]
        self.run['result']['waitlist'][0]['participant_id']=7
        with self.assertRaisesRegex(RunError,'IDs'):
            preflight(self.run,self.current)

    def test_duplicate_apply_rejected(self):
        from workbench.action_app import preflight
        self.run['application_apply']={'status':'completed'}
        with self.assertRaisesRegex(RunError,'already'):preflight(self.run,self.current)

class RealApplicationHandoff(unittest.TestCase):
    def test_preview_and_explicit_apply_in_real_chrome(self):
        from workbench.action_app import apply, context
        from workbench.browser_control import BrowserControl
        import csv,io
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);store=Store(directory);vault=FileVault(directory);browser=BrowserControl(vault);sandbox=Sandbox()
            try:
                browser.connect('https://event.workspace.demo',headless=True)
                people=[{'id':'a','name':'Alex','email':'alex@example.test','first_choice':'agents','second_choice':'design','group_id':'team'},{'id':'b','name':'Sam','email':'sam@example.test','first_choice':'agents','second_choice':'design','group_id':'team'}]
                out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(people[0]));writer.writeheader();writer.writerows(people)
                file=vault.put('roster.csv',out.getvalue().encode());browser.attach_files({file['id']:str(vault.get(file['id'])[1])},None)
                ref=next(e['ref'] for e in browser.cached['elements'] if e['name']=='Import participant CSV')
                browser.act({'action':'upload','ref':ref,'value':file['id']},Budget(max_seconds=30),lambda *a,**k:None)
                initial=copy.deepcopy(browser.cached['event_state'])
                manifest={**MANIFEST,'id':'fixture_app_allocation','input_schema':{'type':'object','properties':{k:{'type':'array'} for k in ('participants','rooms','workshops')},'required':['participants','rooms','workshops']},'output_schema':{'type':'object','properties':{'assignments':{'type':'array'},'waitlist':{'type':'array'}},'required':['assignments','waitlist']}}
                data={k:initial[k] for k in ('participants','rooms','workshops')}
                code='def run(d): return {"assignments":[{"participant_id":p["id"],"workshop_id":p["first_choice"],"rank":1,"group_id":p["group_id"]} for p in d["participants"]],"waitlist":[],"errors":[]}'
                expected={'assignments':[{'participant_id':p['id'],'workshop_id':'agents'} for p in people],'waitlist':[]}
                fixture=store.new_run('Infrastructure fixture',{})
                rich_expected={'assignments':[{**a,'rank':1,'group_id':'team'} for a in expected['assignments']],'waitlist':[],'errors':[]}
                record,_=Engine(Config(),None,sandbox,store).install(fixture,manifest,code,[{'name':'Synthetic paired booking','input':data,'expected':rich_expected}],Budget(),source='test_fixture')
                self.assertEqual(context(store,browser,manifest['id'])['input'],data)
                local=LocalActions(store,sandbox,vault)
                run=local.execute(local.prepare({'id':manifest['id'],'version':record['version'],'code_hash':record['code_hash'],'input':data},ai_paused=True))
                self.assertEqual(browser.cached['event_state']['assignments'],[])
                # A modified artifact must be rejected before the connector writes anything.
                _,artifact_path=vault.get(run['artifacts'][0]['id'])
                original=artifact_path.read_bytes()
                artifact_path.write_text('{"assignments":[],"waitlist":[]}')
                with self.assertRaisesRegex(RunError,'artifact changed'):
                    apply(store,browser,vault,run)
                self.assertNotIn('application_apply',run)
                self.assertEqual(browser.cached['event_state']['assignments'],[])
                artifact_path.write_bytes(original)
                result=apply(store,browser,vault,run)
                self.assertEqual(result['application_apply']['status'],'completed')
                self.assertEqual(result['result'],rich_expected)
                self.assertTrue(any(e['kind']=='application_projection' for e in store.events(result['id'])))
                self.assertEqual(result['model_calls'],0)
                self.assertEqual(browser.cached['event_state']['assignments'],expected['assignments'])
                self.assertIn('Group bookings kept together',result['application_apply']['verification']['checks'])
                self.assertEqual(result['permissions'],['compute'])
                with self.assertRaisesRegex(RunError,'already'):apply(store,browser,vault,run)
                # A second explicit action replaces the roster through the same fixed adapter.
                replacement=[{**p,'id':'new-'+p['id']} for p in people]
                out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(replacement[0]));writer.writeheader();writer.writerows(replacement)
                roster_input={'csv_text':out.getvalue(),'participants':replacement}
                roster_output={'cleaned_csv':out.getvalue(),'participants':replacement}
                roster_manifest={**MANIFEST,'id':'fixture_roster_passthrough','input_schema':{'type':'object','properties':{'csv_text':{'type':'string'},'participants':{'type':'array'}},'required':['csv_text','participants']},'output_schema':{'type':'object','properties':{'cleaned_csv':{'type':'string'},'participants':{'type':'array'}},'required':['cleaned_csv','participants']}}
                roster_code='def run(d): return {"cleaned_csv":d["csv_text"],"participants":d["participants"]}'
                roster_record,_=Engine(Config(),None,sandbox,store).install(store.new_run('Infrastructure roster fixture',{}),roster_manifest,roster_code,[{'name':'Clean replacement roster','input':roster_input,'expected':roster_output}],Budget(),source='test_fixture')
                roster_run=local.execute(local.prepare({'id':roster_manifest['id'],'version':roster_record['version'],'code_hash':roster_record['code_hash'],'input':roster_input},ai_paused=True))
                self.assertEqual(browser.cached['event_state']['assignments'],expected['assignments'])
                apply(store,browser,vault,roster_run)
                self.assertEqual(roster_run['application_apply']['operation'],'replace_roster')
                self.assertEqual(roster_run['model_calls'],0)
                self.assertEqual(browser.cached['event_state']['participants'],replacement)
                self.assertEqual(browser.cached['event_state']['assignments'],[])
                self.assertEqual(browser.cached['event_state']['waitlist'],[])
            finally:
                browser.close();store.close()
