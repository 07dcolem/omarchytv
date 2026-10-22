"""Grok via the xAI API (fallback when the Grok CLI is not signed in). Needs an API key."""
from . import openai_compatible as _oc

KIND, LABEL, STREAMING = "api", "Grok (API)", True
DEFAULTS = {"baseUrl": "https://api.x.ai/v1", "model": "grok-4.7", "key": "env:XAI_API_KEY"}


def available(cfg):
    return _oc.available({**DEFAULTS, **cfg})


def ask(cfg, req):
    return _oc.ask({**DEFAULTS, **cfg}, req)
