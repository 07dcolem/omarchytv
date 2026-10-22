"""Claude Code, signed in with `claude` (Pro/Max subscription or its own login).
Runs `claude -p` with no tools, no MCP servers, one turn, a TV system prompt,
and streams text deltas from --output-format stream-json."""

import json

from .. import ProviderError, json_lines, run_cli, which
from ... import clis

KIND, LABEL, STREAMING = "cli", "Claude", True


def available(cfg):
    if cfg.get("bin") and not which(cfg, "claude"):
        return None
    if not cfg.get("bin") and not clis.detect("claude"):
        return None
    return {"model": cfg.get("model", "haiku")}


def ask(cfg, req):
    argv = [which(cfg, "claude"), "-p", req.transcript(), "--output-format", "stream-json", "--verbose",
            "--include-partial-messages", "--max-turns", "1", "--tools", "", "--strict-mcp-config",
            "--system-prompt", req.system, "--model", cfg.get("model", "haiku")]
    state = {"streamed": "", "blocks": [], "result": None, "error": None}

    def on_line(line):
        for ev in json_lines(line):
            t = ev.get("type")
            if t == "stream_event":
                e = ev.get("event") or {}
                d = e.get("delta") or {}
                if e.get("type") == "content_block_delta" and d.get("type") == "text_delta":
                    state["streamed"] += d.get("text", "")
                    req.delta(d.get("text", ""))
            elif t == "assistant":
                for b in (ev.get("message") or {}).get("content", []):
                    if b.get("type") == "text":
                        state["blocks"].append(b.get("text", ""))
            elif t == "result":
                if ev.get("is_error"):
                    state["error"] = str(ev.get("result") or ev.get("subtype") or "error")
                else:
                    state["result"] = ev.get("result")

    run_cli(argv, req, on_line)
    if state["error"]:
        raise ProviderError("claude: " + state["error"][:160])
    return state["result"] or "".join(state["blocks"]) or state["streamed"]
