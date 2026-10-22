"""Any OpenAI-compatible /chat/completions endpoint (API fallback): LM Studio,
llama.cpp server, vLLM, OpenRouter, Groq, Mistral... Needs "baseUrl" (e.g.
http://192.168.1.20:1234/v1) and "model"; "key" is optional (env:/file:/cmd:).
Streams server-sent events."""

import json

from .. import ProviderError, key_ready, stream_http

KIND, LABEL, STREAMING = "api", "OpenAI-compatible", True
DEFAULTS: dict = {}


def _cfg(cfg):
    return {**DEFAULTS, **cfg}


def available(cfg):
    c = _cfg(cfg)
    if not c.get("baseUrl") or not c.get("model"):
        return None
    if c.get("key") and not key_ready(c["key"]):
        return None
    return {"model": c["model"]}


def ask(cfg, req):
    c = _cfg(cfg)
    headers = {}
    if c.get("key"):
        headers["Authorization"] = "Bearer " + req.ctx.secret(c["key"], c.get("id", "api"))
    body = {"model": c["model"], "stream": True, "max_tokens": int(c.get("maxTokens", 400)),
            "messages": [{"role": "system", "content": req.system}, *req.messages()]}
    out = []

    def on_line(line):
        if not line.startswith("data:"):
            return
        data = line[5:].strip()
        if data == "[DONE]" or not data:
            return
        try:
            ev = json.loads(data)
        except ValueError:
            return
        if ev.get("error"):
            raise ProviderError(str(ev["error"].get("message", ev["error"]) if isinstance(ev["error"], dict) else ev["error"])[:160])
        for ch in ev.get("choices", []):
            chunk = (ch.get("delta") or {}).get("content") or ""
            if chunk:
                out.append(chunk)
                req.delta(chunk)

    stream_http(c["baseUrl"].rstrip("/") + "/chat/completions", headers, body, req, on_line)
    return "".join(out)
