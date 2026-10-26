# OmarchyTV

**An Omarchy-style home screen for Android TV, featuring a native Omarchy TUI Grok Bot assistant, 26 MIT themes with 4K wallpapers, a desktop link to your Omarchy PC / Mac, a native MCP server, and an Android smartphone wireless installer.**

Created by **[Marco Porro](https://www.marcoporro.it)** ([x.com/MarcoPorro](https://x.com/MarcoPorro) · [www.marcoporro.it](https://www.marcoporro.it))

Official Synchronized Repositories: **[GitHub (`github.com/piermark/omarchytv`)](https://github.com/piermark/omarchytv)** · **[GitLab (`gitlab.com/piermark/omarchytv`)](https://gitlab.com/piermark/omarchytv)**

Published: **25 October 2026 (beta)** · Version **2.12.0-beta** (`versionCode 20` — Android TV, PC/Mac Plugin & Mobile Companion) / **2.11.0-testing** (LG webOS experimental) · License **MIT**

> [!WARNING]
> **BETA SOFTWARE: THINGS MAY NOT WORK.** OmarchyTV has been tested on several devices (Sony KD-55XE9005 on Android 9,
> Google TV Streamer on Android 14, Sharp AQUOS, Noblex/Hisense on Android 11) plus the Android TV emulator. Expect rough edges, missing features on some TVs and bugs. It never roots or uninstalls
> anything, and you can always switch back to the stock home screen (see [INSTALL](launcher/docs/INSTALL.md)), but use it at your own risk.

![OmarchyTV home: Liftoff Sunset wallpaper, terminal + OMARCHY TV logo, weather, app row](docs/screenshots/home-preview.svg)

*Default theme since 2.10.2-beta: Tokyo Night with Tom Ballard's "Liftoff Sunset" wallpaper, used with permission (see [Credits](#credits-and-third-party-software)).*

| Workspace 2 · TV | Workspace 4 · PC | Workspace 5 |
|---|---|---|
| ![TV](docs/screenshots/ws2.svg) | ![PC](docs/screenshots/ws4.svg) | ![Workspace 5](docs/screenshots/ws5.svg) |
| **Logo menu** | **Screensaver (tte effects)** | **Workspace 3** |
| ![Menu](docs/screenshots/menu.svg) | ![Screensaver](docs/screenshots/screensaver.png) | ![Workspace 3](docs/screenshots/ws3.svg) |

*Screenshots from the Android TV emulator (API 28, 1920×1080, English UI). The app
tiles (Netflix, Prime Video, YouTube, CHILI, RaiPlay) are the real app icons captured on a Sony KD-55XE9005 running
OmarchyTV; see [Trademarks](#trademarks).*

---

## Release Downloads & Checksums (`v2.12.0-beta`)

Every Android APK is signed with the official OmarchyTV release certificate (`SHA-256: 90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`), so `adb install -r` upgrades cleanly over `2.11.0-beta` and earlier builds while keeping all user settings.

| Artifact | Downloads (GitHub & GitLab Mirrors) | Platform | Version | Size | SHA-256 |
|---|---|---|---|---|---|
| **`omarchytv-release-2.12.0-beta.apk`** | **[GitHub](https://github.com/piermark/omarchytv/releases/download/v2.12.0-beta/omarchytv-release-2.12.0-beta.apk)** · **[GitLab](https://gitlab.com/-/project/87958120/uploads/6cceb57b0e117e4607982769d2affef5/omarchytv-release-2.12.0-beta.apk)** | Android TV / Google TV (`com.omarchytv.home`, `minSdk 24`, `targetSdk 34`) | `2.12.0-omarchytv` (`versionCode 20`) | `3.8 MB` | `9dedc335fb1150afa6027f4123bd295bec8241a4c654842a6be65caff993f035` |
| **`omarchy-tv-pc-plugin-2.12.0-beta.tar.gz`** | **[GitHub](https://github.com/piermark/omarchytv/releases/download/v2.12.0-beta/omarchy-tv-pc-plugin-2.12.0-beta.tar.gz)** · **[GitLab](https://gitlab.com/-/project/87958120/uploads/b99cf1095f23c74fc75abb9cdd0d3322/omarchy-tv-pc-plugin-2.12.0-beta.tar.gz)** | Omarchy Linux / macOS (`omarchy-tv` + `omarchy-link` + `tools/`) | `2.12.0-beta` | `184 KB` | `2aef33b30e38eba6eb4355ad597bf382bb5e7210be59d7070d6b5f509765bd0c` |
| **`omarchytv-mobile-2.12.0-beta.apk`** | **[GitHub](https://github.com/piermark/omarchytv/releases/download/v2.12.0-beta/omarchytv-mobile-2.12.0-beta.apk)** · **[GitLab](https://gitlab.com/-/project/87958120/uploads/b6ff99262524aaf8186ab44906a91fdf/omarchytv-mobile-2.12.0-beta.apk)** | Android Smartphone Installer & Companion (`com.omarchytv.mobile`, `minSdk 26`, `targetSdk 34`) | `2.12.0-beta` (`versionCode 21200`) | `178 KB` | `42bb62aa6169c52afacc9b477d25f6f95fffe2eeea9f779394606e1a4e5ad0a4` |
| **`omarchytv-webos-2.11.0-testing.ipk`** | **[GitHub](https://github.com/piermark/omarchytv/releases/download/v2.11.0-testing-webos/omarchytv-webos-2.11.0-testing.ipk)** · **[GitLab](https://gitlab.com/piermark/omarchytv/-/releases)** | LG webOS TV (`com.omarchytv.webos`, experimental `testing`) | `2.11.0-testing` | `124 KB` | `04eb928640a0212cad83457ad50b502bc81da440445e33ea2eee95e6eefcc9df` |

All releases are available on both **[GitHub Releases](https://github.com/piermark/omarchytv/releases)** and **[GitLab Releases](https://gitlab.com/piermark/omarchytv/-/releases)**. Full release notes: **[RELEASE-2.12.0-beta.md](RELEASE-2.12.0-beta.md)** and **[CHANGELOG.md](CHANGELOG.md)**.

---

## What's New in `2.12.0-beta` (`versionCode 20`)

1. **Native Grok Bot · Omarchy TUI (`AskActivity`) on the TV Home Shelf:**
   - Clicking the **Grok Bot** tile (`grokbot@tv:~$ > GROK BOT [ omarchy · tui ]`) on the TV Home shelf — or selecting `Grok Bot (Omarchy TUI)` in the menu — opens a **native Omarchy-styled TUI assistant window** (`BoxView` 2 px border, `btop`-style legend `grok bot · omarchy tui [<theme>]`, translucent theme surface over the live 4K `WallpaperView`, `CaskaydiaMono` font, and `grokbot@omarchytv:~$` prompt) instead of jumping straight into a raw web browser.
   - **Standalone Local TV & MCP Control (works offline without a PC):** Switch any of the 26 MIT themes (`theme jade-horse`, `theme year-of-the-horse`, `theme hermarchy`, `next theme`, `themes`), cycle 4K wallpapers (`wallpaper`), launch or configure the 37 `tte.js` ASCII screensavers (`screensaver`, `speed slow|normal|fast`), launch installed TV apps or Live TV (`open YouTube`, `open TV`, `apps`), or inspect TV/network/MCP status (`status`, `mcp`) via voice, keyboard, or 1-click D-pad quick chips (`[ ⏭ next theme ]`, `[ 🖼 wallpaper ]`, `[ ✦ screensaver ]`, `[ 📊 status ]`, `[ 📦 apps ]`, `[ ❓ help ]`).
   - **Paired PC / Mac AI Bridge (`OmarchyLink`):** Automatically forwards open-ended AI questions over the encrypted LAN link to your already-authenticated PC/Mac CLI (`grok`, `claude`, `codex`, `gemini`, `hermes`, or local `ollama`) and streams the reply typewriter-style in the TUI terminal.
   - **Optional 1-Click Full Browser WebApp Mode (`[ 🌐 grok.com ]` / `[ 🌐 web ▾ ]`):** Whenever you want the full web interface, select `[ 🌐 grok.com ]` or `[ 🌐 web ▾ ]` inside the TUI header (or from `> Grok Bot & AI`) to open **Grok Web** (`grok.com`), **Grok (X)** (`x.com/i/grok`), **ChatGPT** (`chatgpt.com`), **Claude** (`claude.ai`), or **Hermes** (`hermes.nousresearch.com`) in the sandboxed `:web` process (`WebAppActivity`) with persistent cookies/DOM storage and D-pad cursor.
2. **26 100%-MIT Themes & Bundled 4K Wallpapers + `Sync PC wallpaper` Toggle:**
   - Added 3 new 100%-MIT community themes with all their original 4K wallpapers: DHH's **[`jade-horse`](https://github.com/dhh/omarchy-jade-horse-theme)** and **[`year-of-the-horse`](https://github.com/dhh/omarchy-year-of-the-horse-theme)**, plus Archer Clawbot's **[`hermarchy`](https://github.com/archer-clawbot/omarchy-hermarchy-theme)**.
   - Added 4K Omarchy wordmark wallpapers (`01-omarchy.webp`) for **[`last-horizon`](https://github.com/containerscrew/omarchy-last-horizon-theme)**, **[`solitude`](https://github.com/containerscrew/omarchy-solitude-theme)**, and **[`starship`](https://github.com/vyrx-dev/omarchy-starship-theme)**, so all **26 bundled MIT themes** include at least one 100%-MIT 4K wallpaper.
   - **`Sync PC wallpaper` Toggle (off by default):** Pairing or syncing with a PC never overwrites the TV's bundled 4K MIT wallpaper unless you explicitly enable *Sync PC wallpaper* in the TV's Themes or Wallpaper menu.
3. **Native MCP Server (TV `POST /mcp` & PC `omarchy-tv mcp`):**
   - Control your TV from **Grok Bot**, **Claude Desktop**, **Cursor**, **Hermes**, or any Model Context Protocol (`2024-11-05`, JSON-RPC 2.0) client using a strict TV-only tool whitelist (`tv_get_status`, `tv_list_themes`, `tv_set_theme`, `tv_send_key`, `tv_launch_app`, `tv_cast_media`, `tv_show_notification`, `tv_open_ai_webapp`).
4. **Screensaver Effect Speed (`Slow / Normal / Fast`):**
   - Adjust the animation speed for all 37 `tte.js` effects and the native ASCII fallback from the Screensaver menu or via the Grok Bot TUI (`speed slow`, `speed normal`, `speed fast`).
5. **Multi-Brand Live TV & Menu Fixes (Community Feedback):**
   - Native **Sharp AQUOS** (`jp.co.sharp.av.android.aquostvapp`) and multi-brand Live TV detection alongside Sony BRAVIA (`com.sony.dtv.tvx`), Google TV (`com.google.android.tv`), TCL, Hisense, and Philips.
   - Smooth D-pad scrolling across long menus (`Themes` menu scrolls smoothly through all 26 themes on 1080p TVs).
   - Fixed `Hide from launcher` on the Home shelf and app grid, and added a direct **Hidden apps** manager in Workspace 5 (`System`).

---

## Complete Feature Overview

### 1. Android TV Launcher (`com.omarchytv.home`)
- **Authentic Omarchy Desktop Look on TV**: Hyprland-style windows (`BoxView` 2 px borders with `btop`-style cut-out legends), Waybar-style top bar, Walker-style fuzzy search (`long OK` or `Search`), and `CaskaydiaMono` font.
- **Workspaces 1–5**: `1` Home, `2` TV & Inputs, `3` All Apps, `4` PC Link & AI, `5` System & Settings. Switch workspaces with number keys `1–5` or the top bar.
- **Native Grok Bot · Omarchy TUI (`AskActivity`)**: Built-in terminal assistant on the Home shelf supporting standalone local TV commands, voice recognition, paired PC CLI streaming, and 1-click launch of full AI WebApps (`Grok Web`, `Grok (X)`, `ChatGPT`, `Claude`, `Hermes`).
- **One-Press Live TV & HDMI Inputs**: Supports Sony BRAVIA, Sharp AQUOS, Google TV, AOSP TV, DTVKit, TCL, Hisense, Philips, and standard Android TV Input Framework (`TIF`) channels.
- **26 Bundled MIT Themes & 4K Wallpapers**: Instant live theme switching with bundled 4K WebP backgrounds, `"next wallpaper"` cycling, custom image support, procedural aurora fallback, and custom theme packs pushed from your PC.
- **Customizable Home Panels**: Toggle individual panels (Clock, Weather with `°C / °F` switch and auto-location, PC Stats, AI Credits, Deploys, Terminal) and move them on a **12×8 grid** with **Arrange panels**.
- **App Shelf & Hidden Apps Manager**: Reorder or pin favorite apps, hide unwanted system tiles (including optional Sony bloatware toggle), restore hidden tiles in Workspace 5 (`System → Hidden apps`), and push custom 16:9 PNG app banners (`omarchy-tv icons push`).
- **37 `tte.js` ASCII Screensaver Effects**: Runs all 37 `TerminalTextEffects` / `tte.js` animations in a dedicated `:saver` process with configurable idle timeout (`1 / 2.5 / 5 / 10 min` or `Never`), **Effect speed (`Slow / Normal / Fast`)**, native fallback for legacy WebViews, and Android Daydream (`OmarchyDream`) support.
- **Cast to TV (opt-in)**: Send videos, audio (Media3 ExoPlayer), images, text, and links from your paired PC/Mac directly to the TV.
- **Crash Watchdog & Safe Debloat**: Independent `:watchdog` process that restores the stock launcher if 3 crashes ever occur within 5 minutes; safe debloat scripts use only reversible `pm disable-user --user 0` (never `pm uninstall`, never touching DNS or `setupwraith`).

### 2. PC / macOS Plugin (`omarchy-tv` + `omarchy-link`) — [pc-plugin/](pc-plugin/README.md)
- **SPAKE2 Encrypted Pairing**: Pair with a 6-digit code shown on the TV; all requests are signed with per-PC `OTV1` HMAC-SHA256 tokens over LAN.
- **Live PC Telemetry**: Pushes CPU, RAM, active media player (`playerctl`), and deploy status every 5 seconds only while the TV Home screen is visible.
- **Theme Sync & Custom Theme Push**: Syncs your active Omarchy desktop theme to the TV (`omarchy-tv themes push` uploads custom themes & 4K wallpapers, up to 50 MB total on TV).
- **Zero-API-Cost AI CLI Bridge**: Answers prompts from the TV's **Grok Bot · Omarchy TUI** using your already-signed-in desktop CLIs (`grok`, `claude`, `codex`, `gemini`, `hermes`, or local `ollama`).
- **Native MCP Server (`omarchy-tv mcp`)**: Exposes your TV to desktop AI agents over stdio (`--stdio`) or localhost HTTP (`--http --port 8990`, bound to `127.0.0.1` with a 256-bit Bearer token in `~/.config/omarchy-tv/mcp-token`).
- **Low-Latency H.264 Desktop Screen Mirroring ("PC Screen")**: Streams your Linux desktop to the TV via `gpu-screen-recorder` or `wf-recorder`.
- **Wireless Updater (`omarchy-tv update`)**: Updates Android TV via `adb` (verifying signing certificate and versionCode) and LG webOS via `ares-install`.

### 3. Android Smartphone Companion (`OmarchyTV Mobile`, `178 KB`) — [mobile-companion/](mobile-companion/README-MOBILE.md)
- **No-PC Wireless TV Installer**: Scans your `/24` Wi-Fi LAN, downloads the latest release from GitLab/GitHub, verifies its SHA-256 checksum, performs a pure-Java 2048-bit RSA Wireless ADB handshake (`:5555`), installs OmarchyTV (`pm install -r`), and pins it as your default Home launcher in one tap.
- **Live Theme Switcher & Touch Remote**: Switch all **26 MIT themes** in real time, control the TV with a tactile D-Pad and media keys, upload custom phone photos as TV wallpapers, and run safe 1-tap reversible brand debloat (`pm disable-user --user 0` / `pm enable`).
- **LG webOS & Universal Smart TV Bridge (`:8765`)**: Serves themes/wallpapers to LG webOS TVs and hosts the full 1080p HTML5 OmarchyTV Web Launcher (`http://<phone-ip>:8765/tv`) for **Samsung Tizen** and **Hisense VIDAA** TVs.

---

## All 26 Bundled MIT Themes & Repositories

Every theme bundled in OmarchyTV `2.12.0-beta` is **100% MIT-licensed** and ships inside the APK with its palette (`assets/omarchy_themes.json`) and verified 4K WebP wallpapers (`assets/wallpapers/<theme>/`). Full file-by-file provenance is documented in **[THIRD-PARTY.md](THIRD-PARTY.md)**, **[NOTICE](NOTICE)**, and **[launcher/WALLPAPER-PROVENANCE.csv](launcher/WALLPAPER-PROVENANCE.csv)**.

| # | Theme ID | Accent | Bundled 4K Wallpapers | Author | MIT Repository / Source |
|---|---|---|---|---|---|
| 1 | **`tokyo-night`** *(default)* | `#7aa2f7` | `01-liftoff-sunset.webp`, `09-omarchy.webp` | David Heinemeier Hansson / Omarchy · Wallpaper by Tom Ballard ([@tcballard](https://x.com/tcballard), with permission) | [basecamp/omarchy](https://github.com/basecamp/omarchy) · [tcballard/omarchy-theme-tokyo-liftoff](https://github.com/tcballard/omarchy-theme-tokyo-liftoff) |
| 2 | **`jade-horse`** *(new in 2.12)* | `#8bcbb1` | `01-ink-horse.webp`, `02-carved-jade-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp` | David Heinemeier Hansson ([@dhh](https://x.com/dhh)) | [dhh/omarchy-jade-horse-theme](https://github.com/dhh/omarchy-jade-horse-theme) (MIT) |
| 3 | **`year-of-the-horse`** *(new in 2.12)* | `#e5ce78` | `01-ink-horse.webp`, `02-paper-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp` | David Heinemeier Hansson ([@dhh](https://x.com/dhh)) | [dhh/omarchy-year-of-the-horse-theme](https://github.com/dhh/omarchy-year-of-the-horse-theme) (MIT) |
| 4 | **`hermarchy`** *(new in 2.12)* | `#61d6ff` | `01-hermarchy-command.webp`, `02-hermarchy.webp`, `03-hermarchy.webp`, `04-omarchy.webp` | Archer Clawbot | [archer-clawbot/omarchy-hermarchy-theme](https://github.com/archer-clawbot/omarchy-hermarchy-theme) (MIT) |
| 5 | **`catppuccin`** | `#89b4fa` | `04-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/catppuccin`)](https://github.com/basecamp/omarchy/tree/master/themes/catppuccin) (MIT) |
| 6 | **`catppuccin-latte`** | `#1e66f5` | `02-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/catppuccin-latte`)](https://github.com/basecamp/omarchy/tree/master/themes/catppuccin-latte) (MIT) |
| 7 | **`ethereal`** | `#7d82d9` | `03-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/ethereal`)](https://github.com/basecamp/omarchy/tree/master/themes/ethereal) (MIT) |
| 8 | **`everforest`** | `#7fbbb3` | `02-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/everforest`)](https://github.com/basecamp/omarchy/tree/master/themes/everforest) (MIT) |
| 9 | **`flexoki-light`** | `#205EA6` | `02-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/flexoki-light`)](https://github.com/basecamp/omarchy/tree/master/themes/flexoki-light) (MIT) |
| 10 | **`gruvbox`** | `#7daea3` | `06-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/gruvbox`)](https://github.com/basecamp/omarchy/tree/master/themes/gruvbox) (MIT) |
| 11 | **`hackerman`** | `#82FB9C` | `03-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/hackerman`)](https://github.com/basecamp/omarchy/tree/master/themes/hackerman) (MIT) |
| 12 | **`kanagawa`** | `#dcd7ba` | `02-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/kanagawa`)](https://github.com/basecamp/omarchy/tree/master/themes/kanagawa) (MIT) |
| 13 | **`last-horizon`** | `#b59790` | `01-omarchy.webp` | containerscrew / Omarchy contributors | [containerscrew/omarchy-last-horizon-theme](https://github.com/containerscrew/omarchy-last-horizon-theme) · [basecamp/omarchy](https://github.com/basecamp/omarchy) (MIT) |
| 14 | **`lumon`** | `#8bc9eb` | `03-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/lumon`)](https://github.com/basecamp/omarchy/tree/master/themes/lumon) (MIT) |
| 15 | **`lupine`** | `#3264eb` | `06-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/lupine`)](https://github.com/basecamp/omarchy/tree/master/themes/lupine) (MIT) |
| 16 | **`matte-black`** | `#e68e0d` | `04-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/matte-black`)](https://github.com/basecamp/omarchy/tree/master/themes/matte-black) (MIT) |
| 17 | **`miasma`** | `#78824b` | `03-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/miasma`)](https://github.com/basecamp/omarchy/tree/master/themes/miasma) (MIT) |
| 18 | **`nord`** | `#81a1c1` | `04-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/nord`)](https://github.com/basecamp/omarchy/tree/master/themes/nord) (MIT) |
| 19 | **`osaka-jade`** | `#509475` | `04-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/osaka-jade`)](https://github.com/basecamp/omarchy/tree/master/themes/osaka-jade) (MIT) |
| 20 | **`retro-82`** | `#faa968` | `09-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/retro-82`)](https://github.com/basecamp/omarchy/tree/master/themes/retro-82) (MIT) |
| 21 | **`ristretto`** | `#f38d70` | `05-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/ristretto`)](https://github.com/basecamp/omarchy/tree/master/themes/ristretto) (MIT) |
| 22 | **`rose-pine`** | `#56949f` | `04-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/rose-pine`)](https://github.com/basecamp/omarchy/tree/master/themes/rose-pine) (MIT) |
| 23 | **`solitude`** | `#798186` | `01-omarchy.webp` | containerscrew / Omarchy contributors | [containerscrew/omarchy-solitude-theme](https://github.com/containerscrew/omarchy-solitude-theme) · [basecamp/omarchy](https://github.com/basecamp/omarchy) (MIT) |
| 24 | **`starship`** | `#ff9f0a` | `01-omarchy.webp` | vyrx-dev / Omarchy contributors | [vyrx-dev/omarchy-starship-theme](https://github.com/vyrx-dev/omarchy-starship-theme) · [basecamp/omarchy](https://github.com/basecamp/omarchy) (MIT) |
| 25 | **`vantablack`** | `#8d8d8d` | `05-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/vantablack`)](https://github.com/basecamp/omarchy/tree/master/themes/vantablack) (MIT) |
| 26 | **`white`** | `#6e6e6e` | `04-omarchy.webp` | David Heinemeier Hansson / Omarchy contributors | [basecamp/omarchy (`themes/white`)](https://github.com/basecamp/omarchy/tree/master/themes/white) (MIT) |

---

## Installation & Usage Guide

### 1. Install on Android TV / Google TV / Sony BRAVIA / Sharp AQUOS (`2.12.0-beta`)

#### Option A — Install via ADB from a PC / Mac
1. On your TV, enable Developer Options: **Settings → Device Preferences → About → press Build 7 times**, then enable **USB debugging / Network debugging** in **Developer options** and note the TV's IP address.
2. Connect and install the signed release APK:
   ```bash
   adb connect <tv-ip>:5555
   sha256sum omarchytv-release-2.12.0-beta.apk
   # Expected SHA-256: 9dedc335fb1150afa6027f4123bd295bec8241a4c654842a6be65caff993f035
   apksigner verify --print-certs omarchytv-release-2.12.0-beta.apk
   # Expected Signer #1 SHA-256: 90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d
   adb install -r omarchytv-release-2.12.0-beta.apk
   ```
3. **Set OmarchyTV as the default Home screen (optional):**
   ```bash
   adb shell cmd package set-home-activity --user 0 com.omarchytv.home/.MainActivity
   ```
4. **Set OmarchyTV as the system screensaver (optional):**
   ```bash
   adb shell settings put secure screensaver_components com.omarchytv.home/.OmarchyDream
   adb shell settings put secure screensaver_enabled 1
   ```

#### Option B — Install Wirelessly from Your Android Smartphone (`OmarchyTV Mobile`, no PC needed)
1. Install **`omarchytv-mobile-2.12.0-beta.apk`** (`178 KB`, SHA-256: `42bb62aa6169c52afacc9b477d25f6f95fffe2eeea9f779394606e1a4e5ad0a4`) on your Android phone.
2. Tap **Scan LAN** to auto-discover your TV on `:5555` / `:47800`.
3. Tap **1-Tap Install / Update OmarchyTV** — the phone downloads the release APK, verifies the SHA-256 digest, performs a 2048-bit RSA Wireless ADB handshake, installs the APK via `pm install -r`, and pins OmarchyTV as your Home screen.

Full step-by-step guide: **[launcher/docs/INSTALL.md](launcher/docs/INSTALL.md)** · Safe debloat: **[docs/DEBLOAT.md](docs/DEBLOAT.md)** · AI-assisted setup: **[docs/AI-ASSISTED-SETUP.md](docs/AI-ASSISTED-SETUP.md)**.

---

### 2. Using the TV Launcher & Remote Controls

- **Switch Workspaces (`1–5`)**: Press number keys `1`–`5` on your remote, or press **▲ Up** to focus the top Waybar and select `1` (Home), `2` (TV & HDMI Inputs), `3` (All Apps), `4` (PC Link & AI), or `5` (System & Settings).
- **Open the Main Omarchy Menu**: Click the `[ ☰ ]` icon on the top-left of the Waybar, or press the **MENU** key on your remote.
- **Open Walker Fuzzy Search**: Long-press **OK / Center** on the Home screen (or press the Search key) to search apps, themes, settings, and AI commands (`> grok bot`, `> ask`).
- **Switch Themes & 4K Wallpapers**: Open **Menu → Themes** (scrolls smoothly through all 26 MIT themes with D-pad ▲/▼) or **Menu → Wallpaper → Next background** (`Sync PC wallpaper` is off by default so your TV's bundled 4K MIT wallpapers are preserved).
- **Customize App Tiles & Hidden Apps**: Long-press **OK** (or press **MENU**) on any app tile to move it, pin/unpin it from the Home row, or select **Hide from launcher**. To unhide any app later, open **Workspace 5 (`System`) → Hidden apps**.

---

### 3. Using the Native Grok Bot · Omarchy TUI on Your TV

Click the **Grok Bot** tile (`grokbot@tv:~$ > GROK BOT [ omarchy · tui ]`) on the Home shelf — or open **Menu → Grok Bot & AI → Grok Bot (Omarchy TUI)** — to launch the native Omarchy terminal assistant.

You can interact using the **1-click D-pad quick-action chips** at the top of the window, your **TV voice remote (`[ 🎤 voice ]`)**, or the **`grokbot@omarchytv:~$` command prompt**:

| Command / Action | What It Does (Works Offline on the TV!) |
|---|---|
| `theme <name>` (e.g. `theme jade-horse`, `theme year-of-the-horse`, `theme hermarchy`) | Immediately switches the active Omarchy theme and loads its bundled 4K MIT wallpaper |
| `next theme` / `[ ⏭ next theme ]` / `[ 🎨 themes ▾ ]` | Cycles to the next MIT theme or opens the 26-theme popup selector |
| `themes` | Lists all 26 bundled MIT themes in the terminal transcript |
| `wallpaper` / `next wallpaper` / `[ 🖼 wallpaper ]` | Cycles through the bundled 4K wallpapers for the current theme |
| `screensaver` / `[ ✦ screensaver ]` | Starts the 37-effect `tte.js` ASCII screensaver immediately |
| `speed slow` · `speed normal` · `speed fast` | Sets the screensaver animation speed |
| `open <app>` (e.g. `open YouTube`, `open Netflix`, `open TV`) | Launches any installed Android TV app by name or opens Live TV |
| `apps` / `[ 📦 apps ]` | Lists all installed TV apps in the terminal window |
| `status` / `mcp` / `[ 📊 status ]` | Displays TV hardware, Android/SDK version, active theme/wallpaper, and the TV MCP endpoint (`http://<tv-ip>:47800/mcp`) |
| `web` / `grok.com` / `chatgpt` / `claude` / `hermes` / `[ 🌐 grok.com ]` / `[ 🌐 web ▾ ]` | Opens the full browser WebApp in the isolated `:web` process (`WebAppActivity`) with persistent login and D-pad cursor |
| *Any open-ended question* (when paired with a PC via `omarchy-link`) | Streams the answer from your PC's authenticated AI CLI (`grok`, `claude`, `codex`, `gemini`, `hermes`, `ollama`) with optional TTS readout |

---

### 4. PC / macOS Plugin & MCP Server (`omarchy-tv-pc-plugin-2.12.0-beta.tar.gz`)

```bash
tar -xzf omarchy-tv-pc-plugin-2.12.0-beta.tar.gz
cd pc-plugin
mkdir -p ~/.local/share ~/.local/bin
cp -r omarchy-link ~/.local/share/omarchy-link
cp -r omarchy-tv   ~/.local/share/omarchy-tv
ln -sf ~/.local/share/omarchy-link/bin/omarchy-link ~/.local/bin/omarchy-link
ln -sf ~/.local/share/omarchy-tv/bin/omarchy-tv     ~/.local/bin/omarchy-tv

# Pair with your TV (open Logo menu or Workspace 4 on TV → Connect Omarchy Linux):
omarchy-link pair <tv-ip> --code 123456
omarchy-tv

# Start the MCP server for Grok Bot / Claude Desktop / Cursor / Hermes:
omarchy-tv mcp --stdio                 # stdio MCP mode (JSON-RPC 2.0, protocolVersion 2024-11-05)
omarchy-tv mcp --http --port 8990      # HTTP MCP mode (127.0.0.1:8990, token in ~/.config/omarchy-tv/mcp-token)
```

Full PC plugin documentation: **[pc-plugin/README.md](pc-plugin/README.md)** and **[pc-plugin/omarchy-tv/README.md](pc-plugin/omarchy-tv/README.md)**.

---

### 5. LG webOS TV — Experimental (`2.11.0-testing`, not beta)
An experimental **`testing`** edition for **LG webOS TVs** (`omarchytv-webos-2.11.0-testing.ipk`) is available in [`webos/`](webos/INSTALL-WEBOS.md):
- **Install Guide:** **[webos/INSTALL-WEBOS.md](webos/INSTALL-WEBOS.md)**
- **Release Notes & Checksums:** **[webos/RELEASE-2.11.0-testing-webos.md](webos/RELEASE-2.11.0-testing-webos.md)**

---

## Compatible Devices
- **Works**: Android TV and Google TV devices (Android 7+). Tested on Sony KD-55XE9005 (Android 9), Google TV Streamer (Android 14), Sharp AQUOS, and Noblex/Hisense (Android 11). Needs network debugging / adb.
- **Experimental (`testing`)**: **LG webOS TVs** (webOS 3.x+ via Developer Mode / `webOS Dev Manager` or `ares-install`; see [webos/INSTALL-WEBOS.md](webos/INSTALL-WEBOS.md)).
- **Universal WebTV Browser Mode**: Samsung Tizen and Hisense VIDAA via `OmarchyTV Mobile` (`http://<phone-ip>:8765/tv`).
- **Untested**: Fire OS devices (Fire TV Stick 4K Max / 4K Plus, Android-based) and projectors with Android TV (e.g. JMGO global versions).
- **Not supported natively**: Fire TV Stick 4K Select (Amazon Vega OS, not Android), Roku, Apple TV.

## Tested TVs
| TV | Android | WebView | OmarchyTV | Status | Notes |
|---|---|---|---|---|---|
| Sony KD-55XE9005 (2017) | 9 | 138 | 2.12.0-beta | ok | primary development & test TV |
| Android TV emulator (API 28, x86) | 9 | 66 | 2.12.0-beta | ok (software rendering) | tte.js needs WebView ≥ 72: fallback used |
| Google TV Streamer | 14 | ? | 2.11.0-beta | ok (community) | tested by @TheFifeDawg |
| Sharp AQUOS Android TV | 11+ | ? | 2.12.0-beta | ok (community) | Live TV `jp.co.sharp.av.android.aquostvapp` & scrollable menus added; reported & tested by @x_andersonleite |
| Noblex TV (Hisense platform) | 11 | ? | 2.11.0-beta | ok (community) | tested by @ilafayajose |

Tested yours? Open an issue with the "TV report" template.

## Trademarks
Netflix, Prime Video, YouTube, Google, Android, Android TV, Google TV, Chromecast, Sony, BRAVIA, Sharp, AQUOS, LG, webOS, X, Disney+, Spotify
and all other product names, logos and app icons are trademarks of their respective owners. They appear only to
identify apps installed on your TV; app icons are loaded from the TV and are not bundled. "Omarchy" and its logo
are the Omarchy project's branding. OmarchyTV is an unofficial fan project, not affiliated with or endorsed by any
of them.

## Thanks
- A huge thank you to **DHH** ([@dhh](https://x.com/dhh)) for creating Omarchy ([omarchy.org](https://omarchy.org)), the inspiration behind this project, for his kind support of OmarchyTV, and for his MIT themes **[`jade-horse`](https://github.com/dhh/omarchy-jade-horse-theme)** and **[`year-of-the-horse`](https://github.com/dhh/omarchy-year-of-the-horse-theme)**. ❤️ OmarchyTV is an unofficial community project and is not affiliated with Omarchy.
- **Anderson Leite** ([@x_andersonleite](https://x.com/x_andersonleite) / [@anderson-leite](https://gitlab.com/anderson-leite)): Sharp AQUOS testing, Issue #3 / #4 / #5 reports, and MR !1.
- **Michael Pfeifer** ([@TheFifeDawg](https://x.com/TheFifeDawg)): Google TV testing, `setupwraith` Wi-Fi diagnosis, and Android 11+ `<queries>` fix.
- **[@ilafayajose](https://gitlab.com/ilafayajose)** and **@wielorzeczownik**: community bug reports and testing.

## Credits and Third-Party Software
- Inspired by **[tv-vibehack](https://github.com/Gathin23/tv-vibehack)** by Gathin (MIT).
- **Omarchy** by David Heinemeier Hansson and contributors ([github.com/basecamp/omarchy](https://github.com/basecamp/omarchy), MIT): logo, icon, theme palettes, wordmark backgrounds, plus **[`omarchy-jade-horse-theme`](https://github.com/dhh/omarchy-jade-horse-theme)** and **[`omarchy-year-of-the-horse-theme`](https://github.com/dhh/omarchy-year-of-the-horse-theme)** (MIT).
- **[`omarchy-hermarchy-theme`](https://github.com/archer-clawbot/omarchy-hermarchy-theme)** by Archer Clawbot (MIT).
- **[`omarchy-last-horizon-theme`](https://github.com/containerscrew/omarchy-last-horizon-theme)** and **[`omarchy-solitude-theme`](https://github.com/containerscrew/omarchy-solitude-theme)** by containerscrew (MIT palettes + Omarchy wordmark 4K wallpapers).
- **[`omarchy-starship-theme`](https://github.com/vyrx-dev/omarchy-starship-theme)** by vyrx-dev (MIT palette + Omarchy wordmark 4K wallpaper).
- **"Liftoff Sunset"** (default Tokyo Night wallpaper) by **Tom Ballard** ([@tcballard](https://x.com/tcballard)), from
  [omarchy-theme-tokyo-liftoff](https://github.com/tcballard/omarchy-theme-tokyo-liftoff); original photograph SpaceX
  (public domain per author); included with the author's permission granted on X on Oct 22, 2026. Thank you, Tom!
- **tte.js** by Flavio Copes, **TerminalTextEffects** by ChrisBuilds, **ttfx** by 37signals/omacom (MIT).
- **Free My TV** contributors (MIT): on-device adb client port.
- **Cascadia Code / CaskaydiaMono** (Microsoft, SIL OFL 1.1) with Nerd Fonts patches (MIT).
- **AndroidX / Media3 ExoPlayer** (Apache 2.0).

Full list with sources, licences, modifications and licence texts: [THIRD-PARTY.md](THIRD-PARTY.md), [NOTICE](NOTICE), and [launcher/WALLPAPER-PROVENANCE.csv](launcher/WALLPAPER-PROVENANCE.csv).
Third-party wallpapers whose licence could not be verified are **not** included.

## License
MIT, see [LICENSE](LICENSE).
Copyright (c) 2026 Marco Porro ([x.com/MarcoPorro](https://x.com/MarcoPorro) · [www.marcoporro.it](https://www.marcoporro.it)).
