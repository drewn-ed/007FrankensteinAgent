"""Fault-injection probes. Handwritten fixtures NEVER count as agent generation."""
import json
import sys
from pathlib import Path
from dataclasses import replace

snapshot = Path(sys.argv[1])
sys.path.insert(0, str(snapshot))
from workbench.config import Config
from workbench.engine import Engine
from workbench.store import Store, digest
from workbench.sandbox import Sandbox

manifest = {
    "id": "review_contact_normalizer", "title": "Review contact normalizer",
    "description": "Normalize emails to lowercase, trim whitespace and remove duplicates in order.",
    "kind": "task", "permissions": ["compute"],
    "input_schema": {"type": "object", "properties": {"emails": {"type": "array", "items": {"type": "string"}}}, "required": ["emails"]},
    "output_schema": {"type": "array", "items": {"type": "string"}}
}
cases = [
    {"name": "Whitespace", "input": {"emails": [" a@example.test "]}, "expected": ["a@example.test"]},
    {"name": "Case", "input": {"emails": ["A@EXAMPLE.TEST"]}, "expected": ["a@example.test"]},
    {"name": "Duplicates", "input": {"emails": ["a@example.test", "a@example.test"]}, "expected": ["a@example.test"]},
]
code = '''def run(data):
    if "broken@example.test" in data["emails"]:
        raise ValueError("Synthetic unseen-case failure")
    return list(dict.fromkeys(x.strip().lower() for x in data["emails"]))
'''

class FixtureModel:
    def __init__(self, replies):
        self.replies, self.count = replies, 0
    def ready(self):
        return None
    def ask(self, system, payload, budget):
        budget.reserve()
        answer = self.replies[self.count]
        self.count += 1
        return answer

store = Store(snapshot / "loop-fixture-data")
config = replace(Config(), data_dir=snapshot / "loop-fixture-data")
model = FixtureModel([
    {"action": "create", "reason": "Synthetic probe gap", "manifest": manifest},
    {"cases": cases}, {"code": "def run(data): return []"}, {"code": code},
    {"action": "call", "id": manifest["id"], "input": {"emails": [" A@EXAMPLE.TEST "]}},
    {"action": "finish", "message": "Fixture completed", "result": ["a@example.test"]},
])
engine = Engine(config, model, Sandbox(config.image), store)
first = store.new_run("Fixture: normalize contact emails", {})
engine.execute(first)
first_events = store.events(first["id"])
assert first["status"] == "completed", first
assert [e["kind"] for e in first_events].count("repair") == 1
assert [e["kind"] for e in first_events].index("tests_failed") < [e["kind"] for e in first_events].index("tests_passed") < [e["kind"] for e in first_events].index("installed")
before = digest(store.registry())
second_model = FixtureModel([{"action": "call", "id": manifest["id"], "input": {"emails": ["broken@example.test"]}}])
engine.model = second_model
second = store.new_run("Fixture: exercise unseen execution failure", {})
engine.execute(second)
second_events = store.events(second["id"])
assert second["status"] == "failed", second
assert not any(e["kind"] in ("repair", "candidate", "installed") for e in second_events)
assert before == digest(store.registry())
result = {"source": "handwritten deterministic fault-injection fixtures; NOT a contest demonstration",
          "creation_failure_gets_one_repair": True, "execution_failure_gets_no_repair": True,
          "creation_run": first, "creation_events": first_events,
          "execution_run": second, "execution_events": second_events}
(snapshot / "loop-probes.json").write_text(json.dumps(result, indent=2))
print(json.dumps({"creation_status": first["status"], "creation_model_calls": first["model_calls"],
                  "execution_status": second["status"], "execution_model_calls": second["model_calls"],
                  "execution_error": second.get("error"), "registry_unchanged_on_execution_failure": True}, indent=2))
store.close()
