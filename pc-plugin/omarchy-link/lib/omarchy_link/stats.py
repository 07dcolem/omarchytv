"""v2.9 home widgets: "omarchy · pc" (CPU, RAM, now playing), "deploys · pc" (opt-in) and screensaver.txt.

Cheap reads only: /proc/stat delta, /proc/meminfo, `playerctl metadata` (if installed). Deploys only when the
user configured a source in config.json:
  "deploys": {"command": ["my-deploys", "--json"]}   # argv, no shell; prints [{"name","status"}]
  "deploys": {"file": "~/.cache/deploys.json"}       # same JSON
status: green|yellow|red (or ok|building|failed). Nothing configured = no deploys widget on the TV.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from . import config

SCREENSAVER = config.HOME / ".config/omarchy/branding/screensaver.txt"
_last_cpu: tuple[int, int] | None = None


def cpu_percent() -> int | None:
    global _last_cpu
    try:
        f = [int(x) for x in Path("/proc/stat").read_text().split("\n", 1)[0].split()[1:]]
    except (OSError, ValueError):
        return None
    idle, total = f[3] + (f[4] if len(f) > 4 else 0), sum(f)
    prev, _last_cpu = _last_cpu, (idle, total)
    if not prev or total == prev[1]:
        return None
    return max(0, min(100, round(100 * (1 - (idle - prev[0]) / (total - prev[1])))))


def ram_percent() -> int | None:
    try:
        m = {l.split(":")[0]: int(l.split()[1]) for l in Path("/proc/meminfo").read_text().splitlines() if ":" in l}
        return max(0, min(100, round(100 * (1 - m["MemAvailable"] / m["MemTotal"]))))
    except (OSError, KeyError, ValueError, ZeroDivisionError, IndexError):
        return None


def now_playing() -> dict | None:
    if not shutil.which("playerctl"):
        return None
    try:
        r = subprocess.run(["playerctl", "metadata", "--format", "{{status}}\t{{artist}}\t{{title}}"],
                           capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return None
    parts = r.stdout.strip().split("\t")
    if r.returncode != 0 or len(parts) < 3 or parts[0] != "Playing" or not parts[2]:
        return None
    return {"artist": parts[1][:64], "title": parts[2][:96]}


def deploys(cfg: dict) -> list | None:
    src = cfg.get("deploys")
    if not isinstance(src, dict):
        return None
    try:
        if isinstance(src.get("command"), list) and src["command"]:
            r = subprocess.run([str(x) for x in src["command"]], capture_output=True, text=True, timeout=10)
            data = json.loads(r.stdout or "[]")
        elif src.get("file"):
            data = json.loads(Path(os.path.expanduser(str(src["file"]))).read_text())
        else:
            return None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    out = []
    for d in data if isinstance(data, list) else []:
        st = str(d.get("status", "")).lower() if isinstance(d, dict) else ""
        if st in ("green", "yellow", "red", "ok", "building", "failed"):
            out.append({"name": str(d.get("name", ""))[:24], "status": st})
    return out[:8]


def payload(cfg: dict) -> dict:
    p: dict = {}
    c, r = cpu_percent(), ram_percent()
    if c is not None:
        p["cpu"] = c
    if r is not None:
        p["ram"] = r
    np = now_playing()
    if np:
        p["nowPlaying"] = np
    d = deploys(cfg)
    if d is not None:
        p["deploys"] = d
    return p


def screensaver_text() -> tuple[str, float]:
    """(text, mtime) of ~/.config/omarchy/branding/screensaver.txt; ("", 0) when missing."""
    try:
        return SCREENSAVER.read_text(errors="replace")[:16384], SCREENSAVER.stat().st_mtime
    except OSError:
        return "", 0.0
