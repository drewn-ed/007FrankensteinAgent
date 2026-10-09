"""Synthetic accounting fixtures. They never enter product task history."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from workbench.config import Config
from workbench.engine import Engine
from workbench.model import Budget, Gemini, RunError
from workbench.store import Store
from workbench.usage import analytics, estimate, operations, price_snapshot, read_usage, summarize


META = {"promptTokenCount": 1000, "cachedContentTokenCount": 200,
        "candidatesTokenCount": 100, "thoughtsTokenCount": 50, "totalTokenCount": 1150}


def response(text='{"answer": "ok"}', reason="STOP", usage=META):
    return io.BytesIO(json.dumps({"usageMetadata": usage, "modelVersion": "gemini-3.5-flash-lite",
        "candidates": [{"finishReason": reason, "content": {"parts": [{"text": text}]}}]}).encode())


class UsageTests(unittest.TestCase):
    def setUp(self):
        self.model = Gemini(Config(key="synthetic-key", free_confirmed=True))

    def test_cached_tokens_and_thinking_are_priced_once(self):
        record = {"usage": read_usage(META), "pricing": price_snapshot("gemini-3.5-flash-lite", True)}
        cost = estimate(record)
        self.assertEqual(cost["usd"], 0)
        self.assertAlmostEqual(cost["paid_equivalent_usd"], (800*.30 + 200*.03 + 150*2.50)/1_000_000)
        record["service_tier"] = "standard"  # Actual provider response uses lowercase.
        self.assertEqual(estimate(record), cost)
        record["service_tier"] = "priority"
        self.assertIsNone(estimate(record)["paid_equivalent_usd"])
        record["pricing"]["tier"] = "unknown"
        self.assertIsNone(estimate(record)["usd"])

    def test_missing_or_inconsistent_usage_is_not_zero_cost(self):
        for metadata in (None, {}, {**META, "totalTokenCount": 3}, {**META, "cachedContentTokenCount": 9000}):
            self.assertIsNone(estimate({"usage": read_usage(metadata), "pricing": price_snapshot("gemini-3.5-flash-lite", True)})["usd"])

    def test_request_records_pending_and_consumed_tokens_even_on_invalid_json(self):
        snapshots=[]
        budget=Budget(on_usage=lambda b:snapshots.append(json.loads(json.dumps(b.usage))))
        budget.purpose="Writing a skill"
        with patch("urllib.request.urlopen", return_value=response(text="invalid json")):
            with self.assertRaises(RunError):
                self.model.ask("system", {"private": "do not log payload"}, budget)
        self.assertEqual(snapshots[0][0]["status"], "pending")
        self.assertEqual(budget.usage[0]["status"], "failed")
        self.assertEqual(budget.usage[0]["purpose"], "Writing a skill")
        self.assertEqual(budget.tokens, 1150)
        self.assertEqual(estimate(budget.usage[0])["usd"], 0)
        self.assertNotIn("do not log payload", json.dumps(budget.usage))
        self.assertNotIn("synthetic-key", json.dumps(budget.usage))

    def test_http_failure_counts_attempt_without_fabricating_usage(self):
        budget=Budget()
        with patch("urllib.request.urlopen", side_effect=HTTPError("url",429,"quota",{},None)):
            with self.assertRaisesRegex(RunError,"quota"):
                self.model.ask("system", {}, budget)
        cost=summarize({"usage_version":1,"model_calls":budget.calls,"model_usage":budget.usage})
        self.assertEqual(cost["unknown_cost_calls"],1)
        self.assertIsNone(cost["estimated_usd"])
        self.assertFalse(cost["cost_complete"])

    def test_pending_attempt_and_legacy_task_remain_unpriced(self):
        self.assertFalse(summarize({"model_calls":4,"tokens":1500})["cost_complete"])
        self.assertIsNone(summarize({"model_calls":4,"tokens":1500})["estimated_usd"])
        self.assertEqual(summarize({"usage_version":1,"model_calls":0})["estimated_usd"],0)
        self.assertFalse(summarize({"usage_version":1,"model_calls":1,"model_usage":[{"status":"pending"}]})["cost_complete"])

    def test_reuse_requires_earlier_version_provenance(self):
        versions=[{"manifest":{"id":"a"},"version":1,"provenance":{"run_id":"old"}},
                  {"manifest":{"id":"b"},"version":1,"provenance":{"run_id":"current"}}]
        logs=[{"kind":"used","capability":key,"version":1} for key in ("a","b","unknown")]
        logs += [{"kind":"tests_failed","tests":[{"passed":False},{"passed":True}]}]
        result=operations(logs,versions,"current")
        self.assertEqual(result["skill_calls"],3)
        self.assertEqual(result["reused_skill_calls"],1)
        self.assertEqual(result["test_cases"],2)
        self.assertEqual(result["test_cases_passed"],1)

    def test_analytics_covers_more_than_recent_thirty_and_keeps_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp))
            try:
                for i in range(35):
                    run=store.new_run("Synthetic accounting case",{})
                    run.update(status="completed" if i<20 else "failed", model_calls=2,tokens=100)
                    store.save_run(run)
                result=analytics(store)
                self.assertEqual(len(store.runs()),30)
                self.assertEqual(len(result["runs"]),35)
                self.assertEqual(result["summary"]["completed"],20)
                self.assertEqual(result["summary"]["failed"],15)
                self.assertEqual(result["summary"]["model_calls"],70)
                self.assertIsNone(result["summary"]["estimated_usd"])
                self.assertEqual(result["summary"]["cost_complete_tasks"],0)
            finally:
                store.close()

    def test_engine_persists_actual_call_metadata_across_store_reopen(self):
        class ReadySandbox:
            def status(self): return True
        with tempfile.TemporaryDirectory() as temp:
            store=Store(Path(temp))
            run=store.new_run("Synthetic task",{})
            engine=Engine(self.model.config,self.model,ReadySandbox(),store)
            with patch("urllib.request.urlopen",return_value=response(text='{"action":"finish","result":"done"}')):
                engine.execute(run)
            store.close()
            store=Store(Path(temp))
            try:
                saved=store.run(run["id"])
                self.assertEqual(saved["status"],"completed")
                self.assertEqual(saved["model_calls"],1)
                self.assertEqual(saved["tokens"],1150)
                self.assertEqual(saved["model_usage"][0]["purpose"],"Planning")
                self.assertTrue(saved["cost"]["cost_complete"])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
