# Third-party components, credits and licences

OmarchyTV respects the work of others: everything not written for this project is listed here with author,
source, licence and what we changed. Full licence texts are in `launcher/app/src/main/assets/licenses/`
(also shipped inside the APK) and `launcher/app/src/main/assets/saver/tte-js/`.
Audit date: 2026-10-22. Per-background provenance: `launcher/WALLPAPER-PROVENANCE.csv`.

## 1. Project origin
| Item | Author | Source | Licence | Modifications |
|---|---|---|---|---|
| tv-vibehack / cleanyourtv (repo base: debloat scripts, `tools/`, original launcher, install flow) | Gathin (Gathin23) and contributors | https://github.com/Gathin23/tv-vibehack (renamed cleanyourtv) | MIT, `LICENSE` (Copyright (c) 2026 Gathin, kept unchanged) | OmarchyTV fork: launcher rewritten/restyled (`com.omarchytv.home`), screensaver, themes, PC link. Modifications Copyright (c) 2026 Marco Porro, added *alongside* Gathin's notice. |
| Free My TV (`LocalAdb.java` port of `Adb.java`; watchdog and home-mode ideas) | Free My TV contributors | https://github.com/simbasjungles/free-my-tv | MIT, `licenses/FREE-MY-TV-MIT.txt` | Ported to the launcher's package, adapted to its config. |

## 2. Omarchy
| Item | Author | Source | Licence | Modifications |
|---|---|---|---|---|
| `logo.txt` (home/screensaver logo), `icon.txt` (bar icon → `res/drawable/omarchy_icon.xml`) | David Heinemeier Hansson / Omarchy contributors | https://github.com/basecamp/omarchy (omacom/omarchy) | MIT, `licenses/OMARCHY-LICENSE-MIT.txt` | Icon vectorised; logo animated; "TV" glyphs original. |
| Theme palettes (`themes/*/colors.toml`, colour values only) → `assets/omarchy_themes.json` | same | same, commit be54892 | MIT | Converted to JSON. Tokyo Night palette originally by enkia/folke (colour values only). |
| Theme backgrounds: **only the 20 Omarchy-original wordmark images** (`NN-omarchy.webp`, flat theme-background + accent) | David Heinemeier Hansson (commit "Add omarchy bg option to all themes", 2026-04-28) | same | MIT | PNG → WebP, scaled to 3840x2160. |
| ttfx (reference for screensaver behaviour, via tte.js) | 37signals / omacom | https://github.com/omacom/ttfx | MIT + NOTICE, `licenses/ttfx-*` | none (no ttfx code bundled; notice kept). |

"Omarchy" and its logo are the Omarchy project's branding. OmarchyTV is an unofficial fan project, not affiliated
with or endorsed by Omarchy, omacom, Basecamp or 37signals.

### Backgrounds EXCLUDED from the APK until clarified (77 files)
Omarchy's repository is MIT, but it carries **no per-image author or licence** for its wallpapers, and several are
clearly third-party works. We therefore removed every background whose author and licence we could not verify:
- **Not redistributable:** `starship/*` (SpaceX photographs; upstream theme states "SpaceX retains all rights",
  not MIT); `lumon/*` (Severance / Lumon Industries imagery, Apple TV+).
- **Likely third-party, licence unknown:** `hackerman/01-synth-scape` (stock-image metadata); `nord/03-night-hawks`
  (if Edward Hopper's *Nighthawks*, still in copyright in the EU until 2037); `kanagawa/01` (looks like Hokusai,
  public domain, but the reproduction is unverified); `gruvbox/01-04` (paintings, unidentified);
  `tokyo-night/01-liftoff` (Tom Ballard), `03-quattro` (vulturetone), `solitude/*` and `last-horizon/*` (HANCORE):
  authors named, licence not stated.
- **All others** (catppuccin, ethereal, everforest, flexoki-light, lupine, matte-black, miasma, nord, osaka-jade,
  retro-82, ristretto, rose-pine, tokyo-night, vantablack, white non-wordmark images): no author/licence documented.
Themes left with no image (last-horizon, solitude, starship) fall back to the wordmark/procedural wallpaper.
Any of them can be re-added once the author confirms a redistributable licence; record it in the CSV.

## 3. Screensaver
| Item | Author | Source | Licence | Modifications |
|---|---|---|---|---|
| tte.js (`assets/saver/tte-js/`) | Flavio Copes | https://github.com/flaviocopes/tte-js @ 9b120c2 | MIT, `tte-js/LICENSE` + `THIRD_PARTY_NOTICES.md` | Unmodified. Wrapper `saver/index.html` (polyfills, diagnostics) is original. |
| TerminalTextEffects (37 effect designs adapted by tte.js) | ChrisBuilds | https://github.com/ChrisBuilds/terminaltexteffects | MIT, `licenses/terminaltexteffects-MIT.txt` | none by us. |
| Native fallback screensaver (`TteSaver`, `OmarchyDream`) | OmarchyTV | — | MIT (this repo) | Original; re-creates the idea, no code copied. |

## 4. Fonts
| Item | Author | Source | Licence | Modifications |
|---|---|---|---|---|
| CaskaydiaMono Nerd Font Mono (`res/font/`, `assets/fonts/`) | Cascadia Code: Microsoft Corporation (Reserved Font Name "Cascadia Code"); Nerd Fonts patch: Ryan L McIntyre | https://github.com/microsoft/cascadia-code, https://github.com/ryanoasis/nerd-fonts | SIL OFL 1.1 (`licenses/CaskaydiaMono-OFL.txt`); Nerd Fonts `licenses/NERD-FONTS-MIT.txt` | Subset to Latin + box/block/arrows (no Nerd icon glyphs kept); not renamed to the reserved name. |
| JetBrains Mono | JetBrains Mono Project Authors | https://github.com/JetBrains/JetBrainsMono | OFL 1.1 (`licenses/JETBRAINS-MONO-OFL.txt`) | **Not bundled** any more; licence kept for older builds. |

## 5. Libraries (Android)
| Item | Licence |
|---|---|
| AndroidX RecyclerView, DynamicAnimation, Media3 ExoPlayer 1.4.1 (+ Guava etc.) — The Android Open Source Project / Google | Apache 2.0, `licenses/APACHE-2.0.txt` |

## 6. Icons and code snippets
- Line icons `res/drawable/ln_*.xml`, `ic_*.xml`, banner, app icon, OMARCHY TV block wordmark, procedural wallpaper: drawn for
  OmarchyTV (simple geometric strokes, no icon set copied). Only `omarchy_icon.xml` is derived (Omarchy, MIT).
- 2.10.1 additions (`link/CustomThemes.java`, `LanHttpDataSource.java`, `/v1/themes` endpoints, omarchy-tv plugin) are original
  OmarchyTV code (MIT); they use only the Android SDK, java.util.zip and the existing Media3 `BaseDataSource` API.
- No Stack Overflow or other copied snippets were found in the sources (searched for "adapted/based on/copied").

## 7. Omarchy PC plugin and omarchy-link
`pc-plugin/omarchy-tv` and `pc-plugin/omarchy-link` are by Marco Porro, MIT (pc-plugin/LICENSE, pc-plugin/NOTICE). Python standard library only. Themes/colours read at runtime
from the user's Omarchy install (not redistributed). If published, the plugin must carry this file's Omarchy credit.

## 8. Trademarks
Netflix, YouTube, Google, Android, Android TV, Google TV, Chromecast, Sony, BRAVIA, X, Prime Video, Disney+, Spotify and
all other product names, logos and app icons that appear in the launcher or in screenshots are trademarks of their
respective owners. They appear only to show third-party apps installed on the user's TV; their use does not imply
any affiliation with or endorsement by them. App icons are loaded from the TV at runtime and are not bundled.
