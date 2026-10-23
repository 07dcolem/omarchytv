import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from omarchy_tv.update import check, CERT_SHA256
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


if __name__ == "__main__":
    unittest.main()
