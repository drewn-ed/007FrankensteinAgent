from dataclasses import dataclass, field
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def bounded_int(name, default, ceiling):
    return max(1, min(int(os.environ.get(name, default)), ceiling))


@dataclass
class Config:
    key: str = field(default="", repr=False)
    model: str = "gemini-3.5-flash-lite"
    free_confirmed: bool = False
    max_calls: int = 18
    max_output: int = 8192
    max_seconds: int = 240
    image: str = "python:3.12-slim"
    data_dir: Path = ROOT / ".runtime"
    provider: str = "gemini"
    max_run_usd: str = "0"
    spend_policy: str = "strict"
    chatgpt_auth_dir: Path = Path.home() / ".config" / "007-frankenstein"

    @classmethod
    def from_env(cls):
        load_env()
        provider = os.environ.get("MODEL_PROVIDER", "gemini")
        return cls(key=os.environ.get("GEMINI_API_KEY", ""),
                   provider=provider,
                   max_run_usd=os.environ.get("MAX_RUN_USD", "0"),
                   spend_policy=os.environ.get("SPEND_POLICY", "strict"),
                   model=os.environ.get("CHATGPT_MODEL", "") if provider == "chatgpt" else os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
                   free_confirmed=os.environ.get("GEMINI_FREE_TIER_CONFIRMED") == "true",
                   max_calls=bounded_int("MAX_MODEL_CALLS", 18, 20),
                   max_output=bounded_int("MAX_OUTPUT_TOKENS", 8192, 8192),
                   max_seconds=bounded_int("MAX_RUN_SECONDS", 240, 600),
                   image=os.environ.get("SANDBOX_IMAGE", "python:3.12-slim"))
