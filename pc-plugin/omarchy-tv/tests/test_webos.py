import json, os, sys, threading, unittest, urllib.request
from http.server import HTTPServer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from omarchy_tv import webos


class WebOSBridgeTest(unittest.TestCase):
    def test_status_and_themes_endpoints(self):
        srv = HTTPServer(("127.0.0.1", 0), webos.WebOSHandler)
        port = srv.server_port
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/status", timeout=5) as r:
                self.assertEqual(r.status, 200)
                self.assertEqual(r.headers.get("Access-Control-Allow-Origin"), "*")
                st = json.loads(r.read().decode("utf-8"))
                self.assertIn("cpu", st)
                self.assertIn("ram", st)
                self.assertIn("host", st)
                self.assertEqual(st.get("version"), "2.11.0-testing")
                self.assertIsInstance(st.get("ai"), list)

            with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/themes", timeout=5) as r:
                self.assertEqual(r.status, 200)
                th = json.loads(r.read().decode("utf-8"))
                self.assertIn("themes", th)
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
