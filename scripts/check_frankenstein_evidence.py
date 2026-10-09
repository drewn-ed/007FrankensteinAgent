#!/usr/bin/env python3
"""Independently replay published Wisp evidence in real Docker, without a model.

Run from any directory with the repository's Python environment. Docker and the
approved python:3.12-slim image must already be available. No API credentials are
read. This team-written verifier and its domain metadata fixtures are NOT
agent-created skills. Actual generated code is read unchanged from public evidence.
Results overwrite only the two derived check JSON files beside that evidence.
"""
import copy
import csv
import io
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from workbench.config import Config
from workbench.engine import Engine
from workbench.model import Budget
from workbench.sandbox import Sandbox
from workbench.store import Store, digest
from tests.test_track_completion import DOMAIN_MANIFEST, DOMAIN_CODE, DOMAIN_CASES

EVIDENCE = ROOT / 'docs/frankenstein-final-evidence-2026-10-09'

def check_management():
    source_path = EVIDENCE / 'learning-chatgpt.json'
    source = json.loads(source_path.read_text())
    assert source['status'] in ('completed', 'failed')
    helpers = [r for r in source['registry_after_records'] if r['manifest'].get('kind') == 'discovery']
    assert len(helpers) == 1
    helper = helpers[0]
    assert helper['provenance']['run_id'] == source['id']
    assert helper['provenance']['source'] == 'agent'
    assert helper['code_hash'] == digest(helper['code'])
    assert all(t['passed'] for t in helper['tests'])
    proof = {
        'description': 'Independent real-Docker replay of the actual agent-generated catalog against synthetic registry lifecycle changes. The domain records and updates below are handwritten test fixtures, not additional agent-created abilities.',
        'source_run_id': source['id'], 'source_run_status': source['status'], 'source_run_error': source.get('error'), 'source_evidence': source_path.name,
        'helper_id': helper['manifest']['id'], 'helper_code_hash': helper['code_hash'],
        'source': 'agent-generated catalog replay; handwritten domain metadata fixtures',
        'model_calls': 0, 'permissions': ['compute'], 'checks': {}, 'snapshots': []
    }
    with tempfile.TemporaryDirectory() as folder:
        store = Store(Path(folder))
        try:
            engine = Engine(Config(), None, Sandbox(), store)
            run = store.new_run('Independent catalog lifecycle fixture replay', {})
            report = engine.test(helper['manifest'], helper['code'], helper['cases'], Budget())
            assert all(t['passed'] for t in report)
            store.accept(copy.deepcopy(helper['manifest']), helper['code'], copy.deepcopy(helper['cases']), report,
                {'source': 'evidence_replay', 'original_run_id': source['id'], 'original_code_hash': helper['code_hash']})
            proof['checks']['original_generated_catalog_cases_pass_again'] = True
            record, _ = engine.install(run, copy.deepcopy(DOMAIN_MANIFEST), DOMAIN_CODE, copy.deepcopy(DOMAIN_CASES), Budget(), source='test_fixture')
            assert record
            def search(label):
                before = digest(store.registry())
                result = engine.discover(run, 'CONTACT', ['emails'], Budget())
                assert digest(store.registry()) == before
                proof['snapshots'].append({'stage': label, 'catalog': store.catalog(), 'matched_versions': [{'id': x['manifest']['id'], 'version': x['version']} for x in result['matches']], 'registry_unchanged_by_lookup': True})
                return result
            first = search('initial_v1')
            assert first['matches'][0]['version'] == 1
            engine.install(run, copy.deepcopy(DOMAIN_MANIFEST), DOMAIN_CODE, copy.deepcopy(DOMAIN_CASES), Budget(), source='test_fixture')
            second = search('updated_v2')
            assert second['matches'][0]['version'] == 2
            assert proof['snapshots'][0]['catalog']['source_hash'] != proof['snapshots'][1]['catalog']['source_hash']
            proof['checks']['rebuilds_index_for_new_active_version'] = True
            store.deactivate(DOMAIN_MANIFEST['id'])
            assert search('deactivated')['matches'] == []
            assert store.catalog()['index'] == []
            proof['checks']['deactivated_version_not_discoverable'] = True
            store.activate(DOMAIN_MANIFEST['id'], 1)
            assert search('operator_rollback_to_v1')['matches'][0]['version'] == 1
            proof['checks']['reflects_operator_rollback_without_changing_authority'] = True
            assert all(r['manifest']['permissions'] == ['compute'] for r in store.registry())
            assert run['model_calls'] == 0
            proof['checks']['lookup_never_changes_registry_or_permissions'] = True
            proof['checks']['no_model_required'] = True
            proof['events'] = [e for e in store.events(run['id']) if e['kind'] == 'discovered']
            proof['catalog_test_report'] = report
        finally:
            store.close()
    assert digest(json.loads(source_path.read_text())) == digest(source)
    proof['checks']['original_evidence_unmodified'] = True
    path = EVIDENCE / 'management-check-complete-chain.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(proof, indent=2, ensure_ascii=False) + '\n')
    return {'output': str(path.relative_to(ROOT)), 'checks': proof['checks'], 'helper_id': proof['helper_id']}


def check_events():
    first = json.loads((EVIDENCE / 'learning-chatgpt.json').read_text())
    second = json.loads((EVIDENCE / 'fresh-session-strict.json').read_text())
    records = {r['manifest']['id']: r for r in first['registry_after_records']}
    sandbox = Sandbox()
    proof = {'description': 'Independent fixed verifier and real Docker replay of nonempty recorded event cases. These checks were written by the team after learning; they are additional evidence, not agent-authored admission tests.', 'learning_run_spend_note': 'The first ChatGPT learning run predates financial admission enforcement. Only the later Gemini reuse run has strict zero-dollar admission evidence.', 'runs': []}
    for run in (first,second):
        used = [e for e in run['events'] if e['kind']=='used']
        clean = next(e for e in used if 'clean_workshop_roster' in e['capability'])
        allocation = next(e for e in used if 'allocate_workshop_groups' in e['capability'])
        raw = run['input']['files'][0]['content']
        assert clean['input']['csv_text'] == raw
        seen = set(); expected_roster=[]
        for record in csv.DictReader(io.StringIO(raw)):
            row={k:(v or '').strip() for k,v in record.items()}
            row['email']=row['email'].lower()
            if row['email'] in seen: continue
            assert all(row[k] for k in ('id','name','email','first_choice','second_choice'))
            seen.add(row['email']);expected_roster.append(row)
        assert clean['output']['roster'] == expected_roster
        assert allocation['input']['roster'] == expected_roster
        assert allocation['input']['rooms'] == run['input']['rooms']
        assert allocation['input']['workshops'] == run['input']['workshops']
        rooms={r['id']:r for r in run['input']['rooms']}
        workshops={w['id']:w for w in run['input']['workshops']}
        remaining={key:r['capacity'] if r['open'] else 0 for key,r in rooms.items()}
        units={}
        for row in expected_roster:
            key=('group',row['group_id']) if row['group_id'] else ('person',row['id'])
            units.setdefault(key,[]).append(row)
        expected={}
        for members in units.values():
            target=''
            leader=members[0]
            for choice in dict.fromkeys([leader['first_choice'],leader['second_choice']]):
                room_id=workshops[choice]['room']
                if all(choice in (p['first_choice'],p['second_choice']) for p in members) and rooms[room_id]['open'] and remaining[room_id]>=len(members):
                    target=choice;remaining[room_id]-=len(members);break
            for member in members: expected[member['id']]=target
        actual=allocation['output']['assignments']
        assert len(actual)==len(expected) and len({r['id'] for r in actual})==len(expected)
        assert {r['id']:r['workshop_id'] for r in actual}==expected
        for row in actual:
            assert row['status']==('assigned' if expected[row['id']] else 'waitlisted')
            if not expected[row['id']]:assert row['reason']
        assigned=sum(bool(value) for value in expected.values())
        assert allocation['output']['assigned_count']==assigned
        assert allocation['output']['waitlisted_count']==len(expected)-assigned
        replay=[]
        for event in (clean,allocation):
            record=records[event['capability']]
            assert digest(record['code']) == event['code_hash'] == record['code_hash']
            assert sandbox.run(record['code'],event['input'])==event['output']
            replay.append({'id':event['capability'],'code_hash':event['code_hash'],'replay_matches_recorded_output':True})
        proof['runs'].append({'run_id':run['id'],'status':run['status'],'participants':len(expected),'assigned':assigned,'waitlisted':len(expected)-assigned,'expected_assignments':expected,'checks':{'source_csv_preserved':True,'first_valid_email_order_preserved':True,'actual_cleaner_output_used_by_allocator':True,'room_and_workshop_inputs_preserved':True,'every_participant_accounted_once':True,'group_integrity_and_leader_preference_policy':True,'closed_rooms_and_capacity_respected':True,'nonempty_actual_outputs_replayed_in_docker':True},'replayed_capabilities':replay})
    path=EVIDENCE / 'independent-event-check.json'
    path.write_text(json.dumps(proof,indent=2)+'\n')
    return {'output': str(path.relative_to(ROOT)), 'runs': [{k: r[k] for k in ('run_id', 'participants', 'assigned', 'waitlisted')} for r in proof['runs']]}


if __name__ == "__main__":
    print(json.dumps({"management": check_management(), "events": check_events(), "model_calls": 0}, indent=2))
