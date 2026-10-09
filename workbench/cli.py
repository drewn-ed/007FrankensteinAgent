"""Run a real task through the same engine as the UI; no seeded capabilities."""
import argparse
import json
from pathlib import Path

from .config import Config
from .engine import Engine
from .model import Gemini
from .sandbox import Sandbox
from .store import Store


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    config = Config.from_env()
    if args.data_dir:
        config.data_dir = args.data_dir
    store = Store(config.data_dir)
    try:
        run = store.new_run(args.task, json.loads(args.input.read_text()))
        engine = Engine(config, Gemini(config), Sandbox(config.image), store)
        original = engine.event
        def event(run_record, kind, message, **data):
            original(run_record, kind, message, **data)
            print(json.dumps({"kind": kind, "message": message}, ensure_ascii=False), flush=True)
        engine.event = event
        engine.execute(run)
        print(json.dumps(run, ensure_ascii=False, indent=2))
        raise SystemExit(0 if run["status"] == "completed" else 1)
    finally:
        store.close()


if __name__ == "__main__":
    main()
