"""Anthropic (Claude API): organisation cost this month via the Admin API
(GET /v1/organizations/cost_report, admin key sk-ant-admin...). Amounts are
decimal strings in cents. No official prepaid-balance endpoint exists, so
`limit` is your "budget" from ai.json or null. The Admin API is unavailable for
individual accounts; Claude Pro/Max plan limits have no API: use "manual".
"""

from urllib.parse import urlencode

from .. import entry, iso, month_window, utcnow


def fetch(cfg, ctx):
    key = ctx.secret(cfg.get("key", "env:ANTHROPIC_ADMIN_KEY"), "anthropic")
    base = cfg.get("baseUrl", "https://api.anthropic.com")
    start, reset = month_window()
    cents, page = 0.0, None
    for _ in range(10):
        q = {"starting_at": iso(start), "ending_at": iso(utcnow()), "bucket_width": "1d", "limit": 31}
        if page:
            q["page"] = page
        data = ctx.http_json("GET", f"{base}/v1/organizations/cost_report?{urlencode(q)}",
                             {"x-api-key": key, "anthropic-version": "2023-06-01"})
        for bucket in data.get("data", []):
            for r in bucket.get("results", []):
                cents += float(r.get("amount") or 0)
        page = data.get("next_page")
        if not data.get("has_more") or not page:
            break
    return [entry(cfg.get("name", "Claude API"), cents / 100.0, cfg.get("budget"), "$", iso(reset))]
