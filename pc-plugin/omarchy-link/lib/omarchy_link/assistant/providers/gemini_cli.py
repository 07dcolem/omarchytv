"""Google Gemini CLI, signed in with its Google login (or its own API key).
Runs `gemini -p` headless with --output-format stream-json in an empty temp dir.
Note: Google moved free/Google One users to Antigravity CLI in June 2026; this
works for whoever still has a working `gemini` login."""

from .. import ProviderError, json_lines, run_cli, which
from ... import clis

KIND, LABEL, STREAMING = "cli", "Gemini", True


def available(cfg):
    if cfg.get("bin"):
        return {"model": cfg.get("model")} if which(cfg, "gemini") else None
    return {"model": cfg.get("model")} if clis.detect("gemini") else None


def ask(cfg, req):
    argv = [which(cfg, "gemini"), "-p", req.flat_prompt(), "--output-format", "stream-json"]
    if cfg.get("model"):
        argv += ["-m", cfg["model"]]
    state = {"text": "", "error": None, "final": None}

    def on_line(line):
        for ev in json_lines(line):
            t = ev.get("type")
            if t == "message" and ev.get("role") == "assistant":
                chunk = ev.get("content") or ""
                if isinstance(chunk, str):
                    state["text"] += chunk
                    req.delta(chunk)
            elif t == "result":
                if ev.get("status") == "error" or ev.get("error"):
                    err = ev.get("error") or {}
                    state["error"] = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                state["final"] = ev.get("response")
            elif t == "error" and ev.get("severity") != "warning":
                state["error"] = str(ev.get("message", "error"))

    run_cli(argv, req, on_line)
    if state["error"] and not state["text"]:
        raise ProviderError("gemini: " + state["error"][:160])
    return state["text"] or state["final"] or ""
