# Changelog

## [2.12.0-beta] — 2026-10-25 (versionCode 20 — 26 MIT Themes & Original Wallpapers, Grok Bot & AI Hub, Native MCP Server, Sharp AQUOS & Scrollable Menus)

### Release Artifacts (`v2.12.0-beta`)
- **Android TV Launcher APK (`omarchytv-release-2.12.0-beta.apk`):** `versionCode 20`, SHA-256 `9dedc335fb1150afa6027f4123bd295bec8241a4c654842a6be65caff993f035`
- **PC / Mac Plugin (`omarchy-tv-pc-plugin-2.12.0-beta.tar.gz`):** `2.12.0-beta`, SHA-256 `2aef33b30e38eba6eb4355ad597bf382bb5e7210be59d7070d6b5f509765bd0c`
- **Android Phone Companion (`omarchytv-mobile-2.12.0-beta.apk`):** `versionCode 21200`, SHA-256 `42bb62aa6169c52afacc9b477d25f6f95fffe2eeea9f779394606e1a4e5ad0a4`
- **Signing Certificate SHA-256:** `90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`

### Added
- **26 MIT-Only Themes & Original Bundled MIT Wallpapers:**
  - Added 3 new 100%-MIT community themes with their original MIT wallpapers:
    - **`jade-horse`** ([dhh/omarchy-jade-horse-theme](https://github.com/dhh/omarchy-jade-horse-theme), MIT, © 2026 David Heinemeier Hansson): `01-ink-horse.webp`, `02-carved-jade-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp`.
    - **`year-of-the-horse`** ([dhh/omarchy-year-of-the-horse-theme](https://github.com/dhh/omarchy-year-of-the-horse-theme), MIT, © 2026 David Heinemeier Hansson): `01-ink-horse.webp`, `02-paper-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp`.
    - **`hermarchy`** ([archer-clawbot/omarchy-hermarchy-theme](https://github.com/archer-clawbot/omarchy-hermarchy-theme), MIT, © 2026 Archer Clawbot): `01-hermarchy-command.webp`, `02-hermarchy.webp`, `03-hermarchy.webp`, `04-omarchy.webp`.
  - Generated 3840×2160 flat two-color Omarchy wordmark wallpapers (`01-omarchy.webp`) for `last-horizon`, `solitude`, and `starship` using each theme's exact MIT `background` and `accent` colors, so all **26 bundled MIT themes** have at least one bundled 100%-MIT wallpaper.
- **Native Grok Bot · Omarchy TUI (`AskActivity`) + AI WebApps:**
  - **Grok Bot Omarchy TUI on Home Shelf:** Clicking the **Grok Bot** tile (`grokbot@tv:~$ > GROK BOT [ omarchy · tui ]`) on the Home screen opens the native Omarchy-styled TUI window (`BoxView` 2 px border, `grok bot · omarchy tui [<theme>]` legend, live 4K `WallpaperView` backdrop, `grokbot@omarchytv:~$` prompt, D-pad quick-action chips, voice & keyboard input).
  - **Standalone Local TV Commands + Paired PC AI Bridge:** Control themes (`theme jade-horse`, `next theme`, `themes`), 4K wallpapers (`wallpaper`), ASCII screensavers (`screensaver`, `speed slow|normal|fast`), installed TV apps (`open YouTube`, `apps`), and system/MCP status (`status`) directly on the TV without a PC, or stream answers from a paired PC's CLI (`grok`, `claude`, `codex`, `gemini`, `hermes`, `ollama`) over `OmarchyLink`.
  - **Built-in AI WebApps (`[ 🌐 grok.com ]` / `[ 🌐 web ▾ ]`):** Open **Grok Web** (`grok.com`), **Grok (X)** (`x.com/i/grok`), **ChatGPT**, **Claude**, or **Hermes** in the sandboxed `:web` process (`WebAppActivity`) with persistent cookies/DOM storage and D-pad cursor.
  - **Grok Bot & AI Hub** reachable from the Main Menu, Workspace 4 (`PC`), Workspace 5 (`System`), and `AI & terminal`.
  - Added `grok` (`Grok Bot`) and `hermes` (`Hermes Agent`) CLI/API providers to `omarchy-link` (`AUTO_ORDER` and `clis.py`).
- **Native MCP Server (TV `:8999/mcp` + PC `omarchy-tv mcp`):**
  - **TV Native MCP Server (`POST /mcp` & `POST /v1/mcp` in `LinkServer.java`):** JSON-RPC 2.0 MCP endpoint (`protocolVersion: "2024-11-05"`) authenticated via `OTV1` HMAC or `Authorization: Bearer <token>`, exposing `tv_get_status`, `tv_list_themes`, `tv_set_theme`, `tv_send_key`, `tv_launch_app`, `tv_cast_media`, `tv_show_notification`, and `tv_open_ai_webapp`. Advertises `"mcp"` in `/v1/status` capabilities.
  - **PC MCP Bridge (`omarchy-tv mcp [--stdio|--http] [--port 8990]`):** Stdio and HTTP JSON-RPC 2.0 MCP server with 256-bit Bearer token auth (`~/.config/omarchy-tv/mcp-token`, `0600`) and strict TV-only tool whitelist.
- **Screensaver Effect Speed:** Added `"screensaverSpeed": "slow" | "normal" | "fast"` (`Effect speed` in the Screensaver menu), scaling both `tte.js` WebView effects and the native ASCII fallback.

### Fixed
- **Issue #3 — Bundled MIT Wallpapers Overwritten by PC Sync & Non-Scrollable Theme Menu:**
  - Wrapped `AsciiMenu` rows in a `<ScrollView>` (`popup_inputs.xml` + `AsciiMenu.java` `scrollIntoView`) so long menus (including the 26-theme list) scroll smoothly past `matte-black` all the way to the bottom on 1080p TVs.
  - Added `Sync PC wallpaper` toggle (`syncPcWallpaper`, default `false`) in the Themes and Wallpaper menus so PC pairing/sync never overwrites the TV's bundled MIT wallpaper unless explicitly enabled.
- **Issue #4 — Sharp AQUOS & Multi-Brand Live TV Detection:**
  - Expanded `live_tv_packages` (`com.sony.dtv.tvx`, `jp.co.sharp.av.android.aquostvapp`, `com.google.android.tv`, `com.android.tv`, `org.dtvkit.inputsource`, `com.tcl.tv`, `com.hisense.tv.livetv`, `com.philips.tv.tvapp`) and added explicit `jp.co.sharp.av.android.aquostvapp/.TvActivity` fallback when TIF returns only internal tuner services.
- **Issue #5 — App Hiding & Unhiding Broken:**
  - Fixed `appTileMenu()` storing `pkg/activity` instead of `packageAt(position)` when hiding apps from the Home shelf or grid, updated `LauncherConfig.isHidden()` and `hiddenPage()` to normalize legacy `pkg/activity` entries and support `web:<id>` WebApp tiles, and added a direct **Hidden apps** row to Workspace 5 (`System`).

### Thanks
- **Anderson Leite** ([@x_andersonleite](https://x.com/x_andersonleite) / [@anderson-leite](https://gitlab.com/anderson-leite)): Sharp AQUOS testing, Issue #3, Issue #4, Issue #5 reports, and MR !1.
- **David Heinemeier Hansson** ([@dhh](https://x.com/dhh)): `jade-horse` and `year-of-the-horse` MIT themes & wallpapers.
- **Archer Clawbot**: `hermarchy` MIT theme & wallpapers.

## [2.11.0-beta-mobile] — 2026-10-24 (OmarchyTV Mobile — Universal Smart TV Phone Installer & Companion)

### Added (`mobile-companion/` — `omarchytv-mobile-2.11.0-beta.apk`)
- **OmarchyTV Mobile (`com.omarchytv.mobile`, `2.11.0-beta`):** Official MIT-licensed Android smartphone companion and wireless installer for **Android TV / Google TV, LG webOS, Samsung Tizen, and Hisense VIDAA** (`minSdk 26`, `targetSdk 34`, signed with the official OmarchyTV release certificate `90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`).
- **Pure-Java Wireless ADB over TCP (`AdbTcpClient.java`):** 2048-bit RSA keypair generation, 524-byte Android `RSAPublicKey` struct encoding, `CNXN`/`AUTH` handshake over `:5555`, binary `sync:` (`SEND`/`DATA`/`DONE`/`OKAY`) `.apk` upload, `pm install -r`, and 1-tap default Home launcher pinning.
- **HMAC-SHA256 `omarchy-link` Client (`OmarchyLinkClient.java`):** Parallel `/24` LAN subnet scanner (`:8999`, `:5555`, `:47800`, `:8001`), dual-header HMAC-SHA256 signing (`Authorization: OTV1` + `X-Omarchy-Signature`), live switching across all **23 official Omarchy themes**, tactile D-Pad & media remote, AI/terminal prompt sender, custom wallpaper upload, and custom app banner upload.
- **Safe Reversible Brand Debloat (`DebloatProfiles.java`):** Non-destructive `--user 0` bloatware disable & 1-tap restore profiles for **Sony Bravia**, **Google TV Streamer**, **Sharp AQUOS**, **TCL**, **Hisense**, and **Xiaomi**, guarded by a hardcoded `PROTECTED_PACKAGES` denylist.
- **LG webOS Phone Bridge & Universal WebTV Server (`WebOsBridgeServer.java`):** Embedded `:8765` HTTP bridge server implementing `/v1/status`, `/v1/themes`, `/v1/wallpaper`, `/omarchytv.ipk` (with Debian `!<arch>` and `appinfo.json` inspector), and `/tv` Universal 1080p HTML5/Canvas OmarchyTV Launcher for Samsung Tizen (`:8001` SmartView auto-launch) and Hisense VIDAA TVs.
- **Dual-Mirror Release & Theme Client (`GitLabReleaseClient.java`):** Resolves `.apk` and `.ipk` releases and live `omarchy_themes.json` across both GitLab (`projects/87958120`) and GitHub (`piermark/omarchytv`) with SHA-256 verification.

All OmarchyTV releases stay available on both [GitHub Releases](https://github.com/piermark/omarchytv/releases) and [GitLab Releases](https://gitlab.com/piermark/omarchytv/-/releases).
Every APK is signed with the same certificate (SHA-256 `90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`),
so each version installs over the previous one.

## 2.11.0-testing (LG webOS Edition) — 24 October 2026

Experimental **`testing`** release (not beta) bringing OmarchyTV `2.11.0` to **LG webOS TVs** as an `.ipk` package (`com.omarchytv.home`), along with an updated dual-platform PC plugin (`omarchy-tv-pc-plugin-2.11.0-testing.tar.gz`). The Android TV `2.11.0-beta` release is unchanged. Community feedback from LG webOS TV users is welcome!

- **LG webOS App (`omarchytv-webos-2.11.0-testing.ipk`)**:
  - All 23 official Omarchy themes (`omarchy_themes.json`), Tom Ballard's *"Liftoff Sunset"* default wallpaper for Tokyo Night, and the 20 MIT Omarchy wordmark wallpapers.
  - Workspaces `1`–`5` (`home`, `tv`, `apps`, `pc`, `sys`), animated ASCII `OMARCHY` logo, and all 37 `tte.js` screensaver effects.
  - Includes all `2.11.0` improvements: `°C / °F` temperature unit switch in the Weather menu, full English / Italian / German localization (`weather`, `omarchy · pc`, `ai credits · pc`, `system`, `theme`, `up`), and non-overlapping top box titles.
  - Native LG webOS Luna Bus (`luna://com.webos.applicationManager/launch`) app launching and full Magic Remote (D-pad, pointer/cursor, number keys `1`–`5`, and webOS Back `461`) support.
- **PC Plugin (`omarchy-tv-pc-plugin-2.11.0-testing.tar.gz`)**:
  - Added `.ipk` package validation and `ares-install` support to `omarchy-tv update`.
  - Added `omarchy-tv webos-serve` (`--port 8765`) LAN HTTP + CORS bridge (`/v1/status`, `/v1/themes`, `/v1/wallpaper`) for live PC telemetry and theme sync on LG webOS TVs.
  - Full details and installation guide: [webos/INSTALL-WEBOS.md](webos/INSTALL-WEBOS.md) and [webos/RELEASE-2.11.0-testing-webos.md](webos/RELEASE-2.11.0-testing-webos.md).

## 2.11.0-beta — 23 October 2026 (versionCode 19)

Defaults are unchanged from 2.10.2-beta: every new option is off until you turn it on. Same bundled wallpapers as
2.10.2-beta (default: Tom Ballard's "Liftoff Sunset" for Tokyo Night).

### Fixes
- **Apps missing on Android 11+ TVs** (issue #2): the manifest now declares `<queries>` for `MAIN` + `LEANBACK_LAUNCHER`
  and `MAIN` + `LAUNCHER`, so Netflix, Prime Video, Disney+ and other apps show in the dock and grid on Android 11+.
  No `QUERY_ALL_PACKAGES`. No change on Android 8/9.
- **Google TV Wi-Fi**: `com.google.android.tungsten.setupwraith` is never disabled; `tools/disable.sh` / `disable.ps1`
  skip it even if a list includes it, and docs/DEBLOAT.md lists it as "never touch". Home is set with
  `cmd package set-home-activity`. DNS / `private_dns_*` are never touched.
- **TV tile**: `"tv": {"enabled": false}` now also hides the TV tile in the home row.
- **Translations**: the "weather", "system", "theme" and "up" labels were hard-coded in Italian; they now follow the
  TV language (English, Italian, German). An English TV shows no Italian text.
- **Box titles**: the titles of the top boxes (weather, omarchy · pc, ai credits · pc) no longer overlap the border line.

### New (off by default)
- **°C/°F**: Weather menu → "Temperature unit" (`"tempUnit": "F"` in omarchytv.json; default °C). Works with the
  manual city ("Search city…"); "Automatic (from IP)" stays the default.
- **Custom app banners**: `banners/<package>.png` in `Android/data/com.omarchytv.home/files/`, or pushed from the PC with
  `omarchy-tv icons list | push | delete` (PNGs in `~/.config/omarchy-tv/banners/<package>.png`). TV endpoints
  `PUT/DELETE /v1/banners/<package>`, `GET /v1/banners`, capability `banners`. Without a file the app's own banner is used.
- **Pane timestamps**: `PUT /v1/widgets` panes may carry `"at"` (unix seconds); without it the push time is used, as before.
- **PC plugin**: Italian/English UI following the system language (or the `language` config key); the new
  `icons` subcommand. All other commands are unchanged; with an older launcher the plugin says banners are unsupported.

### Unchanged
- Default theme, wallpapers, layout, menus, screensaver, Omarchy Link protocol and all existing settings.

### Thanks
- Michael Pfeifer ([@TheFifeDawg](https://x.com/TheFifeDawg)): Google TV feedback, the setupwraith Wi-Fi issue, the
  `<queries>` diagnosis and the TV tile bug.
- [@ilafayajose](https://gitlab.com/ilafayajose): issue #2 report (Noblex/Hisense, Android 11), diagnosed by @TheFifeDawg.
- @wielorzeczownik: the box title / border overlap report.

## Older versions
- 2.10.2-beta, 2.10.1-beta, 2.10-beta: see [launcher/docs/RELEASE-NOTES-2.10-beta.md](launcher/docs/RELEASE-NOTES-2.10-beta.md).
