"""Reviewer harness: real model, empty isolated registry, one OS process per task.

No generated capability is seeded. Only synthetic event data is sent to Gemini.
Run from repo root with SNAPSHOT_PATH STAGE arguments; existing Free confirmation
and bounded configuration are inherited without printing credentials.
"""
import sys
import json
import os
from pathlib import Path
from dataclasses import replace

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from workbench.config import load_env
load_env()
for name in list(sys.modules):
    if name == "workbench" or name.startswith("workbench."):
        del sys.modules[name]
snapshot, stage = Path(sys.argv[1]), int(sys.argv[2])
sys.path.insert(0, str(snapshot))
from workbench.config import Config
from workbench.model import Gemini
from workbench.sandbox import Sandbox
from workbench.store import Store, digest
from workbench.engine import Engine

normalization = (
    "Read this event registration CSV and return valid unique registrations plus rejected rows. "
    "Trim names and group IDs, lowercase and trim email, split preferences by | and trim each. "
    "A valid email has exactly one @ and nonempty parts on both sides. "
    "Reject missing names and invalid emails. For duplicate normalized emails keep the first valid row. "
    "Preserve valid row order. Each registration needs name, email, group, preferences (an array). "
    "Every rejected row needs its original 1-based data-row number and reason."
)
allocation = (
    "Allocate these event registrations to workshops with the given capacities. Keep groups together. "
    "Process groups by their first appearance; empty group means one individual. "
    "For each group consider the first member's preference order, choosing the first workshop "
    "that every member lists and that has enough remaining places for the entire group. "
    "Otherwise waitlist the whole group. Return assignments with email and workshop, waitlisted "
    "emails, and remaining capacities. Never exceed capacity or split a group."
)
TASKS = {
    1: (normalization, {"csv": "name,email,group,preferences\n Ada , ADA@example.test , G1 ,Design|AI\nBen,ben@example.test,G1,Design|AI\nAda duplicate,ada@example.test,,AI\nCy,invalid,,AI\nDee,dee@example.test,,AI\n"}),
    2: (allocation, {"registrations": [
        {"name": "Ada", "email": "ada@example.test", "group": "G1", "preferences": ["Design", "AI"]},
        {"name": "Ben", "email": "ben@example.test", "group": "G1", "preferences": ["Design", "AI"]},
        {"name": "Dee", "email": "dee@example.test", "group": "", "preferences": ["AI"]}],
        "capacities": {"Design": 1, "AI": 2}}),
    3: ("Our large room was cancelled. Prepare the new placement list directly from this new raw CSV. "
        + normalization + " Then " + allocation + " Return the rejected rows as well as the allocation.",
        {"csv": "name,email,group,preferences\n Erin , ERIN@example.test , G2 ,Design|AI\nFinn,finn@example.test,G2,Design|AI\nGale,gale@example.test,,AI\nHana,hana@example.test,,Design\nErin dup,erin@example.test,,AI\nIra,not-an-email,,AI\n", "capacities": {"Design": 1, "AI": 2}}),
}
config = replace(Config.from_env(), data_dir=snapshot / "acceptance-data")
store = Store(config.data_dir)
task, data = TASKS[stage]
before = store.registry()
run = store.new_run(task, data)
run["conversation"] = []
engine = Engine(config, Gemini(config), Sandbox(config.image), store)
engine.execute(run)
events, after = store.events(run["id"]), store.registry()
result = {"stage": stage, "pid": os.getpid(), "config": {"model": config.model,
          "free_confirmed": config.free_confirmed, "max_calls": config.max_calls,
          "max_seconds": config.max_seconds, "max_output": config.max_output},
          "before": before, "after": after, "run": run, "events": events,
          "catalog": store.catalog()}
(snapshot / f"live-{stage}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({"stage": stage, "status": run["status"], "error": run.get("error"),
      "calls": run["model_calls"], "result": run["result"], "catalog": bool(store.catalog()),
      "events": [{k:v for k,v in e.items() if k in ("kind", "message", "capability", "version")}
                 for e in events]}, ensure_ascii=False, indent=2), flush=True)
store.close()
