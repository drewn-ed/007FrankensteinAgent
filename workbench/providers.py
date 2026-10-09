"""Explicit provider selection; never fallback between billing/auth modes."""
import json
import re
import time
from urllib.request import Request
from urllib.error import HTTPError, URLError

from .model import Gemini, RunError, ModelFormatError
from .chatgpt_auth import ChatGPTAuth, RESOURCE, open_direct


def create_model(config, auth=None):
    if config.provider == "gemini":
        return Gemini(config)
    if config.provider == "chatgpt":
        return ChatGPTModel(config, auth or ChatGPTAuth(config.chatgpt_auth_dir))
    raise RunError("Unknown model provider. Choose gemini or chatgpt.")


def response_usage(value):
    if not isinstance(value, dict):
        return None
    def number(v):
        return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None
    inp, out, total = (number(value.get(k)) for k in ("input_tokens", "output_tokens", "total_tokens"))
    thinking = number((value.get("output_tokens_details") or {}).get("reasoning_tokens", 0))
    cached = number((value.get("input_tokens_details") or {}).get("cached_tokens", 0))
    if None in (inp, out, total, thinking, cached) or thinking > out or cached > inp or total != inp + out:
        return None
    return {"input": inp, "output": out - thinking, "thinking": thinking,
            "cached_input": cached, "total": total, "tool_input": 0}


def safe_error(value):
    code = (value.get("code") or value.get("type") or "") if isinstance(value, dict) else ""
    if not isinstance(code, str) or not re.fullmatch(r"[a-zA-Z0-9_]{1,100}", code):
        code = "unknown_error"
    if code == "subscription_sharing_usage_limit_exceeded":
        return "ChatGPT plan usage limit reached. Check Settings → Usage in ChatGPT. No fallback was attempted."
    param = value.get("param") if isinstance(value, dict) else None
    suffix = f" (field: {param})" if isinstance(param, str) and re.fullmatch(r"[a-zA-Z0-9_.\[\]-]{1,100}", param) else ""
    return "OpenAI response failed: " + code + suffix


class ChatGPTModel:
    def __init__(self, config, auth):
        self.config, self.auth = config, auth

    def ready(self):
        try:
            if not self.auth.status()["connected"]:
                return "Connect ChatGPT and allow plan usage in Settings."
        except RunError as error:
            return str(error)
        if not self.config.model:
            return "Choose an available ChatGPT model in Settings."
        return None

    def ask(self, system, payload, budget):
        if error := self.ready():
            raise RunError(error)
        token = self.auth.access_token()
        budget.reserve()
        started = time.monotonic()
        record = {"call": budget.calls, "purpose": budget.purpose, "provider": "OpenAI · ChatGPT plan",
                  "model": self.config.model, "started_at": time.time(), "status": "pending", "usage": None,
                  "pricing": {"tier": "chatgpt_plan", "currency": "USD", "paid_standard_per_million": None,
                              "source": "https://developers.openai.com/siwc/token-sharing-open-source"}}
        budget.usage.append(record)
        budget.notify_usage()
        try:
            body = {"model": self.config.model, "instructions": system,
                    # JSON mode requires an explicit JSON instruction in input,
                    # even when the separate instructions field already has one.
                    "input": [{"role": "developer", "content": "Return only a valid JSON object following the provided instructions."},
                              {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
                    "store": False, "stream": True, "text": {"format": {"type": "json_object"}}}
            request = Request(RESOURCE + "/responses", data=json.dumps(body).encode(),
                              headers={"Authorization": "Bearer " + token, "Content-Type": "application/json",
                                       "Accept": "text/event-stream"})
            completed = None
            text_parts = {}
            with open_direct(request, timeout=min(55, budget.remaining_seconds())) as stream:
                data_lines, total_bytes = [], 0
                while True:
                    budget.check()
                    line = stream.readline(262_145)
                    if not line:
                        break
                    total_bytes += len(line)
                    if len(line) > 262_144 or total_bytes > 1_500_000:
                        raise RunError("OpenAI response exceeded the local stream size limit.")
                    line = line.decode("utf-8").rstrip("\r\n")
                    if line.startswith("data:"):
                        data_lines.append(line[5:].lstrip())
                        continue
                    if line or not data_lines:
                        continue
                    data = "\n".join(data_lines)
                    data_lines = []
                    if data == "[DONE]":
                        continue
                    event = json.loads(data)
                    kind = event.get("type")
                    if kind in ("response.output_text.delta", "response.output_text.done"):
                        key = (event.get("output_index", 0), event.get("content_index", 0))
                        value = event.get("delta" if kind.endswith("delta") else "text", "")
                        if not all(isinstance(i, int) for i in key) or not isinstance(value, str):
                            raise RunError("OpenAI returned an invalid text event.")
                        text_parts[key] = text_parts.get(key, "") + value if kind.endswith("delta") else value
                    if kind in ("response.completed", "response.failed", "response.incomplete"):
                        response = event.get("response", {})
                        record["usage"] = response_usage(response.get("usage"))
                        budget.tokens += (record["usage"] or {}).get("total") or 0
                        record["resolved_model"] = response.get("model", self.config.model)
                        if kind != "response.completed" or response.get("status") != "completed":
                            raise RunError(safe_error(response.get("error")) if kind == "response.failed" else "OpenAI response was incomplete; no partial result was accepted.")
                        completed = response
                        break
                    if kind == "error":
                        raise RunError(safe_error(event))
            if completed is None:
                raise RunError("OpenAI stream ended without a completed response. No partial result was accepted.")
            text = "".join(part.get("text", "") for item in completed.get("output", [])
                           if item.get("type") == "message" for part in item.get("content", [])
                           if part.get("type") == "output_text")
            # Plan-usage streams can omit output from the terminal envelope.
            # Use accumulated text only after a successful completed event.
            if not text:
                text = "".join(text_parts[key] for key in sorted(text_parts))
            try:
                result = json.loads(text)
            except ValueError:
                raise ModelFormatError("OpenAI returned invalid JSON.") from None
            if not isinstance(result, dict):
                raise ModelFormatError("OpenAI must return a JSON object.")
            budget.check()
            record["status"] = "completed"
            return result
        except HTTPError as error:
            record["status"] = "failed"
            try:
                detail = json.loads(error.read(16_384)).get("error", {})
            except (ValueError, AttributeError):
                detail = {}
            raise RunError(f"OpenAI request failed (HTTP {error.code}). " + safe_error(detail)) from None
        except (URLError, TimeoutError, UnicodeError, ValueError):
            record["status"] = "failed"
            raise RunError("OpenAI connection or response failed. No fallback was attempted.") from None
        except Exception:
            record["status"] = "failed"
            raise
        finally:
            record["duration_ms"] = round((time.monotonic() - started) * 1000)
            budget.notify_usage()
