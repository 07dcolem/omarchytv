import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from omarchy_tv.update import check, check_ipk, ipk_info, CERT_SHA256, PACKAGE
from omarchy_tv import i18n


class T(unittest.TestCase):
    def test_ok(self): self.assertIsNone(check(CERT_SHA256, 17, 16))
    def test_fresh_tv(self): self.assertIsNone(check(CERT_SHA256, 16, None))
    def tearDown(self): i18n.set_lang(None)

    def test_wrong_cert_it(self):
        i18n.set_lang("it"); self.assertIn("diverso", check("0" * 64, 17, 16))

    def test_downgrade_it(self):
        i18n.set_lang("it"); self.assertIn("non più recente", check(CERT_SHA256, 16, 16))

    def test_wrong_cert_en(self):
        i18n.set_lang("en"); self.assertIn("does not match", check("0" * 64, 17, 16))

    def test_downgrade_en(self):
        i18n.set_lang("en"); self.assertIn("not newer", check(CERT_SHA256, 16, 16))

    def test_no_tools(self): self.assertIsNotNone(check(None, 17, 16))

    def test_ipk_check_ok(self):
        self.assertIsNone(check_ipk({"id": PACKAGE, "version": "2.11.0"}))

    def test_ipk_check_wrong_id(self):
        i18n.set_lang("en"); self.assertIn("does not match", check_ipk({"id": "com.other.app", "version": "2.11.0"}))
        i18n.set_lang("it"); self.assertIn("diverso", check_ipk({"id": "com.other.app", "version": "2.11.0"}))

    def test_ipk_real_package(self):
        candidates = [
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "webos", "releases", "omarchytv-webos-2.11.0-testing.ipk"),
            "/workspace/omarchytv-webos/omarchytv-webos-2.11.0-testing.ipk",
        ]
        for ipk_path in candidates:
            if os.path.isfile(ipk_path):
                info = ipk_info(ipk_path)
                self.assertIsNotNone(info)
                self.assertEqual(info.get("id"), PACKAGE)
                self.assertEqual(info.get("version"), "2.11.0")
                self.assertIsNone(check_ipk(info))
                break


if __name__ == "__main__":
    unittest.main()
