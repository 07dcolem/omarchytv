"""Finds the AI-usage bar widgets installed on this Omarchy PC, so the TV can mirror
exactly what the bar shows instead of computing its own numbers.

Looks at ~/.config/omarchy/plugins/*/manifest.json (third-party plugins), the
built-in Agents panel's records, and ~/.config/omarchy/shell.json (is the widget
actually placed in the bar?). Reads manifests and settings only.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

# plugin id -> mirror preset (see ai/providers/mirror.py)
KNOWN = {
    "io.github.baranskyi.omacash": "omacash",
    "omarchy.agents": "omarchy-agents",
    "robzolkos.agent-usage": "agent-usage",
    "mryll.claudebar": "claudebar",
    "akitaonrails.ai-usagebar": "ai-usagebar",
    "digitalpals.model-usage": "model-usage",
}
PREFERENCE = ["omarchy-agents", "omacash", "agent-usage", "claudebar", "ai-usagebar", "model-usage"]
AI_WORDS = re.compile(r"\b(ai|llm|claude|codex|gpt|openai|anthropic|grok|gemini|openrouter|agents?|models?|copilot|kimi)\b", re.I)
USAGE_WORDS = re.compile(r"\b(usage|quota|credits?|balances?|billing|spend|limits?|tokens?|cost)\b", re.I)


def config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")


def state_home() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")


def plugins_dir() -> Path:
    return config_home() / "omarchy" / "plugins"


def read_json(path: Path, limit: int = 1 << 20):
    """Bounded read of a regular file owned by us; never follows a symlink at the leaf."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    except OSError:
        return None
    try:
        st = os.fstat(fd)
        import stat as _s
        if not _s.S_ISREG(st.st_mode) or st.st_uid != os.geteuid() or st.st_size > limit:
            return None
        with os.fdopen(fd, "rb", closefd=False) as f:
            data = f.read(limit + 1)
        return json.loads(data.decode("utf-8")) if len(data) <= limit else None
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    finally:
        os.close(fd)


def bar_entries() -> dict:
    """Widget entries placed in the bar (shell.json), by plugin id, with their inline settings."""
    out = {}
    shell = read_json(config_home() / "omarchy" / "shell.json")

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("id"), str):
                out.setdefault(o["id"], o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(shell or {})
    return out


def find_plugin(plugin_id: str) -> Path | None:
    base = plugins_dir()
    direct = base / plugin_id
    if (direct / "manifest.json").is_file():
        return direct
    if base.is_dir():
        for d in sorted(base.iterdir()):
            m = read_json(d / "manifest.json", 256 << 10)
            if isinstance(m, dict) and m.get("id") == plugin_id:
                return d
    return None


def agents_usage_dir() -> Path:
    return state_home() / "omarchy" / "agents" / "usage"


def candidates() -> list[dict]:
    """[{id, name, preset|None, inBar, path, why}] best first."""
    bar = bar_entries()
    out = []
    base = plugins_dir()
    if base.is_dir():
        for d in sorted(base.iterdir()):
            m = read_json(d / "manifest.json", 256 << 10)
            if not isinstance(m, dict) or not isinstance(m.get("id"), str):
                continue
            pid = m["id"]
            bw = m.get("barWidget") or {}
            text = " ".join(str(x) for x in (pid, m.get("name"), m.get("description"), bw.get("displayName"),
                                             bw.get("description"), bw.get("category")))
            preset = KNOWN.get(pid)
            looks = bool(AI_WORDS.search(text) and USAGE_WORDS.search(text))
            if not preset and not looks:
                continue
            out.append({"id": pid, "name": str(m.get("name") or pid)[:48], "preset": preset, "inBar": pid in bar,
                        "path": str(d), "version": m.get("version"),
                        "why": "known widget" if preset else "looks like an AI usage widget (generic mirror needed)"})
    usage = agents_usage_dir()
    records = sorted(usage.glob("*.json")) if usage.is_dir() else []
    if records:
        out.append({"id": "omarchy.agents", "name": "Agents (built into Omarchy)", "preset": "omarchy-agents",
                    "inBar": "omarchy.agents" in bar, "path": str(usage), "version": None,
                    "why": f"{len(records)} usage record(s): " + ", ".join(r.stem for r in records[:6])})

    def rank(c):
        return (0 if c["preset"] else 1, 0 if c["preset"] == PREFERENCE[0] else 1, 0 if c["inBar"] else 1,
                PREFERENCE.index(c["preset"]) if c["preset"] in PREFERENCE else 99)
    return sorted(out, key=rank)


def default_preset() -> str | None:
    """The built-in Agents panel when it has records; else the best known widget in the bar;
    else the best known widget installed. `ai setup --use` overrides this."""
    known = [c for c in candidates() if c["preset"]]
    for c in known:
        if c["preset"] == "omarchy-agents":
            return c["preset"]
    for c in known:
        if c["inBar"]:
            return c["preset"]
    return known[0]["preset"] if known else None
