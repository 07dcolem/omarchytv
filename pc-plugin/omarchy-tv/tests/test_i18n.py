import json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from omarchy_tv import i18n


class ResolveTest(unittest.TestCase):
    def test_config_wins(self):
        self.assertEqual(i18n.resolve("it", {"LANG": "en_US.UTF-8"}), "it")
        self.assertEqual(i18n.resolve("en", {"LC_ALL": "it_IT.UTF-8"}), "en")

    def test_auto_uses_env_order(self):
        env = {"LC_ALL": "it_IT.UTF-8", "LC_MESSAGES": "en_US.UTF-8", "LANG": "en_US.UTF-8"}
        self.assertEqual(i18n.resolve("auto", env), "it")
        env = {"LC_ALL": "", "LC_MESSAGES": "it_IT.UTF-8", "LANG": "en_US.UTF-8"}
        self.assertEqual(i18n.resolve("auto", env), "it")
        self.assertEqual(i18n.resolve("auto", {"LANG": "it_IT.UTF-8"}), "it")
        self.assertEqual(i18n.resolve("auto", {"LC_ALL": "en_GB.UTF-8", "LANG": "it_IT.UTF-8"}), "en")

    def test_fallback_english(self):
        self.assertEqual(i18n.resolve("auto", {}), "en")
        self.assertEqual(i18n.resolve("auto", {"LANG": "de_DE.UTF-8"}), "en")
        self.assertEqual(i18n.resolve("auto", {"LANG": "C"}), "en")
        self.assertEqual(i18n.resolve("bogus", {"LANG": "it_IT"}), "it")

    def test_reads_config_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "omarchy-link"; p.mkdir()
            (p / "config.json").write_text(json.dumps({"language": "it"}))
            old = os.environ.get("XDG_CONFIG_HOME"); os.environ["XDG_CONFIG_HOME"] = d
            try:
                self.assertEqual(i18n.resolve(None, {"LANG": "en_US"}), "it")
                (p / "config.json").write_text(json.dumps({"language": "auto"}))
                self.assertEqual(i18n.resolve(None, {"LANG": "en_US"}), "en")
            finally:
                if old is None: os.environ.pop("XDG_CONFIG_HOME")
                else: os.environ["XDG_CONFIG_HOME"] = old

    def test_tables_match(self):
        self.assertEqual(set(i18n.EN), set(i18n.IT))

    def test_t_formats(self):
        try:
            i18n.set_lang("it"); it = i18n.t("themes.deleted", name="x")
            i18n.set_lang("en"); en = i18n.t("themes.deleted", name="x")
        finally:
            i18n.set_lang(None)
        self.assertIn("eliminato", it); self.assertIn("deleted", en)


class ItalianRegressionTest(unittest.TestCase):
    """On an Italian PC the output must stay byte-identical to the pre-i18n strings."""
    def setUp(self): i18n.set_lang("it")
    def tearDown(self): i18n.set_lang(None)

    def test_italian_unchanged(self):
        t = i18n.t
        cases = {
            t("menu.status"): "Stato", t("menu.pair"): "Abbina TV", t("menu.themes"): "Temi e sfondi",
            t("menu.screen"): "Schermo PC", t("menu.update"): "Aggiorna APK", t("menu.cast"): "Cast",
            t("menu.remote"): "Telecomando",
            t("not_paired"): "TV non abbinata: omarchy-tv pair",
            t("themes.push"): "Invia un tema", t("themes.list"): "Temi sulla TV",
            t("themes.select"): "Scegli sulla TV", t("themes.delete"): "Elimina", t("themes.prompt"): "Temi…",
            t("themes.row", name="a", n=3, mb=1.234): "★ a  3 sfondi  1.2 MB",
            t("themes.used", used=1.25, cap=50.0): "usati 1.2 / 50 MB",
            t("themes.push_prompt"): "Tema da inviare…",
            t("themes.none"): "Nessun tema utente in ~/.config/omarchy/themes.",
            t("themes.pushed", name="a", n=3, mb=1.234): "✓ a: 3 sfondi, 1.2 MB",
            t("themes.sent", name="a"): "Tema a inviato alla TV",
            t("themes.select_prompt"): "Tema…", t("themes.selected", name="a"): "TV: tema a",
            t("themes.delete_prompt"): "Elimina…", t("themes.delete_confirm", name="a"): "Eliminare a dalla TV?",
            t("themes.deleted", name="a"): "✗ a eliminato",
            t("screen.prompt"): "Schermo PC…", t("remote.prompt"): "Tasto…",
            t("update.apk_prompt"): "Percorso dell'APK", t("error", e="x"): "Errore: x",
            t("not_found", cmd="c"): "c non trovato: installa il plugin omarchy-link.",
            t("confirm.suffix"): " [s/N] ",
            t("update.no_cert"): "certificato non leggibile (serve apksigner)",
            t("update.bad_cert"): "certificato diverso da quello di OmarchyTV: rifiutato",
            t("update.no_vc"): "versionCode non leggibile (serve aapt)",
            t("update.not_newer", apk=16, tv=16): "versione 16 non più recente di quella sulla TV (16)",
            t("update.no_adb"): "adb non trovato (pacchetto android-tools).",
            t("update.no_answer", serial="s"): "adb connect s: nessuna risposta",
            t("update.info", vc=1, tvc=2, cert="?"): "APK versionCode 1, TV 2, cert ?",
            t("update.cancelled", why="w"): "Aggiornamento annullato: w",
            t("update.confirm", apk="a", serial="s"): "Installare a sulla TV s?",
            t("update.no_changes"): "Nessuna modifica.",
            t("update.done", vc=5): "OmarchyTV aggiornata (versionCode 5)",
        }
        for got, want in cases.items():
            self.assertEqual(got, want)

