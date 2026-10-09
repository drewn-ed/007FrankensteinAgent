"""Infrastructure verification; these fixtures are not agent-created capabilities."""
import tempfile
import unittest
from pathlib import Path
from workbench.store import Store
from workbench.model import Budget, RunError
from workbench.browser_control import BrowserControl

M = {"id": "shared_contract", "title": "Fixture", "description": "Synthetic infrastructure fixture", "permissions": ["compute"]}
CASES = [{"name": "fixture", "input": {}, "expected": {}}]
REPORT = [{"name": "fixture", "passed": True, "actual": {}, "expected": {}}]


class WorkspaceBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name))

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_project_scope_cannot_read_or_replace_another_project_skill(self):
        a, b = self.store.scoped("project-a"), self.store.scoped("project-b")
        self.store.accept(M, "fixture", CASES, REPORT, {})
        local = {**M, "id": "p_a_contract"}
        a.accept(local, "fixture", CASES, REPORT, {})
        self.assertIsNone(b.get(local["id"]))
        self.assertIsNotNone(b.get(M["id"]))
        self.assertEqual(len(b.versions()), 1)
        with self.assertRaises(ValueError):
            b.accept(local, "replacement", CASES, REPORT, {})
        a.save_catalog({"project": "a"})
        self.assertIsNone(b.catalog())

    def test_rollback_selects_an_existing_tested_version(self):
        one = self.store.accept(M, "v1", CASES, REPORT, {})
        self.store.accept(M, "v2", CASES, REPORT, {})
        self.store.deactivate(M["id"])
        self.assertIsNone(self.store.get(M["id"]))
        self.store.activate(M["id"], one["version"])
        self.assertEqual(self.store.get(M["id"])["code"], "v1")
        with self.assertRaises(ValueError):
            self.store.activate(M["id"], 999)

    def test_workspace_persists_and_rejects_invalid_records(self):
        payload = {"projects": [{"id": "a", "name": "A", "instructions": "Keep context local"}], "chats": [], "workflows": []}
        self.store.save_workspace(payload)
        fresh = Store(Path(self.temp.name))
        try:
            self.assertEqual(fresh.workspace(), payload)
        finally:
            fresh.close()
        with self.assertRaises(ValueError):
            self.store.save_workspace({"projects": [None], "chats": [], "workflows": []})

    def test_cancel_prevents_another_model_reservation(self):
        budget = Budget(cancelled=lambda: True)
        with self.assertRaisesRegex(RunError, "Stopped"):
            budget.reserve()
        self.assertEqual(budget.calls, 0)

    def test_application_memory_never_stores_field_values_or_ephemeral_refs(self):
        self.store.remember_app({"connected": True, "origin": "https://example.test", "title": "Example", "elements": [{"name": "Name", "tag": "input", "ref": "e1", "value": "private"}], "screenshot": "private"})
        memory = self.store.applications()[0]
        self.assertEqual(memory["elements"], [{"name": "Name", "tag": "input"}])
        self.assertNotIn("screenshot", memory)


class BrowserBoundaries(unittest.TestCase):
    def test_real_form_refs_and_origin_boundary(self):
        browser = BrowserControl()
        try:
            current = browser.connect("https://workspace.demo", headless=True)
            self.assertEqual(current["title"], "Event desk · Practice app")
            first_ref = current["elements"][0]["ref"]
            def act(action, name, value=None):
                ref = next(el["ref"] for el in browser.cached["elements"] if el["name"] == name)
                return browser.act({"action": action, "ref": ref, "value": value}, Budget(), lambda *a, **k: None)
            act("fill", "Name", "Connector fixture")
            with self.assertRaisesRegex(RunError, "stale"):
                browser.act({"action": "fill", "ref": first_ref, "value": "wrong"}, Budget(), lambda *a, **k: None)
            act("fill", "Email", "connector@example.test")
            act("select", "Workshop", "agents")
            act("check", "Checked in", True)
            current = act("click", "Add participant")
            self.assertIn("connector@example.test", current["text"])
            self.assertIn("Connector fixture", current["text"])
            self.assertIn("Checked in", current["text"])
            plan = {"origin": "https://workspace.demo", "steps": [
                {"action": "fill", "target": {"name": "Name", "tag": "input"}, "value": "Plan fixture"},
                {"action": "fill", "target": {"name": "Email", "tag": "input"}, "value": "plan@example.test"},
                {"action": "click", "target": {"name": "Add participant", "tag": "button"}}
            ], "expected_text": ["Plan fixture", "plan@example.test"]}
            verified = browser.run_plan(plan, Budget(), lambda *a, **k: None)
            self.assertTrue(verified["observed"])
            self.assertEqual(verified["steps"], 3)
            with self.assertRaisesRegex(RunError, "outside"):
                browser.act({"action": "navigate", "value": "https://example.com"}, Budget(), lambda *a, **k: None)
            with self.assertRaisesRegex(RunError, "Unsupported"):
                browser.act({"action": "evaluate", "value": "arbitrary code"}, Budget(), lambda *a, **k: None)
        finally:
            browser.close()

class BrowserPlanContract(unittest.TestCase):
    def test_made_up_selectors_and_option_labels_cannot_pass_mapping_checks(self):
        from workbench.browser_control import check_plan_controls
        page = {"origin": "https://workspace.demo", "elements": [{"name": "Workshop", "tag": "select", "options": [{"label": "Building agents", "value": "agents"}]}]}
        plan = {"origin": page["origin"], "steps": [{"action": "select", "target": {"name": "Workshop", "tag": "select"}, "value": "agents"}], "expected_text": ["Alex"]}
        check_plan_controls(plan, page)
        for step in [
            {"action": "fill", "selector": "#imaginary", "value": "Alex"},
            {"action": "select", "target": {"name": "Workshop", "tag": "select"}, "value": "Building agents"},
            {"action": "click", "target": {"name": "Nonexistent control", "tag": "button"}},
        ]:
            with self.assertRaises(RunError):
                check_plan_controls({**plan, "steps": [step]}, page)

    def test_plan_cannot_gain_a_site_or_code_execution_permission(self):
        from workbench.browser_control import validate_plan
        valid = {"origin": "https://workspace.demo", "steps": [{"action": "fill", "target": {"name": "Name", "tag": "input"}, "value": "Alex"}], "expected_text": ["Alex"]}
        validate_plan(valid, "https://workspace.demo")
        for bad in [
            {**valid, "origin": "https://other.test"},
            {**valid, "steps": [{"action": "evaluate", "value": "code"}]},
            {**valid, "steps": [{"action": "navigate", "value": "file:///etc/passwd"}]},
            {**valid, "steps": valid["steps"] * 21},
            {**valid, "expected_text": [""]},
        ]:
            with self.assertRaises(RunError):
                validate_plan(bad, "https://workspace.demo")

    def test_external_action_waits_and_cancellation_clears_pending_review(self):
        import threading
        import time
        from unittest.mock import patch
        browser = BrowserControl()
        browser.cached = {"connected": True, "origin": "https://external.test"}
        cancelled = threading.Event()
        errors = []
        def work():
            try:
                browser.act({"action": "click", "ref": "e1"}, Budget(cancelled=cancelled.is_set), lambda *a, **k: None)
            except RunError as error:
                errors.append(str(error))
        with patch.object(browser, "request") as request:
            thread = threading.Thread(target=work)
            thread.start()
            deadline = time.monotonic() + 2
            while not browser.pending and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertIsNotNone(browser.pending)
            request.assert_not_called()
            cancelled.set()
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive())
            self.assertIsNone(browser.pending)
            self.assertIn("Stopped", errors[0])
            request.assert_not_called()
        browser.close()
