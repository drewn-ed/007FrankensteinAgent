"""Explicit operator handoff from a local preview to the fixed Fieldwork connector.

This adapter is team-authored. It is not a skill, and grants generated code no
browser access. A preview cannot be applied after the source app data changes.
"""
import csv
import io
import copy
import time

from .engine import validate_data
from .event_validation import verify_event, source_roster
from .local_actions import checked_record, strict_inputs
from .model import Budget, RunError
from .store import digest

ORIGIN = 'https://event.workspace.demo'
KEYS = ('participants', 'rooms', 'workshops')


def snapshot(browser):
    if browser.cached.get('origin') != ORIGIN or not browser.cached.get('connected'):
        raise RunError('Connect the Fieldwork event showcase first.')
    current = browser.request('act', {'action':'inspect'})
    if current.get('origin') != ORIGIN or not isinstance(current.get('event_state'), dict):
        raise RunError('The connected app is not the Fieldwork showcase.')
    return current['event_state']


def context(store, browser, ident):
    record = store.get(ident)
    if not record: raise RunError('Action not found.')
    checked_record(store, ident, record['version'], record['code_hash'])
    schema = record['manifest']['input_schema']
    if not all(key in schema.get('properties', {}) for key in KEYS):
        raise RunError('This action does not accept a Fieldwork roster, rooms and workshops. Import its inputs from a file instead.')
    current = snapshot(browser)
    inputs = {key: current[key] for key in KEYS}
    # Replanners may explicitly accept the old allocation. Never infer arbitrary fields.
    for key in ('assignments', 'waitlist'):
        if key in schema.get('properties', {}): inputs[key] = current[key]
    validate_data(inputs, schema)
    strict_inputs(inputs, schema)
    return {'input':inputs, 'application':ORIGIN, 'revision':current['revision'], 'app_context':{'origin':ORIGIN,'revision':current['revision'],'state_hash':digest(current)}}


def preflight(run, current):
    if run.get('kind') != 'local_action' or run.get('status') != 'completed':
        raise RunError('Only a completed local action can be applied.')
    if run.get('application_apply'):
        raise RunError('This preview already had an apply attempt. Inspect the app and create a fresh preview.')
    binding = run.get('app_context')
    if binding and (binding.get('origin') != ORIGIN or binding.get('revision') != current.get('revision') or binding.get('state_hash') != digest(current)):
        raise RunError('The application changed after inputs were loaded. Load current app data and preview again.')
    inputs, output = run.get('input'), run.get('result')
    if isinstance(output, dict) and isinstance(output.get('cleaned_csv'), str) and isinstance(output.get('participants'), list):
        if len(output['cleaned_csv'].encode()) > 120_000:
            raise RunError('The cleaned CSV exceeds the Fieldwork input limit.')
        reader = csv.DictReader(io.StringIO(output['cleaned_csv']))
        columns = ['id','name','email','first_choice','second_choice']
        if reader.fieldnames not in (columns, columns+['group_id']):
            raise RunError('The cleaned CSV needs the documented Fieldwork column order.')
        raw = list(reader)
        if not 1 <= len(raw) <= 200 or raw != output['participants']:
            raise RunError('The cleaned CSV rows do not exactly match the preview participants.')
        expected = source_roster({'files':[{'name':'clean.csv','content':output['cleaned_csv']}]})
        if not expected or expected != output['participants'] or len({p['id'] for p in expected}) != len(expected):
            raise RunError('The cleaned CSV does not match a valid unique Fieldwork roster.')
        return output
    if not isinstance(inputs, dict) or not all(inputs.get(k) == current.get(k) for k in KEYS):
        raise RunError('The preview inputs differ from the current app. Load current app data and preview again.')
    if any(key in inputs and inputs[key] != current.get(key) for key in ('assignments','waitlist')):
        raise RunError('The existing allocation changed after this preview. Load current app data and preview again.')
    if not isinstance(output, dict) or output.get('errors') or not isinstance(output.get('assignments'), list) or not isinstance(output.get('waitlist'), list):
        raise RunError('This result is not a successful Fieldwork allocation.')
    # The fixed adapter projects explicit IDs from either the minimal contract or
    # richer learned results (which retain reasons/ranks in the original preview).
    try:
        plan = {'assignments':[{'participant_id':a['participant_id'],'workshop_id':a['workshop_id']} for a in output['assignments']],
                'waitlist':[a['participant_id'] if isinstance(a,dict) else a for a in output['waitlist']]}
        if any(not isinstance(a[k], str) for a in plan['assignments'] for k in ('participant_id','workshop_id')) or any(not isinstance(a,str) for a in plan['waitlist']):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise RunError('The allocation must contain explicit participant and workshop IDs.') from None
    if not current.get('participants'):
        raise RunError('Import a roster into Fieldwork first.')
    after = {**copy.deepcopy(current), **plan, 'applied_revision':current['revision']+1}
    try:
        verify_event(after, current, {})
    except (KeyError, TypeError, ValueError) as error:
        raise RunError('The allocation is malformed.') from error
    return plan


def apply(store, browser, vault, run):
    current = snapshot(browser)
    plan = preflight(run, current)
    roster_import = 'cleaned_csv' in plan
    # Deactivated or changed skills cannot apply a stale preview.
    ref = run['action']
    checked_record(store.scoped(run.get('project_id')),ref['id'],ref['version'],ref['code_hash'])
    artifact = next((a for a in run.get('artifacts',[]) if a.get('name')=='action-result.json'), None)
    if not artifact: raise RunError('The preview artifact is missing.')
    _, path = vault.get(artifact['id'])
    import json
    if json.loads(path.read_text()) != run['result']: raise RunError('The preview artifact changed.')
    run['application_apply'] = {'status':'applying','origin':ORIGIN,'source_revision':current['revision'],'before_hash':digest(current),'started_at':time.time()}
    store.save_run(run)
    budget = Budget(max_calls=0,max_seconds=30)
    def event(kind, message, **data): store.event(run['id'],kind,message,**data)
    def operate(name, action, value=None):
        matches=[e for e in browser.cached.get('elements',[]) if e.get('name')==name and not e.get('disabled')]
        if len(matches)!=1: raise RunError('The Fieldwork control changed: '+name)
        args={'action':action,'ref':matches[0]['ref']}
        if value is not None:args['value']=value
        return browser.act(args,budget,event)
    try:
        browser.attach_files({artifact['id']:str(path)},run['id'])
        event('application_approval','Operator requested applying this exact preview to the local Fieldwork showcase. Generated code retains compute-only permission.',result_hash=digest(plan))
        if roster_import:
            csv_file = vault.put('cleaned-roster.csv',plan['cleaned_csv'].encode(),run_id=run['id'],source='local_action')
            browser.allowed_files[csv_file['id']] = str(vault.get(csv_file['id'])[1])
            operate('Overview 01','click')
            operate('Import participant CSV','upload',csv_file['id'])
            after = browser.cached.get('event_state',{})
            if after.get('participants') != plan['participants'] or after.get('assignments') or after.get('waitlist') or after.get('revision',-1) <= current['revision']:
                raise RunError('The application does not match the approved roster import.')
            run['application_apply'].update(status='completed',operation='replace_roster',verification={'participants':len(plan['participants']),'checks':['Imported roster matches preview','Previous assignments cleared']},finished_at=time.time())
            event('application_verified','The approved roster was imported and checked in Fieldwork.',participants=len(plan['participants']),model_calls=0)
            return run
        projected = vault.put('fieldwork-allocation.json',json.dumps(plan).encode(),run_id=run['id'],source='local_action_adapter')
        browser.allowed_files[projected['id']] = str(vault.get(projected['id'])[1])
        event('application_projection','Applying only participant/workshop IDs and waitlist IDs. Extra explanation fields remain in the original result.',projection=plan)
        operate('Workshop board 03','click')
        operate('Import allocation JSON','upload',projected['id'])
        fresh=browser.cached.get('event_state',{})
        # Upload may show a proposal but must not alter the underlying input data.
        if any(fresh.get(k)!=current.get(k) for k in KEYS) or fresh.get('revision')!=current['revision']:
            raise RunError('The application changed during preview. Recompute before applying.')
        operate('Apply verified allocation','click')
        after=browser.cached.get('event_state',{})
        checks=verify_event(after,current,{})
        if after.get('assignments')!=plan['assignments'] or after.get('waitlist')!=plan['waitlist']:
            raise RunError('The application does not match the approved preview.')
        run['application_apply'].update(status='completed',verification=checks,finished_at=time.time())
        event('application_verified','The approved preview was applied and independently checked in Fieldwork.',verification=checks,model_calls=0)
    except Exception as error:
        run['application_apply'].update(status='needs_review',error=str(error)[:500])
        event('application_error','Apply did not finish with a verified result. Inspect Fieldwork before retrying.',error=str(error)[:500])
        raise
    finally:
        browser.attach_files({},None)
        store.save_run(run)
    return run
