"""Observed usage and explicit estimates. No provider billing access is implied."""
from collections import Counter

PRICING_SOURCE = "https://ai.google.dev/gemini-api/docs/pricing"
PRICING_CHECKED = "2026-10-09"
# Standard, text requests, USD per million tokens. Not a paid fallback.
RATES = {
    "gemini-3.5-flash-lite": {"input": 0.30, "output": 2.50, "cached_input": 0.03},
    "gemini-3.1-flash-lite": {"input": 0.25, "output": 1.50, "cached_input": 0.025},
}


def price_snapshot(model, free_confirmed):
    return {"tier": "free_confirmed" if free_confirmed else "unknown", "currency": "USD",
            "source": PRICING_SOURCE, "checked_at": PRICING_CHECKED,
            "paid_standard_per_million": RATES.get(model)}


def read_usage(metadata):
    if not isinstance(metadata, dict):
        return None
    def count(key, default=None):
        value = metadata.get(key, default)
        return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None
    return {"input": count("promptTokenCount"), "output": count("candidatesTokenCount", 0),
            "thinking": count("thoughtsTokenCount", 0), "cached_input": count("cachedContentTokenCount", 0),
            "total": count("totalTokenCount"), "tool_input": count("toolUsePromptTokenCount", 0)}


def estimate(record):
    usage, pricing = record.get("usage"), record.get("pricing", {})
    if not usage or any(usage.get(k) is None for k in ("input", "output", "thinking", "cached_input", "total")):
        return {"usd": None, "paid_equivalent_usd": None}
    if usage["cached_input"] > usage["input"] or usage["total"] != usage["input"] + usage["output"] + usage["thinking"]:
        return {"usd": None, "paid_equivalent_usd": None}
    rates = pricing.get("paid_standard_per_million")
    equivalent = None
    # This adapter sends text, no grounding/tools, and requests the standard service.
    service_tier = str(record.get("service_tier") or "STANDARD").upper()
    if rates and not usage.get("tool_input") and service_tier in ("STANDARD", "SERVICE_TIER_UNSPECIFIED"):
        equivalent = round(((usage["input"] - usage["cached_input"]) * rates["input"]
                            + usage["cached_input"] * rates["cached_input"]
                            + (usage["output"] + usage["thinking"]) * rates["output"]) / 1_000_000, 9)
    return {"usd": 0.0 if pricing.get("tier") == "free_confirmed" else None,
            "paid_equivalent_usd": equivalent}


def summarize(run):
    records = run.get("model_usage", [])
    calls = max(run.get("model_calls", 0), len(records))
    estimates = [estimate(r) for r in records]
    known = [e["usd"] for e in estimates if e["usd"] is not None]
    equivalent = [e["paid_equivalent_usd"] for e in estimates if e["paid_equivalent_usd"] is not None]
    tracked = run.get("usage_version") == 1
    return {"tracked": tracked, "calls": calls, "recorded_calls": len(records),
            "known_cost_calls": len(known), "unknown_cost_calls": calls - len(known),
            "estimated_usd": round(sum(known), 9) if known or (tracked and calls == 0) else None,
            "cost_complete": tracked and calls == len(known),
            "paid_equivalent_usd": round(sum(equivalent), 9) if equivalent else None,
            "paid_equivalent_calls": len(equivalent), "billed_usd": None}


def operations(events, versions, run_id):
    counts = Counter(e["kind"] for e in events)
    known = {(r["manifest"]["id"], r["version"]): r for r in versions}
    uses = [e for e in events if e["kind"] in ("used", "discovered")]
    reused = [e for e in uses if (r := known.get((e.get("capability"), e.get("version"))))
              and r.get("provenance", {}).get("run_id") not in (None, run_id)]
    tests = [t for e in events for t in e.get("tests", [])]
    return {"skill_calls": len(uses), "reused_skill_calls": len(reused),
            "browser_attempts": counts["browser_step"],
            "test_cases": len(tests), "test_cases_passed": sum(t.get("passed") is True for t in tests),
            "versions_installed": counts["installed"]}


def analytics(store):
    # History must include more than the 30 most recent chat runs.
    runs, versions = store.runs(limit=None), store.versions()
    rows = []
    for run in runs:
        row = {k: run.get(k) for k in ("id", "task", "status", "created_at", "duration_ms", "tokens", "model_calls", "project_id", "chat_id", "kind", "mode")}
        row.update(cost=summarize(run), operations=operations(store.events(run["id"]), versions, run["id"]))
        rows.append(row)
    counts = Counter(r["status"] for r in rows)
    priced = [r["cost"]["estimated_usd"] for r in rows if r["cost"]["estimated_usd"] is not None]
    return {"runs": rows, "summary": {"tasks": len(rows), "completed": counts["completed"],
            "failed": counts["failed"], "stopped": counts["cancelled"] + counts["interrupted"],
            "active": counts["running"] + counts["queued"],
            "needs_attention": counts["needs_input"] + counts["needs_review"],
            "model_calls": sum(r["model_calls"] or 0 for r in rows),
            "tokens": sum(r["tokens"] or 0 for r in rows),
            "estimated_usd": round(sum(priced), 9) if priced else None,
            "cost_complete_tasks": sum(r["cost"]["cost_complete"] for r in rows),
            "reused_tasks": sum(r["operations"]["reused_skill_calls"] > 0 for r in rows),
            "active_skills": len(store.registry()), "versions": len(versions),
            **{key: sum(r["operations"][key] for r in rows) for key in
               ("skill_calls", "reused_skill_calls", "browser_attempts", "test_cases", "test_cases_passed", "versions_installed")}}}
