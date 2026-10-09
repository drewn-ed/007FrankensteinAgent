"""Durable local schedules. No daemon installation and no replay burst after downtime."""
import json
import sqlite3
import threading
import time
import uuid
from .model import RunError

class Scheduler:
    def __init__(self, directory, start, busy, *, clock=time.time):
        self.db = sqlite3.connect(directory / 'schedules.sqlite', check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS schedules(id TEXT PRIMARY KEY, body TEXT)'); self.db.commit()
        self.lock = threading.RLock(); self.start = start; self.busy = busy; self.clock = clock
        self.stopped = threading.Event(); self.thread = None

    def rows(self):
        with self.lock: return [json.loads(r[0]) for r in self.db.execute('SELECT body FROM schedules ORDER BY id')]

    def save(self, row):
        with self.lock, self.db: self.db.execute('INSERT OR REPLACE INTO schedules VALUES(?,?)', (row['id'], json.dumps(row)))
        return row

    def create(self, payload):
        title, task = payload.get('title'), payload.get('task')
        if not isinstance(title, str) or not 1 <= len(title) <= 120 or not isinstance(task, str) or not 1 <= len(task) <= 4000:
            raise RunError('A schedule needs a title and task.')
        interval = payload.get('interval_minutes', 0)
        if type(interval) is not int or interval not in (0, 15, 60, 1440, 10080): raise RunError('Choose one time, every 15 minutes, hourly, daily or weekly.')
        due = payload.get('next_at')
        if type(due) not in (int, float) or not self.clock() - 5 <= due <= self.clock() + 366 * 86400:
            raise RunError('Choose a time within the next year.')
        mode = payload.get('mode', 'data')
        if mode not in ('data','browser','desktop'): raise RunError('Invalid scheduled mode.')
        if mode != 'data' and not isinstance(payload.get('connection'), str): raise RunError('An interactive schedule needs an explicit application connection.')
        return self.save({'id': uuid.uuid4().hex, 'title': title, 'task': task, 'input': payload.get('input', {}),
                          'project_id': payload.get('project_id'), 'interval_minutes': interval, 'next_at': due,
                          'enabled': True, 'history': [], 'mode': mode, 'connection': payload.get('connection')})

    def update(self, ident, enabled):
        with self.lock:
            row = next((r for r in self.rows() if r['id'] == ident), None)
            if not row: raise RunError('Schedule not found.')
            row['enabled'] = bool(enabled)
            if enabled and row['next_at'] < self.clock(): row['next_at'] = self.clock()
            return self.save(row)

    def tick(self):
        with self.lock:
            if self.busy(): return
            due = sorted([r for r in self.rows() if r['enabled'] and r['next_at'] <= self.clock()], key=lambda r: r['next_at'])
            if not due: return
            row = due[0]; scheduled_for = row['next_at']
            # Persist the claim before launching. Restart cannot launch this occurrence twice.
            row['enabled'] = bool(row['interval_minutes'])
            row['next_at'] = self.clock() + row['interval_minutes'] * 60
            row['history'] = (row['history'] + [{'scheduled_for': scheduled_for, 'started_at': self.clock(), 'status': 'dispatching'}])[-30:]
            self.save(row)
            try:
                run = self.start(row['task'], row['input'], kind='task', project_id=row['project_id'], chat_id=None, mode=row['mode'], connection=row.get('connection'))
                row['history'][-1].update(status='started', run_id=run['id'])
            except (RunError, ValueError) as error:
                row['history'][-1].update(status='failed', error=str(error)); row['enabled'] = False
            self.save(row)

    def start_loop(self):
        if self.thread: return
        def loop():
            while not self.stopped.wait(2):
                try: self.tick()
                except Exception: self.stopped.set()  # Fail closed; never silently continue a broken dispatcher.
        self.thread = threading.Thread(target=loop, daemon=True, name='workspace-scheduler'); self.thread.start()

    def close(self):
        self.stopped.set()
        if self.thread: self.thread.join(timeout=5)
        self.db.close()
