"""OpenAI API: organisation costs this month (Admin API key, GET /v1/organization/costs).

OpenAI has no official endpoint for the prepaid credit balance, so `limit` is
your own monthly budget from ai.json ("budget": 20) or null.
ChatGPT Plus/Pro message limits have no API at all: use the "manual" provider.
"""

from urllib.parse import urlencode

from .. import entry, iso, month_window


def fetch(cfg, ctx):
    key = ctx.secret(cfg.get("key", "env:OPENAI_ADMIN_KEY"), "openai")
    base = cfg.get("baseUrl", "https://api.openai.com")
    start, reset = month_window()
    total, page = 0.0, None
    for _ in range(10):
        q = {"start_time": int(start.timestamp()), "bucket_width": "1d", "limit": 31}
        if cfg.get("projectIds"):
            q["project_ids"] = cfg["projectIds"]
        if page:
            q["page"] = page
        data = ctx.http_json("GET", f"{base}/v1/organization/costs?{urlencode(q, doseq=True)}",
                             {"Authorization": f"Bearer {key}"})
        for bucket in data.get("data", []):
            for r in bucket.get("results", []):
                amount = r.get("amount") or {}
                total += float(amount.get("value") or 0)
        page = data.get("next_page")
        if not data.get("has_more") or not page:
            break
    return [entry(cfg.get("name", "OpenAI API"), total, cfg.get("budget"), "$", iso(reset))]
