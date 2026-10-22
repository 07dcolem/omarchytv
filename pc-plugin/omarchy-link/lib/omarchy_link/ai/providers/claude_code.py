"""Claude Code subscription limits without an API key.

1. Runs `claude -p "/usage"` (a local slash command of the signed-in CLI, no model
   call) and parses the lines it prints, e.g.
       Current session: 23% used · resets Oct 9 at 2am (Europe/Rome)
       Current week (all models): 41% used · resets Oct 12 at 11pm (Europe/Rome)
   -> one "%" entry per line ("Claude session", "Claude week", "Claude week (Fable)").
2. If that yields nothing (API-key login, older CLI, format change) it falls back to
   ccusage-style accounting of the local logs (~/.claude/projects/**/*.jsonl):
   tokens used in the last 5 hours, unit "tokens", limit unknown.
"""

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .. import ProviderError, entry, iso, utcnow

LINE_RE = re.compile(r"^\s*(Current [^:]{1,60}):\s*(\d+(?:\.\d+)?)\s*%\s*used(?:\s*[·•|\-–]\s*resets?\s+(.+?))?\s*$",
                     re.I | re.M)


def _name(label: str) -> str:
    l = label.lower()
    rest = re.sub(r"^current\s+", "", label, flags=re.I)
    if l.startswith("current session"):
        return "Claude session"
    m = re.match(r"week\s*\(([^)]+)\)", rest, re.I)
    if m:
        return "Claude week" if m.group(1).lower() == "all models" else f"Claude week ({m.group(1)})"
    return "Claude " + rest


def parse_reset(text: str | None, now: dt.datetime | None = None) -> str | None:
    """'Oct 9 at 2am (Europe/Rome)' | '3:45pm (Europe/Rome)' -> ISO UTC, or None."""
    if not text:
        return None
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    m = re.match(r"^(.*?)\s*(?:\(([^)]+)\))?\s*$", text.strip())
    when, zone = m.group(1).strip(), m.group(2)
    try:
        tz = ZoneInfo(zone) if zone else dt.datetime.now().astimezone().tzinfo
    except (ZoneInfoNotFoundError, ValueError):
        tz = dt.datetime.now().astimezone().tzinfo
    now = (now or utcnow()).astimezone(tz)
    when = re.sub(r"\s+", " ", when.replace(" at ", " ")).strip().lower()
    for fmt, has_date in (("%b %d %I%p", True), ("%b %d %I:%M%p", True), ("%b %d %H:%M", True),
                          ("%I%p", False), ("%I:%M%p", False), ("%H:%M", False)):
        try:
            t = dt.datetime.strptime(("2000 " + when) if has_date else when, ("%Y " + fmt) if has_date else fmt)
        except ValueError:
            continue
        if has_date:
            cand = t.replace(year=now.year, tzinfo=tz)
            if cand < now - dt.timedelta(days=2):
                cand = cand.replace(year=now.year + 1)
        else:
            cand = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            if cand < now:
                cand += dt.timedelta(days=1)
        return iso(cand)
    return None


def parse_usage(text: str) -> list[dict]:
    out = []
    for label, pct, reset in LINE_RE.findall(text or ""):
        out.append(entry(_name(label), float(pct), 100, "%", parse_reset(reset or None),
                         source="claude /usage", resetsText=(reset or None)))
    return out


def local_tokens(root: Path, hours: float = 5) -> int:
    """Tokens in Claude Code's local logs during the last `hours` (deduplicated like ccusage)."""
    since = time.time() - hours * 3600
    seen, total = set(), 0
    for f in root.glob("projects/**/*.jsonl"):
        try:
            if f.stat().st_mtime < since:
                continue
            for line in f.open(errors="replace"):
                if '"usage"' not in line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                ts = ev.get("timestamp", "")
                try:
                    t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    continue
                msg = ev.get("message") or {}
                u = msg.get("usage") or {}
                key = (msg.get("id"), ev.get("requestId"))
                if t < since or not u or (key != (None, None) and key in seen):
                    continue
                seen.add(key)
                total += sum(int(u.get(k) or 0) for k in ("input_tokens", "output_tokens",
                                                          "cache_creation_input_tokens", "cache_read_input_tokens"))
        except OSError:
            continue
    return total


def fetch(cfg, ctx):
    binary = shutil.which(cfg.get("bin", "claude"))
    entries = []
    if binary and cfg.get("usageCommand", True):
        with tempfile.TemporaryDirectory(prefix="omarchy-link-usage-") as cwd:
            try:
                r = subprocess.run([binary, "-p", "/usage"], cwd=cwd, capture_output=True, text=True,
                                   timeout=float(cfg.get("timeout", 45)), stdin=subprocess.DEVNULL,
                                   env={**os.environ, "NO_COLOR": "1"})
                entries = parse_usage(r.stdout)
            except (OSError, subprocess.SubprocessError):
                entries = []
    if entries:
        return entries
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    if root.is_dir():
        hours = float(cfg.get("windowHours", 5))
        return [entry(cfg.get("name", "Claude Code 5h"), local_tokens(root, hours), cfg.get("tokenLimit"),
                      "tokens", None, source="local logs")]
    raise ProviderError("claude: no /usage output and no local logs")
