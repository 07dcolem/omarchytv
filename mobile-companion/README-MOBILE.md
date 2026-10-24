# OmarchyTV Mobile (`com.omarchytv.mobile` v2.11.0-beta)

**OmarchyTV Mobile** (`omarchytv-mobile-2.11.0-beta.apk`) is the official 100% original MIT-licensed Android smartphone companion and wireless installer for **OmarchyTV**, supporting **Android TV / Google TV, LG webOS, Samsung Tizen, Hisense VIDAA, and all Smart TVs**.

## Universal Smart TV Architecture

1. **Android TV / Google TV (`ADB :5555` + `omarchy-link :8999` / `:47800`):**
   - **Parallel `/24` LAN Subnet Scanner:** Probes ports `8999` (`omarchy-link` daemon), `5555` (Wireless ADB), `47800` (Omarchy Link v1 socket), and `8001` (Samsung SmartView).
   - **Pure-Java Wireless ADB over TCP (`AdbTcpClient.java`):** Generates a 2048-bit RSA keypair (`omarchytv@mobile\0`), encodes the 524-byte little-endian Android `RSAPublicKey` struct with Montgomery parameters, performs `CNXN` + `AUTH`, pushes `.apk` payloads via `sync:` (`SEND`/`DATA`/`DONE`/`OKAY`) to `/data/local/tmp/omarchytv.apk`, runs `pm install -r`, and pins `com.omarchytv.launcher/.HomeV29` & `com.omarchytv.home/.MainActivity`.
   - **HMAC-SHA256 `omarchy-link` Client (`OmarchyLinkClient.java`):** Signs requests with both `Authorization: OTV1 ...` and `X-Omarchy-Signature: sha256=...` for real-time theme switching (`PUT /v1/theme`), tactile D-Pad & media remote keys (`POST /v1/remote/key`), AI/terminal prompts (`POST /v1/prompt`), custom wallpaper uploads (`PUT /v1/wallpaper`), and custom app banners (`PUT /v1/banners/<pkg>`).
   - **Safe Reversible Debloat (`DebloatProfiles.java`):** Uses `pm disable-user --user 0 <pkg>` and 1-tap `pm enable <pkg>` with brand profiles (`Sony Bravia`, `Google TV Streamer`, `Sharp AQUOS`, `TCL`, `Hisense`, `Xiaomi`) and an immutable `PROTECTED_PACKAGES` denylist (`com.google.android.tungsten.setupwraith`, `com.google.android.gms`, `com.google.android.apps.mediashell`, Live TV & HDMI packages).

2. **LG webOS TV (`WebOsBridgeServer :8765` + `.ipk` Inspector & Server):**
   - Runs an embedded HTTP server on port `:8765` on the phone's Wi-Fi IP implementing the exact `omarchy-tv webos-serve` JSON & CORS contract (`/v1/status`, `/v1/themes`, `/v1/wallpaper`), allowing an LG webOS TV running OmarchyTV to sync themes, wallpapers, and remote keys directly from the phone without a PC.
   - Fetches `v2.11.0-testing-webos` (`omarchytv-webos-2.11.0-testing.ipk`), validates the Debian `!<arch>` archive and `appinfo.json` (`id == com.omarchytv.home`), and serves `/omarchytv.ipk` over LAN HTTP.

3. **Samsung Tizen, Hisense VIDAA & Universal Smart TV Mode (`http://<phone-ip>:8765/tv` + `:8001` SmartView):**
   - Bundles the full 1080p HTML5/Canvas OmarchyTV Launcher inside `assets/webtv/` and serves it live at `http://<phone-ip>:8765/tv` with real-time theme & D-Pad remote sync from the phone.
   - Includes a 1-tap Samsung Tizen SmartView (`:8001/api/v2/applications/org.tizen.browser`) launcher.

4. **Dual-Mirror Release & Theme Resolution (`GitLabReleaseClient.java`):**
   - Queries **GitLab** (`https://gitlab.com/api/v4/projects/87958120/releases`) as primary mirror and **GitHub** (`https://api.github.com/repos/piermark/omarchytv/releases`) as fallback mirror, verifying SHA-256 digests and signing certificate SHA-256 (`90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d`).

## Building & Testing

```bash
./build-mobile.sh
python3 test_adb_protocol.py
```
