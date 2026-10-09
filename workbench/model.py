"""Only this trusted adapter receives the provider credential."""
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field


class RunError(Exception):
    pass


@dataclass
class Budget:
    max_calls: int = 12
    max_seconds: int = 240
    calls: int = 0
    tokens: int = 0
    started: float = field(default_factory=time.monotonic)

    def check(self):
        if time.monotonic() - self.started >= self.max_seconds:
            raise RunError("Běh dosáhl časového limitu.")

    def reserve(self):
        self.check()
        if self.calls >= self.max_calls:
            raise RunError("Běh vyčerpal povolený počet volání modelu.")
        self.calls += 1

    def remaining_seconds(self):
        self.check()
        return max(0.1, self.max_seconds - (time.monotonic() - self.started))


class Gemini:
    # Explicitly verified against Google's pricing page on 2026-10-09.
    FREE_MODELS = {"gemini-3.5-flash-lite", "gemini-3.1-flash-lite"}

    def __init__(self, config):
        self.config = config

    def ready(self):
        if not self.config.key:
            return "Chybí GEMINI_API_KEY v lokálním .env."
        if not self.config.free_confirmed:
            return "Nejdřív potvrď Free tarif projektu v Google AI Studiu; inference je pozastavená."
        if self.config.model not in self.FREE_MODELS:
            return "Model není na ověřeném seznamu pro bezplatné testování."
        return None

    def ask(self, system, payload, budget):
        if error := self.ready():
            raise RunError(error)
        budget.reserve()  # Failed requests count too. No automatic retry/fallback.
        body = {"systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": json.dumps(payload, ensure_ascii=False)}]}],
                "generationConfig": {"responseMimeType": "application/json",
                                     "maxOutputTokens": self.config.max_output}}
        request = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.config.key})
        try:
            with urllib.request.urlopen(request, timeout=min(55, budget.remaining_seconds())) as response:
                raw = response.read(500_001)
            if len(raw) > 500_000:
                raise RunError("Odpověď modelu překročila limit velikosti.")
            result = json.loads(raw)
        except urllib.error.HTTPError as exc:
            # Never surface provider response bodies or request headers.
            if exc.code == 429:
                raise RunError("Gemini vyčerpalo kvótu. Běh zastaven, bez placeného fallbacku.") from None
            raise RunError(f"Gemini odmítlo požadavek (HTTP {exc.code}).") from None
        except (TimeoutError, urllib.error.URLError):
            raise RunError("Gemini neodpovědělo v limitu; běh zastaven.") from None
        budget.check()
        budget.tokens += int(result.get("usageMetadata", {}).get("totalTokenCount", 0))
        candidates = result.get("candidates", [])
        if not candidates or candidates[0].get("finishReason") != "STOP":
            raise RunError("Model nedokončil celou odpověď; částečný výsledek se nepoužije.")
        try:
            text = "".join(p.get("text", "") for p in candidates[0]["content"]["parts"] if not p.get("thought"))
            data = json.loads(text)
        except (KeyError, ValueError):
            raise RunError("Model vrátil neplatný JSON.") from None
        if not isinstance(data, dict):
            raise RunError("Model musí vrátit JSON objekt.")
        return data

