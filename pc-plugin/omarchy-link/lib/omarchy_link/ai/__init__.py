"""AI credits collector. Runs on the PC only; API keys never leave it.

Each provider is one module in ai/providers/ exposing
    fetch(cfg: dict, ctx: Context) -> list[dict]
that returns entries {"name","used","limit","unit","resetsAt","updatedAt"}
(see docs/AI-CREDITS.md). The TV only ever receives those numbers.
"""

from __future__ import annotations

import datetime as dt
import importlib
import json
import os
import re
import shlex
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from .. import config

PROVIDER_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
UNITS = {"$", "tokens", "%", "credits"}


class ProviderError(Exception):
    pass


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(t: dt.datetime | None) -> str | None:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if t else None


def month_window(now: dt.datetime | None = None) -> tuple[dt.datetime, dt.datetime]:
    now = now or utcnow()
    start = now.replace(day=1, hour=0, minute=0, second=0)
    nxt = (start + dt.timedelta(days=32)).replace(day=1)
    return start, nxt


class Context:
    def __init__(self, ai_file_private: bool, timeout: float = 15.0):
        self.ai_file_private = ai_file_private
        self.timeout = timeout

    def secret(self, ref: str | None, what: str) -> str:
        """env:NAME | file:PATH (0600) | cmd:ARGV | literal (only if ai.json is 0600)."""
        if not ref:
            raise ProviderError(f"{what}: no key configured")
        ref = str(ref)
        if ref.startswith("env:"):
            val = os.environ.get(ref[4:], "")
        elif ref.startswith("file:"):
            path = Path(os.path.expanduser(ref[5:]))
            if not path.is_file():
                raise ProviderError(f"{what}: key file {path} not found")
            if not config.is_private_file(path):
                raise ProviderError(f"{what}: key file {path} must be chmod 600")
            val = path.read_text().strip()
        elif ref.startswith("cmd:"):
            argv = [os.path.expanduser(a) for a in shlex.split(ref[4:])]
            try:
                val = subprocess.run(argv, capture_output=True, text=True, timeout=20, check=True).stdout.strip()
            except (OSError, subprocess.SubprocessError) as e:
                raise ProviderError(f"{what}: key command failed: {e}") from e
        else:
            if not self.ai_file_private:
                raise ProviderError(f"{what}: inline keys need ai.json to be chmod 600 (or use env:/file:/cmd:)")
            val = ref
        if not val:
            raise ProviderError(f"{what}: key is empty")
        return val.splitlines()[0]

    def http_json(self, method: str, url: str, headers: dict, body: dict | None = None) -> dict:
        if not url.startswith("https://") and not url.startswith("http://127.0.0.1"):
            raise ProviderError("provider URLs must be https")
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "User-Agent": "omarchy-link/0.1", "Accept": "application/json",
            **({"Content-Type": "application/json"} if data else {}), **headers})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read(4 << 20) or b"{}")
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = json.loads(e.read(65536)).get("error", "")
                detail = detail.get("message", "") if isinstance(detail, dict) else str(detail)
            except (ValueError, AttributeError, OSError):
                pass
            raise ProviderError(f"HTTP {e.code} {detail}".strip()) from e
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise ProviderError(str(e)) from e


def entry(name: str, used, limit, unit: str, resets_at: str | None = None, **extra) -> dict:
    e = {
        "name": str(name)[:48],
        "used": None if used is None else round(float(used), 4),
        "limit": None if limit is None else round(float(limit), 4),
        "unit": unit,
        "resetsAt": resets_at,
        "updatedAt": iso(utcnow()),
    }
    e.update({k: v for k, v in extra.items() if v is not None})
    return e


def load_provider(kind: str):
    if not PROVIDER_RE.match(kind or ""):
        raise ProviderError(f"bad provider type {kind!r}")
    try:
        return importlib.import_module(f"{__name__}.providers.{kind}")
    except ImportError as e:
        raise ProviderError(f"unknown provider type {kind!r}") from e


def payload(ai_file: Path | None = None) -> dict:
    """What PUT /v1/ai carries: the entries plus the mirror sources the TV can switch."""
    from . import sources
    data = collect(None, ai_file)
    data["aiSources"] = sources.listing(ai_file)
    return data


def collect(ai_cfg: dict | None = None, ai_file: Path | None = None) -> dict:
    """Runs every configured provider. A failing provider yields an error entry, never a crash."""
    ai_file = ai_file or config.AI_FILE
    if ai_cfg is None:
        ai_cfg = config.read_json(ai_file, {"providers": []})
    private = ai_file.exists() and config.is_private_file(ai_file)
    ctx = Context(ai_file_private=private)
    out = []
    providers = [p for p in ai_cfg.get("providers", []) if isinstance(p, dict)]
    mirroring = any(p.get("type") == "mirror" for p in providers)
    if not providers and ai_cfg.get("mirror", True):
        # Preferred: mirror the AI-usage widget already in the Omarchy bar (built-in Agents panel first).
        from .. import widgets
        preset = widgets.default_preset()
        if preset:
            providers, mirroring = [{"type": "mirror", "preset": preset, "auto": True}], True
    # Mirroring shows exactly what the bar shows: no extra collectors unless asked for.
    if ai_cfg.get("autoDetect", not mirroring):
        from .. import clis
        have = {p.get("type") for p in providers}
        for kind, tool in (("claude_code", "claude"), ("codex", "codex")):
            if kind not in have and kind not in ai_cfg.get("disabled", []) and clis.detect(tool):
                providers.append({"type": kind, "auto": True})
    for p in providers[:16]:
        if not isinstance(p, dict) or p.get("enabled") is False:
            continue
        name = p.get("name") or p.get("preset") or p.get("type", "?")
        try:
            mod = load_provider(p.get("type", ""))
            for e in mod.fetch(p, ctx):
                if e.get("unit") not in UNITS and not str(e.get("unit", "")).isupper():
                    raise ProviderError(f"bad unit {e.get('unit')!r}")
                e.setdefault("provider", p.get("type"))
                e.setdefault("status", "ok")
                out.append(e)
        except ProviderError as err:
            out.append(entry(name, None, None, p.get("unit", "$"), provider=p.get("type"),
                             status="error", error=str(err)[:120]))
    return {"ai": out}
