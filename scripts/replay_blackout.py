#!/usr/bin/env python3
"""Credential-free replay of published agent-authored code. NOT fresh learning.

Generated code is only executed through the existing networkless Docker sandbox.
The harness connects the two stages explicitly; it does not demonstrate discovery.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from workbench.config import Config
from workbench.engine import Engine, validate_manifest
from workbench.model import Budget, RunError
from workbench.server import Application, WorkspaceHTTPServer, handler_for
from workbench.store import digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,default=ROOT/'docs/patch-blackout-evidence-2026-10-09/replay-bundle.json')
    parser.add_argument('--data-dir',type=Path,default=ROOT/'.runtime/blackout-replay')
    parser.add_argument('--serve',action='store_true',help='Open the replay workspace at the printed URL after verification')
    parser.add_argument('--port',type=int,default=8789)
    args=parser.parse_args()
    bundle=json.loads(args.bundle.read_text())
    if bundle.get('format')!='wisp-blackout-replay-v1':raise RunError('Unsupported replay bundle.')
    app=Application(Config(data_dir=args.data_dir.resolve(),key='',provider='gemini',model='gemini-3.5-flash-lite',chatgpt_auth_dir=args.data_dir.resolve()/'no-account'))
    server=None
    try:
        if app.store.registry():raise RunError('Use a fresh --data-dir. The replay will not replace existing skills.')
        app.store.save_workspace({'projects':[{'id':'patch-workshops','name':'Workshop operations (recorded replay)','instructions':'Recorded agent-authored skills, retested locally. No model connected.'}], 'chats':[],'workflows':[]})
        scope=app.store.scoped('patch-workshops')
        engine=Engine(app.config,None,app.sandbox,scope)
        total=0
        for saved in bundle['skills']:
            validate_manifest(saved['manifest'])
            if saved['manifest'].get('kind','task')!='task' or digest(saved['code'])!=saved['code_hash']:
                raise RunError('Replay accepts intact compute task skills only.')
            report=engine.test(saved['manifest'],saved['code'],saved['cases'],Budget(max_calls=0,max_seconds=120))
            scope.accept(saved['manifest'],saved['code'],saved['cases'],report,{'source':'recorded_evidence_replay','original_provenance':saved['provenance'],'original_code_hash':saved['code_hash'],'test_source':'original_model_cases_reexecuted'})
            total+=len(report)
        app.set_blackout(True)
        def execute(ident,inputs):
            record=scope.get(ident)
            run=app.start_local({'id':ident,'version':record['version'],'code_hash':record['code_hash'],'project_id':'patch-workshops','input':inputs})
            app.future.result(timeout=15)
            result=app.store.run(run['id'])
            if result['status']!='completed':raise RunError(result.get('error','Replay failed.'))
            if result['model_calls']!=0 or result['registry_before']!=result['registry_after']:raise RunError('Replay invariants failed.')
            return result
        clean=execute(bundle['cleaner'],bundle['cleaner_input'])
        allocation=execute(bundle['allocator'],{**bundle['allocation_context'],'participants':clean['result']['participants']})
        if allocation['result']!=bundle['expected_allocation']:raise RunError('Replay differs from the recorded result.')
        report={'replay':True,'fresh_agent_generation':False,'ai_paused':True,'model_configured':False,'sandbox_tests_passed':total,'model_calls':0,'registry_unchanged':True,'participants':len(clean['result']['participants']),'assigned':len(allocation['result']['assignments']),'waiting':len(allocation['result']['waitlist']),'run_ids':[clean['id'],allocation['id']]}
        print(json.dumps(report,indent=2),flush=True)
        (args.data_dir/'replay-report.json').write_text(json.dumps(report,indent=2))
        if args.serve:
            server=WorkspaceHTTPServer(('127.0.0.1',args.port),handler_for(app,args.port))
            print(f'Recorded replay workspace: http://127.0.0.1:{args.port} · Library → Actions',flush=True)
            try:server.serve_forever()
            except KeyboardInterrupt:pass
    finally:
        if server:server.server_close()
        app.scheduler.close();app.pool.shutdown(wait=True);app.browser.close();app.desktop.close();app.store.close()

if __name__=='__main__':
    try:main()
    except (RunError,ValueError,OSError) as error:
        print('Replay stopped: '+str(error),file=sys.stderr);raise SystemExit(1)
