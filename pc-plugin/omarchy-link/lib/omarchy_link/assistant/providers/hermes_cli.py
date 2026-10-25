"""Nous Research Hermes CLI (`hermes`), signed in locally."""

import json

from .. import ProviderError, run_cli, which
from ... import clis

KIND, LABEL, STREAMING = "cli", "Hermes", False


def available(cfg):
    if cfg.get("bin"):
        return {"model": cfg.get("model")} if which(cfg, "hermes") else None
    return {"model": cfg.get("model")} if clis.detect("hermes") else None


def ask(cfg, req):
    argv = [which(cfg, "hermes"), "-p", req.flat_prompt()]
    if cfg.get("model"):
        argv += ["-m", cfg["model"]]
    out = run_cli(argv, req).strip()
    if out.startswith("{"):
        try:
            obj = json.loads(out)
            out = str(obj.get("result") or obj.get("text") or obj.get("response") or out).strip()
        except ValueError:
            pass
    if not out:
        raise ProviderError("hermes: no answer in output")
    return out
