"""xAI (Grok API): prepaid credit balance via the Management API
(GET https://management-api.x.ai/v1/billing/teams/{team}/prepaid/balance,
management key, not an inference key). Amounts are USD cents; per the docs
purchases are negative and spend positive, so remaining = -total and
used = credits added - remaining. With "postpaid": true it also reports this
month's postpaid invoice against the effective spending limit.
Consumer SuperGrok / X Premium limits have no API: use "manual".
"""

from .. import ProviderError, entry, iso, month_window


def _cents(obj):
    if isinstance(obj, dict):
        obj = obj.get("val", 0)
    return float(obj or 0)


def fetch(cfg, ctx):
    key = ctx.secret(cfg.get("key", "env:XAI_MANAGEMENT_KEY"), "xai")
    team = cfg.get("teamId") or ""
    if not team:
        raise ProviderError("xai: set teamId (xAI Console -> Settings -> Team)")
    base = cfg.get("baseUrl", "https://management-api.x.ai")
    auth = {"Authorization": f"Bearer {key}"}
    data = ctx.http_json("GET", f"{base}/v1/billing/teams/{team}/prepaid/balance", auth)
    remaining = -_cents(data.get("total")) / 100.0
    added = -sum(_cents(c.get("amount")) for c in data.get("changes", []) if _cents(c.get("amount")) < 0) / 100.0
    limit = max(added, remaining)
    name = cfg.get("name", "Grok API")
    out = [entry(name, limit - remaining, limit, "$", None, remaining=round(remaining, 2))]
    if cfg.get("postpaid"):
        _, reset = month_window()
        inv = ctx.http_json("GET", f"{base}/v1/billing/teams/{team}/postpaid/invoice/preview", auth)
        used = _cents((inv.get("coreInvoice") or {}).get("amountAfterVat")) / 100.0
        lim = _cents(inv.get("effectiveSpendingLimit")) / 100.0 or None
        out.append(entry(name + " postpaid", used, lim, "$", iso(reset)))
    return out
