# OmarchyTV Mobile `2.11.0-beta` (Universal Smart TV Phone Installer & Companion) — 24 October 2026

**OmarchyTV Mobile** (`com.omarchytv.mobile`, `omarchytv-mobile-2.11.0-beta.apk`) is the official 100% original MIT-licensed Android smartphone companion and wireless installer for **OmarchyTV**. It allows you to discover, install, update, theme, control, and safely debloat your Smart TV directly from an Android phone over local Wi-Fi — **with no PC required**.

---

## Supported TV Platforms (3 Built-in Modes)

### 1. Android TV / Google TV Mode (`ADB :5555` + `omarchy-link :8999` / `:47800`)
- **Parallel `/24` LAN Subnet Scanner (`OmarchyLinkClient.java`):** Automatically discovers Smart TVs on the local Wi-Fi subnet (`:8999` `omarchy-link` daemon, `:5555` Wireless ADB, `:47800` Omarchy Link v1 socket, and `:8001` Samsung SmartView).
- **Pure-Java Wireless ADB Client (`AdbTcpClient.java`):**
  - Generates a persistent 2048-bit RSA keypair (`omarchytv@mobile\0`) and encodes the 524-byte little-endian Android `RSAPublicKey` struct with Montgomery parameters (`n0inv` & `rr`).
  - Performs the full `CNXN` + `AUTH` (`ADB_AUTH_SIGNATURE` / `ADB_AUTH_RSAPUBLICKEY`) handshake over TCP `:5555`.
  - Streams `.apk` binaries via the binary `sync:` protocol (`SEND` / 64 KB `DATA` chunks / `DONE` / `OKAY`) to `/data/local/tmp/omarchytv.apk`, runs `pm install -r -g /data/local/tmp/omarchytv.apk`, and pins OmarchyTV as the default Home launcher (`cmd package set-home-activity`).
- **HMAC-SHA256 `omarchy-link` Client (`OmarchyLinkClient.java`):**
  - Signs requests using both `Authorization: OTV1 <ts>:<nonce>:<hmac>` and `X-Omarchy-Signature: sha256=<hmac>` for compatibility with both `HomeV29` (`:8999`) and `MainActivity` (`:47800`).
  - Supports instant 1-tap theme switching across all **23 official Omarchy themes** (`PUT /v1/theme`), tactile D-Pad + media remote keys (`POST /v1/remote/key`), AI/terminal prompts (`POST /v1/prompt`), custom phone wallpaper upload (`PUT /v1/wallpaper`), and custom app banner upload (`PUT /v1/banners/<pkg>`).
- **Safe Reversible Brand Debloat (`DebloatProfiles.java`):**
  - Uses non-destructive `pm disable-user --user 0 <pkg>` and 1-tap `pm enable <pkg>` restore.
  - Built-in profiles for **Sony Bravia**, **Google TV Streamer / Chromecast**, **Sharp AQUOS**, **TCL**, **Hisense**, and **Xiaomi TV**, guarded by a hardcoded `PROTECTED_PACKAGES` denylist (`com.google.android.tungsten.setupwraith`, `com.google.android.gms`, `com.google.android.apps.mediashell`, Live TV inputs, HDMI inputs, Bluetooth, and Wi-Fi).

### 2. LG webOS Mode (`WebOsBridgeServer :8765` + `.ipk` Inspector & Server)
- **Embedded Phone Bridge Server (`:8765`):** Runs an HTTP server on the phone's Wi-Fi IP implementing the exact `omarchy-tv webos-serve` JSON & CORS API (`/v1/status`, `/v1/themes`, `/v1/wallpaper`), allowing any LG webOS TV running OmarchyTV (`com.omarchytv.home`) to sync themes, wallpapers, and remote keys directly from the phone without a Linux PC.
- **LG webOS `.ipk` Release Fetcher & Validator:** Downloads `omarchytv-webos-2.11.0-testing.ipk`, verifies its SHA-256 digest, inspects the Debian `!<arch>` archive and `appinfo.json` (`id == com.omarchytv.home`), and serves it over LAN at `http://<phone-ip>:8765/omarchytv.ipk`.

### 3. Samsung Tizen, Hisense VIDAA & Universal Smart TV Mode (`http://<phone-ip>:8765/tv`)
- **Universal HTML5/Canvas Smart TV Launcher (`/tv`):** Serves the complete 1080p OmarchyTV Web Launcher (all 5 workspaces `1:home` `2:tv` `3:apps` `4:pc` `5:sys`, 23 official themes, EN/IT/DE locales, °C/°F weather, and 37 `tte.js` screensaver effects) directly from the phone to any Smart TV browser at `http://<phone-ip>:8765/tv`, with live theme and D-Pad remote sync from the phone.
- **1-Tap Samsung Tizen SmartView Launcher:** Launches `http://<phone-ip>:8765/tv` directly on Samsung Tizen TVs via `:8001/api/v2/applications/org.tizen.browser`.

---

## Dual-Mirror Release & Theme Resolution (`GitLabReleaseClient.java`)
- Queries **GitLab** (`https://gitlab.com/api/v4/projects/87958120/releases`) as primary mirror and **GitHub** (`https://api.github.com/repos/piermark/omarchytv/releases`) as automatic fallback mirror for both Android TV (`.apk`) and LG webOS (`.ipk`) releases plus the live `omarchy_themes.json` catalog.

---

## Downloads & Checksums

- **Android Phone APK:** `omarchytv-mobile-2.11.0-beta.apk` (`com.omarchytv.mobile`, `versionCode 21100`, `versionName "2.11.0-beta"`, `minSdk 26`, `targetSdk 34`, `181,522` bytes)
  - **APK SHA-256:** `cb51e5014d8c80311323361dc231ecbbf774238462f1b900adb6ca9e3c89ef21`
  - **Signing Certificate SHA-256:** `90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d` (`CN=OmarchyTV`, APK Signature Scheme v2 + v3 verified)

Documentation & build instructions: **[`mobile-companion/README-MOBILE.md`](https://gitlab.com/piermark/omarchytv/-/blob/main/mobile-companion/README-MOBILE.md)**
