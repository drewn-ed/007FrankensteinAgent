import json
import mimetypes
import threading
import os
import tempfile
import re
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from .config import Config, ROOT
from .engine import Engine, PERMISSIONS
from .providers import create_model
from .chatgpt_auth import ChatGPTAuth
from .sandbox import Sandbox
from .store import Store, WorkspaceConflict, digest
from .browser_control import BrowserControl
from .desktop_control import DesktopControl
from .files import FileVault
from .scheduler import Scheduler
from .model import RunError
from . import action_app
from .local_actions import LocalActions, action_detail
from .usage import analytics, summarize, operations, estimate

WEB = ROOT / "web"


class WorkspaceHTTPServer(ThreadingHTTPServer):
    # Modern browsers fetch many ES modules, fonts and icons concurrently.
    request_queue_size = 128



class Application:
    def __init__(self, config):
        self.config = config
        self.chatgpt = ChatGPTAuth(config.chatgpt_auth_dir)
        self.model = create_model(config, self.chatgpt)
        self.sandbox = Sandbox(config.image)
        self.store = Store(config.data_dir)
        self.engine = Engine(config, self.model, self.sandbox, self.store)
        self.vault = FileVault(config.data_dir)
        self.local_actions = LocalActions(self.store, self.sandbox, self.vault)
        self.browser = BrowserControl(self.vault)
        self.desktop = DesktopControl()
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.lock = threading.Lock()
        self.future = None
        self.current_run = None
        self.scheduler = Scheduler(config.data_dir, self.start_scheduled, self.busy)
        for run in self.store.runs():
            if run["status"] in ("running", "queued"):
                run.update(status="interrupted", error="The previous process ended before the run completed.")
                self.store.save_run(run)

    def busy(self):
        return self.future is not None and not self.future.done()

    def start(self, task, inputs, kind, project_id=None, chat_id=None, use_browser=False, use_desktop=False, expected_connection=None):
        with self.lock:
            if self.busy():
                raise ValueError("Another task is running. Wait for it to finish.")
            if self.store.setting("ai_paused", False):
                raise ValueError("Blackout is on. Use a saved action, or resume AI to start a new task.")
            if error := self.model.ready():
                raise ValueError(error)
            projects = self.store.workspace()["projects"]
            project = next((p for p in projects if p["id"] == project_id), None)
            if project_id and not project:
                raise ValueError("Save this project before starting a task.")
            if use_browser and not self.browser.cached.get("connected"):
                raise ValueError("Connect a browser before attaching it to a task.")
            if use_browser and use_desktop: raise ValueError("Attach one application at a time.")
            if use_desktop and not self.desktop.cached.get("connected"): raise ValueError("Connect a desktop application first.")
            inputs, file_paths = self.vault.input_files(inputs)
            connector = self.desktop if use_desktop else self.browser if use_browser else None
            if expected_connection and (not connector or connector.cached.get("origin") != expected_connection): raise ValueError("The scheduled application connection changed.")
            conversation = self.store.chat_context(chat_id, project_id) if kind == "task" else []
            run = self.store.new_run(task, inputs, kind)
            run.update(project_id=project_id, chat_id=chat_id, project_instructions=project.get("instructions", "") if project else "",
                       conversation=conversation, registry_scope={"project_id": project_id, "includes_shared": True},
                       registry_before=digest(self.store.scoped(project_id).registry()),
                       mode="desktop" if use_desktop else "browser" if use_browser else "data",
                       permissions=[*PERMISSIONS, "files:artifacts", *["file:"+ident for ident in file_paths], *([("" if use_desktop else "browser:") + connector.cached["origin"]] if connector else [])])
            self.store.save_run(run)
            self.current_run = run
            engine = Engine(self.config, self.model, self.sandbox, self.store.scoped(project_id), connector, self.vault)
            if connector: connector.attach_files(file_paths, run["id"])
            self.future = self.pool.submit(engine.execute, run)
            return run

    def set_blackout(self, paused):
        if not isinstance(paused, bool):
            raise ValueError("Specify whether AI should be paused.")
        with self.lock:
            if self.busy():
                raise ValueError("Wait for the current task to finish before changing Blackout.")
            self.store.set_setting("ai_paused", paused)
        return {"ai_paused": paused}

    def start_local(self, body):
        with self.lock:
            if self.busy():
                raise ValueError("Another task is running. Wait for it to finish.")
            run = self.local_actions.prepare(body, ai_paused=self.store.setting("ai_paused", False))
            self.current_run = run
            self.future = self.pool.submit(self.local_actions.execute, run)
            return run

    def start_scheduled(self, task, inputs, *, mode="data", connection=None, **kwargs):
        target = self.browser if mode == "browser" else self.desktop if mode == "desktop" else None
        # Application.start rechecks the connection while holding the run lock.
        if target and (not target.cached.get("connected") or target.cached.get("origin") != connection):
            raise RunError("The scheduled application is no longer connected. Reconnect it, then resume the schedule.")
        return self.start(task, inputs, use_browser=mode == "browser", use_desktop=mode == "desktop", expected_connection=connection, **kwargs)

    def stop(self):
        with self.lock:
            if self.busy() and self.current_run:
                self.current_run["cancel_requested"] = True
                self.store.save_run(self.current_run)
                return {"ok": True, "message": "Stopping after the current operation. No further steps will run."}
            return {"ok": True, "message": "No task is running."}

    def activate_chatgpt(self, model):
        with self.lock:
            if not isinstance(model, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,99}", model):
                raise RunError("Invalid model name.")
            if self.busy():
                raise RunError("Wait for the current task to finish before changing models.")
            if model not in {m["slug"] for m in self.chatgpt.models()}:
                raise RunError("Choose a model available to the connected ChatGPT account.")
            config = replace(self.config, provider="chatgpt", model=model)
            candidate = create_model(config, self.chatgpt)
            if error := candidate.ready():
                raise RunError(error)
            # Persist only non-secret selection. Preserve the existing Gemini setup.
            path = ROOT / ".env"
            lines = path.read_text().splitlines() if path.exists() else []
            lines = [line for line in lines if line.split("=", 1)[0].strip() not in ("MODEL_PROVIDER", "CHATGPT_MODEL")]
            lines.extend(["MODEL_PROVIDER=chatgpt", "CHATGPT_MODEL=" + model])
            fd, temp = tempfile.mkstemp(dir=ROOT, prefix=".env.")
            try:
                with os.fdopen(fd, "w") as stream:
                    os.fchmod(stream.fileno(), 0o600)
                    stream.write("\n".join(lines) + "\n")
                os.replace(temp, path)
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)
            self.config, self.model = config, candidate
            self.engine = Engine(config, candidate, self.sandbox, self.store)
            return {"ok": True, "provider": "chatgpt", "model": model}


def handler_for(app, port):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    allowed_origins = {f"http://{host}" for host in allowed_hosts}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Request data and provider credentials never enter an access log.

        def allowed(self):
            return self.headers.get("Host") in allowed_hosts and (
                not self.headers.get("Origin") or self.headers["Origin"] in allowed_origins)

        def reply(self, value, status=200):
            raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if not self.allowed():
                return self.reply({"error": "Origin/Host not allowed"}, 403)
            path = urlsplit(self.path).path
            if path == "/auth/callback":
                try:
                    query = parse_qs(urlsplit(self.path).query, strict_parsing=True)
                    if any(len(v) != 1 for v in query.values()):
                        raise RunError("Invalid sign-in callback.")
                    with app.lock:
                        if app.busy():
                            raise RunError("Wait for the current task to finish, then start ChatGPT sign-in again.")
                        app.chatgpt.finish({key: value[0] for key, value in query.items()})
                    self.send_response(303)
                    self.send_header("Location", "/?chatgpt=connected")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Referrer-Policy", "no-referrer")
                    self.end_headers()
                    return
                except (RunError, ValueError) as error:
                    return self.reply({"error": str(error)}, 400)
            if path in ("/api/chatgpt/status", "/api/chatgpt/models"):
                try:
                    return self.reply(app.chatgpt.status() if path.endswith("status") else {"models": app.chatgpt.models()})
                except RunError as error:
                    return self.reply({"error": str(error)}, 400)
            if path == "/api/state":
                return self.reply({"model": app.config.model, "model_ready": app.model.ready() is None,
                                   "model_status": app.model.ready(), "free_tier_confirmed": app.config.provider == "gemini" and app.config.free_confirmed,
                                   "provider": app.config.provider,
                                   "provider_label": "ChatGPT plan" if app.config.provider == "chatgpt" else "Gemini",
                                   "permissions": PERMISSIONS, "busy": app.busy(), "ai_paused": app.store.setting("ai_paused", False),
                                   "runs": app.store.runs(), "registry": app.store.registry(), "versions": app.store.versions(),
                                   "applications": app.store.applications(),
                                   "limits": {"calls": app.config.max_calls, "seconds": app.config.max_seconds}})
            if path.startswith("/api/actions/"):
                try:
                    if path.endswith("/context"):
                        with app.lock:
                            if app.busy(): raise RunError("Wait for the current task to finish.")
                            return self.reply(action_app.context(app.store, app.browser, path.split("/")[-2]))
                    return self.reply(action_detail(app.store, path.rsplit("/", 1)[-1]))
                except RunError as error:
                    return self.reply({"error": str(error)}, 400)
            if path == "/api/health":
                return self.reply({"sandbox": app.sandbox.status(), "model_ready": app.model.ready() is None})
            if path == "/api/workspace":
                return self.reply(app.store.workspace())
            if path == "/api/analytics":
                return self.reply(analytics(app.store))
            if path.startswith("/api/usage/"):
                record = app.store.run(path.rsplit("/", 1)[-1])
                if not record:
                    return self.reply({"error": "Run not found"}, 404)
                return self.reply({"run_id": record["id"], "task": record["task"], "status": record["status"],
                                   "cost": summarize(record), "calls": [{**call, "cost": estimate(call)} for call in record.get("model_usage", [])],
                                   "operations": operations(app.store.events(record["id"]), app.store.versions(), record["id"])})
            if path == "/api/desktop/state":
                return self.reply(app.desktop.public_state())
            if path == "/api/desktop/status":
                return self.reply(app.desktop.status())
            if path == "/api/schedules":
                return self.reply({"schedules": app.scheduler.rows(), "running": bool(app.scheduler.thread and app.scheduler.thread.is_alive()), "requires": "Local server awake and running"})
            if path.startswith("/api/files/"):
                try:
                    meta, file = app.vault.get(path.rsplit("/", 1)[-1]); raw = file.read_bytes()
                    from urllib.parse import quote
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(meta["name"]))
                    self.send_header("X-Content-Type-Options", "nosniff")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw); return
                except RunError as error: return self.reply({"error": str(error)}, 404)
            if path == "/api/showcase/source":
                return self.reply(json.loads((ROOT / "examples/event-showcase.json").read_text()))
            if path == "/api/browser/state":
                return self.reply(app.browser.public_state())
            if path.startswith("/api/runs/"):
                record = app.store.run(path.rsplit("/", 1)[-1])
                return self.reply(record or {"error": "Run not found"}, 200 if record else 404)
            if path.startswith("/api/events/"):
                return self.reply(app.store.events(path.rsplit("/", 1)[-1]))
            asset_root = ROOT / "design" if path.startswith("/design/") else WEB
            relative_path = path[len("/design/"):] if path.startswith("/design/") else ("index.html" if path == "/" else path.lstrip("/"))
            file = (asset_root / relative_path).resolve()
            if not file.is_relative_to(asset_root.resolve()) or not file.is_file():
                return self.reply({"error": "Not found"}, 404)
            raw = file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(file)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; font-src 'self'; img-src 'self' data:; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            if not self.allowed():
                return self.reply({"error": "Origin/Host not allowed"}, 403)
            try:
                size = int(self.headers.get("Content-Length", 0))
                limit = 14_100_000 if self.path == "/api/files/upload" else 3_100_000 if self.path == "/api/workspace" else 180_000
                if not 0 < size <= limit or self.headers.get("Content-Type") != "application/json":
                    raise ValueError("Expected JSON within the request size limit.")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Expected object")
                if self.path == "/api/blackout":
                    return self.reply(app.set_blackout(body.get("paused")))
                if self.path == "/api/actions/apply":
                    with app.lock:
                        if app.busy(): raise RunError("Wait for the current task to finish.")
                        run = app.store.run(body.get("run_id"))
                        if not run: raise RunError("Preview not found.")
                        return self.reply(action_app.apply(app.store, app.browser, app.vault, run))
                if self.path == "/api/actions/run":
                    return self.reply(app.start_local(body), 202)
                if self.path == "/api/files/upload":
                    return self.reply(app.vault.upload(body), 201)
                if self.path == "/api/schedules/create":
                    inputs, _ = app.vault.input_files(body.get("input", {})); body["input"] = inputs
                    row = app.scheduler.create(body); app.scheduler.start_loop(); return self.reply(row, 201)
                if self.path == "/api/schedules/update":
                    return self.reply(app.scheduler.update(body.get("id"), body.get("enabled") is True))
                if self.path == "/api/desktop/reveal":
                    return self.reply(app.desktop.reveal())
                if self.path == "/api/run/review":
                    with app.lock:
                        if app.busy(): raise ValueError("Wait for the active task to finish.")
                        run = app.store.run(body.get("id"))
                        if not run or run.get("status") != "needs_review": raise ValueError("Only a task awaiting review can be confirmed.")
                        import time
                        run.update(status="completed", verification="operator_confirmation", operator_reviewed_at=time.time(), agent_message=run.get("message"), message="You confirmed the result in the connected application.")
                        app.store.save_run(run)
                        app.store.event(run["id"], "operator_review", "The operator confirmed the result. This is not an independent automated outcome check.")
                    return self.reply(run)
                if self.path == "/api/desktop/approve":
                    app.desktop.approve(body.get("approved") is True); return self.reply({"ok": True})
                if self.path in ("/api/desktop/connect", "/api/desktop/disconnect", "/api/desktop/refresh"):
                    with app.lock:
                        if app.busy(): raise ValueError("Stop the active task before changing the desktop connection.")
                        if self.path.endswith("/connect"): result = app.desktop.connect(body.get("bundle_id"))
                        elif self.path.endswith("/disconnect"): result = app.desktop.request("disconnect")
                        else: result = app.desktop.request("act", {"action":"inspect"})
                    return self.reply(result)
                if self.path == "/api/chatgpt/login":
                    if app.busy():
                        raise RunError("Wait for the current task to finish before signing in.")
                    return self.reply({"url": app.chatgpt.begin(f"http://127.0.0.1:{port}/auth/callback", body.get("profile_id"))})
                if self.path == "/api/chatgpt/activate":
                    return self.reply(app.activate_chatgpt(body.get("model")))
                if self.path == "/api/workspace":
                    return self.reply(app.store.merge_workspace(body.get("base"), body.get("value")))
                if self.path == "/api/stop":
                    return self.reply(app.stop())
                if self.path == "/api/browser/approve":
                    app.browser.approve(body.get("approved") is True)
                    return self.reply({"ok": True})
                if self.path in ("/api/browser/connect", "/api/browser/disconnect", "/api/browser/refresh"):
                    with app.lock:
                        if app.busy():
                            raise ValueError("Stop the active task before changing the browser connection.")
                        if self.path.endswith("/connect"):
                            state = app.browser.connect(body.get("url", ""))
                            app.store.remember_app(state)
                        elif self.path.endswith("/disconnect"):
                            state = app.browser.request("disconnect")
                        else:
                            state = app.browser.request("act", {"action": "inspect"})
                            app.store.remember_app(state)
                    return self.reply(state)
                if self.path in ("/api/run", "/api/correct"):
                    task = body.get("task", "")
                    if not isinstance(task, str) or not 1 <= len(task.strip()) <= 4000:
                        raise ValueError("Enter a task between 1 and 4,000 characters long.")
                    kind = "task" if self.path == "/api/run" else "correction"
                    return self.reply(app.start(task.strip(), body.get("input"), kind,
                                                body.get("project_id"), body.get("chat_id"), body.get("use_browser") is True, body.get("use_desktop") is True), 202)
                if self.path in ("/api/deactivate", "/api/activate"):
                    with app.lock:
                        if app.busy():
                            raise ValueError("Wait for the current task to finish.")
                        if self.path == "/api/deactivate":
                            app.store.deactivate(body["id"])
                        else:
                            app.store.activate(body["id"], int(body["version"]))
                    return self.reply({"ok": True})
                return self.reply({"error": "Not found"}, 404)
            except WorkspaceConflict as error:
                return self.reply({"error": str(error), "conflict": True}, 409)
            except (ValueError, TypeError, KeyError, RunError) as error:
                return self.reply({"error": str(error)}, 400)

    return Handler


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    app = Application(Config.from_env())
    app.scheduler.start_loop()
    server = WorkspaceHTTPServer(("127.0.0.1", args.port), handler_for(app, args.port))
    print(f"Wisp running at http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app.scheduler.close()
        app.pool.shutdown(wait=True)
        app.browser.close()
        app.desktop.close()
        app.store.close()


if __name__ == "__main__":
    main()
