import io, json, os, sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from omarchy_tv import themes


class ThemesTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        root = Path(self.td.name)
        d = root / "My Theme!"; (d / "backgrounds").mkdir(parents=True)
        (d / "colors.toml").write_text('accent = "#FF7A59"\nbackground = "#22223b"\ncolor5 = "#c9ada7"\n')
        (d / "backgrounds" / "a b.jpg").write_bytes(b"\xff\xd8\xff\xe0data")
        (d / "backgrounds" / "notes.txt").write_text("x")
        (root / "tokyo-night").mkdir(); (root / "tokyo-night" / "colors.toml").write_text('accent = "#7aa2f7"\n')
        self.root = root

    def tearDown(self):
        self.td.cleanup()

    def test_scan_skips_bundled_and_non_images(self):
        ts = themes.user_themes(self.root)
        self.assertEqual([t.name for t in ts], ["My Theme!"])
        self.assertEqual([p.name for p in ts[0].backgrounds], ["a b.jpg"])

    def test_tv_name(self):
        self.assertEqual(themes.tv_name("My Theme!"), "my-theme")
        with self.assertRaises(ValueError):
            themes.tv_name("!!!")

    def test_zip_layout_is_what_the_tv_accepts(self):
        t = themes.user_themes(self.root)[0]
        data = themes.build_zip(t, encode=lambda p: (p.read_bytes(), "jpg"))
        z = zipfile.ZipFile(io.BytesIO(data))
        self.assertEqual(z.namelist(), ["theme.json", "backgrounds/01-a-b.jpg"])
        tj = json.loads(z.read("theme.json"))
        self.assertEqual(tj["accent"], "#ff7a59")
        self.assertEqual(tj["mode"], "dark")

    def test_cap(self):
        t = themes.user_themes(self.root)[0]
        with self.assertRaises(ValueError):
            themes.build_zip(t, encode=lambda p: (b"\xff\xd8\xff" + b"0" * (themes.CAP + 1), "jpg"))


if __name__ == "__main__":
    unittest.main()
