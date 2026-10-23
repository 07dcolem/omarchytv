# omarchy-tv — front-end Omarchy per OmarchyTV / Omarchy front-end for OmarchyTV

Comando `omarchy-tv`, costruito sopra **omarchy-link** (pairing, link firmato, sessione Waybar). MIT, © 2026 Marco Porro.
Solo libreria standard Python; Pillow facoltativo (sfondi → WebP), altrimenti ffmpeg.

| Comando | Cosa fa |
|---|---|
| `omarchy-tv` / `menu` | menu Walker (dmenu, stile `omarchy-menu`), poi `gum choose`, poi lista numerata; colori del tema attivo; notifiche `notify-send` (mako) |
| `pair`, `status`, `cast`, `remote KEY` | delega a `omarchy-link` |
| `themes list / push NAME / push --all / select NAME [BG] / delete NAME` | temi utente `~/.config/omarchy/themes/*` → TV (`PUT /v1/themes/<name>`, ZIP: theme.json + backgrounds ≤3840×2160), max **50 MB** in totale sulla TV |
| `screen start [--audio] / stop` | "Schermo PC" live (opt-in): gpu-screen-recorder (hw) o wf-recorder (VAAPI se c'è, altrimenti x264 ultrafast/zerolatency) → H.264 MPEG-TS, URL monouso solo per l'IP della TV abbinata; la TV lo riproduce con ExoPlayer (buffer ~0.5 s). Avvio/stop anche dalla TV (icona monitor), il PC chiede conferma |
| `update APK --tv IP:5555 [--yes] [--dry-run]` | solo adb (`install -r`, mai `-d`/uninstall); rifiuta cert ≠ `90aa68d9…a33d` o versionCode non maggiore |
| `stats` | mostra il payload; la sessione omarchy-link lo invia **ogni 5 s solo con la home TV visibile** (`statsIntervalS`) |

Config omarchy-link (`~/.config/omarchy-link/config.json`): `screenAudio` (false), `screenFps` (30), `screenHwEncode` (true),
`screenMirrorFromTv` ("confirm" | "allow" | "off"), `statsIntervalS` (5).

## Perché non Miracast vero / why not real Miracast
Miracast = Wi-Fi Direct P2P + RTSP/RTP + HDCP. Su Linux il P2P dipende da driver/firmware della scheda (spesso niente
P2P GO concorrente con la Wi-Fi normale), da wpa_supplicant/iwd con P2P abilitato e da uno stack sorgente (gnome-network-displays,
MiracleCast) che non è mantenuto in modo affidabile su Hyprland; molte TV Android (Sony incluse) accettano solo sorgenti
certificate e la connessione P2P scollega spesso la Wi-Fi del PC. Lo streaming H.264 sulla LAN tramite il link già abbinato
dà latenza simile (0.5–1.5 s attesi su hardware reale), funziona con qualsiasi scheda e resta cifrato/autorizzato dal pairing
per il controllo (lo stream video è HTTP in chiaro sulla LAN, URL casuale monouso, solo l'IP della TV).

## Custom app icons

Since **2.11.0-beta** you can replace the tile image (banner) of any app on the TV home with your own PNG.
It needs **launcher 2.11.0 or newer** on the TV; with an older launcher `omarchy-tv icons` says
"This TV launcher has no custom banners yet: update OmarchyTV." Without a custom file, the app's own banner is used.

**1. Find the app's package name.** On a paired PC, `omarchy-link apps` prints every TV app as `label<TAB>package`.
Without the plugin: `adb shell pm list packages` (e.g. Netflix is `com.netflix.ninja`).

**2. Make the image.** PNG only (checked by its signature), **max 1 MB**. Tiles are 16:9 (198×111 dp at the
largest size) and the image fills the tile with a centre crop, so use 16:9: 320×180 (the Android TV banner size)
or 640×360. Larger images are scaled down to about 640 px wide.

**3. Put it on the PC** as `~/.config/omarchy-tv/banners/<package>.png`, e.g.
`~/.config/omarchy-tv/banners/com.netflix.ninja.png`. Files whose name is not a valid package name are ignored.

**4. Send it to the TV:**

| Command | What it does |
|---|---|
| `omarchy-tv icons` | menu: push, list or delete |
| `omarchy-tv icons list` | lists the custom banners stored **on the TV** |
| `omarchy-tv icons push PACKAGE` | sends `~/.config/omarchy-tv/banners/PACKAGE.png` (replaces the one on the TV, if any) |
| `omarchy-tv icons push --all` (or just `push`) | sends every `<package>.png` in that folder |
| `omarchy-tv icons delete PACKAGE` | removes it from the TV, the app's own banner comes back (without PACKAGE: pick from a list) |

The TV home refreshes by itself after a push or delete. The TV keeps **up to 200** custom banners.

**Without the PC plugin** you can copy the file with adb into the launcher's files folder:

```sh
adb push com.netflix.ninja.png /sdcard/Android/data/com.omarchytv.home/files/banners/com.netflix.ninja.png
```

It shows up the next time you return to the home screen; delete the file to go back to the original banner.

Use only images you have the right to use (your own artwork, or images whose licence allows it). Nothing is
downloaded or bundled: OmarchyTV shows only the files you provide.

## Language

The menus and messages follow the PC language automatically (`LC_ALL` > `LC_MESSAGES` > `LANG`).
Italian and English are supported; any other language falls back to English.

To force one, set `"language": "it"`, `"en"` or `"auto"` (the default) in `~/.config/omarchy-link/config.json`,
or for a single run: `LC_ALL=it_IT.UTF-8 omarchy-tv`.

`omarchy-link` messages are English-only for now.

## Test
`python3 tests/test_update.py && python3 tests/test_themes.py` (senza TV).
