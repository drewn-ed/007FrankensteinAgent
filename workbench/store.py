import hashlib
import json
import sqlite3
import threading
import time
import uuid


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


class Store:
    def __init__(self, directory):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(directory / "workbench.sqlite", check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS versions(id TEXT, version INTEGER, body TEXT, PRIMARY KEY(id,version));
        CREATE TABLE IF NOT EXISTS active(id TEXT PRIMARY KEY, version INTEGER);
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, body TEXT);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, body TEXT);
        ''')
        self.db.commit()

    def close(self):
        self.db.close()

    def registry(self):
        with self.lock:
            rows = self.db.execute("SELECT v.body FROM versions v JOIN active a ON a.id=v.id AND a.version=v.version ORDER BY v.id").fetchall()
        return [json.loads(row[0]) for row in rows]

    def get(self, ident):
        return next((item for item in self.registry() if item["manifest"]["id"] == ident), None)

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

    def new_run(self, task, inputs, kind="task"):
        run = {"id": uuid.uuid4().hex, "task": task, "input": inputs, "kind": kind,
               "status": "queued", "created_at": time.time(), "result": None,
               "registry_before": digest(self.registry()), "model_calls": 0, "tokens": 0}
        self.save_run(run)
        return run

    def save_run(self, run):
        with self.lock, self.db:
            self.db.execute("INSERT OR REPLACE INTO runs VALUES(?,?)", (run["id"], encoded(run)))

    def runs(self):
        with self.lock:
            rows = self.db.execute("SELECT body FROM runs ORDER BY rowid DESC LIMIT 30").fetchall()
        return [json.loads(row[0]) for row in rows]

    def event(self, run_id, kind, message, **data):
        event = {"kind": kind, "message": message, "at": time.time(), **data}
        with self.lock, self.db:
            self.db.execute("INSERT INTO events(run_id,body) VALUES(?,?)", (run_id, encoded(event)))

    def events(self, run_id):
        with self.lock:
            rows = self.db.execute("SELECT seq,body FROM events WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
        return [{"seq": row[0], **json.loads(row[1])} for row in rows]
