import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from omarchy_tv import banners

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 16


class FakeClient:
    def __init__(self):
        self.calls = []

    def request(self, method, path, payload=None, raw=None, content_type="application/json", timeout=8.0):
        self.calls.append((method, path, raw, content_type))
        return {"ok": True}


class BannersTest(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)
        (self.root / "com.netflix.ninja.png").write_bytes(PNG)
        (self.root / "notapkg.png").write_bytes(PNG)
        (self.root / "com.x.y.jpg").write_bytes(b"\xff\xd8")

    def tearDown(self):
        self.td.cleanup()

    def test_scan_only_package_pngs(self):
        self.assertEqual([p for p, _ in banners.local(self.root)], ["com.netflix.ninja"])
        self.assertEqual(banners.local(self.root / "missing"), [])

    def test_package_names(self):
        self.assertEqual(banners.package("com.a.b_c"), "com.a.b_c")
        for bad in ("../x", "x", ".a.b", "a/b.c", "", "a.b c"):
            with self.assertRaises(ValueError):
                banners.package(bad)

    def test_push_sends_png(self):
        c = FakeClient()
        banners.push(c, "com.netflix.ninja", self.root / "com.netflix.ninja.png")
        self.assertEqual(c.calls, [("PUT", "/v1/banners/com.netflix.ninja", PNG, "image/png")])

    def test_rejects_non_png_and_large(self):
        bad = self.root / "a.b.png"; bad.write_bytes(b"GIF89a")
        with self.assertRaises(ValueError):
            banners.read(bad)
        big = self.root / "c.d.png"; big.write_bytes(PNG + b"\0" * banners.MAX)
        with self.assertRaises(ValueError):
            banners.read(big)

    def test_list_and_delete(self):
        c = FakeClient()
        banners.list_tv(c); banners.delete(c, "com.a.b")
        self.assertEqual([x[:2] for x in c.calls], [("GET", "/v1/banners"), ("DELETE", "/v1/banners/com.a.b")])


if __name__ == "__main__":
    unittest.main()
