"""Numbers you type yourself, for plans with no official API (ChatGPT Plus/Pro,
Claude Pro/Max, SuperGrok, Gemini apps...). Example:
{"type":"manual","name":"Claude Max week","used":42,"limit":100,"unit":"%","resetsAt":"2026-10-23T09:00:00Z"}"""

from .. import ProviderError, UNITS, entry


def fetch(cfg, ctx):
    unit = cfg.get("unit", "%")
    if unit not in UNITS:
        raise ProviderError(f"manual: unit must be one of {sorted(UNITS)}")
    return [entry(cfg.get("name", "Manual"), cfg.get("used"), cfg.get("limit"), unit,
                  cfg.get("resetsAt"), status="manual")]
