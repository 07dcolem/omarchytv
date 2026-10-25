# OmarchyTV `2.12.0-beta` — 25 October 2026 (`versionCode 20`)

**OmarchyTV `2.12.0-beta`** brings **26 100%-MIT Themes & Bundled 4K Wallpapers**, **Zero-API-Cost AI & Grok Bot Integration** across 3 modes (built-in `:web` WebApps, PC/Mac CLI bridge, and a native **MCP Server** on both TV and PC), **Screensaver Effect Speed**, and **Sharp AQUOS / multi-brand Live TV + scrollable menu fixes**.

---

## Release Artifacts & Checksums

Every Android APK is signed with the official OmarchyTV release certificate (`SHA-256: 90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`), so `adb install -r` upgrades cleanly over `2.11.0-beta` and earlier releases while preserving all settings.

| Artifact | Platform | Version | Size | SHA-256 |
|---|---|---|---|---|
| `omarchytv-release-2.12.0-beta.apk` | Android TV / Google TV (`com.omarchytv.home`, `minSdk 24`, `targetSdk 34`) | `2.12.0-omarchytv` (`versionCode 20`) | `3.8 MB` | `f1426db057fdc958fe562d1afd57a710b896e2f63d4fa6c2ec6c8ceefdfee11e` |
| `omarchy-tv-pc-plugin-2.12.0-beta.tar.gz` | Omarchy Linux / macOS (`omarchy-tv` + `omarchy-link` + `tools/`) | `2.12.0-beta` | `184 KB` | `2aef33b30e38eba6eb4355ad597bf382bb5e7210be59d7070d6b5f509765bd0c` |
| `omarchytv-mobile-2.12.0-beta.apk` | Android Smartphone Installer & Companion (`com.omarchytv.mobile`, `minSdk 26`, `targetSdk 34`) | `2.12.0-beta` (`versionCode 21200`) | `178 KB` | `42bb62aa6169c52afacc9b477d25f6f95fffe2eeea9f779394606e1a4e5ad0a4` |

---

## What's New in `2.12.0-beta`

### 1. 26 100%-MIT Themes & Bundled 4K Wallpapers + `Sync PC wallpaper` Toggle
- **3 New 100%-MIT Community Themes with All Original 4K Wallpapers:**
  - **`jade-horse`** ([dhh/omarchy-jade-horse-theme](https://github.com/dhh/omarchy-jade-horse-theme), MIT, © 2026 David Heinemeier Hansson): `01-ink-horse.webp`, `02-carved-jade-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp`.
  - **`year-of-the-horse`** ([dhh/omarchy-year-of-the-horse-theme](https://github.com/dhh/omarchy-year-of-the-horse-theme), MIT, © 2026 David Heinemeier Hansson): `01-ink-horse.webp`, `02-paper-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp`.
  - **`hermarchy`** ([archer-clawbot/omarchy-hermarchy-theme](https://github.com/archer-clawbot/omarchy-hermarchy-theme), MIT, © 2026 Archer Clawbot): `01-hermarchy-command.webp`, `02-hermarchy.webp`, `03-hermarchy.webp`, `04-omarchy.webp`.
- **4K Omarchy Wordmark Wallpapers (`01-omarchy.webp`, `3840×2160`)** generated for `last-horizon`, `solitude`, and `starship` using each theme's exact MIT `background` and `accent` colors, ensuring every one of the **26 bundled MIT themes** ships with at least one 100%-MIT 4K wallpaper. Complete provenance is documented in [`THIRD-PARTY.md`](THIRD-PARTY.md), [`NOTICE`](NOTICE), and [`launcher/WALLPAPER-PROVENANCE.csv`](launcher/WALLPAPER-PROVENANCE.csv).
- **`Sync PC wallpaper` Toggle (`syncPcWallpaper`, default `false`):** Pairing or syncing with a PC never overwrites the TV's bundled MIT wallpaper unless you explicitly turn on **Sync PC wallpaper** in the TV's Themes or Wallpaper menu.

### 2. Zero-API-Cost AI & Grok Bot Integration (3 Modes)
1. **Built-in AI WebApps (`> Grok Bot & AI` Hub & Home Shelf):**
   - Direct on-TV access to **Grok Bot** (`grok.com`), **Grok (X)** (`x.com/i/grok`), **ChatGPT** (`chatgpt.com`), **Claude** (`claude.ai`), and **Hermes** (`hermes.nousresearch.com`).
   - Runs in a sandboxed `:web` process (`WebAppActivity`) with persistent login cookies and DOM storage (sign in once on the TV or via QR code) plus D-pad spatial navigation and a virtual cursor (long-press **Back**).
   - **Grok Bot** appears on the Home screen app shelf out of the box (and can be moved or hidden like any app tile) and in Walker search (`> grok bot`, `> ask`, `Grok Bot`, `ChatGPT`, `Claude`, `Hermes`).
2. **PC / Mac CLI Bridge (`omarchy-link`):**
   - Run `> ask` or `> grok bot` from the TV Walker bar using the AI CLI tools already signed in on your paired PC or Mac (`grok`, `claude`, `codex`, `gemini`, `hermes`, or local `ollama`) with **zero extra API keys**.
3. **Native MCP Server (TV `POST /mcp` & PC `omarchy-tv mcp`):**
   - Control your TV from **Grok Bot**, **Claude Desktop**, **Cursor**, **Hermes**, or any Model Context Protocol (`2024-11-05`, JSON-RPC 2.0) client.
   - Exposes a strict TV-only tool whitelist: `tv_get_status`, `tv_list_themes`, `tv_set_theme`, `tv_send_key`, `tv_launch_app`, `tv_cast_media`, `tv_show_notification`, and `tv_open_ai_webapp`.
   - On PC/Mac, `omarchy-tv mcp --http --port 8990` binds strictly to `127.0.0.1` by default and requires a 256-bit Bearer token stored at `~/.config/omarchy-tv/mcp-token` (`0600`). On the TV, `POST http://<tv-ip>:8999/mcp` requires `OTV1` HMAC signing or `Authorization: Bearer <link-token>`.

### 3. Screensaver Effect Speed (`Slow / Normal / Fast`)
- Added **Effect speed** (`"screensaverSpeed": "slow" | "normal" | "fast"`, default `"normal"`) in the Screensaver menu, scaling all 37 `tte.js` effects as well as the native ASCII fallback.

### 4. Multi-Brand Live TV & Menu Fixes (Community Feedback)
- **Sharp AQUOS & Multi-Brand Live TV Detection:** Added native detection for Sharp AQUOS (`jp.co.sharp.av.android.aquostvapp` + `.TvActivity` explicit fallback), Google TV (`com.google.android.tv`), AOSP TV (`com.android.tv`), DTVKit (`org.dtvkit.inputsource`), TCL (`com.tcl.tv`), Hisense (`com.hisense.tv.livetv`), and Philips (`com.philips.tv.tvapp`) alongside Sony BRAVIA (`com.sony.dtv.tvx`).
- **Scrollable Menus (`AsciiMenu`):** Wrapped popup menu rows in a `<ScrollView>` with automatic D-pad focus scrolling so long menus (including all 26 themes) scroll smoothly to the very bottom on 1080p TVs.
- **App Hiding & Unhiding Fix:** Fixed `Hide from launcher` on the Home shelf and app grid (`packageAt` vs `keyAt` normalization, plus `web:<id>` WebApp support) and added a direct **Hidden apps** manager row in Workspace 5 (`System`).

### Thanks
- **Anderson Leite** ([@x_andersonleite](https://x.com/x_andersonleite) / [@anderson-leite](https://gitlab.com/anderson-leite)): Sharp AQUOS testing, Issue #3, Issue #4, Issue #5 reports, and MR !1.
- **David Heinemeier Hansson** ([@dhh](https://x.com/dhh)): creator of Omarchy ([omarchy.org](https://omarchy.org)), `jade-horse`, and `year-of-the-horse`.
- **Archer Clawbot** ([archer-clawbot/omarchy-hermarchy-theme](https://github.com/archer-clawbot/omarchy-hermarchy-theme)): creator of the MIT `hermarchy` theme.
