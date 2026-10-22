"""DeepSeek: account balance, GET https://api.deepseek.com/user/balance.
Only a balance is published, so used is null and remaining carries the
balance; the unit is "$" for USD, otherwise the ISO currency code."""

from .. import entry


def fetch(cfg, ctx):
    key = ctx.secret(cfg.get("key", "env:DEEPSEEK_API_KEY"), "deepseek")
    base = cfg.get("baseUrl", "https://api.deepseek.com")
    d = ctx.http_json("GET", f"{base}/user/balance", {"Authorization": f"Bearer {key}"})
    out = []
    for info in d.get("balance_infos", []):
        cur = info.get("currency", "USD")
        out.append(entry(cfg.get("name", "DeepSeek"), None, None, "$" if cur == "USD" else cur,
                         remaining=round(float(info.get("total_balance") or 0), 2)))
    return out
