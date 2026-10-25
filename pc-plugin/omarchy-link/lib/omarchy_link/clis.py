"""AI tools that are already installed and signed in on this PC.

Detection only looks at whether a binary is on PATH and whether its own
sign-in file *exists* (never reads it), or asks the tool itself
(`codex login status`, ollama's local /api/tags). Results are cached briefly.
Nothing here holds or forwards a credential: the tools use their own login.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

_cache: dict = {}
_lock = threading.Lock()
TTL = 300


def _home(*parts: str) -> Path:
    return Path.home().joinpath(*parts)


def _exists(*paths) -> bool:
    return any(Path(p).exists() for p in paths)


def ollama_url() -> str:
    host = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")
    if not host.startswith("http"):
        host = "http://" + host
    return host.rstrip("/")


def ollama_models(timeout: float = 1.5) -> list[str]:
    try:
        with urllib.request.urlopen(ollama_url() + "/api/tags", timeout=timeout) as r:
            return [m.get("name", "") for m in json.loads(r.read(1 << 20)).get("models", []) if m.get("name")]
    except (OSError, ValueError):
        return []


def _check(name: str) -> dict | None:
    """-> {"bin": path, "auth": how} or None when not usable."""
    if name == "ollama":
        models = ollama_models()
        return {"bin": shutil.which("ollama") or "", "auth": "local", "models": models} if models else None
    binary = shutil.which(name)
    if not binary:
        return None
    if name == "claude":
        cfg = Path(os.environ.get("CLAUDE_CONFIG_DIR", _home(".claude")))
        ok = _exists(cfg / ".credentials.json", _home(".claude.json")) or "ANTHROPIC_API_KEY" in os.environ
        return {"bin": binary, "auth": "claude login"} if ok else None
    if name == "codex":
        try:
            r = subprocess.run([binary, "login", "status"], capture_output=True, text=True, timeout=8,
                               stdin=subprocess.DEVNULL)
            return {"bin": binary, "auth": (r.stdout or r.stderr).strip()[:60] or "codex login"} if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None
    if name == "gemini":
        g = _home(".gemini")
        ok = _exists(g / "oauth_creds.json", g / "google_accounts.json") or \
            any(k in os.environ for k in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI"))
        return {"bin": binary, "auth": "gemini login"} if ok else None
    if name == "grok":
        ok = _exists(_home(".grok", "auth.json")) or "XAI_API_KEY" in os.environ or "GROK_DEPLOYMENT_KEY" in os.environ
        return {"bin": binary, "auth": "grok login"} if ok else None
    if name == "hermes":
        ok = _exists(_home(".hermes", "auth.json"), _home(".config", "hermes", "auth.json")) or             any(k in os.environ for k in ("HERMES_API_KEY", "NOUS_API_KEY"))
        return {"bin": binary, "auth": "hermes login"} if ok else None
    if name == "grok-bot":
        ok = _exists(_home(".grok-bot", "auth.json"), _home(".config", "grok-bot", "auth.json")) or             "GROK_BOT_TOKEN" in os.environ
        return {"bin": binary, "auth": "grok-bot login"} if ok else None
    return None


def detect(name: str, fresh: bool = False) -> dict | None:
    with _lock:
        hit = _cache.get(name)
        if hit and not fresh and time.time() - hit[0] < TTL:
            return hit[1]
    res = _check(name)
    with _lock:
        _cache[name] = (time.time(), res)
    return res


def clear_cache() -> None:
    with _lock:
        _cache.clear()
