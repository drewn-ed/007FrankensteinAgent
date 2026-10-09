"""Fixed host connector. Generated skills cannot execute code in this process."""
import json
import re
from collections import Counter
import os
from pathlib import Path
import selectors
import subprocess
import threading
import time
from urllib.parse import urlsplit
from .config import ROOT
from .model import RunError


class BrowserControl:
    kind = "browser"

    def __init__(self, vault=None):
        self.vault = vault
        self.allowed_files = {}
        self.run_id = None
        self.lock = threading.RLock()
        self.proc = None
        self.sequence = 0
        self.cached = {"connected": False}
        self.buffer = bytearray()
        self.pending = None
        self.decision = threading.Event()
        self.closed = False

    def command(self):
        return ["node", str(ROOT / "workbench/browser/driver.cjs")]

    def attach_files(self, paths, run_id):
        self.allowed_files = dict(paths)
        self.run_id = run_id

    def request(self, method, params=None):
        with self.lock:
            if self.closed:
                raise RunError("Browser connector is closed.")
            if not self.proc or self.proc.poll() is not None:
                env = {key: value for key, value in os.environ.items() if key in ("PATH", "HOME", "TMPDIR", "LANG")}
                try:
                    self.proc = subprocess.Popen(self.command(), cwd=ROOT,
                                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
                    self.buffer.clear()
                except OSError:
                    raise RunError("Node.js is not available for the browser connector.") from None
            self.sequence += 1
            packet = {"id": self.sequence, "method": method, "params": params or {}}
            try:
                self.proc.stdin.write((json.dumps(packet) + "\n").encode())
                self.proc.stdin.flush()
                with selectors.DefaultSelector() as sel:
                    sel.register(self.proc.stdout, selectors.EVENT_READ)
                    deadline = time.monotonic() + 35
                    while time.monotonic() < deadline:
                        if b"\n" in self.buffer:
                            line, _, rest = self.buffer.partition(b"\n")
                            self.buffer = bytearray(rest)
                            result = json.loads(line)
                            if result.get("id") != self.sequence:
                                continue
                            if "error" in result:
                                raise RunError(result["error"])
                            self.cached = result["result"]
                            downloads = self.cached.pop("download_files", [])
                            if downloads and self.vault:
                                artifacts = []
                                download_root = (ROOT / ".runtime/browser-downloads").resolve()
                                for item in downloads:
                                    file = Path(item["path"]).resolve()
                                    if file.parent != download_root or not file.is_file() or file.is_symlink():
                                        raise RunError("Invalid download location.")
                                    if file.stat().st_size > 10 * 1024 * 1024:
                                        file.unlink(); raise RunError("Downloaded file exceeded 10 MB.")
                                    try: artifacts.append(self.vault.put(item["name"], file.read_bytes(), run_id=self.run_id, source="browser_download"))
                                    finally: file.unlink(missing_ok=True)
                                self.cached["downloads"] = artifacts
                            return self.cached
                        if sel.select(0.1):
                            chunk = os.read(self.proc.stdout.fileno(), 65536)
                            if not chunk:
                                raise RunError("Browser connector stopped. Run npm install and ensure Google Chrome is installed.")
                            self.buffer.extend(chunk)
                            if len(self.buffer) > 5_000_000:
                                raise RunError("Browser snapshot exceeded its size limit.")
                self.proc.kill()
                self.cached = {"connected": False}
                raise RunError("Browser operation timed out. Reconnect before trying again.")
            except (BrokenPipeError, OSError):
                raise RunError("Browser connector is unavailable. Run npm install and check Google Chrome.") from None

    def connect(self, url, headless=False):
        parsed = urlsplit(url)
        if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Enter an HTTP or HTTPS site URL without credentials.")
        self.cached = {"connected": False}
        return self.request("connect", {"url": url, "headless": headless})

    def public_state(self):
        return {**self.cached, "pending": self.pending}

    def observation(self):
        return {key: value for key, value in self.cached.items() if key not in ("screenshot",)}

    def act(self, action, budget, event):
        operation = {key: action[key] for key in ("action", "ref", "value") if key in action}
        if operation.get("action") not in ("inspect", "navigate", "click", "fill", "select", "check", "press", "upload"):
            raise RunError("Unsupported browser operation.")
        if operation.get("action") == "upload":
            ident = operation.get("value")
            if ident not in self.allowed_files:
                raise RunError("Upload is limited to files attached to this task or created during this run.")
        budget.check()
        # External interactions wait for explicit operator review. The local practice app is unrestricted.
        # A navigation can hit a state-changing GET endpoint; review it too.
        if operation["action"] != "inspect" and self.cached.get("origin") not in ("https://workspace.demo", "https://event.workspace.demo"):
            self.decision.clear()
            self.pending = {"operation": operation, "reason": action.get("reason", "Review this browser step."), "approved": None}
            event("approval", "A browser action is waiting for your review.", operation=operation)
            try:
                while not self.decision.wait(0.2):
                    budget.check()
                budget.check()
                if not self.pending["approved"]:
                    raise RunError("You declined the browser action.")
            finally:
                self.pending = None
        trusted_operation = dict(operation)
        if operation.get("action") == "upload":
            trusted_operation["file_path"] = self.allowed_files[operation["value"]]
            if self.vault:
                meta, _ = self.vault.get(operation["value"])
                trusted_operation.update(file_name=meta["name"], file_mime=meta["mime"])
        self.request("act", trusted_operation)
        for artifact in self.cached.get("downloads", []):
            event("artifact", "Downloaded: " + artifact["name"], artifact=artifact)
        return self.observation()

    def approve(self, approved):
        if self.pending is None:
            raise ValueError("No browser action is awaiting review.")
        self.pending["approved"] = bool(approved)
        self.decision.set()

    def run_plan(self, plan, budget, event):
        """Execute declarative output of a sandboxed, tested capability; never code."""
        validate_plan(plan, self.cached.get("origin"))
        self.request("act", {"action": "inspect"})
        for index, step in enumerate(plan["steps"]):
            budget.check()
            if step["action"] == "navigate":
                operation = {"action": "navigate", "value": step["value"]}
            else:
                target = step["target"]
                matches = [el for el in self.cached.get("elements", []) if el["name"] == target["name"]
                           and (not target.get("tag") or el["tag"] == target["tag"])]
                if len(matches) != 1:
                    raise RunError("The saved step no longer matches exactly one control. Inspect the page before continuing.")
                operation = {"action": step["action"], "ref": matches[0]["ref"], "value": step.get("value")}
            operation["reason"] = f"Saved step {index + 1}/{len(plan['steps'])}: {step['action']}"
            event("browser_step", operation["reason"], operation=operation)
            self.act(operation, budget, event)
        text = self.cached.get("text", "")
        if not text_matches(plan["expected_text"], text):
            raise RunError("The browser steps ran, but the expected text is not visible. Completion was not verified.")
        event("browser_verified", "The expected result is visible after the saved steps.", expected_text=plan["expected_text"])
        return {"url": self.cached["url"], "steps": len(plan["steps"]), "expected_text": plan["expected_text"], "observed": True}

    def verify_registrations(self, expected, before, budget, event):
        budget.check()
        self.request("act", {"action": "inspect"})
        after = self.cached.get("registration_state", {})
        fields = ("name", "email", "workshop", "checked")
        def records(rows):
            return Counter(tuple(r.get(k) for k in fields) for r in rows)
        old = before.get("records", [])
        if before.get("count") != len(old) or after.get("count") != len(old) + len(expected):
            raise RunError("The exact participant count does not match the requested additions.")
        if records(after.get("records", [])) != records(old) + records(expected):
            raise RunError("The observed participants do not match the requested names, emails, workshops and check-in states.")
        event("outcome_verified", "Verified the exact participant count and every requested field against the page.",
              expected_count=len(old)+len(expected), expected_records=expected, observed=after)
        return after

    def close(self):
        with self.lock:
            self.closed = True
            if self.proc and self.proc.poll() is None:
                self.proc.stdin.close()
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=3)
            if self.proc:
                for pipe in (self.proc.stdin, self.proc.stdout):
                    if pipe and not pipe.closed:
                        pipe.close()


def validate_plan(plan, origin):
    if not isinstance(plan, dict) or plan.get("origin") != origin:
        raise RunError("A saved browser plan must target the connected site.")
    steps = plan.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= 20:
        raise RunError("A saved browser plan must contain between 1 and 20 steps.")
    expected = plan.get("expected_text")
    if not isinstance(expected, list) or not 1 <= len(expected) <= 10 or any(not isinstance(t, str) or not 1 <= len(t) <= 300 for t in expected):
        raise RunError("A saved browser plan needs concrete text to verify on the resulting page.")
    for step in steps:
        if not isinstance(step, dict) or step.get("action") not in ("click", "fill", "select", "check", "press", "navigate", "upload"):
            raise RunError("Unsupported action in the saved browser plan.")
        if step["action"] in ("fill", "select", "press", "navigate", "upload") and not isinstance(step.get("value"), str):
            raise RunError("This browser operation requires a text value.")
        if step["action"] == "check" and not isinstance(step.get("value"), bool):
            raise RunError("A checkbox operation requires a boolean value.")
        if step["action"] == "press" and step["value"] not in ("Enter", "Tab", "Escape", "ArrowDown", "ArrowUp", "Space"):
            raise RunError("This key is not permitted in a browser plan.")
        if step["action"] == "navigate":
            parsed = urlsplit(step.get("value", ""))
            if parsed.username or parsed.password or f"{parsed.scheme}://{parsed.netloc}" != origin:
                raise RunError("A saved plan cannot navigate outside the connected site.")
        else:
            target = step.get("target")
            if not isinstance(target, dict) or not isinstance(target.get("name"), str) or not target["name"] or len(target["name"]) > 200:
                raise RunError("Every saved step needs an observed control name.")


def text_matches(expected, observed):
    """Whole text tokens only: '1 registered' must not match '11 registered'."""
    text = " ".join(observed.split())
    return all(re.search(r"(?<![\w@.])" + re.escape(" ".join(value.split())) + r"(?![\w@.])", text) for value in expected)


def equivalent_plans(actual, expected, snapshot):
    """Compare committed form state, allowing reordered setters and extra checks."""
    check_plan_controls(actual, snapshot)
    check_plan_controls(expected, snapshot)
    def canonical(plan):
        state, result = {}, []
        for step in plan["steps"]:
            action = step["action"]
            target = step.get("target", {})
            if action in ("fill", "select", "check"):
                state[(target.get("tag"), target.get("name"))] = (action, step["value"])
            else:
                result.append((sorted(state.items()), step))
                state = {}
        result.append(sorted(state.items()))
        return result
    # A candidate must retain every independent expected assertion. Additional
    # assertions cannot hide a wrong action or remove an existing check.
    required = {" ".join(x.split()) for x in expected["expected_text"]}
    present = {" ".join(x.split()) for x in actual["expected_text"]}
    return actual["origin"] == expected["origin"] and required <= present and canonical(actual) == canonical(expected)


def plan_schema(origin):
    return {"type": "object", "additionalProperties": False, "required": ["origin", "steps", "expected_text"],
            "properties": {
                "origin": {"const": origin},
                "expected_text": {"type": "array", "minItems": 1, "maxItems": 10, "items": {"type": "string", "minLength": 1, "maxLength": 300}},
                "steps": {"type": "array", "minItems": 1, "maxItems": 20, "items": {
                    "type": "object", "additionalProperties": False, "required": ["action"], "properties": {
                        "action": {"enum": ["click", "fill", "select", "check", "press", "navigate", "upload"]},
                        "target": {"type": "object", "additionalProperties": False, "required": ["name", "tag"],
                                   "properties": {"name": {"type": "string", "minLength": 1}, "tag": {"type": "string"}}},
                        "value": {"type": ["string", "boolean"]}}}}}}


def check_plan_controls(plan, snapshot):
    """Check contract fixtures against observed names/options, without interacting."""
    validate_plan(plan, snapshot.get("origin"))
    for step in plan["steps"]:
        if step["action"] == "navigate":
            continue
        target = step["target"]
        matches = [el for el in snapshot.get("elements", []) if el["name"] == target["name"] and el["tag"] == target.get("tag")]
        if len(matches) != 1:
            raise RunError("Browser plan refers to a control not uniquely present in the observed page.")
        if step["action"] == "select" and step.get("value") not in [o["value"] for o in matches[0].get("options", [])]:
            raise RunError("Browser plan uses a select value not present in the observed page.")
