## OmarchyTV `2.11.0-testing` (LG webOS Edition) — 24 October 2026

> **Experimental `testing` release for LG webOS TVs (NOT a beta release).**
> This release brings the **OmarchyTV `2.11.0`** experience to **LG webOS TVs** as an installable `.ipk` package (`com.omarchytv.home`), alongside an updated PC plugin (`omarchy-tv`) that supports both **Android TV** (`.apk` + `omarchy-link`) and **LG webOS** (`.ipk` + `webos-serve`).
> The Android TV release (`v2.11.0-beta`) remains completely unchanged. Community feedback and testing reports from LG webOS TV owners are very welcome!

---

### Highlights (`omarchytv-webos-2.11.0-testing.ipk`)

- **Full `2.11.0` Feature & Visual Parity:**
  - **23 Official Omarchy Themes** (`omarchy_themes.json`) with exact terminal and UI palettes.
  - **Default Theme & Wallpaper:** *Tokyo Night* with Tom Ballard's *"Liftoff Sunset"* wallpaper (used with permission), plus the 20 MIT-licensed official Omarchy wordmark backgrounds (`omarchy.webp`) and procedural canvas fallback. Zero unverified third-party wallpapers.
  - **Hyprland-Style Workspaces `1`–`5`:**
    - `1` **home**: Weather panel, Omarchy PC status panel, AI Credits panel, neofetch terminal + animated ASCII `OMARCHY` logo, and the horizontal app dock.
    - `2` **tv**: One-press launch for LG Live TV (`com.webos.app.livetv`) and HDMI Inputs (`com.webos.app.externalinput.*`), plus custom TV app ID configuration.
    - `3` **apps**: Full filterable application grid with search (`All`, `Streaming`, `Media`, `System`), plus ability to add custom webOS app IDs (`id|Title|Category`) and hide unwanted tiles.
    - `4` **pc**: Live Omarchy Linux PC telemetry (`CPU`, `RAM`, `GPU`, `uptime`, active theme) via the `omarchy-tv webos-serve` LAN HTTP bridge.
    - `5` **sys**: System & WebEngine diagnostics, memory/platform info, and non-destructive LG webOS privacy & ad-limiting guide.
  - **All `2.11.0` Fixes Included:**
    - **°C / °F Temperature Unit Switch:** Weather menu → *Temperature unit* (`°C` default, switches live between Celsius and Fahrenheit via Open-Meteo).
    - **Multi-language UI (English, Italian, German):** Automatically follows the TV locale or can be switched at any time from the menu (`Language: EN / IT / DE`), with all box headers (`weather`, `omarchy · pc`, `ai credits · pc`, `system`, `theme`, `up`) properly localized.
    - **Clean Top-Border Box Titles:** Top panel titles render with clean solid background padding and never overlap the top border line.
  - **37 `tte.js` Screensaver Effects:** Built-in interactive screensaver (`saver/index.html`) powered by `tte.js` / `TerminalTextEffects` (`beams`, `matrix`, `fireworks`, `rain`, `vhstape`, `synthgrid`, `burn`, `decrypt`, and 29 more).
  - **Native LG webOS Integration:**
    - Launches installed webOS apps via the Luna System Bus (`luna://com.webos.applicationManager/launch`).
    - Full support for LG Magic Remote D-pad navigation, cursor/pointer hover & click, number keys `1`–`5` for workspace switching, and the webOS `Back` key (`keyCode 461`).

---

### PC Plugin Updates (`omarchy-tv-pc-plugin-2.11.0-testing.tar.gz`)

- **100% Backwards-Compatible with Android TV (`2.11.0-beta`):** Keeps all existing Android TV commands (`pair`, `themes`, `icons`, `screen`, `cast`, `remote`, `stats`, and `adb` APK updates with signing certificate verification).
- **New `.ipk` Support in `omarchy-tv update`:**
  - `omarchy-tv update omarchytv-webos-2.11.0-testing.ipk --tv lgtv` validates the Debian `ar` archive signature (`!<arch>`), extracts `data.tar.*`, verifies `appinfo.json` (`id == com.omarchytv.home` and version format), and installs onto the target LG TV via `ares-install`.
- **New `omarchy-tv webos-serve` Command:**
  - Runs a zero-dependency LAN HTTP server (`default port 8765`) with CORS headers exposing `/v1/status` (CPU %, RAM %, uptime, active Omarchy theme), `/v1/themes`, and `/v1/wallpaper` for LG webOS TVs.

---

### Downloads & Checksums

- **[`omarchytv-webos-2.11.0-testing.ipk`](https://gitlab.com/piermark/omarchytv/-/raw/main/webos/releases/omarchytv-webos-2.11.0-testing.ipk?inline=false)** (LG webOS package, `com.omarchytv.home`, version `2.11.0`)
  - SHA-256: `04eb928640a0212cad83457ad50b502bc81da440445e33ea2eee95e6eefcc9df`
- **[`omarchy-tv-pc-plugin-2.11.0-testing.tar.gz`](https://gitlab.com/piermark/omarchytv/-/raw/main/webos/releases/omarchy-tv-pc-plugin-2.11.0-testing.tar.gz?inline=false)** (Omarchy Linux PC plugin for Android TV + LG webOS)
  - SHA-256: `44df52534b739b6ca7371283732a3caa57355bf14d86e22d0d9102a142e60a98`

Installation instructions: **[`webos/INSTALL-WEBOS.md`](https://gitlab.com/piermark/omarchytv/-/blob/main/webos/INSTALL-WEBOS.md)**
