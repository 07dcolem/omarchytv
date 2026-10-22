"""OpenAI Codex CLI, signed in with `codex login` (ChatGPT plan or its own login).
Runs `codex exec --json` in a read-only sandbox in an empty temp dir with MCP
servers disabled. Codex emits whole messages, not token deltas."""

from .. import ProviderError, json_lines, run_cli, which
from ... import clis

KIND, LABEL, STREAMING = "cli", "ChatGPT (Codex)", False


def available(cfg):
    if cfg.get("bin"):
        return {"model": cfg.get("model")} if which(cfg, "codex") else None
    return {"model": cfg.get("model")} if clis.detect("codex") else None


def ask(cfg, req):
    argv = [which(cfg, "codex"), "exec", "--json", "--skip-git-repo-check", "--sandbox", "read-only",
            "-c", "mcp_servers={}"]
    if cfg.get("model"):
        argv += ["-m", cfg["model"]]
    argv.append(req.flat_prompt())
    state = {"msgs": [], "error": None}

    def on_line(line):
        for ev in json_lines(line):
            t = ev.get("type")
            item = ev.get("item") or {}
            if t == "item.completed" and item.get("type") == "agent_message":
                state["msgs"].append(item.get("text", ""))
            elif t in ("turn.failed", "error"):
                err = ev.get("error") or ev.get("message") or "failed"
                state["error"] = err.get("message", str(err)) if isinstance(err, dict) else str(err)

    run_cli(argv, req, on_line)
    if state["error"] and not state["msgs"]:
        raise ProviderError("codex: " + state["error"][:160])
    return "\n".join(state["msgs"])
