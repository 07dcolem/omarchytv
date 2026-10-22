"""OpenRouter: with a management key ("management": true) GET /api/v1/credits
gives account credits bought/used; otherwise GET /api/v1/key reports the
calling key's own cap and spend."""

from .. import entry


def fetch(cfg, ctx):
    key = ctx.secret(cfg.get("key", "env:OPENROUTER_API_KEY"), "openrouter")
    base = cfg.get("baseUrl", "https://openrouter.ai")
    auth = {"Authorization": f"Bearer {key}"}
    name = cfg.get("name", "OpenRouter")
    if cfg.get("management"):
        d = ctx.http_json("GET", f"{base}/api/v1/credits", auth).get("data", {})
        return [entry(name, d.get("total_usage"), d.get("total_credits"), "$")]
    d = ctx.http_json("GET", f"{base}/api/v1/key", auth).get("data", {})
    limit = d.get("limit")
    budget = d.get("effective_budget") or {}
    if limit is not None and d.get("limit_remaining") is not None:
        used = float(limit) - float(d["limit_remaining"])
    else:
        used = d.get("usage_monthly") if d.get("limit_reset") == "monthly" else d.get("usage")
    return [entry(name, used, limit, "$", budget.get("resets_at"))]
