"""OpenAI Codex (ChatGPT plan) limits without an API key: reads the newest
`token_count` event with `rate_limits` in Codex's own session logs
($CODEX_HOME/sessions/**/rollout-*.jsonl, default ~/.codex/sessions).
primary = the ~5 h window, secondary = the weekly window, each with used_percent
and resets_at (or resets_in_seconds). Current Codex builds sometimes log
rate_limits: null (notably `codex exec`); then the latest known values are used,
and a window whose reset time has passed is reported as 0 %."""

import datetime as dt
import json
import os
from pathlib import Path

from .. import ProviderError, entry, iso, utcnow


def _window_name(minutes) -> str:
    try:
        m = float(minutes)
    except (TypeError, ValueError):
        return "Codex"
    if m >= 9000:
        return "Codex week"
    return f"Codex {round(m / 60)}h"


def latest_limits(root: Path, max_files: int = 30):
    files = sorted(root.glob("**/rollout-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:max_files]
    for f in files:
        try:
            lines = f.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in reversed(lines):
            if "rate_limits" not in line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            p = ev.get("payload") or {}
            if p.get("type") == "token_count" and p.get("rate_limits"):
                return p["rate_limits"], ev.get("timestamp"), f
    return None, None, None


def fetch(cfg, ctx):
    root = Path(os.path.expanduser(cfg.get("sessionsDir") or
                                   os.path.join(os.environ.get("CODEX_HOME", "~/.codex"), "sessions")))
    if not root.is_dir():
        raise ProviderError("codex: no session logs (run codex once)")
    limits, ts, f = latest_limits(root)
    if not limits:
        raise ProviderError("codex: no rate-limit data in the logs yet")
    try:
        at = dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        at = dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc)
    now = utcnow()
    out = []
    for key in ("primary", "secondary"):
        w = limits.get(key)
        if not isinstance(w, dict):
            continue
        reset = None
        if w.get("resets_at"):
            reset = dt.datetime.fromtimestamp(float(w["resets_at"]), dt.timezone.utc)
        elif w.get("resets_in_seconds") is not None:
            reset = at + dt.timedelta(seconds=float(w["resets_in_seconds"]))
        used = float(w.get("used_percent") or 0)
        if reset and reset <= now:
            used, reset = 0.0, None
        out.append(entry(_window_name(w.get("window_minutes")), used, 100, "%", iso(reset),
                         source="codex logs", observedAt=iso(at)))
    if not out:
        raise ProviderError("codex: unexpected rate_limits format")
    return out
