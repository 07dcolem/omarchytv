"""Tiny i18n: Italian and English, no dependencies.

Language = config.json "language" (en | it | auto, default auto) in ~/.config/omarchy-link/,
then LC_ALL / LC_MESSAGES / LANG, then English.
"""
import json
import os
from pathlib import Path

LANGS = ("en", "it")


def _config_language() -> str:
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    try:
        with open(Path(base) / "omarchy-link" / "config.json", encoding="utf-8") as f:
            v = json.load(f).get("language", "auto")
    except (OSError, ValueError, AttributeError):
        return "auto"
    return str(v or "auto").strip().lower()


def resolve(cfg: str | None = None, env=None) -> str:
    env = os.environ if env is None else env
    cfg = _config_language() if cfg is None else (cfg or "auto").strip().lower()
    if cfg in LANGS:
        return cfg
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = (env.get(var) or "").strip()
        if not val:
            continue
        code = val.split(".")[0].split("@")[0].split("_")[0].lower()
        if code in ("c", "posix"):
            break
        return code if code in LANGS else "en"
    return "en"


_lang = None


def lang() -> str:
    global _lang
    if _lang is None:
        _lang = resolve()
    return _lang


def set_lang(code: str | None) -> None:
    """Force a language (tests); None re-resolves on next use."""
    global _lang
    _lang = code


def t(key: str, **fmt) -> str:
    table = IT if lang() == "it" else EN
    s = table.get(key) or EN.get(key) or key
    return s.format(**fmt) if fmt else s


EN = {
    "menu.status": "Status", "menu.pair": "Pair TV", "menu.themes": "Themes and wallpapers",
    "menu.screen": "PC screen", "menu.update": "Update APK", "menu.cast": "Cast", "menu.remote": "Remote",
    "menu.webos": "LG webOS server (LAN)",
    "not_paired": "TV not paired: run omarchy-tv pair",
    "themes.push": "Push a theme", "themes.list": "Themes on the TV", "themes.select": "Select on the TV",
    "themes.delete": "Delete", "themes.prompt": "Themes…",
    "themes.row": "★ {name}  {n} wallpapers  {mb:.1f} MB", "themes.used": "used {used:.1f} / {cap:.0f} MB",
    "themes.push_prompt": "Theme to push…", "themes.none": "No user themes in ~/.config/omarchy/themes.",
    "themes.pushed": "✓ {name}: {n} wallpapers, {mb:.1f} MB", "themes.sent": "Theme {name} sent to the TV",
    "themes.select_prompt": "Theme…", "themes.selected": "TV: theme {name}",
    "themes.delete_prompt": "Delete…", "themes.delete_confirm": "Delete {name} from the TV?",
    "themes.deleted": "✗ {name} deleted",
    "icons.push": "Push banners", "icons.list": "Banners on the TV", "icons.delete": "Delete a banner",
    "icons.prompt": "App banners…", "icons.none": "No PNG banners in ~/.config/omarchy-tv/banners (name them <package>.png).",
    "icons.pushed": "✓ {pkg}: {kb:.0f} KB", "icons.sent": "{n} banners sent to the TV", "icons.row": "▣ {pkg}",
    "icons.delete_prompt": "Banner to delete…", "icons.deleted": "✗ {pkg} deleted",
    "icons.unsupported": "This TV launcher has no custom banners yet: update OmarchyTV.",
    "screen.prompt": "PC screen…", "remote.prompt": "Key…", "update.apk_prompt": "APK path",
    "error": "Error: {e}", "not_found": "{cmd} not found: install the omarchy-link plugin.",
    "confirm.suffix": " [y/N] ",
    "update.no_cert": "cannot read the certificate (apksigner required)",
    "update.bad_cert": "certificate does not match OmarchyTV's: rejected",
    "update.no_vc": "cannot read versionCode (aapt required)",
    "update.not_newer": "version {apk} is not newer than the one on the TV ({tv})",
    "update.no_adb": "adb not found (android-tools package).",
    "update.no_answer": "adb connect {serial}: no response",
    "update.info": "APK versionCode {vc}, TV {tvc}, cert {cert}",
    "update.cancelled": "Update cancelled: {why}",
    "update.confirm": "Install {apk} on TV {serial}?",
    "update.no_changes": "No changes.",
    "update.done": "OmarchyTV updated (versionCode {vc})",
    "ipk.invalid": "invalid .ipk package or missing appinfo.json",
    "ipk.bad_id": "package id {got!r} does not match {want!r}: rejected",
    "ipk.no_version": "missing version in appinfo.json",
    "ipk.no_ares": "ares-install not found (install @webos-tools/cli: npm install -g @webos-tools/cli).",
    "ipk.info": "IPK webOS id={id} version={ver} (testing)",
    "ipk.confirm": "Install {ipk} (v{ver}) on LG webOS TV ({device})?",
    "ipk.done": "OmarchyTV webOS updated (v{ver})",
}

IT = {
    "menu.status": "Stato", "menu.pair": "Abbina TV", "menu.themes": "Temi e sfondi",
    "menu.screen": "Schermo PC", "menu.update": "Aggiorna APK", "menu.cast": "Cast", "menu.remote": "Telecomando",
    "menu.webos": "Server LG webOS (LAN)",
    "not_paired": "TV non abbinata: omarchy-tv pair",
    "themes.push": "Invia un tema", "themes.list": "Temi sulla TV", "themes.select": "Scegli sulla TV",
    "themes.delete": "Elimina", "themes.prompt": "Temi…",
    "themes.row": "★ {name}  {n} sfondi  {mb:.1f} MB", "themes.used": "usati {used:.1f} / {cap:.0f} MB",
    "themes.push_prompt": "Tema da inviare…", "themes.none": "Nessun tema utente in ~/.config/omarchy/themes.",
    "themes.pushed": "✓ {name}: {n} sfondi, {mb:.1f} MB", "themes.sent": "Tema {name} inviato alla TV",
    "themes.select_prompt": "Tema…", "themes.selected": "TV: tema {name}",
    "themes.delete_prompt": "Elimina…", "themes.delete_confirm": "Eliminare {name} dalla TV?",
    "themes.deleted": "✗ {name} eliminato",
    "icons.push": "Invia i banner", "icons.list": "Banner sulla TV", "icons.delete": "Elimina un banner",
    "icons.prompt": "Banner delle app…", "icons.none": "Nessun banner PNG in ~/.config/omarchy-tv/banners (chiamali <pacchetto>.png).",
    "icons.pushed": "✓ {pkg}: {kb:.0f} KB", "icons.sent": "{n} banner inviati alla TV", "icons.row": "▣ {pkg}",
    "icons.delete_prompt": "Banner da eliminare…", "icons.deleted": "✗ {pkg} eliminato",
    "icons.unsupported": "Il launcher della TV non supporta ancora i banner: aggiorna OmarchyTV.",
    "screen.prompt": "Schermo PC…", "remote.prompt": "Tasto…", "update.apk_prompt": "Percorso dell'APK",
    "error": "Errore: {e}", "not_found": "{cmd} non trovato: installa il plugin omarchy-link.",
    "confirm.suffix": " [s/N] ",
    "update.no_cert": "certificato non leggibile (serve apksigner)",
    "update.bad_cert": "certificato diverso da quello di OmarchyTV: rifiutato",
    "update.no_vc": "versionCode non leggibile (serve aapt)",
    "update.not_newer": "versione {apk} non più recente di quella sulla TV ({tv})",
    "update.no_adb": "adb non trovato (pacchetto android-tools).",
    "update.no_answer": "adb connect {serial}: nessuna risposta",
    "update.info": "APK versionCode {vc}, TV {tvc}, cert {cert}",
    "update.cancelled": "Aggiornamento annullato: {why}",
    "update.confirm": "Installare {apk} sulla TV {serial}?",
    "update.no_changes": "Nessuna modifica.",
    "update.done": "OmarchyTV aggiornata (versionCode {vc})",
    "ipk.invalid": "pacchetto .ipk non valido o appinfo.json mancante",
    "ipk.bad_id": "id pacchetto {got!r} diverso da {want!r}: rifiutato",
    "ipk.no_version": "version mancante in appinfo.json",
    "ipk.no_ares": "ares-install non trovato (installa @webos-tools/cli: npm install -g @webos-tools/cli).",
    "ipk.info": "IPK webOS id={id} version={ver} (testing)",
    "ipk.confirm": "Installare {ipk} (v{ver}) sulla TV LG webOS ({device})?",
    "ipk.done": "OmarchyTV webOS aggiornata (v{ver})",
}
