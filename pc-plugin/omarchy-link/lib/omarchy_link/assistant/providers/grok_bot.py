"""Grok Bot provider (`grok-bot` CLI or OpenAI-compatible/webhook endpoint)."""

import json

from .. import ProviderError, key_ready, run_cli, stream_http, which
from ... import clis

KIND, LABEL, STREAMING = "cli", "Grok Bot", False


def available(cfg):
    if cfg.get("baseUrl"):
        if cfg.get("key") and not key_ready(cfg.get("key")):
            return None
        return {"model": cfg.get("model") or "grok-bot"}
    if cfg.get("bin"):
        return {"model": cfg.get("model") or "grok-bot"} if which(cfg, "grok-bot") else None
    if clis.detect("grok-bot"):
        return {"model": cfg.get("model") or "grok-bot"}
    return None


def ask(cfg, req):
    if cfg.get("baseUrl"):
        headers = {}
        if cfg.get("key"):
            headers["Authorization"] = f"Bearer {req.ctx.secret(cfg['key'])}"
        chunks = []
        body = {
            "model": cfg.get("model") or "grok-bot",
            "messages": [{"role": "system", "content": req.system}, *req.messages()],
            "stream": False,
        }
        def on_line(line):
            if line.strip():
                chunks.append(line)
        stream_http(cfg["baseUrl"].rstrip("/"), headers, body, req, on_line)
        raw = "\n".join(chunks).strip()
        if raw.startswith("{"):
            try:
                obj = json.loads(raw)
                if "choices" in obj and obj["choices"]:
                    return str(obj["choices"][0].get("message", {}).get("content", "")).strip()
                for k in ("text", "result", "response", "reply"):
                    if isinstance(obj.get(k), str) and obj[k].strip():
                        return obj[k].strip()
            except ValueError:
                pass
        return raw
    binary = which(cfg, "grok-bot")
    if not binary:
        raise ProviderError("grok-bot is not installed")
    argv = [binary, "-p", req.flat_prompt()]
    if cfg.get("model"):
        argv += ["-m", cfg["model"]]
    out = run_cli(argv, req).strip()
    if out.startswith("{"):
        try:
            obj = json.loads(out)
            out = str(obj.get("result") or obj.get("text") or obj.get("response") or out).strip()
        except ValueError:
            pass
    if not out:
        raise ProviderError("grok-bot: no answer in output")
    return out
