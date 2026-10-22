"""Mirror sources: which bar widgets feed the TV's AI pane. Toggled with `omarchy-link ai sources`,
`ai setup --use`, or remotely from the TV ("ai_sources" event). Only known presets can be toggled;
the TV can never add commands, files or keys."""
from __future__ import annotations

import shutil
from pathlib import Path

from .. import config, widgets
from .providers import mirror

NAMES = {"omarchy-agents": "Omarchy Agents panel", "omacash": "Omacash", "agent-usage": "Agent usage (weekly)",
         "claudebar": "claudebar", "ai-usagebar": "ai-usagebar", "model-usage": "Model usage"}
MAX_SOURCES = 8


class SourceError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _file(ai_file: Path | None) -> Path:
    return ai_file or config.AI_FILE


def _providers(cfg: dict) -> list[dict]:
    return [p for p in cfg.get("providers", []) if isinstance(p, dict)]


def enabled(ai_file: Path | None = None) -> list[str]:
    """Presets the next collect() will mirror, in order."""
    cfg = config.read_json(_file(ai_file), {})
    provs = _providers(cfg)
    if not provs:
        d = widgets.default_preset() if cfg.get("mirror", True) else None
        return [d] if d else []
    return [p["preset"] for p in provs if p.get("type") == "mirror" and p.get("preset") in mirror.PRESETS
            and p.get("enabled") is not False]


def listing(ai_file: Path | None = None) -> list[dict]:
    """[{id, name, enabled, available, inBar}]: every detected known widget plus any configured one."""
    on = enabled(ai_file)
    seen, out = set(), []
    for c in widgets.candidates():
        p = c["preset"]
        if p and p not in seen:
            seen.add(p)
            out.append({"id": p, "name": NAMES.get(p, c["name"]), "enabled": p in on, "available": True,
                        "inBar": bool(c["inBar"])})
    for p in on:
        if p not in seen:
            seen.add(p)
            out.append({"id": p, "name": NAMES.get(p, p), "enabled": True, "available": False, "inBar": False})
    out.sort(key=lambda s: (not s["enabled"], on.index(s["id"]) if s["id"] in on else 99))
    return out[:MAX_SOURCES * 2]


def set_enabled(ids: list[str], ai_file: Path | None = None, require_available: bool = False) -> list[str]:
    """Make exactly `ids` (in order) the enabled mirror presets. Options already in ai.json for a
    preset (include, max, ...) are kept; non-preset providers (manual, generic, API) are untouched."""
    if not isinstance(ids, list) or len(ids) > MAX_SOURCES or not all(isinstance(i, str) for i in ids):
        raise SourceError("bad_request", f"expected a list of at most {MAX_SOURCES} source ids")
    ids = list(dict.fromkeys(i.strip() for i in ids if i.strip()))
    unknown = [i for i in ids if i not in mirror.PRESETS]
    if unknown:
        raise SourceError("unknown_source", "unknown source: " + ", ".join(unknown)[:120])
    if require_available:
        avail = {c["preset"] for c in widgets.candidates() if c["preset"]} | set(enabled(ai_file))
        missing = [i for i in ids if i not in avail]
        if missing:
            raise SourceError("not_installed", "not found on this PC: " + ", ".join(missing)[:120])
    f = _file(ai_file)
    cfg = config.read_json(f, {})
    provs = _providers(cfg)
    presets = {p["preset"]: p for p in provs if p.get("type") == "mirror" and p.get("preset") in mirror.PRESETS}
    others = [p for p in provs if not (p.get("type") == "mirror" and p.get("preset") in mirror.PRESETS)]
    new = []
    for i in ids:
        p = {k: v for k, v in presets.pop(i, {"type": "mirror", "preset": i}).items() if k != "enabled"}
        new.append(p)
    new += [{**p, "enabled": False} for p in presets.values()]  # keep their options, switched off
    out = {**cfg, "providers": new + others}
    if not provs:
        out["autoDetect"] = False
    if out != cfg:
        if f.exists():
            shutil.copy2(f, f.with_suffix(".json.bak"))
        config.write_json_private(f, out)
    return ids
