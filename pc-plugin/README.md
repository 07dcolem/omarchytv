# OmarchyTV PC plugin (Omarchy Linux)

Two parts, both MIT, © 2026 Marco Porro (see [LICENSE](LICENSE), [NOTICE](NOTICE)):

- **`omarchy-link/`**: the link daemon and CLI: SPAKE2 pairing, signed requests, auto-reconnect, theme sync,
  stats (every 5 s while the TV home is visible), cast, live screen sharing, remote, Waybar widget, notifications.
  Protocol: [omarchy-link/docs/PROTOCOL.md](omarchy-link/docs/PROTOCOL.md).
- **`omarchy-tv/`**: the Omarchy-style front-end (`omarchy-tv`): Omarchy menu via `omarchy-menu-select` (Omarchy 4.5+),
  `walker --dmenu` on older Omarchy, gum / numbered list over SSH, theme push
  (50 MB cap), adb APK update with certificate/version checks, screen start/stop. Uses `omarchy-link/lib` from this folder.

Python 3.10+ standard library only. Optional: Pillow (backgrounds → WebP), ffmpeg, gpu-screen-recorder or wf-recorder
(screen sharing), android-tools (`adb`, `apksigner`/`aapt` for updates), gum, Walker (Omarchy < 4.5), notify-send.

## Install on an Omarchy PC
```bash
git clone <this repo> omarchytv && cd omarchytv/pc-plugin
mkdir -p ~/.local/share ~/.local/bin
cp -r omarchy-link ~/.local/share/omarchy-link          # omarchy-tv also finds it here
cp -r omarchy-tv   ~/.local/share/omarchy-tv
ln -sf ~/.local/share/omarchy-link/bin/omarchy-link ~/.local/bin/omarchy-link
ln -sf ~/.local/share/omarchy-tv/bin/omarchy-tv     ~/.local/bin/omarchy-tv

# On the TV: logo menu → Connect Omarchy Linux (shows a 6-digit code)
omarchy-link pair --code 123456        # or: omarchy-link pair <tv-ip> --code 123456
omarchy-tv                             # menu
```
Optional:
- **Waybar module + session**: see [omarchy-link/README.md](omarchy-link/README.md) (`omarchy-link status --waybar`, `omarchy-link session`).
- **Theme hook**: `omarchy-link/hooks/theme-set` follows `omarchy theme set`.
- **Keybinding** (Hyprland): `bindd = SUPER ALT, T, OmarchyTV, exec, omarchy-tv`.
- **Omarchy menu entry** (Omarchy 4.5+, the documented user extension file `~/.config/omarchy/extensions/omarchy-menu.jsonc`):
  add `"omarchytv": {"icon":"󰔂","label":"OmarchyTV","action":"omarchy-tv"},` inside its `{ }`, then `omarchy menu refresh`.
  (`omarchy-menu-plugin` manages Omarchy *shell* plugins, not menu rows, so OmarchyTV does not use it.)

Everything is LAN-only and opt-in. Screen sharing is off until you start it. `screenAudio`, `screenFps`,
`screenMirrorFromTv` ("confirm" | "allow" | "off") and `statsIntervalS` go in `~/.config/omarchy-link/config.json`.

## Tests (no TV needed)
```bash
(cd omarchy-link/tests && ./run.sh)                    # needs ffmpeg for the mirror test
python3 omarchy-tv/tests/test_update.py && python3 omarchy-tv/tests/test_themes.py && python3 omarchy-tv/tests/test_ui.py
```
