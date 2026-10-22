# OmarchyTV PC plugin — design (bozza da rivedere / draft for review)

Stato: **implementato in 2.10.1** (vedi README.md); questa resta la nota di progetto.
(`/workspace/omarchy-link`, già con pairing SPAKE2, sync tema, widget barra, stats, cast, agenti AI).
Proposta: non un secondo plugin, ma un **front-end `omarchy-tv`** dentro omarchy-link che raccoglie tutto in un
menu stile Omarchy, più due funzioni nuove: **temi/sfondi sulla TV** e **aggiornamento APK**.

## 1. Aspetto (come gli strumenti ufficiali Omarchy)
- **Menu**: Walker in modalità dmenu, come `omarchy-menu` (`walker --dmenu --width 295 --minheight 1 --maxheight 630 -p "OmarchyTV…"`),
  voci con icone Nerd Font e la stessa gerarchia: `OmarchyTV → Abbina / Stato / Temi / Sfondi / Aggiorna / Cast / Telecomando`.
  Fallback senza Walker: `gum choose` nel terminale; senza gum: elenco numerato.
- **Terminale**: output stile `omarchy-*` con `gum style`/`gum spin`, colori del tema **attivo** letti da
  `~/.config/omarchy/current/theme/colors.toml` (accent, foreground, background) — riusa `theme.py` di omarchy-link.
- **Notifiche**: `notify-send` (mako) come gli script Omarchy, es. "OmarchyTV aggiornata a 2.10".
- **Barra**: il widget Waybar/QML esistente di omarchy-link (stato TV, telecomando) resta; il menu si apre anche dal click.
- Keybinding suggerito (non installato): `SUPER+ALT+T` → `omarchy-tv menu`.

## 2. Funzioni
| Funzione | Come | Stato |
|---|---|---|
| Abbina TV | mDNS `_omarchytv._tcp` → scelta TV → codice a 6 cifre mostrato sulla TV → `POST /v1/pair/start|confirm` (SPAKE2) | esiste (`omarchy-link pair`), solo menu nuovo |
| Statistiche | `PUT /v1/stats` ogni 5 s solo se la TV dice che la home è visibile (evento `home_visible`), altrimenti 60 s | esiste, da regolare a 5 s |
| Tema attivo | hook `omarchy theme set` → `PUT /v1/theme` + `PUT /v1/wallpaper` (JPEG 4K) | esiste |
| **Installa temi/sfondi sulla TV** | la 2.10 contiene già i 23 temi ufficiali; il plugin aggiunge i **temi utente** (`~/.config/omarchy/themes/*`) e sfondi personali: per ognuno `colors.toml` → palette + sfondi ridotti a 3840×2160 WebP q≈80 → nuovo endpoint `PUT /v1/themes/<name>` (multipart: palette JSON + immagini). La TV li salva in `files/themes/<name>/` e li mostra nel menu Temi accanto a quelli inclusi | **nuovo** (TV + PC) |
| **Aggiorna APK** | `omarchy-tv update <apk>`: verifica `versionCode` maggiore e **cert SHA-256 = 90aa68d9…ea33d** (con `apksigner`), poi `adb connect` + `adb install -r`. Mai `uninstall`, mai `-d` (downgrade). Variante senza adb (futura): `PUT /v1/update` → la TV apre l'installer di sistema (serve conferma sul telecomando) | **nuovo** (fase 1 solo adb) |
| Cast | `omarchy-link cast` (link, file, testo, appunti; Google Cast via catt) | esiste, solo voce di menu |
| Telecomando | `omarchy-link key/launch` | esiste |

## 3. Sicurezza
- Tutto solo in LAN, richieste firmate con il token per-PC (già nel protocollo v1); la TV non contatta servizi esterni.
- Update: rifiuta APK con certificato diverso o versione più bassa; mostra hash prima di installare; chiede conferma.
- Mai `pm uninstall`, mai DNS / `private_dns_*`. adb solo verso l'IP della TV abbinata.
- Chiave di firma **non** sul PC del plugin per la distribuzione pubblica: il plugin installa solo APK già firmati.

## 4. Struttura (skeleton in questa cartella)
```
bin/omarchy-tv              # entry point (menu, status, themes, update)
lib/omarchy_tv/ui.py        # walker/gum/plain menu + stile con colori del tema attivo
lib/omarchy_tv/themes.py    # raccolta temi utente, conversione sfondi, payload /v1/themes
lib/omarchy_tv/update.py    # controlli APK (versione, cert) + adb install -r
tests/test_update.py        # test dei controlli (senza TV)
```
Riusa `omarchy_link` (client, theme, config) quando disponibile; lo skeleton gira anche da solo per i controlli.

## 5. Decisioni (approvate)
1. Nome comando: `omarchy-tv` (proposto) o voci dentro `omarchy-link`?
2. Temi utente sulla TV: sì/no, e limite di spazio (proposta 50 MB).
3. Update senza adb (installer di sistema, conferma sul telecomando): fase 2?
4. Statistiche ogni 5 s solo con home visibile: ok?
