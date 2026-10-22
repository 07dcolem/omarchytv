import json
import unittest

import helpers  # noqa: F401
from omarchy_link import crypto as c

import make_vectors


class SpakeTest(unittest.TestCase):
    def test_group(self):
        self.assertEqual(pow(c.G, c.Q, c.P), 1)
        for e in (c.M, c.N):
            self.assertEqual(pow(e, c.Q, c.P), 1)
            self.assertNotIn(e, (1, c.P - 1))

    def test_same_code_agrees(self):
        a = c.PcPairing("042042", "pcpcpcpcpc")
        b = c.TvPairing("042042", "tvtv", "pcpcpcpcpc", a.message())
        k = a.finish("tvtv", b.message())
        self.assertEqual(k.token, b.keys.token)
        self.assertEqual(k.confirm_pc, b.keys.confirm_pc)
        self.assertEqual(k.confirm_tv, b.keys.confirm_tv)
        self.assertEqual(len(k.token), 32)

    def test_wrong_code_disagrees(self):
        a = c.PcPairing("111111", "pcpcpcpcpc")
        b = c.TvPairing("111112", "tvtv", "pcpcpcpcpc", a.message())
        k = a.finish("tvtv", b.message())
        self.assertNotEqual(k.confirm_pc, b.keys.confirm_pc)
        self.assertNotEqual(k.token, b.keys.token)

    def test_identity_binding(self):
        a = c.PcPairing("111111", "pcpcpcpcpc")
        b = c.TvPairing("111111", "tvtv", "pcpcpcpcpc", a.message())
        self.assertNotEqual(a.finish("other-tv", b.message()).token, b.keys.token)

    def test_rejects_small_subgroup_and_junk(self):
        for bad in (0, 1, c.P - 1, c.P, c.P - 4):  # -4 is a non-residue (p = 3 mod 4)
            with self.assertRaises(ValueError):
                c.parse_element(bad.to_bytes(256, "big") if bad < 1 << 2048 else b"\xff" * 256)
        with self.assertRaises(ValueError):
            c.parse_element(b"\x01" * 255)

    def test_code_format(self):
        for bad in ("12345", "1234567", "12a456", ""):
            with self.assertRaises(ValueError):
                c.code_scalar(bad)
        self.assertEqual(c.code_scalar("123 456"), c.code_scalar("123456"))

    def test_vectors_file_is_current(self):
        with open(helpers.ROOT / "docs/vectors.json") as f:
            self.assertEqual(json.load(f), make_vectors.vectors())


class AuthTest(unittest.TestCase):
    def test_sign_parse(self):
        auth, nonce = c.sign_request(b"k" * 32, "pc1abcdef", "PUT", "/v1/theme", b"{}", 1700000000)
        f = c.parse_authorization(auth)
        self.assertEqual(f["pc"], "pc1abcdef")
        self.assertEqual(f["nonce"], nonce)

    def test_sealed_messages(self):
        key = b"s" * 32
        frame = c.seal_message(key, b'{"seq":1}')
        self.assertEqual(c.open_message(key, frame), b'{"seq":1}')
        mac, _, payload = frame.partition(" ")
        with self.assertRaises(ValueError):
            c.open_message(key, mac + " " + payload.replace("1", "2"))
        with self.assertRaises(ValueError):
            c.open_message(b"x" * 32, frame)


if __name__ == "__main__":
    unittest.main()
