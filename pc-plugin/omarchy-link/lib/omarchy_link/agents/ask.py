"""Instruct a PC agent from the TV ("agent_ask"). Off unless "agentControlFromTv": true.

Safe method per agent: run the agent's own headless resume of that session, in its cwd, when the
session is NOT working right now (no second writer next to a live turn). Tool permissions are
never auto-approved unless "agentToolApprovalFromTv": true. Live terminal prompts (a pending
"Allow Bash?") are not answered from the TV: that needs the terminal. With "agentConfirm"
(default true) every instruction waits for a click on a PC notification first.
"""
from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path

from .. import config
from .redact import short

MAX_TEXT = 2000
ANSWER_MAX = 1200
APPROVE_SECONDS = 120
RUN_TIMEOUT = 900
PENDING_DIR = "agent-asks"
DEFAULT_AGENTS = ["claude-code", "codex", "grok", "hermes"]
WHY_NOT = {
    "grok-bot": "Grok Bot has no local input API; use the app",
    "gemini": "monitoring only for Gemini CLI",
}


class AskError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _text(t: str) -> str:
    t = str(t or "").strip()
    return (" " + t) if t.startswith("-") else t


def argv_for(a: dict, text: str, allow_tools: bool) -> tuple[list[str], str | None]:
    """(argv, stdin) for a headless resume of this session."""
    agent, sid = a["agent"], a["session"]
    if agent == "claude-code":
        return (["claude", "-p", "--resume", sid, "--output-format", "text",
                 "--permission-mode", "acceptEdits" if allow_tools else "default"], text)
    if agent == "codex":
        return (["codex", "exec", "resume", sid,
                 "-c", 'sandbox_mode="workspace-write"' if allow_tools else 'sandbox_mode="read-only"',
                 "-c", 'approval_policy="never"', "-"], text)
    if agent == "grok":
        argv = ["grok", "--no-auto-update", "-p", _text(text), "--resume", sid, "--output-format", "plain"]
        if a.get("cwd"):
            argv += ["--cwd", a["cwd"]]
        return (argv + (["--allow", "Edit", "--allow", "Write"] if allow_tools else ["--permission-mode", "default"]), None)
    if agent == "hermes":
        return (["hermes", "chat", "-q", _text(text), "--resume", sid], None)
    raise AskError("unsupported", WHY_NOT.get(agent, f"{agent} cannot take instructions from the TV"))


def check(cfg: dict, a: dict | None, text) -> str:
    """Raise AskError unless this ask may run; returns the cleaned text."""
    if not cfg.get("agentControlFromTv", False):
        raise AskError("disabled", "instructions from the TV are off on the PC (agentControlFromTv)")
    if a is None:
        raise AskError("not_found", "that agent session is not active on the PC")
    allowed = cfg.get("agentControlAgents") or DEFAULT_AGENTS
    if a["agent"] not in allowed or not a.get("canAsk"):
        raise AskError("unsupported", WHY_NOT.get(a["agent"], f"{a['agentName']} cannot take instructions from the TV"))
    if a["status"] == "waiting":
        raise AskError("unsupported", f"{a['agentName']} is waiting for an answer in its terminal; answer it on the PC")
    if a["status"] in ("running", "thinking"):
        raise AskError("busy", f"{a['agentName']} is working; ask again when it is done")
    t = str(text or "").strip()
    if not t or len(t) > MAX_TEXT:
        raise AskError("bad_request", f"text must be 1-{MAX_TEXT} characters")
    argv, _ = argv_for(a, t, False)
    if not shutil.which(argv[0]):
        raise AskError("unsupported", f"{argv[0]} is not installed on the PC")
    if not a.get("cwd") or not Path(a["cwd"]).is_dir():
        raise AskError("unsupported", "the session's folder is gone")
    return t


def run(cfg: dict, a: dict, text: str) -> str:
    argv, stdin = argv_for(a, text, bool(cfg.get("agentToolApprovalFromTv", False)))
    try:
        io = {"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}
        r = subprocess.run(argv, cwd=a["cwd"], capture_output=True, text=True,
                           timeout=int(cfg.get("agentAskTimeout", RUN_TIMEOUT)), **io)
    except subprocess.TimeoutExpired as e:
        raise AskError("timeout", f"{a['agentName']} did not finish in time") from e
    except OSError as e:
        raise AskError("failed", str(e)[:160]) from e
    if r.returncode != 0:
        raise AskError("failed", short((r.stderr or r.stdout or f"exit {r.returncode}").strip().splitlines()[-1:] or "", 200))
    return short(r.stdout.strip(), ANSWER_MAX) or "(done, no reply text)"


# ------------------------------------------------------------------ PC-side approval
def pending_dir() -> Path:
    d = config.STATE_DIR / PENDING_DIR
    d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def request_approval(a: dict, text: str, exe: str) -> str:
    """Show a PC notification; clicking it runs `omarchy-link agents approve <token>`."""
    tool = shutil.which("omarchy-notification-send") or shutil.which("notify-send")
    if not tool:
        raise AskError("cannot_confirm", "no notification tool to confirm on the PC (or set agentConfirm: false)")
    token = secrets.token_urlsafe(18)
    rec = {"agentId": a["id"], "text": text, "expires": time.time() + APPROVE_SECONDS}
    p = pending_dir() / f"{token}.json"
    config.write_json_private(p, rec)
    body = f"TV asks {a['agentName']} ({a.get('project') or '?'}): {short(text, 120)}  Click to run."
    if os.path.basename(tool) == "omarchy-notification-send":
        argv = [tool, "-g", "󰚩", "OmarchyTV → agent", body, "--exec", exe, "agents", "approve", token]
    else:  # plain notify-send: no click action; approve with the printed command
        argv = [tool, "-a", "omarchy-link", "OmarchyTV → agent", body + f"  (omarchy-link agents approve {token})"]
    subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return token


def approve(token: str) -> bool:
    if not token.replace("-", "").replace("_", "").isalnum():
        return False
    p = pending_dir() / f"{token}.json"
    rec = config.read_json(p, None)
    if not isinstance(rec, dict) or rec.get("expires", 0) < time.time():
        return False
    rec["approved"] = True
    config.write_json_private(p, rec)
    return True


def wait_approval(token: str, timeout: float = APPROVE_SECONDS, stop=None) -> bool:
    p = pending_dir() / f"{token}.json"
    end = time.time() + timeout
    try:
        while time.time() < end and not (stop and stop.is_set()):
            rec = config.read_json(p, {})
            if isinstance(rec, dict) and rec.get("approved"):
                return True
            time.sleep(0.3)
        return False
    finally:
        p.unlink(missing_ok=True)


# ------------------------------------------------------------------ Claude Code hooks (optional, sharper status)
HOOK_EVENTS = ("UserPromptSubmit", "PreToolUse", "PostToolUse", "Notification", "Stop", "SessionEnd")
MARK = "agents hook"


def claude_settings() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "settings.json"


def hooks_install(exe: str) -> Path:
    f = claude_settings()
    data = config.read_json(f, {}) if f.exists() else {}
    if not isinstance(data, dict):
        raise AskError("bad_settings", f"{f} is not a JSON object; not touching it")
    if f.exists():
        shutil.copy2(f, f.with_suffix(".json.omarchy-link.bak"))
    hooks = data.setdefault("hooks", {})
    cmd = f"{exe} {MARK}"
    for ev in HOOK_EVENTS:
        lst = [h for h in hooks.get(ev, []) if MARK not in json.dumps(h)]
        entry = {"hooks": [{"type": "command", "command": cmd, "timeout": 5}]}
        if ev in ("PreToolUse", "PostToolUse"):
            entry["matcher"] = "*"
        hooks[ev] = lst + [entry]
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, indent=2) + "\n")
    return f


def hooks_remove() -> bool:
    f = claude_settings()
    data = config.read_json(f, None)
    if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
        return False
    changed = False
    for ev in list(data["hooks"]):
        lst = data["hooks"][ev]
        keep = [h for h in lst if MARK not in json.dumps(h)] if isinstance(lst, list) else lst
        if keep != lst:
            changed = True
            if keep:
                data["hooks"][ev] = keep
            else:
                del data["hooks"][ev]
    if not data["hooks"]:
        del data["hooks"]
    if changed:
        f.write_text(json.dumps(data, indent=2) + "\n")
    return changed
