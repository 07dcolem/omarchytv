"""ChatGPT via the OpenAI API (fallback when Codex CLI is not signed in). Needs an API key."""
from . import openai_compatible as _oc

KIND, LABEL, STREAMING = "api", "ChatGPT (API)", True
DEFAULTS = {"baseUrl": "https://api.openai.com/v1", "model": "gpt-6-luna", "key": "env:OPENAI_API_KEY"}


def available(cfg):
    return _oc.available({**DEFAULTS, **cfg})


def ask(cfg, req):
    return _oc.ask({**DEFAULTS, **cfg}, req)
