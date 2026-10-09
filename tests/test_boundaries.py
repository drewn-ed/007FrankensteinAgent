"""Synthetic infrastructure fixtures, NOT agent-authored skills or a contest demo."""
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from workbench.config import Config
from workbench.engine import Engine, validate_manifest, public_manifest
from workbench.model import Budget, Gemini, RunError
from workbench.sandbox import Sandbox
from workbench.store import Store, digest

MANIFEST = {"id": "registration_contacts", "title": "Kontakty registrací",
            "description": "Return normalized email contacts without changing order. Ignore surrounding spaces.",
            "permissions": ["compute"], "kind": "task",
            "input_schema": {"type": "object", "properties": {"emails": {"type": "array", "items": {"type": "string"}}}, "required": ["emails"]},
            "output_schema": {"type": "array", "items": {"type": "string"}}}
CODE = 'def run(data):\n    return [x.strip() for x in data["emails"]]\n'
CASES = [{"name": "Surrounding spaces", "input": {"emails": [" a@example.test "]}, "expected": ["a@example.test"]},
         {"name": "Empty input", "input": {"emails": []}, "expected": []}]


class Boundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = Sandbox()
        if not cls.sandbox.status():
            raise RuntimeError("These tests require real Docker. They must not silently skip sandbox verification.")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))
        self.config = Config()
        self.engine = Engine(self.config, None, self.sandbox, self.store)
        self.run_record = self.store.new_run("Infrastructure fixture", {})

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_failed_tests_cannot_replace_working_version(self):
        good, _ = self.engine.install(self.run_record, MANIFEST, CODE, CASES, Budget(), source="test_fixture")
        before = digest(self.store.registry())
        bad, report = self.engine.install(self.run_record, MANIFEST, 'def run(data): return []', CASES, Budget(), source="test_fixture")
        self.assertIsNotNone(good)
        self.assertIsNone(bad)
        self.assertTrue(any(not item["passed"] for item in report))
        self.assertEqual(before, digest(self.store.registry()))
        with self.assertRaises(ValueError):
            self.store.accept(MANIFEST, CODE, CASES, [], {})

    def test_permission_escalation_is_rejected(self):
        with self.assertRaises(RunError):
            validate_manifest({**MANIFEST, "permissions": ["compute", "network"]})
        self.assertEqual(self.store.registry(), [])

    def test_container_has_no_key_network_or_writable_root(self):
        code = '''def run(data):
    import os,socket
    result={"credential":os.getenv("GEMINI_API_KEY"),"root_writable":False,"network":False}
    try:
        open("/unauthorized", "w").write("test")
        result["root_writable"]=True
    except OSError:
        pass
    try:
        socket.create_connection(("1.1.1.1",443),timeout=0.5).close()
        result["network"]=True
    except OSError:
        pass
    return result
'''
        with patch.dict("os.environ", {"GEMINI_API_KEY": "synthetic-host-canary"}):
            result = self.sandbox.run(code, {})
        self.assertEqual(result, {"credential": None, "root_writable": False, "network": False})

    def test_timeout_and_output_limit_stop_execution(self):
        with self.assertRaisesRegex(RunError, "časový limit"):
            self.sandbox.run('def run(data):\n    while True: pass', {}, timeout=1)
        with self.assertRaisesRegex(RunError, "limit výstupu"):
            self.sandbox.run('def run(data):\n    print("x" * 70000)\n    return {}', {})

    def test_fresh_store_preserves_capability_and_deactivation(self):
        self.engine.install(self.run_record, MANIFEST, CODE, CASES, Budget(), source="test_fixture")
        before = digest(self.store.registry())
        fresh = Store(Path(self.temp.name))
        try:
            record = fresh.get(MANIFEST["id"])
            self.assertEqual(before, digest(fresh.registry()))
            self.assertEqual(self.sandbox.run(record["code"], {"emails": [" b@example.test "]}), ["b@example.test"])
            fresh.deactivate(MANIFEST["id"])
            self.assertIsNone(fresh.get(MANIFEST["id"]))
        finally:
            fresh.close()

    def test_hard_limits_and_free_tier_gate(self):
        budget = Budget(max_calls=1)
        budget.reserve()
        with self.assertRaises(RunError):
            budget.reserve()
        with self.assertRaises(RunError):
            Budget(max_seconds=1, started=time.monotonic() - 2).check()
        model = Gemini(Config(key="synthetic", free_confirmed=False))
        with patch("urllib.request.urlopen") as request:
            with self.assertRaisesRegex(RunError, "Free"):
                model.ask("x", {}, Budget())
            request.assert_not_called()
        model = Gemini(Config(key="synthetic", free_confirmed=True))
        with patch("urllib.request.urlopen", side_effect=HTTPError("", 429, "quota", {}, None)) as request:
            with self.assertRaisesRegex(RunError, "kvótu"):
                model.ask("x", {}, Budget())
            self.assertEqual(request.call_count, 1)

    def test_external_schema_refs_are_rejected(self):
        with self.assertRaises(RunError):
            validate_manifest({**MANIFEST, "input_schema": {"$ref": "https://example.test/schema"}})

    def test_candidate_code_cannot_leak_into_test_author_contract(self):
        raw = {**MANIFEST, "code": "private candidate", "implementation": "alternative", "extra": 1}
        self.assertEqual(public_manifest(raw), MANIFEST)
        class FixtureModel:
            def __init__(self):
                self.calls = 0
                self.seen = []
            def ready(self):
                return None
            def ask(self, system, payload, budget):
                budget.reserve()
                self.seen.append(payload)
                self.calls += 1
                return [{"action": "create", "manifest": raw},
                        {"cases": CASES + [{"name": "Another address", "input": {"emails": ["b@example.test"]}, "expected": ["b@example.test"]}]},
                        {"code": CODE},
                        {"action": "finish", "message": "fixture", "result": {}}][self.calls-1]
        model = FixtureModel()
        self.engine.model = model
        self.engine.execute(self.run_record)
        self.assertEqual(self.run_record["status"], "completed")
        self.assertNotIn("code", model.seen[1]["manifest"])
        self.assertNotIn("implementation", model.seen[1]["manifest"])
        self.assertNotIn("code", self.store.get(MANIFEST["id"])["manifest"])

    def test_correction_keeps_old_cases_and_installs_only_passing_candidate(self):
        self.engine.install(self.run_record, MANIFEST, CODE, CASES, Budget(), source="test_fixture")
        class FixtureModel:
            def ready(self):
                return None
            def ask(self, *args):
                return {"code": 'def run(data): return [x.strip().lower() for x in data["emails"]]'}
        self.engine.model = FixtureModel()
        run = self.store.new_run("Normalize uppercase emails too", {
            "capability": MANIFEST["id"],
            "case": {"name": "Uppercase address", "input": {"emails": ["A@EXAMPLE.TEST"]}, "expected": ["a@example.test"]}}, "correction")
        self.engine.execute(run)
        self.assertEqual(run["status"], "completed", run.get("error"))
        record = self.store.get(MANIFEST["id"])
        self.assertEqual(record["version"], 2)
        self.assertEqual(record["cases"][:len(CASES)], CASES)
        self.assertEqual(record["manifest"]["permissions"], ["compute"])
        self.assertTrue(all(item["passed"] for item in record["tests"]))


if __name__ == "__main__":
    unittest.main()
