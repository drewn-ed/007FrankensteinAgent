"""Only this trusted adapter receives the provider credential."""
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from .usage import price_snapshot, read_usage


class NoCredentialRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def provider_open(request, timeout):
    # Provider credentials must never follow even a same-origin redirect.
    return urllib.request.build_opener(NoCredentialRedirect()).open(request, timeout=timeout)


class RunError(Exception):
    pass


class ModelFormatError(RunError):
    """A completed response could not be parsed; not a quota/transport error."""
    pass


@dataclass
class Budget:
    max_calls: int = 12
    max_seconds: int = 240
    calls: int = 0
    tokens: int = 0
    started: float = field(default_factory=time.monotonic)
    cancelled: object = None
    purpose: str = "Planning"
    usage: list = field(default_factory=list)
    on_usage: object = None
    format_retry_used: bool = False
    on_format_retry: object = None
    spend: object = None

    def authorize_spend(self, config):
        from .spend import SpendLedger, SpendError
        try:
            if self.spend is None:
                self.spend = SpendLedger(config.max_run_usd, config.spend_policy)
            return self.spend.authorize(config)
        except SpendError as error:
            self.notify_usage()
            raise RunError(str(error)) from None

    def notify_usage(self):
        if self.on_usage:
            self.on_usage(self)

    def check(self):
        if self.cancelled and self.cancelled():
            raise RunError("Stopped by you. No further steps will run.")
        if time.monotonic() - self.started >= self.max_seconds:
            raise RunError("The run reached its time limit.")

    def reserve(self):
        self.check()
        if self.calls >= self.max_calls:
            raise RunError("The run reached its model call limit.")
        self.calls += 1

    def remaining_seconds(self):
        self.check()
        return max(0.1, self.max_seconds - (time.monotonic() - self.started))


def response_schema(system, payload):
    """Constrain transport shape; capability tests still validate semantic correctness."""
    if system.startswith("Implement the given capability contract"):
        return {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"], "additionalProperties": False}
    if system.startswith("You design contract tests") and isinstance(payload.get("manifest"), dict):
        manifest = payload["manifest"]
        return {"type": "object", "properties": {"cases": {"type": "array", "items": {
            "type": "object", "properties": {"name": {"type": "string"}, "input": manifest["input_schema"], "expected": manifest["output_schema"]},
            "required": ["name", "input", "expected"], "additionalProperties": False}}}, "required": ["cases"], "additionalProperties": False}
    return None


class Gemini:
    # Explicitly verified against Google's pricing page on 2026-10-09.
    FREE_MODELS = {"gemini-3.5-flash-lite", "gemini-3.1-flash-lite"}

    def __init__(self, config):
        self.config = config

    def ready(self):
        if not self.config.key:
            return "GEMINI_API_KEY is missing from the local .env file."
        if not self.config.free_confirmed:
            return "Confirm the project uses the Free tier in Google AI Studio before running inference."
        if self.config.model not in self.FREE_MODELS:
            return "The model is not on the verified list for free testing."
        return None

    def ask(self, system, payload, budget):
        if error := self.ready():
            raise RunError(error)
        budget.check()
        admission = budget.authorize_spend(self.config)
        budget.reserve()  # Failed requests count too. No automatic retry/fallback.
        started = time.monotonic()
        record = {"call": budget.calls, "purpose": budget.purpose, "provider": "Google Gemini",
                  "model": self.config.model, "started_at": time.time(), "status": "pending", "usage": None,
                  "pricing": price_snapshot(self.config.model, self.config.free_confirmed),
                  "spend_admission": admission}
        budget.usage.append(record)
        budget.notify_usage()
        try:
            return self._request(system, payload, budget, record)
        except Exception:
            record["status"] = "failed"
            raise
        finally:
            record["duration_ms"] = round((time.monotonic() - started) * 1000)
            budget.notify_usage()

    def _request(self, system, payload, budget, record):
        body = {"systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": json.dumps(payload, ensure_ascii=False)}]}],
                "generationConfig": {"responseMimeType": "application/json",
                                     "maxOutputTokens": self.config.max_output}}
        schema = response_schema(system, payload)
        if schema:
            body["generationConfig"]["responseJsonSchema"] = schema
        request = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.config.key})
        try:
            with provider_open(request, timeout=min(55, budget.remaining_seconds())) as response:
                raw = response.read(500_001)
            if len(raw) > 500_000:
                raise RunError("The model response exceeded the size limit.")
            result = json.loads(raw)
        except urllib.error.HTTPError as exc:
            # Never surface provider response bodies or request headers.
            if exc.code == 429:
                raise RunError("Gemini quota exhausted. The run stopped without a paid fallback.") from None
            raise RunError(f"Gemini rejected the request (HTTP {exc.code}).") from None
        except (TimeoutError, urllib.error.URLError):
            raise RunError("Gemini did not respond in time; the run stopped.") from None
        if not isinstance(result, dict):
            raise RunError("The model returned an invalid response envelope.")
        record["usage"] = read_usage(result.get("usageMetadata"))
        record["resolved_model"] = result.get("modelVersion")
        record["service_tier"] = (result.get("usageMetadata") or {}).get("serviceTier")
        budget.tokens += (record["usage"] or {}).get("total") or 0
        budget.check()
        candidates = result.get("candidates", [])
        if not candidates or candidates[0].get("finishReason") != "STOP":
            raise RunError("The model response was incomplete; the partial result will not be used.")
        try:
            text = "".join(p.get("text", "") for p in candidates[0]["content"]["parts"] if not p.get("thought"))
            data = json.loads(text)
        except json.JSONDecodeError as error:
            record["format_error"] = {"line": error.lineno, "column": error.colno, "reason": error.msg}
            raise ModelFormatError("The model returned invalid JSON.") from None
        except KeyError:
            raise ModelFormatError("The model response is missing JSON content.") from None
        if not isinstance(data, dict):
            raise ModelFormatError("The model must return a JSON object.")
        record["status"] = "completed"
        return data
