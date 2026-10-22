"""Make a step safe to show on a TV: no secrets, no file contents, no full paths, short."""
from __future__ import annotations

import json
import os
import re
import urllib.parse

MAX = 72
SECRET_PATTERNS = [
    re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9_-]{12,}"),            # OpenAI / Anthropic / Stripe style
    re.compile(r"\bxai-[A-Za-z0-9]{12,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),                # GitHub
    re.compile(r"\bglpat-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                        # AWS
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),                    # Google
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),              # Slack
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),  # JWT
    re.compile(r"(?i)\b(bearer|basic|token)\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(-----END [A-Z ]*PRIVATE KEY-----|$)", re.S),
    re.compile(r"\b[A-Fa-f0-9]{32,}\b"),                        # long hex (keys, hashes)
    re.compile(r"\b[A-Za-z0-9+/_-]{40,}={0,2}"),                # long base64-ish blobs
]
ENV_ASSIGN = re.compile(r"(?i)\b([A-Z_][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASS(?:WORD)?|PWD|AUTH|CREDENTIALS?|COOKIE|SESSION)"
                        r"[A-Z0-9_]*)\s*[=:]\s*(\"[^\"]*\"|'[^']*'|\S+)")
ANY_ENV = re.compile(r"\b([A-Z_][A-Z0-9_]{2,})=(\"[^\"]*\"|'[^']*'|\S+)")
FLAG_SECRET = re.compile(r"(?i)(--?(?:api[-_]?key|token|password|passwd|secret|auth|header)[= ])(\"[^\"]*\"|'[^']*'|\S+)")
URL_CREDS = re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://)[^/\s:@]+:[^/\s@]+@")
URL_QUERY_SECRET = re.compile(r"(?i)([?&](?:key|token|access_token|api_key|apikey|sig|signature|password|secret|code)=)[^&\s]+")
DOTS = "•••"


def redact(text) -> str:
    s = str(text or "")
    s = URL_CREDS.sub(lambda m: m.group(1) + DOTS + "@", s)
    s = URL_QUERY_SECRET.sub(lambda m: m.group(1) + DOTS, s)
    s = ENV_ASSIGN.sub(lambda m: f"{m.group(1)}={DOTS}", s)
    s = ANY_ENV.sub(lambda m: f"{m.group(1)}={DOTS}", s)          # env values are never shown
    s = FLAG_SECRET.sub(lambda m: m.group(1) + DOTS, s)
    for p in SECRET_PATTERNS:
        s = p.sub(DOTS, s)
    return s


def short(text, n: int = MAX) -> str:
    s = " ".join(redact(text).split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def base(path) -> str:
    p = str(path or "").rstrip("/")
    return os.path.basename(p) or p


def _host(url) -> str:
    try:
        return urllib.parse.urlparse(str(url)).hostname or ""
    except ValueError:
        return ""


def _args(raw):
    if isinstance(raw, str):
        try:
            v = json.loads(raw)
            return v if isinstance(v, dict) else {"input": raw}
        except ValueError:
            return {"input": raw}
    return raw if isinstance(raw, dict) else {}


FILE_KEYS = ("file_path", "path", "filePath", "notebook_path", "target_file", "file", "absolute_path", "filename")
CMD_KEYS = ("command", "cmd", "script")
PATTERN_KEYS = ("pattern", "query", "regex", "q", "search")


def tool_step(name, raw_input=None, title=None) -> str:
    """'Bash: npm test', 'Edit: cli.py', 'Grep: "TODO"', 'WebFetch: docs.x.ai'. Never contents."""
    n = str(name or title or "tool")
    args = _args(raw_input)
    if n.startswith("mcp__"):
        parts = n.split("__")
        n = "mcp " + ".".join(parts[1:3])
    low = n.lower()
    target = ""
    cmd = next((args[k] for k in CMD_KEYS if isinstance(args.get(k), (str, list))), None)
    if isinstance(cmd, list):
        cmd = " ".join(str(x) for x in cmd if str(x) not in ("bash", "-lc", "-c", "sh", "zsh"))
    fpath = next((args[k] for k in FILE_KEYS if isinstance(args.get(k), str)), None)
    url = args.get("url") if isinstance(args.get("url"), str) else None
    pat = next((args[k] for k in PATTERN_KEYS if isinstance(args.get(k), str)), None)
    if cmd and any(w in low for w in ("bash", "shell", "exec", "terminal", "command", "run")):
        target = str(cmd).strip().splitlines()[0] if str(cmd).strip() else ""
    elif fpath:
        target = base(fpath)
    elif url:
        target = _host(url)
    elif pat:
        target = '"' + short(pat, 32) + '"'
    elif cmd:
        target = str(cmd).strip().splitlines()[0]
    elif isinstance(args.get("description"), str):
        target = args["description"]
    elif title and title != name:
        target = str(title)
    return short(f"{n}: {target}" if target else n)
