# AI credits / usage on the TV

The PC collects how much of each AI plan or budget is used and pushes numbers to the TV
(`PUT /v1/ai`, shown in the AI pane; stored in the TV's top-level `"ai"` in omarchytv.json).
**The PC collects and the TV only displays.** The plugin prefers tools that are already
signed in on the PC and their local data, so most entries need **no API key**.

Entry format: `{"name","used","limit","unit":"$"|"tokens"|"%","resetsAt","updatedAt"}`, plus
optional `remaining`, `status` (`ok|error|manual`), `error`, `provider`, `source`. `used`/`limit` may be
`null` (unknown). Refreshed every `aiRefreshMinutes` (default 15, minimum 5) and on connect.
`omarchy-link push-ai --dry-run` shows what would be sent.

## Mirror mode (preferred): the TV shows exactly what your bar shows

If an AI-usage widget is already in your Omarchy bar, omarchy-link **mirrors** it and
does not measure anything itself, so the TV and the PC can never disagree. With no `ai.json`
(or one without providers) the plugin looks under `~/.config/omarchy/plugins/` and in the
Agents panel records. When it finds a known widget it uses it: **the built-in Omarchy Agents panel
first** (when it has usage records), then the first known widget that is actually in your bar
(`~/.config/omarchy/shell.json`), then any other known widget that is installed. Omacash and the
others are always available with `ai setup --use <preset>`. In that case
no CLI collectors are added (`autoDetect` defaults to off once a mirror is in use).

```sh
omarchy-link ai setup --list            # widgets found on this PC
omarchy-link ai setup                   # shows what each one reads now, asks which to mirror
omarchy-link ai setup --use omacash --include openrouter,elevenlabs   # rows and their order
omarchy-link ai setup --use omacash --dry-run
```

### Switching sources on and off (PC or TV)

Each known widget is a *source* that can be switched on or off. The built-in Agents panel is the
default; the others, such as Omacash, are opt-in:

```sh
omarchy-link ai sources                     # [x] omarchy-agents  [ ] omacash ...
omarchy-link ai sources enable omacash      # add Omacash rows after the Agents rows
omarchy-link ai sources disable omacash
omarchy-link ai sources only omarchy-agents
omarchy-link ai setup --use omarchy-agents,omacash   # same, from setup
```

Switching a source off keeps its options (`include`, …) in `ai.json` as `"enabled": false`.
The source list is pushed to the TV with the credits (`aiSources`), so the TV's AI-pane
options can show the same switches. Flipping one sends an `ai_sources` event, and the PC
applies it and re-pushes the pane (docs/PROTOCOL.md). The TV can only switch widgets
installed on the PC on or off; it can never add commands or files.
`"aiSourcesFromTv": false` in `config.json` turns remote switching off.

`ai setup` writes `ai.json` (0600, previous copy kept as `ai.json.bak`) with
`"autoDetect": false` and your mirror providers. The agent list is exactly the rows the widget
shows (or your `include`, in that order). Nothing is recomputed: amounts, percentages,
rounding, units, reset times and the widget's own fetch time are copied as they are.

| preset | widget (repo, licence) | how it is read (read-only) |
|---|---|---|
| `omarchy-agents` | built-in Omarchy 4 Agents panel (`omarchy.agents`), **default** | `~/.local/state/omarchy/agents/usage/<id>.json` in `agents/order.json` order, skipping providers disabled in the bar entry. Percent is `round(percent×100)`, a window past its reset reads 0 (like the panel), and balances (Fireworks/Kimi…) appear as `$`. `"accounts": "all"` adds per-account rows. |
| `omacash` | Omacash, `io.github.baranskyi.omacash`, <https://github.com/baranskyi/omacash> (MIT) | runs `python3 <plugin>/bin/omacash status`, the same no-network command its popup uses, which prints its cached snapshot. Falls back to `~/.local/state/omarchy/io.github.baranskyi.omacash/snapshot.json`. Rows are per provider in Omacash's order, with `used=spent`, `limit=funded`, `remaining`, unit `$` or `credits`, `resetsAt`, `detail`, `severity`, `stale`, `estimated`. `unconfigured` providers are hidden (`"showUnconfigured": true` shows them) and errors pass through. `"total": true` adds Omacash's "total remaining". It never runs `sync` (Omacash's own service does that) and never reads its key/config files. |
| `agent-usage` | robzolkos `omarchy-agent-usage` | same records, weekly window only (what that widget shows). |
| `claudebar` | <https://github.com/mryll/claudebar> (MIT) | `claudebar --json`: windows plus extra-usage credits. |
| `ai-usagebar` | <https://github.com/akitaonrails/ai-usagebar> (MIT) | `ai-usagebar usage --json`: metric sections. |
| `model-usage` | <https://github.com/DigitalPals/omarchy-modelusage> (MIT) | its `scripts/usage-fetch.py` with a throw-away `--state-dir` (this one does contact the providers, as the widget itself does). |

Common options: `include` (ids/names, ordered), `max`, `name` (prefix), `timeout`.

### Generic mirror (any other widget)

```json
{ "type": "mirror", "name": "My bar AI",
  "source": { "command": ["my-widget", "--json"] },          // or { "file": "~/.cache/x.json" }
  "format": "json",                                          // json | text | waybar
  "items": "$.agents[*]",
  "fields": { "name": "$.title", "used": "$.frac", "limit": "=100", "unit": "=%", "resetsAt": "$.ends" },
  "scale": { "used": 100 } }
```

`fields` uses a tiny JSONPath (`$.a.b`, `[0]`, `[*]`, `['key']`), and `=value` is a literal.
`format: "text"` takes a `regex` with named groups (`name`, `used`, `limit`, `unit`,
`resetsAt`, `remaining`), one row per match. `format: "waybar"` reads the first number in a
Waybar-style `{"text": …}`. Commands are an argv list (no shell), run with a timeout. Files
must be regular files you own and are opened without following symlinks.

## How each provider is measured (when nothing is mirrored)

| Plan / product | Without an API key | Type | What you get |
|---|---|---|---|
| **Claude Pro/Max (Claude Code)** | `claude -p "/usage"` (the signed-in CLI's own usage report, no model call), parsed | `claude_code`, **auto** | "Claude session" (5 h), "Claude week", "Claude week (<model>)" in %, with reset times |
| ↳ fallback | ccusage-style reading of `~/.claude/projects/**/*.jsonl` | same | tokens in the last 5 h, limit unknown |
| **ChatGPT Plus/Pro (Codex CLI)** | latest `rate_limits` in `~/.codex/sessions/**/rollout-*.jsonl` (written by Codex itself) | `codex`, **auto** | "Codex 5h" and "Codex week" in %, with reset times. Some Codex builds log `rate_limits: null` (notably `codex exec`). The last known value is then shown, and an expired window shows 0 %. |
| **Gemini CLI** | not available: `/stats model` only works inside an interactive session, and headless JSON stats are per run | `manual` | type your numbers (daily request quota: 1000 / 1500 / 2000 by tier) |
| **Grok (SuperGrok, Grok CLI)** | no local usage data or status command | `manual` | type your numbers |
| **ChatGPT app / claude.ai web usage** | not exposed | `manual` | |
| **ollama / local models** | unlimited | — | not shown |
| **Grok Bot** | no usage API | `manual` | |

### API fallbacks (need an admin/management key; use only if you want API spend)

| Provider | Endpoint | Key | Gives |
|---|---|---|---|
| OpenAI API | `GET /v1/organization/costs` | Admin key | month-to-date cost in $. No balance API. Set `budget` for a limit. |
| Anthropic API | `GET /v1/organizations/cost_report` | Admin key (organisations only) | month-to-date cost in $. No balance API. |
| xAI API | `GET management-api.x.ai/v1/billing/teams/{teamId}/prepaid/balance` (+ `postpaid/invoice/preview`) | Management key | prepaid credit used/remaining in $. Optionally postpaid vs spending limit. |
| OpenRouter | `GET /api/v1/key` (normal key) or `/api/v1/credits` (management key) | key | key limit/remaining with reset, or credits/usage |
| DeepSeek | `GET /user/balance` | API key | balance (unit $ or currency code) |
| anything else | `command`: your script prints the JSON | — | whatever it prints |

## `~/.config/omarchy-link/ai.json` (optional)

With no file, signed-in Claude Code and Codex are picked up automatically. Example:

```json
{
  "autoDetect": true,
  "disabled": [],
  "providers": [
    { "type": "manual", "name": "SuperGrok", "used": 30, "limit": 100, "unit": "%", "resetsAt": "2026-10-20T00:00:00Z" },
    { "type": "manual", "name": "Gemini (requests)", "used": 120, "limit": 1500, "unit": "tokens" },
    { "type": "xai", "teamId": "your-team-id", "key": "env:XAI_MANAGEMENT_KEY" },
    { "type": "openrouter", "key": "file:~/.config/omarchy-link/keys/openrouter" },
    { "type": "command", "name": "My script", "exec": ["~/bin/my-usage", "--json"] }
  ]
}
```

Key references work as in ASSISTANT.md (`env:`, `file:` chmod 600, `cmd:`; literal only if ai.json is 600).
Every HTTP call is https only. A failing provider becomes an `error` entry; the others still show.

## Adding a provider

`lib/omarchy_link/ai/providers/<type>.py` with `fetch(cfg, ctx) -> list[entry(...)]`. Use
`ctx.secret(ref, name)` for keys and `ctx.http_json(...)` for HTTPS. To be auto-detected, add it to the
list in `ai/__init__.py: collect()` together with a `clis.detect` check.
