import json
import mimetypes
import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .config import Config, ROOT
from .engine import Engine, PERMISSIONS
from .model import Gemini
from .sandbox import Sandbox
from .store import Store

WEB = ROOT / "web"


class Application:
    def __init__(self, config):
        self.config = config
        self.model = Gemini(config)
        self.sandbox = Sandbox(config.image)
        self.store = Store(config.data_dir)
        self.engine = Engine(config, self.model, self.sandbox, self.store)
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.lock = threading.Lock()
        self.future = None
        for run in self.store.runs():
            if run["status"] in ("running", "queued"):
                run.update(status="interrupted", error="Předchozí proces skončil před dokončením.")
                self.store.save_run(run)

    def busy(self):
        return self.future is not None and not self.future.done()

    def start(self, task, inputs, kind):
        with self.lock:
            if self.busy():
                raise ValueError("Jiný úkol právě běží. Počkej na jeho dokončení.")
            if error := self.model.ready():
                raise ValueError(error)
            run = self.store.new_run(task, inputs, kind)
            self.future = self.pool.submit(self.engine.execute, run)
            return run


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
            if path == "/api/state":
                return self.reply({"model": app.config.model, "model_ready": app.model.ready() is None,
                                   "model_status": app.model.ready(), "free_tier_confirmed": app.config.free_confirmed,
                                   "permissions": PERMISSIONS, "busy": app.busy(),
                                   "runs": app.store.runs(), "registry": app.store.registry(),
                                   "limits": {"calls": app.config.max_calls, "seconds": app.config.max_seconds}})
            if path == "/api/health":
                return self.reply({"sandbox": app.sandbox.status(), "model_ready": app.model.ready() is None})
            if path.startswith("/api/events/"):
                return self.reply(app.store.events(path.rsplit("/", 1)[-1]))
            file = (WEB / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
            if not file.is_relative_to(WEB.resolve()) or not file.is_file():
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
                if not 0 < size <= 64000 or self.headers.get("Content-Type") != "application/json":
                    raise ValueError("Expected JSON request under 64 KB")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Expected object")
                if self.path in ("/api/run", "/api/correct"):
                    task = body.get("task", "")
                    if not isinstance(task, str) or not 1 <= len(task.strip()) <= 4000:
                        raise ValueError("Zadej úkol o délce 1–4 000 znaků.")
                    kind = "task" if self.path == "/api/run" else "correction"
                    return self.reply(app.start(task.strip(), body.get("input"), kind), 202)
                if self.path == "/api/deactivate":
                    with app.lock:
                        if app.busy():
                            raise ValueError("Počkej na dokončení běžícího úkolu.")
                        app.store.deactivate(body["id"])
                    return self.reply({"ok": True})
                return self.reply({"error": "Not found"}, 404)
            except (ValueError, TypeError, KeyError) as error:
                return self.reply({"error": str(error)}, 400)

    return Handler


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    app = Application(Config.from_env())
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(app, args.port))
    print(f"Workbench running at http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app.pool.shutdown(wait=True)
        app.store.close()


if __name__ == "__main__":
    main()

