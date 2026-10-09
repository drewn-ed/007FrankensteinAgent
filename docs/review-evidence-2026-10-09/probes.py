"""Reviewer probes: synthetic models only; failures reproduce missing guarantees.
No API calls, browser actions, credentials, or changes to the live workspace.
"""
import json
import tempfile
from pathlib import Path
from workbench.config import Config
from workbench.engine import Engine
from workbench.store import Store, digest

class FinishOnly:
    def ready(self): return None
    def ask(self, system, payload, budget):
        budget.reserve()
        return {"action": "finish", "message": "The requested item was created.", "result": {"created": True}}

class NoExecutionSandbox:
    def status(self): return True
    def run(self, *args, **kwargs): raise AssertionError("Unexpected execution")

class UnchangedBrowser:
    cached = {"origin": "https://example.test"}
    def observation(self): return {"connected": True, "origin": "https://example.test", "url": "https://example.test/", "text": "No items", "elements": []}
    def act(self, *args, **kwargs): raise AssertionError("Unexpected browser action")

manifest = {"id": "project_b_fixture", "title": "Fixture", "description": "Synthetic fixture, not an agent-created skill", "kind": "task", "permissions": ["compute"], "input_schema": {"type": "object"}, "output_schema": {"type": "object"}}
results = {}
with tempfile.TemporaryDirectory() as directory:
    store = Store(Path(directory))
    store.scoped("project-b").accept(manifest, "def run(data): return data", [{"name": "Fixture", "input": {}, "expected": {}}], [{"passed": True}], {"source": "review_fixture"})
    before = digest(store.registry())
    run = store.new_run("Read-only task in project A", {})
    run["project_id"] = "project-a"
    Engine(Config(), FinishOnly(), NoExecutionSandbox(), store.scoped("project-a")).execute(run)
    results["project_registry_fingerprint"] = {"actual_global_registry_unchanged": before == digest(store.registry()), "recorded_before_equals_after": run["registry_before"] == run["registry_after"], "status": run["status"]}
    store.scoped("project-a").remember_app({"connected": True, "origin": "https://example.test", "title": "Project A", "elements": [{"tag": "button", "name": "Synthetic project A item"}]})
    results["application_memory_scope"] = {"project_b_can_read_project_a_map": bool(store.scoped("project-b").applications()), "map_count": len(store.scoped("project-b").applications())}
    run = store.new_run("Create one item in the connected app and confirm it exists", {})
    run["mode"] = "browser"
    Engine(Config(), FinishOnly(), NoExecutionSandbox(), store.scoped(None), UnchangedBrowser()).execute(run)
    results["unverified_browser_completion"] = {"status": run["status"], "result": run["result"], "events": [event["kind"] for event in store.events(run["id"])], "browser_action_count": 0, "note": "Fault-injected planner response, not observed real Gemini behavior"}
    store.close()
print(json.dumps(results, indent=2))
