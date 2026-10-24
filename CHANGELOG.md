# Changelog

## [2.11.0-beta-mobile] — 2026-10-24 (OmarchyTV Mobile — Universal Smart TV Phone Installer & Companion)

### Added (`mobile-companion/` — `omarchytv-mobile-2.11.0-beta.apk`)
- **OmarchyTV Mobile (`com.omarchytv.mobile`, `2.11.0-beta`):** Official MIT-licensed Android smartphone companion and wireless installer for **Android TV / Google TV, LG webOS, Samsung Tizen, and Hisense VIDAA** (`minSdk 26`, `targetSdk 34`, signed with the official OmarchyTV release certificate `90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`).
- **Pure-Java Wireless ADB over TCP (`AdbTcpClient.java`):** 2048-bit RSA keypair generation, 524-byte Android `RSAPublicKey` struct encoding, `CNXN`/`AUTH` handshake over `:5555`, binary `sync:` (`SEND`/`DATA`/`DONE`/`OKAY`) `.apk` upload, `pm install -r`, and 1-tap default Home launcher pinning.
- **HMAC-SHA256 `omarchy-link` Client (`OmarchyLinkClient.java`):** Parallel `/24` LAN subnet scanner (`:8999`, `:5555`, `:47800`, `:8001`), dual-header HMAC-SHA256 signing (`Authorization: OTV1` + `X-Omarchy-Signature`), live switching across all **23 official Omarchy themes**, tactile D-Pad & media remote, AI/terminal prompt sender, custom wallpaper upload, and custom app banner upload.
- **Safe Reversible Brand Debloat (`DebloatProfiles.java`):** Non-destructive `--user 0` bloatware disable & 1-tap restore profiles for **Sony Bravia**, **Google TV Streamer**, **Sharp AQUOS**, **TCL**, **Hisense**, and **Xiaomi**, guarded by a hardcoded `PROTECTED_PACKAGES` denylist.
- **LG webOS Phone Bridge & Universal WebTV Server (`WebOsBridgeServer.java`):** Embedded `:8765` HTTP bridge server implementing `/v1/status`, `/v1/themes`, `/v1/wallpaper`, `/omarchytv.ipk` (with Debian `!<arch>` and `appinfo.json` inspector), and `/tv` Universal 1080p HTML5/Canvas OmarchyTV Launcher for Samsung Tizen (`:8001` SmartView auto-launch) and Hisense VIDAA TVs.
- **Dual-Mirror Release & Theme Client (`GitLabReleaseClient.java`):** Resolves `.apk` and `.ipk` releases and live `omarchy_themes.json` across both GitLab (`projects/87958120`) and GitHub (`piermark/omarchytv`) with SHA-256 verification.

All OmarchyTV releases stay available on the [Releases page](https://gitlab.com/piermark/omarchytv/-/releases).
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
