"""ollama on this PC (or OLLAMA_HOST on the LAN): local models, no account, no key.
Streams /api/chat NDJSON. Model: "model" in config, else the first installed one."""

import json

from .. import ProviderError, stream_http
from ... import clis

KIND, LABEL, STREAMING = "local", "Local (ollama)", True


def _base(cfg):
    return (cfg.get("baseUrl") or clis.ollama_url()).rstrip("/")


def available(cfg):
    if cfg.get("baseUrl"):
        return {"model": cfg.get("model")} if cfg.get("model") else None
    det = clis.detect("ollama")
    if not det:
        return None
    model = cfg.get("model") or det["models"][0]
    return {"model": model}


def ask(cfg, req):
    model = available(cfg)
    if not model or not model.get("model"):
        raise ProviderError("ollama: no model")
    msgs = [{"role": "system", "content": req.system}, *req.messages()]
    out = []

    def on_line(line):
        if not line.strip():
            return
        try:
            ev = json.loads(line)
        except ValueError:
            return
        if ev.get("error"):
            raise ProviderError("ollama: " + str(ev["error"])[:160])
        chunk = (ev.get("message") or {}).get("content", "")
        if chunk:
            out.append(chunk)
            req.delta(chunk)

    stream_http(_base(cfg) + "/api/chat", {}, {"model": model["model"], "messages": msgs, "stream": True,
                                              "options": {"num_predict": 300}}, req, on_line)
    return "".join(out)
