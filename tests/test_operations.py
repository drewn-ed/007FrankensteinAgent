import base64
import copy
import json
import tempfile
import time
import unittest
from pathlib import Path
from workbench.files import FileVault
from workbench.browser_control import BrowserControl
from workbench.event_validation import source_roster, verify_event
from workbench.model import Budget, RunError
from workbench.scheduler import Scheduler
from workbench.config import ROOT


class FilesAndSchedules(unittest.TestCase):
    def test_file_scope_and_binary_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault=FileVault(Path(tmp)); file=vault.upload({'name':'clip.bin','base64':base64.b64encode(b'\x00\x01\xff').decode()})
            inputs,paths=vault.input_files({'files':[file]})
            self.assertNotIn('content',inputs['files'][0]); self.assertEqual(Path(paths[file['id']]).read_bytes(),b'\x00\x01\xff')
            with self.assertRaises(RunError): vault.get('../credentials')
            with self.assertRaises(RunError): vault.put('../leak',b'a')
            browser=BrowserControl(vault); browser.cached={'connected':True,'origin':'https://event.workspace.demo'}
            with self.assertRaisesRegex(RunError,'attached'):browser.act({'action':'upload','ref':'e1','value':file['id']},Budget(1,30),lambda *a,**k:None)
            browser.close()

    def test_schedule_restart_once_pause_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock=[1000.];calls=[]
            def start(task,data,**kwargs):calls.append((task,data,kwargs));return {'id':'run-'+str(len(calls))}
            scheduler=Scheduler(Path(tmp),start,lambda:False,clock=lambda:clock[0])
            row=scheduler.create({'title':'Scheduled data','task':'Check roster','next_at':1000.,'interval_minutes':0})
            scheduler.tick();scheduler.tick();self.assertEqual(len(calls),1)
            scheduler.close();scheduler=Scheduler(Path(tmp),start,lambda:False,clock=lambda:clock[0]);scheduler.tick();self.assertEqual(len(calls),1)
            self.assertEqual(scheduler.rows()[0]['history'][0]['run_id'],'run-1')
            interval=scheduler.create({'title':'Recurring','task':'Check data','next_at':1000.,'interval_minutes':15})
            clock[0]+=86400;scheduler.tick();scheduler.tick();self.assertEqual(len(calls),2)
            self.assertEqual(next(r for r in scheduler.rows() if r['id']==interval['id'])['next_at'],clock[0]+900)
            scheduler.update(interval['id'],False);clock[0]+=1000;scheduler.tick();self.assertEqual(len(calls),2)
            scheduler.update(interval['id'],True)
            def unavailable(*a,**kw):raise RunError('Model not ready')
            scheduler.start=unavailable;scheduler.tick();row=next(r for r in scheduler.rows() if r['id']==interval['id'])
            self.assertFalse(row['enabled']);self.assertEqual(row['history'][-1]['status'],'failed');scheduler.close()

    def test_busy_scheduler_preserves_occurrence(self):
        with tempfile.TemporaryDirectory() as tmp:
            scheduler=Scheduler(Path(tmp),lambda *a,**k:self.fail('busy must not dispatch'),lambda:True,clock=lambda:1000.)
            scheduler.create({'title':'Busy','task':'Work later','next_at':1000.});scheduler.tick()
            self.assertTrue(scheduler.rows()[0]['enabled']);self.assertEqual(scheduler.rows()[0]['history'],[]);scheduler.close()


class EventBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.vault=FileVault(Path(cls.tmp.name));cls.browser=BrowserControl(cls.vault)
        cls.budget=Budget(20,240);cls.events=[]
        cls.browser.connect('https://event.workspace.demo',headless=True)
        cls.before=copy.deepcopy(cls.browser.observation()['event_state'])
        cls.source=json.loads((ROOT/'examples/event-showcase.json').read_text())
        cls.inputs={'files':[{'name':cls.source['name'],'content':cls.source['content']}]}
        cls.people=source_roster(cls.inputs)

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.tmp.cleanup()

    def event(self,kind,text,**data):self.events.append({'kind':kind,**data})
    def act(self,action,name,value=None):
        matches=[e for e in self.browser.cached['elements'] if e['name']==name]
        self.assertEqual(len(matches),1,(name,self.browser.cached['elements']))
        return self.browser.act({'action':action,'ref':matches[0]['ref'],'value':value},self.budget,self.event)
    def upload(self,name,content,control):
        meta=self.vault.put(name,content.encode());self.browser.allowed_files[meta['id']]=str(self.vault.get(meta['id'])[1]);return self.act('upload',control,meta['id'])

    def test_full_import_allocate_replan_export_and_reject_bad_plan(self):
        import csv,io
        stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=['id','name','email','first_choice','second_choice']);writer.writeheader();writer.writerows(self.people)
        self.upload('clean.csv',stream.getvalue(),'Import participant CSV')
        self.assertEqual(len(self.browser.cached['event_state']['participants']),24)
        self.act('click','Workshop board 03')
        allocations=[{'participant_id':p['id'],'workshop_id':p['first_choice']} for p in self.people]
        invalid={'assignments':allocations+[allocations[0]],'waitlist':[]}
        self.upload('invalid.json',json.dumps(invalid),'Import allocation JSON')
        self.assertFalse(self.browser.cached['event_state']['proposal_ready'])
        self.assertFalse(any(e['name']=='Apply verified allocation' for e in self.browser.cached['elements']))
        self.upload('allocation.json',json.dumps({'assignments':allocations,'waitlist':[]}),'Import allocation JSON')
        self.act('click','Apply verified allocation')
        first=copy.deepcopy(self.browser.cached['event_state']);verified=verify_event(first,self.before,self.inputs)
        self.assertEqual(verified['assigned'],24);self.assertEqual(verified['first_preferences'],24)
        unchanged=[a for a in first['assignments'] if a['workshop_id']!='agents']
        self.act('click','Overview 01');self.act('click','Close Hall A');self.assertEqual(self.browser.cached['event_state']['conflicts'],['agents'])
        self.act('click','Move Agents lab to Studio D');self.act('click','Workshop board 03')
        revised={'assignments':[a for a in allocations if a['participant_id'] not in ('p09','p10')],'waitlist':['p09','p10']}
        self.upload('revised.json',json.dumps(revised),'Import allocation JSON');self.act('click','Apply verified allocation')
        final=self.browser.cached['event_state'];verified=verify_event(final,first,{})
        self.assertEqual(verified['assigned'],22);self.assertEqual(verified['waitlist'],2)
        self.assertEqual([a for a in final['assignments'] if a['workshop_id']!='agents'],unchanged)
        with self.assertRaises(RunError):verify_event(final,final,{})
        wrong=copy.deepcopy(final);wrong['participants'][0]['name']='Invented'
        with self.assertRaises(RunError):verify_event(wrong,self.before,self.inputs)
        self.act('click','Export operations report')
        artifacts=[e['artifact'] for e in self.events if e['kind']=='artifact'];self.assertEqual(len(artifacts),1)
        meta,path=self.vault.get(artifacts[0]['id']);export=json.loads(path.read_text());self.assertEqual(export['assignments'],final['assignments']);self.assertEqual(export['waitlist'],['p09','p10'])
        changed=copy.deepcopy(final);changed['assignments']=[a for a in changed['assignments'] if a['participant_id']!='p11'];changed['waitlist'].append('p11')
        with self.assertRaisesRegex(RunError,'unaffected'):
            verify_event(changed,first,{},preserve_unaffected=True)
        (ROOT/'.runtime/event-browser-smoke.json').write_text(json.dumps({'verified':verified,'export_size':meta['size'],'source_rows':28,'cleaned_rows':24,'note':'Deterministic connector test, not a model-generated run'},indent=2))
        import base64
        (ROOT/'.runtime/event-browser-smoke.jpg').write_bytes(base64.b64decode(self.browser.cached['screenshot']))

class StructuredTransport(unittest.TestCase):
    def test_builder_and_tester_share_explicit_shape(self):
        from workbench.model import response_schema
        from workbench.engine import BUILDER,TESTER,PLANNER
        schema=response_schema(BUILDER,{})
        self.assertEqual(schema['required'],['code']);self.assertFalse(schema['additionalProperties'])
        manifest={'input_schema':{'type':'object','properties':{'roster':{'type':'array','items':{'type':'string'}}},'required':['roster']},'output_schema':{'type':'integer'}}
        schema=response_schema(TESTER,{'manifest':manifest})
        self.assertEqual(schema['properties']['cases']['items']['properties']['input'],manifest['input_schema'])
        self.assertIsNone(response_schema(PLANNER,{}))

class ProgressAndNativeBoundaries(unittest.TestCase):
    def test_repeated_computation_stops_without_running_it_again(self):
        from workbench.engine import Engine
        from workbench.store import Store
        from workbench.config import Config
        class Model:
            def ready(self):return None
            def ask(self,system,payload,budget):budget.reserve();return {'action':'call','id':'check_roster','input':{'rows':[1,2,3]}}
        class Sandbox:
            calls=0
            def status(self):return True
            def run(self,*a,**kw):self.calls+=1;return {'count':3}
        with tempfile.TemporaryDirectory() as tmp:
            store=Store(Path(tmp));sandbox=Sandbox()
            manifest={'id':'check_roster','title':'Test fixture','description':'Handwritten progress probe, not agent-generated.', 'permissions':['compute'], 'input_schema':{'type':'object'},'output_schema':{'type':'object'}}
            store.accept(manifest,'fixture', [{}], [{'passed':True}], {'source':'test_fixture'})
            run=store.new_run('Report the supplied queue',{'rows':[1,2,3]})
            Engine(Config(max_calls=10),Model(),sandbox,store).execute(run)
            self.assertEqual(run['status'],'failed');self.assertIn('without making progress',run['error']);self.assertEqual(sandbox.calls,1);self.assertEqual(run['model_calls'],3);store.close()

    def test_native_mutation_waits_for_review_and_decline_has_no_effect(self):
        import threading
        from unittest.mock import Mock
        from workbench.desktop_control import DesktopControl
        desktop=DesktopControl();desktop.cached={'connected':True,'origin':'desktop:fixture'};desktop.request=Mock()
        errors=[]
        def act():
            try:desktop.act({'action':'click','ref':'d1_1'},Budget(5,3),lambda *a,**k:None)
            except RunError as error:errors.append(str(error))
        t=threading.Thread(target=act);t.start()
        for _ in range(100):
            if desktop.pending:break
            time.sleep(.005)
        self.assertIsNotNone(desktop.pending);desktop.request.assert_not_called();desktop.approve(False);t.join(2)
        desktop.request.assert_not_called();self.assertIn('declined',errors[0]);desktop.close()
