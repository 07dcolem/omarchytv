"""Mirror: show on the TV exactly the numbers an existing PC source already shows,
without computing anything. The preferred credits mode.

Presets for Omarchy bar widgets (see docs/AI-CREDITS.md):
  omacash         Omacash (io.github.baranskyi.omacash): `python3 <plugin>/bin/omacash status`,
                  the same no-network snapshot its popup parses; snapshot.json as fallback
  omarchy-agents  Omarchy's built-in Agents panel: ~/.local/state/omarchy/agents/usage/*.json
  agent-usage     robzolkos.agent-usage: the same records, weekly windows only (what its pill shows)
  claudebar       mryll.claudebar: `claudebar --json`
  ai-usagebar     akitaonrails.ai-usagebar: `ai-usagebar usage --json`
  model-usage     digitalpals.model-usage: its scripts/usage-fetch.py (this one makes the
                  same read-only quota calls the widget makes)

Generic (any widget, Waybar module, script or file):
  {"type":"mirror", "name":"My widget",
   "source": {"command": ["~/bin/usage", "--json"]} | {"file": "~/.cache/x/usage.json"},
   "format": "json" | "text" | "waybar",
   "items": "$.providers[*]",                       # JSON: where the rows are (default: the document)
   "fields": {"name": "$.name", "used": "$.used", "limit": "$.limit", "unit": "=%",
              "resetsAt": "$.resets_at", "remaining": "$.remaining"},   # "=literal" for constants
   "scale": {"used": 100},                          # multiply (e.g. 0..1 fractions -> %)
   "regex": "(?P<name>\\w+) (?P<used>[\\d.]+)%"}    # text: one entry per match

Common options: "include": ["Claude", "openrouter", ...] keeps only these rows, in this order
(matched on id or name; the TV list is exactly what you assign), "max": 16.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .. import ProviderError, entry, iso
from ... import widgets

OMACASH_ID = "io.github.baranskyi.omacash"


# ---------------------------------------------------------------- helpers
def _num(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        m = re.search(r"-?\d+(?:[.,]\d+)?", str(v))
        if not m:
            return None
        f = float(m.group(0).replace(",", "."))
    return f if f == f and abs(f) != float("inf") else None


def _time(v) -> str | None:
    """ISO string, unix seconds or ms -> ISO UTC (Z)."""
    if v in (None, "", 0):
        return None
    try:
        if isinstance(v, (int, float)) or str(v).strip().isdigit():
            t = float(v)
            t = t / 1000 if t > 1e12 else t
            return iso(dt.datetime.fromtimestamp(t, dt.timezone.utc))
        t = dt.datetime.fromisoformat(str(v).strip().replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=dt.timezone.utc)
        return iso(t)
    except (ValueError, OverflowError, OSError):
        return None


def _past(ts: str | None) -> bool:
    if not ts:
        return False
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")) <= dt.datetime.now(dt.timezone.utc)


def _run(argv: list[str], timeout: float, ok_codes=(0,), env_extra=None) -> str:
    argv = [os.path.expanduser(str(a)) for a in argv]
    if not argv or not (os.path.isabs(argv[0]) or shutil.which(argv[0])):
        raise ProviderError(f"mirror: {argv[0] if argv else '?'} not found")
    with tempfile.TemporaryDirectory(prefix="omarchy-link-mirror-") as cwd:
        try:
            r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL, env={**os.environ, "NO_COLOR": "1", **(env_extra or {})})
        except subprocess.TimeoutExpired as e:
            raise ProviderError(f"mirror: {Path(argv[0]).name} timed out") from e
        except OSError as e:
            raise ProviderError(f"mirror: {e}") from e
    if r.returncode not in ok_codes and not r.stdout.strip():
        raise ProviderError(f"mirror: {Path(argv[0]).name} exited {r.returncode}: {(r.stderr.strip().splitlines() or [''])[-1][:120]}")
    if len(r.stdout) > 4 << 20:
        raise ProviderError("mirror: output too large")
    return r.stdout


def _json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except ValueError:
        i = text.find("{")
        try:
            return json.loads(text[i:]) if i >= 0 else None
        except ValueError:
            return None


def jpath(doc, path: str):
    """Tiny JSONPath: $, .key, ['key'], [n], [*]. Returns a list of matches."""
    if path in (None, "", "$"):
        return [doc]
    if not path.startswith("$"):
        path = "$." + path
    tokens = re.findall(r"\.([A-Za-z_][\w-]*)|\[(\d+|\*)\]|\['([^']*)'\]|\[\"([^\"]*)\"\]", path[1:])
    cur = [doc]
    for key, idx, q1, q2 in tokens:
        nxt = []
        for c in cur:
            k = key or q1 or q2
            if k:
                if isinstance(c, dict) and k in c:
                    nxt.append(c[k])
            elif idx == "*":
                nxt.extend(c if isinstance(c, list) else list(c.values()) if isinstance(c, dict) else [])
            elif isinstance(c, list) and int(idx) < len(c):
                nxt.append(c[int(idx)])
        cur = nxt
    return cur


def _field(item, spec):
    if spec is None:
        return None
    if isinstance(spec, str) and spec.startswith("="):
        return spec[1:]
    if isinstance(spec, str) and spec.startswith("$"):
        got = jpath(item, spec)
        return got[0] if got else None
    if isinstance(item, dict) and isinstance(spec, str):
        return item.get(spec)
    return spec


def _unit(cur) -> str:
    c = str(cur or "").strip()
    if c.upper() in ("USD", "$"):
        return "$"
    if c.lower() in ("credits", "credit", "cr"):
        return "credits"
    if c in ("%", "tokens"):
        return c
    return c.upper() if re.fullmatch(r"[A-Za-z]{3}", c) else "$"


def _select(entries: list[dict], include) -> list[dict]:
    if not include:
        return entries
    out = []
    for want in include:
        w = str(want).lower()
        for e in entries:
            if e in out:
                continue
            if w in (str(e.get("id", "")).lower(), str(e.get("name", "")).lower(), str(e.get("group", "")).lower()):
                out.append(e)
    return out


# ---------------------------------------------------------------- presets
def omacash(cfg, ctx) -> list[dict]:
    plugin = Path(os.path.expanduser(cfg["pluginDir"])) if cfg.get("pluginDir") else widgets.find_plugin(OMACASH_ID)
    snap = None
    if plugin and (plugin / "bin" / "omacash").is_file():
        # Exactly what Omacash's popup runs on open: prints the last snapshot, no network.
        out = _run(["python3", str(plugin / "bin" / "omacash"), "status"], float(cfg.get("timeout", 20)), ok_codes=(0, 2))
        snap = _json(out)
    if not isinstance(snap, dict) or not snap.get("providers"):
        snap = widgets.read_json(widgets.state_home() / "omarchy" / OMACASH_ID / "snapshot.json") or snap
    if not isinstance(snap, dict) or snap.get("schemaVersion") != 1:
        raise ProviderError("omacash: no snapshot yet (is the Omacash widget installed and configured?)")
    if not snap.get("generatedAt") and not snap.get("providers"):
        raise ProviderError("omacash: no data yet; Omacash has not synced")
    out = []
    if cfg.get("total"):
        total = _num(snap.get("totalRemainingUsd"))
        out.append(entry("AI total", None, None, "$", None, id="total", remaining=total,
                         estimated=bool(snap.get("anyEstimated")), source="omacash"))
    for p in snap.get("providers", [])[:8]:
        if not isinstance(p, dict):
            continue
        status = p.get("status")
        if status == "unconfigured" and not cfg.get("showUnconfigured"):
            continue
        bal = p.get("balance") if isinstance(p.get("balance"), dict) else None
        err = p.get("error") if isinstance(p.get("error"), dict) else None
        extra = {"id": p.get("id"), "source": "omacash", "detail": p.get("detail"), "severity": p.get("severity"),
                 "percentRemaining": p.get("percentRemaining"), "stale": bool(p.get("stale")) or None,
                 "estimated": bool(bal and bal.get("estimated")) or None,
                 "status": "error" if (status == "error" and not bal) else ("manual" if status == "unconfigured" else "ok"),
                 "error": (err or {}).get("message") or p.get("hint")}
        if bal:
            funded = _num(bal.get("funded"))
            out.append(entry(p.get("name") or p.get("id"), _num(bal.get("spent")), funded if funded else None,
                             _unit(bal.get("currency")), _time(p.get("resetsAt")),
                             remaining=_num(bal.get("remaining")), **extra))
        else:
            out.append(entry(p.get("name") or p.get("id"), None, None, "$", _time(p.get("resetsAt")), **extra))
        out[-1]["updatedAt"] = _time(p.get("fetchedAt")) or _time(snap.get("generatedAt")) or out[-1]["updatedAt"]
    return out


def _agents_records(cfg) -> list[dict]:
    d = Path(os.path.expanduser(cfg["dir"])) if cfg.get("dir") else widgets.agents_usage_dir()
    if not d.is_dir():
        raise ProviderError("omarchy agents: no usage records (is the Agents panel on?)")
    settings = widgets.bar_entries().get("omarchy.agents", {})
    disabled = {k for k, v in (settings.get("providers") or {}).items() if isinstance(v, dict) and v.get("enabled") is False}
    order = widgets.read_json(d.parent / "order.json") or []
    recs = []
    for f in sorted(d.glob("*.json")):
        r = widgets.read_json(f)
        if isinstance(r, dict) and f.stem not in disabled:
            r.setdefault("id", f.stem)
            recs.append(r)
    order = [o for o in order if isinstance(o, str)] if isinstance(order, list) else []
    recs.sort(key=lambda r: order.index(r["id"]) if r["id"] in order else len(order))
    return recs


def _short(label: str) -> str:
    return re.sub(r"\s*\((\d+)-(hour|day)\)", "", str(label or "")).strip() or "Limit"


def omarchy_agents(cfg, ctx, weekly_only: bool = False) -> list[dict]:
    out = []
    for r in _agents_records(cfg):
        name = str(r.get("name") or r["id"])
        first = len(out)
        groups = [(None, r.get("limits") or [], r.get("limitsStale"))]
        if cfg.get("accounts") == "all" and isinstance(r.get("accounts"), list) and len(r["accounts"]) > 1:
            groups = [(a.get("label"), a.get("limits") or [], a.get("stale")) for a in r["accounts"] if isinstance(a, dict)]
        for acct, limits, stale in groups:
            for lim in limits:
                if not isinstance(lim, dict) or _num(lim.get("percent")) is None or _num(lim.get("percent")) < 0:
                    continue
                if weekly_only and "week" not in str(lim.get("label", "")).lower():
                    continue
                reset = _time(lim.get("resetsAt"))
                # same as the panel: a window past its reset reads 0 %, shown rounded to whole percent
                used = 0 if _past(reset) else round(_num(lim["percent"]) * 100)
                title = f"{name}{' · ' + acct if acct else ''} {_short(lim.get('label'))}"
                out.append(entry(title, used, 100, "%", None if _past(reset) else reset, id=r["id"], group=name,
                                 source="omarchy agents", plan=r.get("tierLabel") or None, stale=bool(stale) or None))
        bal = r.get("balance") if isinstance(r.get("balance"), dict) else None
        if bal and not weekly_only:
            funded = _num(bal.get("funded"))
            out.append(entry(f"{name} balance", _num(bal.get("spent")), funded or None, _unit(bal.get("currency")),
                             None, id=r["id"], group=name, remaining=_num(bal.get("remaining")),
                             estimated=bool(bal.get("estimated")) or None, source="omarchy agents"))
        if not r.get("limits") and not bal and r.get("usageStatusText"):
            out.append(entry(name, None, None, "%", None, id=r["id"], group=name, status="error",
                             error=str(r.get("usageStatusText"))[:120], source="omarchy agents"))
        when = _time(r.get("limitsFetchedAt")) or _time(r.get("updatedAt"))
        for e in out[first:]:
            e["updatedAt"] = when or e["updatedAt"]
    return out


def claudebar(cfg, ctx) -> list[dict]:
    doc = _json(_run([cfg.get("bin", "claudebar"), "--json"], float(cfg.get("timeout", 30))))
    if not isinstance(doc, dict):
        raise ProviderError("claudebar: no JSON")
    if doc.get("error"):
        raise ProviderError("claudebar: " + str((doc["error"] or {}).get("message", "error"))[:120])
    prefix = cfg.get("prefix", "Claude")
    out = []
    for w in doc.get("windows") or []:
        if not isinstance(w, dict) or _num(w.get("used_pct")) is None:
            continue
        label = " ".join(x for x in (w.get("group") if w.get("group") not in (None, "", w.get("label")) else "", w.get("label")) if x)
        out.append(entry(f"{prefix} {label}".strip(), _num(w["used_pct"]), 100, "%",
                         _time(w.get("reset_at_unix") or w.get("reset_at")), id=w.get("id"), source="claudebar",
                         stale=bool(doc.get("stale")) or None))
    ex = doc.get("extra_usage") if isinstance(doc.get("extra_usage"), dict) else None
    if ex and ex.get("used_credit_cents") is not None:
        lim = ex.get("funded_credit_cents") if ex.get("funded_credit_cents") is not None else ex.get("monthly_limit_cents")
        out.append(entry(f"{prefix} extra usage", _num(ex["used_credit_cents"]) / 100, (_num(lim) or 0) / 100 or None, "$",
                         None, id="extra_usage", source="claudebar",
                         remaining=(_num(ex.get("available_credit_cents")) / 100) if ex.get("available_credit_cents") is not None else None))
    return out


def ai_usagebar(cfg, ctx) -> list[dict]:
    doc = _json(_run([cfg.get("bin", "ai-usagebar"), "usage", "--json"], float(cfg.get("timeout", 60))))
    if not isinstance(doc, dict) or not isinstance(doc.get("entries"), list):
        raise ProviderError("ai-usagebar: unsupported report")
    out = []
    for e in doc["entries"][:64]:
        if not isinstance(e, dict):
            continue
        name = str(e.get("display_name") or e.get("name") or e.get("id"))
        if e.get("error"):
            out.append(entry(name, None, None, "%", None, id=e.get("id"), status="error", error=str(e["error"])[:120],
                             source="ai-usagebar"))
            continue
        for s in e.get("sections") or []:
            if not isinstance(s, dict) or s.get("type") != "metric" or _num(s.get("percent")) is None:
                continue
            out.append(entry(f"{name} {s.get('label', '')}".strip(), _num(s["percent"]), 100, "%", _time(s.get("reset_at")),
                             id=e.get("id"), group=name, detail=s.get("value") or s.get("detail") or None,
                             stale=bool(e.get("stale")) or None, source="ai-usagebar"))
    return out


def model_usage(cfg, ctx) -> list[dict]:
    plugin = Path(os.path.expanduser(cfg["pluginDir"])) if cfg.get("pluginDir") else widgets.find_plugin("digitalpals.model-usage")
    if not plugin or not (plugin / "scripts" / "usage-fetch.py").is_file():
        raise ProviderError("model-usage: plugin not found")
    settings = widgets.bar_entries().get("digitalpals.model-usage", {})
    provs = settings.get("enabledProviders") or ["claude", "codex", "kimi"]
    with tempfile.TemporaryDirectory(prefix="omarchy-link-mu-") as state:  # never touch its history
        doc = _json(_run(["python3", str(plugin / "scripts" / "usage-fetch.py"), "--providers", ",".join(provs),
                          "--state-dir", state], float(cfg.get("timeout", 60)), ok_codes=(0, 1, 2)))
    if not isinstance(doc, dict) or doc.get("schemaVersion") != 1:
        raise ProviderError("model-usage: unsupported output")
    out = []
    for p in doc.get("providers") or []:
        name = str(p.get("name") or p.get("id"))
        if p.get("status") != "ok":
            out.append(entry(name, None, None, "%", None, id=p.get("id"), status="error",
                             error=str(p.get("message") or p.get("errorKind"))[:120], source="model-usage"))
            continue
        for w in p.get("windows") or []:
            out.append(entry(f"{name} {w.get('label', '')}".strip(), _num(w.get("used")), 100, "%", _time(w.get("resetsAt")),
                             id=p.get("id"), group=name, source="model-usage"))
        c = p.get("credits") if isinstance(p.get("credits"), dict) else None
        if c and c.get("used") is not None:
            out.append(entry(f"{name} {c.get('label') or 'credits'}", _num(c["used"]), _num(c.get("limit")),
                             _unit(c.get("currency")), None, id=p.get("id"), remaining=_num(c.get("remaining")),
                             source="model-usage"))
    return out


PRESETS = {
    "omacash": omacash,
    "omarchy-agents": omarchy_agents,
    "agent-usage": lambda cfg, ctx: omarchy_agents(cfg, ctx, weekly_only=True),
    "claudebar": claudebar,
    "ai-usagebar": ai_usagebar,
    "model-usage": model_usage,
}


# ---------------------------------------------------------------- generic
def generic(cfg, ctx) -> list[dict]:
    src = cfg.get("source") or {}
    timeout = float(cfg.get("timeout", 30))
    if src.get("command"):
        if not isinstance(src["command"], list):
            raise ProviderError("mirror: source.command must be an argv list (no shell)")
        text = _run(src["command"], timeout)
    elif src.get("file"):
        p = Path(os.path.expanduser(src["file"]))
        try:
            if p.stat().st_size > 4 << 20:
                raise ProviderError("mirror: file too large")
            text = p.read_text(errors="replace")
        except OSError as e:
            raise ProviderError(f"mirror: cannot read {p}") from e
    else:
        raise ProviderError("mirror: set a preset, source.command or source.file")
    fmt = cfg.get("format", "json")
    name = cfg.get("name", "Mirror")
    if fmt == "text":
        rx = re.compile(cfg.get("regex") or r"(?P<used>\d+(?:\.\d+)?)\s*%")
        rows = [m.groupdict() for m in rx.finditer(text)]
        return [entry(r.get("name") or name, _num(r.get("used")), _num(r.get("limit")) if r.get("limit") else
                      (100 if (r.get("unit") or cfg.get("unit", "%")) == "%" else None),
                      r.get("unit") or cfg.get("unit", "%"), _time(r.get("resetsAt")), source="mirror") for r in rows]
    doc = _json(text)
    if doc is None:
        raise ProviderError("mirror: output is not JSON")
    if fmt == "waybar":
        pct = _num(doc.get("percentage")) if isinstance(doc, dict) else None
        if pct is None and isinstance(doc, dict):
            pct = _num(re.search(r"\d+(?:\.\d+)?(?=\s*%)", str(doc.get("text", ""))) and
                       re.search(r"\d+(?:\.\d+)?(?=\s*%)", str(doc.get("text", ""))).group(0))
        return [entry(name, pct, 100, "%", None, detail=str(doc.get("text", ""))[:64] if isinstance(doc, dict) else None,
                      source="mirror")]
    fields = {"name": "$.name", "used": "$.used", "limit": "$.limit", "unit": "$.unit", "resetsAt": "$.resetsAt",
              "remaining": "$.remaining", **(cfg.get("fields") or {})}
    scale = cfg.get("scale") or {}
    out = []
    for item in jpath(doc, cfg.get("items", "$"))[:64]:
        vals = {k: _field(item, v) for k, v in fields.items()}
        nums = {k: _num(vals.get(k)) for k in ("used", "limit", "remaining")}
        for k, f in scale.items():
            if nums.get(k) is not None:
                nums[k] = nums[k] * float(f)
        unit = str(vals.get("unit") or cfg.get("unit", "%"))
        if unit not in ("$", "%", "tokens", "credits") and not re.fullmatch(r"[A-Z]{3}", unit):
            unit = _unit(unit)
        if nums["limit"] is None and unit == "%":
            nums["limit"] = 100
        out.append(entry(vals.get("name") or name, nums["used"], nums["limit"], unit, _time(vals.get("resetsAt")),
                         remaining=nums["remaining"], source="mirror"))
    return out


def fetch(cfg, ctx):
    preset = cfg.get("preset")
    if preset:
        fn = PRESETS.get(preset)
        if not fn:
            raise ProviderError(f"mirror: unknown preset {preset!r} (known: {', '.join(PRESETS)})")
        out = fn(cfg, ctx)
    else:
        out = generic(cfg, ctx)
    out = _select(out, cfg.get("include"))[: int(cfg.get("max", 16))]
    for e in out:
        e.pop("group", None)
    return out
