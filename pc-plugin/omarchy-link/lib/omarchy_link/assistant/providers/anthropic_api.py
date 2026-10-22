"""Claude via the Anthropic Messages API (fallback when Claude Code is not signed in).
Needs an API key. Streams server-sent events."""

import json

from .. import ProviderError, key_ready, stream_http

KIND, LABEL, STREAMING = "api", "Claude (API)", True
DEFAULTS = {"baseUrl": "https://api.anthropic.com", "model": "claude-haiku-5-5", "key": "env:ANTHROPIC_API_KEY"}


def available(cfg):
    c = {**DEFAULTS, **cfg}
    return {"model": c["model"]} if key_ready(c["key"]) else None


def ask(cfg, req):
    c = {**DEFAULTS, **cfg}
    headers = {"x-api-key": req.ctx.secret(c["key"], "anthropic"), "anthropic-version": "2023-06-01"}
    body = {"model": c["model"], "max_tokens": int(c.get("maxTokens", 400)), "stream": True,
            "system": req.system, "messages": req.messages()}
    out = []

    def on_line(line):
        if not line.startswith("data:"):
            return
        try:
            ev = json.loads(line[5:].strip())
        except ValueError:
            return
        if ev.get("type") == "error":
            raise ProviderError("anthropic: " + str((ev.get("error") or {}).get("message", "error"))[:160])
        d = ev.get("delta") or {}
        if ev.get("type") == "content_block_delta" and d.get("type") == "text_delta":
            out.append(d.get("text", ""))
            req.delta(d.get("text", ""))

    stream_http(c["baseUrl"].rstrip("/") + "/v1/messages", headers, body, req, on_line)
    return "".join(out)
