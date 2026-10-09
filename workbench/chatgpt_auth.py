"""Official SIWC public-client flow. Credentials never leave trusted Python code.

https://developers.openai.com/siwc/token-sharing-open-source/sign-in
No Codex credential extraction, reverse proxy or paid API-key fallback.
"""
import base64
import fcntl
import hashlib
import json
import os
import secrets
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

import jwt
from .model import RunError

ISSUER = "https://auth.openai.com"
AUTHORIZE = ISSUER + "/api/accounts/authorize"
TOKEN = ISSUER + "/api/accounts/oauth/token"
JWKS = ISSUER + "/.well-known/jwks.json"
RESOURCE = "https://api.openai.com/v1"
PLAN_SCOPE = "chatgpt.tokens.use.direct"
SCOPES = "openid profile email offline_access resource.invoke " + PLAN_SCOPE


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_direct(request, timeout=20):
    return build_opener(NoRedirect).open(request, timeout=timeout)


def request_json(url, *, form=None, access_token=None):
    headers = {"Accept": "application/json"}
    if access_token:
        headers["Authorization"] = "Bearer " + access_token
    data = None
    if form is not None:
        data = urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        with open_direct(Request(url, data=data, headers=headers)) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise RunError("ChatGPT returned an oversized response.")
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError()
        return result
    except HTTPError as error:
        # Never expose OAuth response bodies, codes, headers or tokens.
        raise RunError(f"ChatGPT request failed (HTTP {error.code}). Check your connection and plan access.") from None
    except (URLError, TimeoutError, ValueError):
        raise RunError("ChatGPT did not return a valid response. Try again later.") from None


def atomic_private(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".write-")
    try:
        with os.fdopen(fd, "w") as stream:
            os.fchmod(stream.fileno(), 0o600)
            json.dump(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def validate_identity(id_token, client_id, nonce=None, expected=None):
    try:
        keys = request_json(JWKS).get("keys", [])
        header = jwt.get_unverified_header(id_token)
        if header.get("alg") != "RS256":
            raise ValueError()
        key = next(k for k in keys if k.get("kid") == header.get("kid"))
        identity = jwt.decode(id_token, jwt.PyJWK.from_dict(key).key, algorithms=["RS256"],
                              audience=client_id, issuer=ISSUER, leeway=5,
                              options={"require": ["iss", "aud", "exp", "iat", "sub"]})
        if not isinstance(identity["sub"], str) or not identity["sub"]:
            raise ValueError()
        if nonce is not None and not secrets.compare_digest(str(identity.get("nonce", "")), nonce):
            raise ValueError()
        if expected and expected.get("subject") and identity["sub"] != expected["subject"]:
            raise ValueError()
        return identity
    except (jwt.PyJWTError, ValueError, TypeError, KeyError, StopIteration):
        raise RunError("ChatGPT identity verification failed. Start sign-in again.") from None


class ChatGPTAuth:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / "accounts.json"
        self.pending = {}
        self.lock = threading.RLock()

    @contextmanager
    def locked(self):
        with self.lock:
            self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(self.directory, 0o700)
            fd = os.open(self.directory / ".lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "w") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                yield

    def read(self):
        if not self.path.exists():
            return {"host_id": None, "active": None, "profiles": {}}
        if self.path.is_symlink() or self.path.stat().st_mode & 0o077:
            raise RunError("ChatGPT credential file must be private to its owner.")
        try:
            return json.loads(self.path.read_text())
        except (OSError, ValueError):
            raise RunError("ChatGPT credential storage could not be read.") from None

    def status(self):
        record = self.read()
        selected = record["profiles"].get(record["active"], {})
        return {"connected": bool(selected.get("access_token")) and PLAN_SCOPE in selected.get("scopes", []),
                "active": record["active"],
                "profiles": [{"id": key, "email": p.get("email", "ChatGPT account"),
                              "sharing": PLAN_SCOPE in p.get("scopes", [])} for key, p in record["profiles"].items()],
                "pending_registration": next(iter(record.get("pending_registrations", {})), None)}

    def begin(self, redirect_uri, profile_id=None):
        parsed = urlsplit(redirect_uri)
        if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path != "/auth/callback" or not parsed.port or parsed.query or parsed.fragment:
            raise RunError("ChatGPT requires the configured loopback callback.")
        with self.locked():
            record = self.read()
            if not record["host_id"]:
                record["host_id"] = "urn:uuid:" + str(uuid.uuid4())
                atomic_private(self.path, record)
            if profile_id is not None and not isinstance(profile_id, str):
                raise RunError("Invalid ChatGPT account selection.")
            selected = (record["profiles"].get(profile_id) or record.get("pending_registrations", {}).get(profile_id)) if profile_id else None
            if profile_id is None and not record["active"] and record.get("pending_registrations"):
                selected = next(iter(record["pending_registrations"].values()))
            if profile_id and selected is None:
                raise RunError("Unknown ChatGPT account.")
            state, nonce, verifier = (secrets.token_urlsafe(48) for _ in range(3))
            self.pending = {k: v for k, v in self.pending.items() if v["expires"] > time.time()}
            if len(self.pending) >= 5:
                raise RunError("Finish an existing sign-in attempt or wait for it to expire.")
            self.pending[state] = {"nonce": nonce, "verifier": verifier, "redirect": redirect_uri,
                                   "expires": time.time() + 600, "selected": selected}
            params = {"client_id": selected["client_id"] if selected else "dynamic_agent_client",
                      "ext_agent_host_id": record["host_id"], "response_type": "code",
                      "redirect_uri": redirect_uri, "scope": SCOPES, "resource": RESOURCE,
                      "state": state, "nonce": nonce, "code_challenge_method": "S256",
                      "code_challenge": base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")}
            if not selected:
                params["agent_name_hint"] = "Wisp"
            # No token hints in URLs/logs; returning accounts can use the account selector.
            return AUTHORIZE + "?" + urlencode(params)

    def finish(self, query):
        state = query.get("state", "")
        with self.lock:
            pending = self.pending.pop(state, None)  # One-time consumption, including failed attempts.
        if not pending or pending["expires"] <= time.time():
            raise RunError("Sign-in expired or could not be verified. Start again.")
        if query.get("iss", ISSUER) != ISSUER:
            raise RunError("Unexpected sign-in issuer.")
        if query.get("error"):
            raise RunError("ChatGPT sign-in was not approved. Your existing connection is unchanged.")
        selected = pending["selected"]
        client_id = query.get("client_id") or (selected or {}).get("client_id")
        if not client_id or client_id == "dynamic_agent_client" or (selected and selected["client_id"] != client_id) or not query.get("code"):
            raise RunError("ChatGPT registration is incomplete or does not match this account.")
        # Retain an issued registration even if exchange needs to be retried.
        with self.locked():
            record = self.read()
            record.setdefault("pending_registrations", {})[client_id] = {"client_id": client_id}
            atomic_private(self.path, record)
        tokens = request_json(TOKEN, form={"grant_type": "authorization_code", "client_id": client_id,
                               "code": query["code"], "code_verifier": pending["verifier"],
                               "redirect_uri": pending["redirect"], "resource": RESOURCE})
        identity = validate_identity(tokens.get("id_token", ""), client_id, pending["nonce"], selected)
        scopes = str(tokens.get("scope", "")).split()
        if PLAN_SCOPE not in scopes or not tokens.get("access_token") or str(tokens.get("token_type", "")).lower() != "bearer":
            raise RunError("Sign-in succeeded but ChatGPT plan usage was not granted. Enable it during sign-in.")
        with self.locked():
            record = self.read()
            key = hashlib.sha256((client_id + "\0" + identity["sub"]).encode()).hexdigest()[:24]
            record["profiles"][key] = {"client_id": client_id, "issuer": ISSUER,
                "subject": identity["sub"], "email": identity.get("email", "ChatGPT account"),
                "id_token": tokens["id_token"], "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"), "scopes": scopes,
                "expires_at": time.time() + int(tokens.get("expires_in", 0))}
            record["active"] = key
            record.get("pending_registrations", {}).pop(client_id, None)
            atomic_private(self.path, record)
        return self.status()

    def access_token(self):
        with self.locked():  # Serializes rotating refresh tokens across local processes.
            record = self.read()
            profile = record["profiles"].get(record["active"])
            if not profile or PLAN_SCOPE not in profile.get("scopes", []):
                raise RunError("Connect ChatGPT and allow plan usage in Settings first.")
            if profile.get("expires_at", 0) < time.time() + 60:
                if not profile.get("refresh_token"):
                    raise RunError("ChatGPT sign-in expired. Reconnect this account in Settings.")
                tokens = request_json(TOKEN, form={"grant_type": "refresh_token", "client_id": profile["client_id"],
                                      "refresh_token": profile["refresh_token"], "resource": RESOURCE})
                scopes = str(tokens.get("scope", " ".join(profile["scopes"]))).split()
                if PLAN_SCOPE not in scopes or not tokens.get("access_token"):
                    raise RunError("ChatGPT plan usage is no longer authorized. Reconnect in Settings.")
                if tokens.get("id_token"):
                    validate_identity(tokens["id_token"], profile["client_id"], expected=profile)
                profile.update(access_token=tokens["access_token"],
                               refresh_token=tokens.get("refresh_token", profile["refresh_token"]),
                               id_token=tokens.get("id_token", profile.get("id_token")),
                               scopes=scopes, expires_at=time.time() + int(tokens.get("expires_in", 0)))
                atomic_private(self.path, record)
            return profile["access_token"]

    def models(self):
        result = request_json(RESOURCE + "/models", access_token=self.access_token())
        return [{"slug": m["slug"], "display_name": m.get("display_name", m["slug"])}
                for m in result.get("models", []) if m.get("visibility") == "list" and isinstance(m.get("slug"), str)]
