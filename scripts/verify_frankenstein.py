#!/usr/bin/env python3
"""Team-written verification harness, NOT an agent-created capability.

Run the two phases as separate processes. Only declared persistent registry data
passes between them; no conversation history or manually connected skill IDs do.
Every attempt keeps a unique evidence file, including failed attempts. These are
real Gemini Free requests, not a replay; no paid fallback is available.
"""
import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from workbench.config import Config
from workbench.engine import Engine
from workbench.providers import create_model
from workbench.sandbox import Sandbox
from workbench.spend import policy_status
from workbench.store import Store, digest

FIRST_TASK = "Prepare workshop places from the registration CSV and the supplied rooms. Trim fields and normalize emails, keep the first valid row per email, preserve participant IDs and group_id. Allocate each nonempty group together, processing booking units by their first member in the roster. Try that member's first then second choice only if every member accepts it and the whole booking fits an open room; otherwise waitlist the entire group. Return a cleaned roster/CSV and assignments with reasons for anyone waiting. I also need to hand this desk to another coordinator tomorrow: they need to look up the available reusable operations by what they do and the input fields they accept, without another model conversation each time. That lookup must stay current as operations are added, corrected or retired, and must not recommend inactive or failed versions. Make both the event result and that ongoing operational handover usable, and verify them. Choose the implementation yourself; reuse compatible work if it already exists. Do not open or modify a live application."
SECOND_TASK = "Hall A is now closed and a late two-person booking has joined our workshops. Prepare a revised allocation from the attached current roster and rooms. Keep the same first-valid-email cleaning and first-member-order group policy: a booking stays together, try its leader's first then second choice only if all members accept it and the whole booking fits, otherwise waitlist it. Find the suitable saved operations using their accepted inputs, reuse them and explain who cannot get a seat. Also give the coordinator an up-to-date list of usable operations for the next shift. Do not modify a live application."


def inputs_for(phase):
    bundle = json.loads((ROOT / 'docs/patch-blackout-evidence-2026-10-09/replay-bundle.json').read_text())
    name = 'group-bookings.csv' if phase == 'first' else 'group-bookings-late.csv'
    inputs = {'files': [{'name': name, 'content': (ROOT / 'examples' / name).read_text()}],
              **bundle['allocation_context']}
    if phase == 'second':
        inputs['rooms'][0]['open'] = False
    return inputs


def checks_for(phase, run, before, after, events, catalog):
    tasks = [r for r in after if r['manifest'].get('kind', 'task') == 'task']
    helpers = [r for r in after if r['manifest'].get('kind') == 'discovery']
    spend = run.get('spend_budget') or {}
    checks = {
        'completed': run['status'] == 'completed',
        'compute_only_permissions': all(r['manifest']['permissions'] == ['compute'] for r in after),
        'all_active_versions_tested': bool(after) and all(r.get('tests') and all(t.get('passed') is True for t in r['tests']) for r in after),
        'at_least_two_task_skills': len(tasks) >= 2,
        'discovery_skill_present': bool(helpers),
        'catalog_persisted': bool(catalog),
        'discovery_executed': any(e['kind'] == 'discovered' for e in events),
        'strict_zero_budget': spend.get('policy') == 'strict' and spend.get('max_usd') == '0' and spend.get('guaranteed') is True,
        'fresh_conversation': not run.get('conversation'),
    }
    if phase == 'first':
        checks['started_empty'] = not before
        checks['discovery_generated_this_run'] = any(r.get('provenance', {}).get('run_id') == run['id'] for r in helpers)
    else:
        prior_tasks = {r['manifest']['id'] for r in before if r['manifest'].get('kind', 'task') == 'task'}
        used = {e.get('capability') for e in events if e['kind'] == 'used'}
        checks.update(registry_unchanged=digest(before) == digest(after),
                      no_new_installation=not any(e['kind'] == 'installed' for e in events),
                      combined_two_prior_tasks=len(prior_tasks & used) >= 2)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=('first', 'second'))
    parser.add_argument('--data-dir', type=Path, default=ROOT / '.runtime/frankenstein-verification')
    args = parser.parse_args()
    config = replace(Config.from_env(), provider='gemini', model=os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash-lite'),
                     spend_policy='strict', max_run_usd='0', max_calls=20, max_seconds=600,
                     data_dir=args.data_dir.resolve())
    status = policy_status(config)
    model = create_model(config)
    if error := model.ready() or status['error']:
        parser.exit(2, error + '\n')
    store = Store(config.data_dir)
    try:
        before = store.registry()
        if args.phase == 'first' and before:
            parser.exit(2, 'First phase requires an empty registry. Choose a new --data-dir; existing evidence is retained.\n')
        if args.phase == 'second':
            kinds = [r['manifest'].get('kind', 'task') for r in before]
            if kinds.count('task') < 2 or 'discovery' not in kinds:
                parser.exit(2, 'Second phase requires at least two tested task skills and a discovery skill from the first phase.\n')
        run = store.new_run(FIRST_TASK if args.phase == 'first' else SECOND_TASK, inputs_for(args.phase))
        run['conversation'] = []
        store.save_run(run)
        engine = Engine(config, model, Sandbox(config.image), store)
        original_event = engine.event
        def event(record, kind, message, **data):
            original_event(record, kind, message, **data)
            print(json.dumps({'event': kind, 'message': message[:300]}, ensure_ascii=False), flush=True)
        engine.event = event
        engine.execute(run)
        events, after, catalog = store.events(run['id']), store.registry(), store.catalog()
        checks = checks_for(args.phase, run, before, after, events, catalog)
        evidence = {**run, 'phase': args.phase, 'harness': 'team-written verification infrastructure',
                    'events': events, 'registry_before_records': before, 'registry_after_records': after,
                    'catalog': catalog, 'verification_checks': checks}
        path = config.data_dir / (run['id'] + '.json')
        with path.open('x') as output:
            json.dump(evidence, output, ensure_ascii=False, indent=2)
        print(json.dumps({'id': run['id'], 'phase': args.phase, 'status': run['status'],
                          'model_calls': run['model_calls'], 'evidence': str(path),
                          'checks_passed': all(checks.values()), 'failed_checks': [k for k,v in checks.items() if not v],
                          'error': run.get('error')}, ensure_ascii=False), flush=True)
        return 0 if all(checks.values()) else 1
    finally:
        store.close()


if __name__ == '__main__':
    raise SystemExit(main())
