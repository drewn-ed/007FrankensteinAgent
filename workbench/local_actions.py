"""PATCH actions: trusted, model-free execution of active, tested compute skills.

The UI/form is infrastructure. The executed code retains its recorded authorship.
No provider, planner, browser or host-code execution is reachable from this module.
"""
import copy
import json
import time

from .engine import validate_manifest, validate_data
from .model import RunError
from .store import digest


def strict_inputs(value, schema, path="input"):
    """Do not silently ignore unsupported parameters, even for old open schemas."""
    if isinstance(value, dict) and schema.get("type") == "object" and "properties" in schema:
        properties = schema["properties"]
        unknown = set(value) - set(properties)
        if unknown:
            raise RunError(f"{path}: unsupported fields: {', '.join(sorted(unknown))}. Improve the skill before using new parameters.")
        for key, item in value.items():
            strict_inputs(item, properties.get(key, {}), f"{path}.{key}")
    elif isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(value):
            strict_inputs(item, schema["items"], f"{path}[{i}]")


def checked_record(store, ident, version, code_hash):
    record = store.get(ident)
    if not record:
        raise RunError("This action is inactive or outside the selected project.")
    if record["version"] != version or record["code_hash"] != code_hash:
        raise RunError("This action changed. Reopen it to review the active version.")
    validate_manifest(record["manifest"])
    if record["manifest"].get("kind", "task") != "task":
        raise RunError("Only compute skills can run as local actions. Browser plans still need a connected application.")
    if digest(record["code"]) != record["code_hash"]:
        raise RunError("The saved code does not match its tested fingerprint.")
    if not record.get("cases") or len(record.get("tests", [])) != len(record["cases"]) or not all(t.get("passed") is True for t in record["tests"]):
        raise RunError("This action does not have a complete passing test report.")
    return record


def action_detail(store, ident):
    record = store.get(ident)
    if not record:
        raise RunError("Action not found.")
    checked_record(store, ident, record["version"], record["code_hash"])
    # A prior successful execution is useful input, not a claim about a new result.
    example, source = None, None
    for run in store.runs(limit=None):
        if run.get("project_id") != record.get("provenance", {}).get("project_id") or run.get("status") != "completed":
            continue
        for event in reversed(store.events(run["id"])):
            if event.get("kind") == "used" and event.get("capability") == ident and event.get("version") == record["version"] and "input" in event:
                example, source = event["input"], {"kind": "previous_run", "run_id": run["id"]}
                break
        if source:
            break
    if source is None:
        example, source = record["cases"][0]["input"], {"kind": "test_case", "name": record["cases"][0].get("name", "Example")}
    return {"manifest": record["manifest"], "version": record["version"], "code_hash": record["code_hash"],
            "project_id": record.get("provenance", {}).get("project_id"), "tests_passed": len(record["tests"]),
            "provenance": record.get("provenance", {}), "input": example, "input_source": source}


class LocalActions:
    def __init__(self, store, sandbox, vault):
        self.store, self.sandbox, self.vault = store, sandbox, vault

    def prepare(self, body, *, ai_paused=False):
        project_id = body.get("project_id")
        if project_id and not any(p["id"] == project_id for p in self.store.workspace()["projects"]):
            raise RunError("The selected project no longer exists.")
        scope = self.store.scoped(project_id)
        record = checked_record(scope, body.get("id"), body.get("version"), body.get("code_hash"))
        binding = body.get("app_context")
        if binding is not None and (not isinstance(binding, dict) or set(binding) != {"origin", "revision", "state_hash"} or not isinstance(binding.get("origin"), str) or not isinstance(binding.get("revision"), int) or not isinstance(binding.get("state_hash"), str) or len(binding["state_hash"]) != 64):
            raise RunError("Invalid application snapshot. Load current app data again.")
        inputs = body.get("input")
        validate_data(inputs, record["manifest"]["input_schema"])
        strict_inputs(inputs, record["manifest"]["input_schema"])
        if len(json.dumps(inputs, allow_nan=False).encode()) > 120_000:
            raise RunError("Keep local action inputs under 120 KB.")
        run = self.store.new_run(record["manifest"]["title"], copy.deepcopy(inputs), "local_action")
        run.update(project_id=project_id, mode="local", permissions=["compute"],
                   action={"id": record["manifest"]["id"], "version": record["version"], "code_hash": record["code_hash"]},
                   usage_version=1, model_usage=[], ai_paused=ai_paused, conversation=[], app_context=binding,
                   registry_before=digest(scope.registry()))
        self.store.save_run(run)
        return run

    def execute(self, run):
        started = time.monotonic()
        scope = self.store.scoped(run.get("project_id"))
        try:
            run["status"] = "running"
            self.store.save_run(run)
            ref = run["action"]
            record = checked_record(scope, ref["id"], ref["version"], ref["code_hash"])
            self.store.event(run["id"], "local_action", "Running saved code locally. No model or application connection is used.", ai_paused=run["ai_paused"], permissions=["compute"])
            if run.get("cancel_requested"):
                raise RunError("Stopped before execution.")
            output = self.sandbox.run(record["code"], run["input"], timeout=8)
            if run.get("cancel_requested"):
                raise RunError("Stopped after the sandbox operation. No result was published.")
            validate_data(output, record["manifest"]["output_schema"])
            self.store.event(run["id"], "used", "Executed the saved, tested version without AI.", capability=ref["id"], version=ref["version"], code_hash=ref["code_hash"], input=run["input"], output=output)
            artifact = self.vault.put("action-result.json", json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False).encode(), run_id=run["id"], source="local_action")
            run.update(status="completed", result=output, artifacts=[artifact], verification="output_schema", message="Saved action completed locally. Review the result before using it. No external application was changed.")
            self.store.event(run["id"], "completed", "Output matched the declared schema. This is not an independent check of every business rule.")
        except Exception as error:
            run.update(status="stopped" if run.get("cancel_requested") else "failed", error=str(error)[:1000])
            self.store.event(run["id"], "error", run["error"])
        finally:
            run.update(model_calls=0, tokens=0, model_usage=[], usage_version=1, finished_at=time.time(), duration_seconds=round(time.monotonic()-started, 3), duration_ms=round((time.monotonic()-started)*1000), registry_after=digest(scope.registry()))
            self.store.save_run(run)
        return run
