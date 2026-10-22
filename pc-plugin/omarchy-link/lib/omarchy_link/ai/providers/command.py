"""Your own collector: runs "exec" (argv list, no shell) and reads JSON from its
stdout, either one entry or {"ai": [entries]}. Lets the community add providers
without touching this plugin. The script runs as you, on the PC."""

import json
import os
import subprocess

from .. import ProviderError, entry


def fetch(cfg, ctx):
    argv = cfg.get("exec")
    if not isinstance(argv, list) or not argv:
        raise ProviderError("command: exec must be a non-empty argv list")
    argv = [os.path.expanduser(str(a)) for a in argv]
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=30, check=True).stdout
        data = json.loads(out)
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        raise ProviderError(f"command failed: {e}") from e
    items = data.get("ai", [data]) if isinstance(data, dict) else data
    res = []
    for it in items[:8]:
        res.append(entry(it.get("name", cfg.get("name", "Custom")), it.get("used"), it.get("limit"),
                         it.get("unit", "$"), it.get("resetsAt"), remaining=it.get("remaining")))
    return res
