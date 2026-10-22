"""xAI Grok Build CLI (`grok`), signed in with `grok login`.
Runs `grok -p` headless, one turn, no memory/subagents/plan/web search,
--output-format json, in an empty temp dir."""

import json

from .. import ProviderError, run_cli, which
from ... import clis

KIND, LABEL, STREAMING = "cli", "Grok", False


def available(cfg):
    if cfg.get("bin"):
        return {"model": cfg.get("model")} if which(cfg, "grok") else None
    return {"model": cfg.get("model")} if clis.detect("grok") else None


def _find_text(obj):
    if isinstance(obj, dict):
        if obj.get("is_error") or obj.get("error"):
            err = obj.get("error") or obj.get("result")
            raise ProviderError("grok: " + str(err.get("message", err) if isinstance(err, dict) else err)[:160])
        for k in ("result", "response", "text", "content", "message"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v
            if isinstance(v, (dict, list)):
                t = _find_text(v)
                if t:
                    return t
    if isinstance(obj, list):
        texts = [t for t in (_find_text(x) for x in obj) if t]
        return "\n".join(texts) if texts else None
    return None


def ask(cfg, req):
    argv = [which(cfg, "grok"), "--no-auto-update", "-p", req.flat_prompt(), "--output-format", "json",
            "--max-turns", "1", "--no-memory", "--no-subagents", "--no-plan", "--disable-web-search"]
    if cfg.get("model"):
        argv += ["-m", cfg["model"]]
    out = run_cli(argv, req).strip()
    try:
        text = _find_text(json.loads(out[out.find("{"):] if "{" in out else out))
    except ValueError:
        text = out
    if not text:
        raise ProviderError("grok: no answer in output")
    return text
