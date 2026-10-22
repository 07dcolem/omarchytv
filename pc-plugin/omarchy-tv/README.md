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

## Test
`python3 tests/test_update.py && python3 tests/test_themes.py` (senza TV).
