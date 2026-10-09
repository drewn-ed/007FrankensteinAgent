import hashlib
import json
import sqlite3
import threading
import time
import uuid


class WorkspaceConflict(ValueError):
    pass


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


class Store:
    def __init__(self, directory):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        # mkdir(exist_ok=True) does not tighten permissions on an older workspace.
        directory.chmod(0o700)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(directory / "workbench.sqlite", check_same_thread=False)
        (directory / "workbench.sqlite").chmod(0o600)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS versions(id TEXT, version INTEGER, body TEXT, PRIMARY KEY(id,version));
        CREATE TABLE IF NOT EXISTS active(id TEXT PRIMARY KEY, version INTEGER);
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, body TEXT);
        CREATE TABLE IF NOT EXISTS runtime_settings(key TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE IF NOT EXISTS catalog_state(key TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE IF NOT EXISTS workspace_state(key TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE IF NOT EXISTS application_maps(origin TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE IF NOT EXISTS application_map_scopes(scope TEXT, origin TEXT, body TEXT, PRIMARY KEY(scope,origin));
        INSERT OR IGNORE INTO application_map_scopes SELECT 'personal',origin,body FROM application_maps;
        ''')
        self.db.commit()

    def close(self):
        self.db.close()

    def setting(self, key, default=None):
        with self.lock:
            row = self.db.execute("SELECT body FROM runtime_settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO runtime_settings VALUES(?,?)", (key, encoded(value)))

    def registry(self):
        with self.lock:
            rows = self.db.execute("SELECT v.body FROM versions v JOIN active a ON a.id=v.id AND a.version=v.version ORDER BY v.id").fetchall()
        return [json.loads(row[0]) for row in rows]

    def get(self, ident):
        return next((item for item in self.registry() if item["manifest"]["id"] == ident), None)

    def versions(self):
        with self.lock:
            rows = self.db.execute("SELECT body FROM versions ORDER BY id,version").fetchall()
        return [json.loads(row[0]) for row in rows]

    def save_catalog(self, record, scope="current"):
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO catalog_state VALUES(?,?)", (scope, encoded(record)))

    def catalog(self, scope="current"):
        with self.lock:
            row = self.db.execute("SELECT body FROM catalog_state WHERE key=?", (scope,)).fetchone()
        return json.loads(row[0]) if row else None

    def scoped(self, project_id):
        return ScopedStore(self, project_id)

    def remember_app(self, snapshot, project_id=None):
        if not snapshot.get("connected"):
            return
        record = {"origin": snapshot["origin"], "title": snapshot.get("title", ""), "observed_at": time.time(),
                  "source": "browser_observation", "project_id": project_id, "elements": [{k: v for k, v in el.items() if k in ("tag", "role", "name", "type")} for el in snapshot.get("elements", [])]}
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO application_map_scopes VALUES(?,?,?)", ("project:"+project_id if project_id else "personal", record["origin"], encoded(record)))

    def applications(self, project_id=None):
        with self.lock:
            rows = self.db.execute("SELECT body FROM application_map_scopes WHERE scope=? ORDER BY origin", ("project:"+project_id if project_id else "personal",)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def accept(self, manifest, code, cases, report, provenance):
        if not report or not all(case["passed"] for case in report) or len(report) != len(cases):
            raise ValueError("A failed or incomplete test report cannot be installed")
        with self.lock:
            ident = manifest["id"]
            version = self.db.execute("SELECT COALESCE(MAX(version),0)+1 FROM versions WHERE id=?", (ident,)).fetchone()[0]
            record = {"manifest": manifest, "version": version, "code": code,
                      "code_hash": digest(code), "cases": cases, "tests": report,
                      "provenance": provenance, "created_at": time.time()}
            with self.db:
                self.db.execute("INSERT INTO versions VALUES(?,?,?)", (ident, version, encoded(record)))
                self.db.execute("INSERT OR REPLACE INTO active VALUES(?,?)", (ident, version))
            return record

    def deactivate(self, ident):
        with self.lock, self.db:
            self.db.execute("DELETE FROM active WHERE id=?", (ident,))

    def activate(self, ident, version):
        with self.lock, self.db:
            row = self.db.execute("SELECT body FROM versions WHERE id=? AND version=?", (ident, version)).fetchone()
            if not row:
                raise ValueError("This skill version does not exist.")
            record = json.loads(row[0])
            if not record["tests"] or not all(test["passed"] for test in record["tests"]):
                raise ValueError("Only a tested version can be activated.")
            self.db.execute("INSERT OR REPLACE INTO active VALUES(?,?)", (ident, version))
            return record

    def workspace(self):
        with self.lock:
            row = self.db.execute("SELECT body FROM workspace_state WHERE key='workspace'").fetchone()
            return json.loads(row[0]) if row else {"projects": [], "chats": [], "workflows": []}

    def save_workspace(self, value):
        if not isinstance(value, dict) or any(not isinstance(value.get(key), list) for key in ("projects", "chats", "workflows")):
            raise ValueError("Invalid workspace data.")
        if len(encoded(value)) > 1_500_000:
            raise ValueError("Workspace data exceeds the local storage limit.")
        for key in ("projects", "chats", "workflows"):
            if len(value[key]) > 500 or any(not isinstance(item, dict) or not isinstance(item.get("id"), str) for item in value[key]):
                raise ValueError("Invalid workspace records.")
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO workspace_state VALUES('workspace',?)", (encoded(value),))

    def run(self, ident):
        with self.lock:
            row = self.db.execute("SELECT body FROM runs WHERE id=?", (ident,)).fetchone()
        return json.loads(row[0]) if row else None

    def merge_workspace(self, base, value):
        """Merge only client changes, rejecting conflicting edits atomically."""
        for document in (base, value):
            if not isinstance(document, dict) or any(not isinstance(document.get(k), list) for k in ("projects", "chats", "workflows")):
                raise ValueError("Workspace updates require the snapshot they were edited from. Reload this tab.")
            for key in ("projects", "chats", "workflows"):
                rows = document[key]
                if any(not isinstance(r, dict) or not isinstance(r.get("id"), str) for r in rows) or len({r["id"] for r in rows}) != len(rows):
                    raise ValueError("Invalid or duplicate workspace record.")
        missing = object()
        with self.lock:
            merged = self.workspace()
            for key in ("projects", "chats", "workflows"):
                before, after, current = ({r["id"]: r for r in d[key]} for d in (base, value, merged))
                for ident in before.keys() | after.keys():
                    old, new, latest = before.get(ident), after.get(ident), current.get(ident)
                    if old == new:
                        continue
                    if old is None:
                        if latest is not None and latest != new:
                            raise WorkspaceConflict("This new item conflicts with another tab. Your local edits have not been saved.")
                        current[ident] = new
                    elif new is None:
                        if latest is not None and latest != old:
                            raise WorkspaceConflict("Another tab edited the item you are removing. Your local edits have not been saved.")
                        current.pop(ident, None)
                    else:
                        if latest is None:
                            raise WorkspaceConflict("Another tab removed this item. Your local edits have not been saved.")
                        result = dict(latest)
                        for field in old.keys() | new.keys():
                            a, b, c = old.get(field, missing), new.get(field, missing), latest.get(field, missing)
                            if a == b:
                                continue
                            if c != a and c != b:
                                if field == "runIds" and all(isinstance(x, list) for x in (a, b, c)) and set(a) <= set(b) and set(a) <= set(c):
                                    b = list(dict.fromkeys(c + b))
                                else:
                                    raise WorkspaceConflict("Another tab changed the same field. Your local edits have not been saved.")
                            if b is missing:
                                result.pop(field, None)
                            else:
                                result[field] = b
                        current[ident] = result
                merged[key] = list(current.values())
            self.save_workspace(merged)
            return merged

    def chat_context(self, chat_id, project_id):
        if not chat_id:
            return []
        chat = next((c for c in self.workspace()["chats"] if c["id"] == chat_id), None)
        if not chat or chat.get("projectId") != project_id:
            raise ValueError("The chat does not belong to this project. Reload before sending.")
        result, size = [], 0
        for run in self.runs(limit=None):
            if run.get("chat_id") != chat_id or run.get("project_id") != project_id:
                continue
            item = {"run_id": run["id"], "task": run["task"], "status": run["status"],
                    "result": run.get("result"), "input": run.get("input"), "message": run.get("message")}
            if size + len(encoded(item)) > 100_000:
                result.append({"run_id": run["id"], "task": run["task"], "status": run["status"], "context_omitted": True})
                break
            result.append(item)
            size += len(encoded(item))
            if len(result) == 6:
                break
        return result[::-1]

    def new_run(self, task, inputs, kind="task"):
        run = {"id": uuid.uuid4().hex, "task": task, "input": inputs, "kind": kind,
               "status": "queued", "created_at": time.time(), "result": None,
               "registry_before": digest(self.registry()), "model_calls": 0, "tokens": 0}
        self.save_run(run)
        return run

    def save_run(self, run):
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO runs VALUES(?,?)", (run["id"], encoded(run)))

    def runs(self, limit=30):
        with self.lock:
            rows = self.db.execute("SELECT body FROM runs").fetchall()
        records = sorted((json.loads(row[0]) for row in rows), key=lambda r: r["created_at"], reverse=True)
        return records if limit is None else records[:limit]

    def event(self, run_id, kind, message, **data):
        event = {"kind": kind, "message": message, "at": time.time(), **data}
        with self.lock, self.db:
            self.db.execute("INSERT INTO events(run_id,body) VALUES(?,?)", (run_id, encoded(event)))

    def events(self, run_id):
        with self.lock:
            rows = self.db.execute("SELECT seq,body FROM events WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
        return [{"seq": row[0], **json.loads(row[1])} for row in rows]


class ScopedStore:
    """A project sees its own capabilities plus explicitly unscoped capabilities."""
    def __init__(self, store, project_id):
        self.store, self.project_id = store, project_id

    def __getattr__(self, name):
        return getattr(self.store, name)

    def allowed(self, record):
        return record.get("provenance", {}).get("project_id") in (None, self.project_id)

    def registry(self):
        return [r for r in self.store.registry() if self.allowed(r)]

    def versions(self):
        return [r for r in self.store.versions() if self.allowed(r)]

    def get(self, ident):
        return next((r for r in self.registry() if r["manifest"]["id"] == ident), None)

    def accept(self, manifest, code, cases, report, provenance):
        existing = [v for v in self.store.versions() if v["manifest"]["id"] == manifest["id"]]
        if existing and existing[-1].get("provenance", {}).get("project_id") != self.project_id:
            raise ValueError("A project cannot replace a skill belonging to another scope.")
        return self.store.accept(manifest, code, cases, report, {**provenance, "project_id": self.project_id})

    def save_catalog(self, record):
        return self.store.save_catalog(record, self.project_id or "current")

    def catalog(self):
        return self.store.catalog(self.project_id or "current")

    def remember_app(self, snapshot):
        return self.store.remember_app(snapshot, self.project_id)

    def applications(self):
        return self.store.applications(self.project_id)
