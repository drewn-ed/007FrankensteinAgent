"""Real-Docker infrastructure checks, not evidence of agent authorship.

The catalog below is deliberately a handwritten TEST FIXTURE. Runtime-generated
contest artifacts are kept separately under docs/ and must carry actual run IDs.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from workbench import catalog
from workbench.config import Config
from workbench.engine import Engine
from workbench.model import Budget, RunError
from workbench.sandbox import Sandbox
from workbench.store import Store, digest


FIXTURE_CATALOG = '''def run(data):
    import re, unicodedata
    def tokens(value):
        text = unicodedata.normalize("NFKD", value.lower())
        text = "".join(c for c in text if not unicodedata.combining(c))
        return set(re.findall(r"[^\\W_]+", text))
    index = []
    for record in data["records"]:
        if not (record["active"] and record["tested"] and record["permissions"] == ["compute"]):
            continue
        text = " ".join([record["id"], record["title"], record["description"]] + record["input_fields"] + record["output_fields"])
        index.append({"id": record["id"], "version": record["version"], "input_fields": record["input_fields"], "terms": sorted(tokens(text))})
    index.sort(key=lambda item: item["id"])
    query = tokens(data["query"])
    required = set(data["required_inputs"])
    matches = [item["id"] for item in index if required.issubset(item["input_fields"]) and (not query or query.intersection(item["terms"]))]
    return {"index": index, "matches": matches}
'''

CATALOG_MANIFEST = {
    "id": "fixture_catalog", "title": "Test fixture catalog", "description": catalog.PROTOCOL["contract"],
    "kind": "discovery", "permissions": ["compute"],
    "input_schema": catalog.INPUT_SCHEMA, "output_schema": catalog.OUTPUT_SCHEMA,
}
DOMAIN_MANIFEST = {
    "id": "contact_roster", "title": "Contact roster", "description": "Normalize contact addresses in source order.",
    "kind": "task", "permissions": ["compute"],
    "input_schema": {"type": "object", "properties": {"emails": {"type": "array", "items": {"type": "string"}}}, "required": ["emails"]},
    "output_schema": {"type": "array", "items": {"type": "string"}},
}
DOMAIN_CODE = 'def run(data):\n    return [value.strip().lower() for value in data["emails"]]\n'
DOMAIN_CASES = [{"name": "Fixture address normalization", "input": {"emails": [" A@EXAMPLE.TEST "]}, "expected": ["a@example.test"]}]
EMPTY_CASE = {"name": "Empty catalog", "input": {"records": [], "query": "", "required_inputs": []}, "expected": {"index": [], "matches": []}}


class CatalogTestAdmission(unittest.TestCase):
    def test_fixed_platform_examples_have_consistent_expectations(self):
        self.assertEqual(catalog.case_errors(catalog.invariant_cases()), [])

    def test_omitted_id_word_and_invented_stem_are_detected(self):
        case = copy.deepcopy(catalog.invariant_cases()[2])
        case["expected"]["index"][0]["terms"] = ["clean", "row"]
        errors = catalog.case_errors([case])
        self.assertEqual(errors[0]["term_differences"], [{"id": "clean_rows", "missing_terms": ["rows"], "extra_terms": ["row"]}])
        self.assertEqual(errors[0]["expected_by_contract"]["matches"], ["clean_rows"])

    def test_query_filter_cannot_resurrect_inactive_or_incompatible_record(self):
        case = copy.deepcopy(catalog.invariant_cases()[1])
        case["expected"]["matches"].append("render_report")
        errors = catalog.case_errors([case])
        self.assertEqual(errors[0]["expected_by_contract"]["matches"], ["clean_rows"])
        self.assertEqual(errors[0]["term_differences"], [])

    def test_exact_accent_normalization_without_translation(self):
        record = {"id": "cafe_roster", "version": 1, "title": "Café", "description": "Données", "input_fields": ["rows"], "output_fields": ["rows"], "active": True, "tested": True, "permissions": ["compute"]}
        case = {"name": "Accented words", "input": {"records": [record], "query": "CAFÉ", "required_inputs": ["rows"]}, "expected": {"index": [{"id": "cafe_roster", "version": 1, "input_fields": ["rows"], "terms": ["cafe", "donnees", "roster", "rows"]}], "matches": ["cafe_roster"]}}
        self.assertEqual(catalog.case_errors([case]), [])
        case["expected"]["index"][0]["terms"][1] = "data"
        self.assertEqual(catalog.case_errors([case])[0]["term_differences"][0]["missing_terms"], ["donnees"])
        self.assertTrue(catalog.case_errors([{}]))


class TrackCatalogIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox = Sandbox()
        if not cls.sandbox.status():
            raise RuntimeError("Real Docker is required; these tests may not silently skip.")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.store = Store(self.path)
        self.engine = Engine(Config(), None, self.sandbox, self.store)
        self.run = self.store.new_run("Handwritten infrastructure test fixtures", {})

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def install(self, manifest, code, cases):
        return self.engine.install(self.run, copy.deepcopy(manifest), code, copy.deepcopy(cases), Budget(), source="test_fixture")

    def test_catalog_test_gate_precedes_registration(self):
        record, report = self.install(CATALOG_MANIFEST, FIXTURE_CATALOG, [EMPTY_CASE])
        self.assertIsNotNone(record)
        self.assertEqual(len(report), 1 + len(catalog.invariant_cases()))
        events = self.store.events(self.run["id"])
        kinds = [event["kind"] for event in events]
        self.assertLess(kinds.index("tests_passed"), kinds.index("installed"))
        before = digest(self.store.registry())
        # This passes the model-style empty case but fails mandatory platform cases.
        bad, failed = self.install(CATALOG_MANIFEST, 'def run(data): return {"index": [], "matches": []}', [EMPTY_CASE])
        self.assertIsNone(bad)
        self.assertTrue(any(not case["passed"] for case in failed))
        self.assertEqual(before, digest(self.store.registry()))

    def test_fresh_process_rebuilds_index_after_version_change_without_model(self):
        self.install(DOMAIN_MANIFEST, DOMAIN_CODE, DOMAIN_CASES)
        self.install(CATALOG_MANIFEST, FIXTURE_CATALOG, [EMPTY_CASE])
        first = self.engine.discover(self.run, "contact", ["emails"], Budget())
        self.assertEqual([item["manifest"]["id"] for item in first["matches"]], ["contact_roster"])
        initial_snapshot = self.store.catalog()
        self.install(DOMAIN_MANIFEST, DOMAIN_CODE, DOMAIN_CASES)
        self.store.close()
        self.store = Store(self.path)
        fresh = Engine(Config(), None, self.sandbox, self.store)
        new_run = self.store.new_run("Fresh infrastructure-only lookup", {})
        registry_before = digest(self.store.registry())
        result = fresh.discover(new_run, "roster", ["emails"], Budget())
        self.assertEqual(result["matches"][0]["version"], 2)
        snapshot = self.store.catalog()
        self.assertNotEqual(snapshot["source_hash"], initial_snapshot["source_hash"])
        self.assertEqual(snapshot["index"][0]["version"], 2)
        self.assertEqual(registry_before, digest(self.store.registry()))
        self.assertEqual(new_run["model_calls"], 0)
        self.assertTrue(all(record["manifest"]["permissions"] == ["compute"] for record in self.store.registry()))
        self.store.deactivate("contact_roster")
        self.assertEqual(fresh.discover(new_run, "contact", [], Budget())["matches"], [])
        self.assertEqual(self.store.catalog()["index"], [])
        self.assertTrue(all(event["kind"] != "installed" for event in self.store.events(new_run["id"])))

    def test_normalized_whole_words_and_required_fields(self):
        record = {"id": "booking_roster", "version": 3, "title": "Réservations", "description": "Keeps groups together", "input_fields": ["rows", "capacities"], "output_fields": ["assignments"], "active": True, "tested": True, "permissions": ["compute"]}
        for query, required, expected in [("RESERVATIONS", ["rows"], ["booking_roster"]), ("book", [], []), ("booking", ["missing"], [])]:
            output = self.sandbox.run(FIXTURE_CATALOG, {"records": [record], "query": query, "required_inputs": required})
            catalog.check_result([record], output, required)
            self.assertEqual(output["matches"], expected)

    def test_catalog_shaped_task_is_classified_and_tested_as_discovery(self):
        proposed = copy.deepcopy(CATALOG_MANIFEST)
        proposed["kind"] = "task"
        # Simulates the agent proposing the right interface without the kind label.
        proposed["input_schema"] = {"type": "object", "properties": {key: {} for key in ("records", "query", "required_inputs")}}
        proposed["output_schema"] = {"type": "object", "properties": {key: {} for key in ("index", "matches")}}

        class FixtureModel:
            def __init__(self, code):
                self.code = code
                self.calls = 0
                self.seen = []
            def ready(self):
                return None
            def ask(self, system, payload, budget):
                budget.reserve()
                self.seen.append(payload)
                self.calls += 1
                if self.calls == 1:
                    return {"action": "create", "reason": "Synthetic catalog-shaped proposal", "manifest": proposed}
                if system.startswith("You design contract tests"):
                    cases = [copy.deepcopy(EMPTY_CASE) for _ in range(3)]
                    if "draft_cases" not in payload:
                        cases[0]["expected"]["matches"] = ["invented_id"]
                    return {"cases": cases}
                if system.startswith("Implement the given capability"):
                    return {"code": self.code}
                return {"action": "finish", "message": "Infrastructure fixture only", "result": {}}

        model = FixtureModel(FIXTURE_CATALOG)
        self.engine.model = model
        self.engine.execute(self.run)
        self.assertEqual(self.run["status"], "completed", self.run.get("error"))
        installed = self.store.get("fixture_catalog")
        self.assertEqual(installed["manifest"]["kind"], "discovery")
        self.assertEqual(installed["manifest"]["input_schema"], catalog.INPUT_SCHEMA)
        self.assertEqual(installed["manifest"]["output_schema"], catalog.OUTPUT_SCHEMA)
        self.assertEqual(len(installed["tests"]), 3 + len(catalog.invariant_cases()))
        self.assertEqual(model.seen[1]["runtime_contract"], catalog.PROTOCOL["contract"])
        review = next(payload for payload in model.seen if "draft_cases" in payload)
        self.assertNotIn("previous_code", review)
        self.assertNotIn("test_failures", review)
        self.assertNotIn("code", review["manifest"])
        self.assertEqual(self.store.catalog()["helper_id"], "fixture_catalog")
        # A new ID and empty-output implementation must still face platform tests.
        proposed["id"] = "invalid_catalog"
        bad_model = FixtureModel('def run(data): return {"index": [], "matches": []}')
        self.engine.model = bad_model
        failed_run = self.store.new_run("Synthetic invalid catalog proposal", {})
        self.engine.execute(failed_run)
        self.assertEqual(failed_run["status"], "failed")
        self.assertIsNone(self.store.get("invalid_catalog"))
        self.assertTrue(any(event["kind"] == "tests_failed" for event in self.store.events(failed_run["id"])))

    def test_inconsistent_review_blocks_builder_before_code_exists(self):
        class InvalidTestAuthor:
            def __init__(self):
                self.builder_called = False
            def ready(self):
                return None
            def ask(self, system, payload, budget):
                budget.reserve()
                if system.startswith("You are a work assistant"):
                    return {"action": "create", "manifest": copy.deepcopy(CATALOG_MANIFEST)}
                if system.startswith("You design contract tests"):
                    cases = [copy.deepcopy(EMPTY_CASE) for _ in range(3)]
                    cases[0]["expected"]["matches"] = ["invented_id"]
                    return {"cases": cases}
                self.builder_called = True
                raise AssertionError("Builder must not see inconsistent test expectations")
        model = InvalidTestAuthor()
        self.engine.model = model
        self.engine.execute(self.run)
        self.assertEqual(self.run["status"], "failed")
        self.assertIn("contradict", self.run["error"])
        self.assertFalse(model.builder_called)
        self.assertEqual(self.store.registry(), [])

    def test_discovery_cannot_change_protocol_or_permissions(self):
        for changes in ({"permissions": ["compute", "network"]}, {"input_schema": {"type": "object"}}):
            with self.assertRaises(RunError):
                self.install({**CATALOG_MANIFEST, **changes}, FIXTURE_CATALOG, [EMPTY_CASE])
        self.assertEqual(self.store.registry(), [])


if __name__ == "__main__":
    unittest.main()
