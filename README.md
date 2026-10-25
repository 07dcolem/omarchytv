# OmarchyTV

**An Omarchy-style home screen for Android TV, plus a desktop link to your Omarchy PC / Mac and zero-API-cost AI & Grok Bot integration.**

Created by **Marco Porro** · based on [tv-vibehack](https://github.com/Gathin23/tv-vibehack) by **Gathin**
· [X / @MarcoPorro](https://x.com/MarcoPorro) · [marcoporro.it](https://www.marcoporro.it)

Published: **25 October 2026 (beta)** · Version **2.12.0-beta** (Android TV, PC/Mac Plugin & Mobile Companion) / **2.11.0-testing** (LG webOS experimental) · License **MIT**

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

## What's New in `2.12.0-beta` (`versionCode 20`)

- **26 100%-MIT Themes & Bundled 4K Wallpapers:**
  - Added 3 new 100%-MIT themes with all their original 4K wallpapers: DHH's **`jade-horse`** (`01-ink-horse.webp`, `02-carved-jade-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp`) and **`year-of-the-horse`** (`01-ink-horse.webp`, `02-paper-horse.webp`, `03-mountain-horses.webp`, `04-omarchy.webp`), plus Archer Clawbot's **`hermarchy`** (`01-hermarchy-command.webp`, `02-hermarchy.webp`, `03-hermarchy.webp`, `04-omarchy.webp`).
  - Added 4K Omarchy wordmark wallpapers (`01-omarchy.webp`) for **`last-horizon`**, **`solitude`**, and **`starship`**, so all **26 bundled MIT themes** include at least one 100%-MIT 4K wallpaper (full provenance in [`THIRD-PARTY.md`](THIRD-PARTY.md), [`NOTICE`](NOTICE), and [`launcher/WALLPAPER-PROVENANCE.csv`](launcher/WALLPAPER-PROVENANCE.csv)).
  - **`Sync PC wallpaper` Toggle (off by default):** Pairing or syncing with your PC never overwrites the TV's bundled 4K MIT wallpaper unless you explicitly enable *Sync PC wallpaper* in the TV's Themes or Wallpaper menu.
- **Zero-API-Cost AI & Grok Bot Integration (3 Modes):**
  1. **Built-in AI WebApps (`> Grok Bot & AI` hub & Home shelf):** Open **Grok Bot** (`grok.com`), **Grok (X)** (`x.com/i/grok`), **ChatGPT** (`chatgpt.com`), **Claude** (`claude.ai`), and **Hermes** (`hermes.nousresearch.com`) directly on the TV in a sandboxed `:web` process with persistent cookies/DOM storage (sign in once) and D-pad spatial navigation + virtual cursor (long-press Back).
  2. **PC / Mac CLI Bridge (`omarchy-link`):** Run `> ask` or `> grok bot` from the TV Walker bar using your already-authenticated PC/Mac CLI tools (`grok`, `claude`, `codex`, `gemini`, `hermes`, or local `ollama`) with zero extra API keys.
  3. **Native MCP Server (TV `/mcp` & PC `omarchy-tv mcp`):** Control the TV from any MCP-compatible AI desktop client or voice assistant (`tv_get_status`, `tv_list_themes`, `tv_set_theme`, `tv_send_key`, `tv_launch_app`, `tv_cast_media`, `tv_show_notification`, `tv_open_ai_webapp`), bound to `127.0.0.1` by default on PC with 256-bit Bearer token auth (`~/.config/omarchy-tv/mcp-token`).
- **Screensaver Effect Speed (`Slow / Normal / Fast`):** Adjust the animation speed for all 37 `tte.js` effects and the native ASCII fallback from the Screensaver menu.
- **Multi-Brand Live TV & Menu Fixes (Community Feedback):**
  - Native **Sharp AQUOS** (`jp.co.sharp.av.android.aquostvapp`) and multi-brand Live TV detection alongside Sony BRAVIA (`com.sony.dtv.tvx`), Google TV (`com.google.android.tv`), TCL, Hisense, and Philips.
  - Full D-pad scrolling across long menus (`Themes` menu scrolls smoothly through all 26 themes on 1080p TVs).
  - Fixed `Hide from launcher` on the Home shelf and app grid, and added a direct **Hidden apps** manager in Workspace 5 (`System`).

Full release notes: **[RELEASE-2.12.0-beta.md](RELEASE-2.12.0-beta.md)** and **[CHANGELOG.md](CHANGELOG.md)**.

---

## Features

### TV launcher (`com.omarchytv.home`)
- **Omarchy look**: Hyprland-style windows, Waybar-style top bar, Walker-style menus, CaskaydiaMono font.
- **Workspaces 1–5** like Hyprland: 1 home, 2 TV, 3 apps, 4 PC, 5 system. Number keys or the bar switch them.
- **TV tile**: one press to Live TV / HDMI inputs (supports Sony BRAVIA, Sharp AQUOS, Google TV, TCL, Hisense, Philips, and standard Android TV Input Framework).
- **Default theme/wallpaper**: "Liftoff Sunset" by **Tom Ballard** ([@tcballard](https://x.com/tcballard),
  [omarchy-theme-tokyo-liftoff](https://github.com/tcballard/omarchy-theme-tokyo-liftoff)), used with permission.
- **Themes**: all **26 MIT Omarchy themes** with bundled 4K MIT wallpapers (`jade-horse`, `year-of-the-horse`, `hermarchy`, `tokyo-night`, and 22 more), "next background", your own image, a procedural fallback, and custom themes pushed from your PC.
- **Grok Bot & AI Hub**: built-in WebApps (**Grok Bot**, **Grok (X)**, **ChatGPT**, **Claude**, **Hermes**) with persistent login and D-pad cursor, `> ask` / `> grok bot` PC CLI prompt, and native `/mcp` JSON-RPC 2.0 server.
- **Panels**: every panel (clock, weather with `°C / °F` switch, PC stats, AI credits, deploys, terminal…) has its own toggle, and **Arrange panels** lets you place them on a 12×8 grid with the remote.
- **Reorder & hide apps** in the row or grid; **Hidden apps** manager in Workspace 5; **custom 16:9 PNG app banners** (`omarchy-tv icons push`); **text tiles** for apps without a banner.
- **Animated OMARCHY logo** (on by default, several text effects).
- **Screensaver**: the 37 effects of `tte.js` / TerminalTextEffects with adjustable **Effect speed (`Slow / Normal / Fast`)**, native fallback for old WebViews, and Android Daydream support.
- **Cast to TV** (opt-in): text, links, images, video and audio from your PC over the paired link.
- **Omarchy Link** (opt-in): SPAKE2 pairing with your Omarchy PC/Mac, HMAC-signed requests, live events.
- **Safe debloat helper**: uses only `pm disable-user --user 0` (never uninstall), never touches DNS (`private_dns_*`) or `setupwraith`; one-press return to the stock launcher.

### PC / Mac side: `omarchy-tv` + `omarchy-link` — [pc-plugin/](pc-plugin/README.md)
- **Pairing** with a 6-digit code shown on the TV (SPAKE2), per-PC token, LAN only.
- **Auto-reconnect** after TV/PC restarts and network drops.
- **Stats** (CPU, RAM, now playing, deploys) every 5 s, only while the TV home is visible.
- **Theme sync and theme push**: the active Omarchy theme follows to the TV (`Sync PC wallpaper` off by default on the TV so bundled 4K MIT wallpapers stay intact); `omarchy-tv themes push` sends custom themes and backgrounds (up to 50 MB total on the TV, strictly validated).
- **Zero-API-Cost AI CLI Bridge**: answers TV `> ask` and `> grok bot` prompts using your local authenticated `grok`, `claude`, `codex`, `gemini`, `hermes`, or `ollama` CLI.
- **Native MCP Server (`omarchy-tv mcp`)**: stdio (`--stdio`) and HTTP (`--http --port 8990`, bound to `127.0.0.1` with a 256-bit Bearer token in `~/.config/omarchy-tv/mcp-token`) MCP bridge for desktop AI agents.
- **APK / IPK update**: `omarchy-tv update` updates Android TV via `adb` (refusing any APK with a different certificate or a lower version) and LG webOS via `ares-install`.
- **LG webOS LAN bridge**: `omarchy-tv webos-serve` exposes `/v1/status`, `/v1/themes`, and `/v1/wallpaper` over LAN for LG webOS TVs.
- **Live screen sharing ("PC Screen")**: your desktop on the TV as a low-latency H.264 stream (`gpu-screen-recorder` or `wf-recorder`, hardware encoding when available, optional audio).
- **Custom app icons**: your own PNG tile for any app, `omarchy-tv icons push` ([how-to](pc-plugin/omarchy-tv/README.md#custom-app-icons-banners)).
- **Remote**: Home, Back, media keys and app launching from the PC; Waybar widget and desktop notifications.

---

## Installation & Usage Guide

### 1. Android TV / Google TV / Sony BRAVIA / Sharp AQUOS (`2.12.0-beta`)

#### Option A — Install via ADB from PC / Mac
1. On your TV, enable Developer Options: **Settings → Device Preferences → About → press Build 7 times**, then enable **USB debugging / Network debugging** in **Developer options** and note the TV's IP address.
2. Connect and install the signed release APK:
   ```bash
   adb connect <tv-ip>:5555
   sha256sum omarchytv-release-2.12.0-beta.apk
   # Expected SHA-256: f1426db057fdc958fe562d1afd57a710b896e2f63d4fa6c2ec6c8ceefdfee11e
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

#### Option B — Install Wirelessly from Your Android Phone (`OmarchyTV Mobile`, `178 KB`, no PC needed)
1. Install **`omarchytv-mobile-2.12.0-beta.apk`** (SHA-256: `42bb62aa6169c52afacc9b477d25f6f95fffe2eeea9f779394606e1a4e5ad0a4`) on your Android phone.
2. Tap **Scan LAN** to auto-discover your TV on `:5555` / `:8999`.
3. Tap **1-Tap Install / Update OmarchyTV** — the phone downloads the latest release, verifies the SHA-256 digest, performs a pure-Java 2048-bit RSA Wireless ADB handshake, installs the APK via `pm install -r`, and pins OmarchyTV as your Home screen.

Full step-by-step guide (English + Italiano): **[launcher/docs/INSTALL.md](launcher/docs/INSTALL.md)**
- Safe, reversible debloat (`pm disable-user --user 0`, never `pm uninstall`, never touches DNS): **[docs/DEBLOAT.md](docs/DEBLOAT.md)**
- Setup with an AI assistant (Claude Code, Codex, Gemini CLI, Cursor, ChatGPT, Grok Bot): **[docs/AI-ASSISTED-SETUP.md](docs/AI-ASSISTED-SETUP.md)**

---

### 2. PC / macOS Plugin & MCP Server (`omarchy-tv-pc-plugin-2.12.0-beta.tar.gz`)

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
omarchy-tv mcp --stdio                 # stdio MCP mode
omarchy-tv mcp --http --port 8990      # HTTP MCP mode (127.0.0.1:8990, token in ~/.config/omarchy-tv/mcp-token)
```

Full PC plugin documentation: **[pc-plugin/README.md](pc-plugin/README.md)** and **[pc-plugin/omarchy-tv/README.md](pc-plugin/omarchy-tv/README.md)**.

---

### 3. LG webOS TV — Experimental (`2.11.0-testing`, not beta)
An experimental **`testing`** edition for **LG webOS TVs** (`omarchytv-webos-2.11.0-testing.ipk`) is available in [`webos/`](webos/INSTALL-WEBOS.md):
- **Install Guide:** **[webos/INSTALL-WEBOS.md](webos/INSTALL-WEBOS.md)**
- **Release Notes & Checksums:** **[webos/RELEASE-2.11.0-testing-webos.md](webos/RELEASE-2.11.0-testing-webos.md)**
- **Direct Downloads:**
  - [`omarchytv-webos-2.11.0-testing.ipk`](https://gitlab.com/piermark/omarchytv/-/releases) (SHA-256: `04eb928640a0212cad83457ad50b502bc81da440445e33ea2eee95e6eefcc9df`)
  - [`omarchy-tv-pc-plugin-2.12.0-beta.tar.gz`](https://gitlab.com/piermark/omarchytv/-/releases) (SHA-256: `2aef33b30e38eba6eb4355ad597bf382bb5e7210be59d7070d6b5f509765bd0c`)

---

### 4. OmarchyTV Mobile (`2.12.0-beta` — Android Phone Installer & Companion)
**OmarchyTV Mobile** (`com.omarchytv.mobile`, `omarchytv-mobile-2.12.0-beta.apk`, `178 KB`) is the no-PC Android smartphone companion and wireless installer for **Android TV / Google TV, LG webOS, Samsung Tizen & Hisense VIDAA**:
- **Android TV / Google TV Mode (`ADB :5555` + `omarchy-link :8999` / `:47800`):** Parallel `/24` LAN subnet scanner, pure-Java Wireless ADB 2048-bit RSA handshake & `sync:` APK installer (`pm install -r`), 1-tap default Home launcher pinning, HMAC-SHA256 `omarchy-link` client (live theme switching across all **26 MIT Omarchy themes**, tactile D-Pad & media remote, custom phone wallpaper & banner upload), and safe reversible brand debloat (`pm disable-user --user 0` / `pm enable` for **Sony Bravia**, **Google TV Streamer**, **Sharp AQUOS**, **TCL**, **Hisense**, and **Xiaomi**) guarded by an immutable `PROTECTED_PACKAGES` denylist.
- **LG webOS Mode (`WebOsBridgeServer :8765` + `.ipk` Inspector & Server):** Runs an embedded `:8765` HTTP bridge server on the phone (`/v1/status`, `/v1/themes`, `/v1/wallpaper`) so LG webOS TVs can sync themes, wallpapers, and remote keys directly from an Android phone without a Linux PC, plus `.ipk` Debian `ar` verification and LAN serving (`/omarchytv.ipk`).
- **Samsung Tizen, Hisense VIDAA & Universal Smart TV Mode (`http://<phone-ip>:8765/tv`):** Serves the full 1080p HTML5/Canvas OmarchyTV Web Launcher (with all 26 MIT themes) directly from the phone to any Smart TV web browser with real-time theme & D-Pad remote sync, plus 1-tap Samsung Tizen SmartView (`:8001/api/v2/`) auto-launch.
- **Documentation & Build Guide:** **[mobile-companion/README-MOBILE.md](mobile-companion/README-MOBILE.md)**

---

## Compatible devices
- **Works**: Android TV and Google TV devices (Android 7+). Tested on Sony KD-55XE9005 (Android 9), Google TV Streamer (Android 14), Sharp AQUOS, and Noblex/Hisense (Android 11). Needs network debugging / adb.
- **Experimental (`testing`)**: **LG webOS TVs** (webOS 4.0+ via Developer Mode / `webOS Dev Manager` or `ares-install`; see [webos/INSTALL-WEBOS.md](webos/INSTALL-WEBOS.md)). Community feedback from LG webOS TV users is welcome!
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
- A huge thank you to **DHH** ([@dhh](https://x.com/dhh)) for creating Omarchy ([omarchy.org](https://omarchy.org)), the inspiration behind this project, for his kind support of OmarchyTV, and for his MIT themes **`jade-horse`** and **`year-of-the-horse`**. ❤️ OmarchyTV is an unofficial community project and is not affiliated with Omarchy.
- **Anderson Leite** ([@x_andersonleite](https://x.com/x_andersonleite) / [@anderson-leite](https://gitlab.com/anderson-leite)): Sharp AQUOS testing, Issue #3 / #4 / #5 reports, and MR !1.
- **Michael Pfeifer** ([@TheFifeDawg](https://x.com/TheFifeDawg)): Google TV testing, `setupwraith` Wi-Fi diagnosis, and Android 11+ `<queries>` fix.
- **[@ilafayajose](https://gitlab.com/ilafayajose)** and **@wielorzeczownik**: community bug reports and testing.

## Credits and third-party software
- **tv-vibehack / cleanyourtv** by Gathin (MIT): the original project this is built on
  ([original README](docs/UPSTREAM-README-tv-vibehack.md)).
- **Omarchy** by David Heinemeier Hansson and contributors (MIT): logo, icon, theme palettes, wordmark backgrounds, plus **`omarchy-jade-horse-theme`** and **`omarchy-year-of-the-horse-theme`** (MIT).
- **`omarchy-hermarchy-theme`** by Archer Clawbot (MIT).
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
Copyright (c) 2026 Gathin · Copyright (c) 2026 Marco Porro (OmarchyTV).
