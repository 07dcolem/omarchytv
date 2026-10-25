import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from omarchy_tv import mcp_server


class FakeTvClient:
    def __init__(self):
        self.theme = ("tokyo-night", 0)
        self.keys = []

    def status(self):
        return {"ok": True, "theme": self.theme[0], "capabilities": ["themes", "mcp"]}

    def key(self, k):
        self.keys.append(k)
        return {"ok": True, "key": k}

    def apps(self):
        return {"apps": [{"package": "com.netflix.ninja", "label": "Netflix"}]}

    def launch(self, pkg):
        return {"ok": True, "package": pkg}

    def request(self, method, path, body=None):
        if method == "GET" and path == "/v1/themes":
            return {"themes": [{"name": "jade-horse", "backgrounds": ["01-ink-horse.webp"], "bytes": 1000}], "used": 1000, "cap": 100000}
        if method == "POST" and path.startswith("/v1/themes/") and path.endswith("/select"):
            name = path.split("/")[3]
            self.theme = (name, (body or {}).get("bg", 0))
            return {"ok": True, "name": name}
        if method == "PUT" and path == "/v1/screensaver":
            return {"ok": True, "text": (body or {}).get("text", "")}
        return {"ok": True}


class TestMcpServer(unittest.TestCase):
    def test_rpc_initialize_list_and_call(self):
        tv = FakeTvClient()
        init = mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize"}, tv)
        self.assertEqual(init["result"]["serverInfo"]["name"], "omarchy-tv-mcp")

        lst = mcp_server.handle_rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, tv)
        names = [t["name"] for t in lst["result"]["tools"]]
        self.assertIn("tv_status", names)
        self.assertIn("tv_set_theme", names)
        self.assertNotIn("exec", names)

        call = mcp_server.handle_rpc({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "tv_set_theme", "arguments": {"name": "jade-horse"}}
        }, tv)
        self.assertFalse(call["result"]["isError"])
        self.assertEqual(tv.theme[0], "jade-horse")

        bad = mcp_server.handle_rpc({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "shell_exec", "arguments": {"cmd": "id"}}
        }, tv)
        self.assertEqual(bad["error"]["code"], -32601)

    def test_http_bearer_auth(self):
        tv = FakeTvClient()
        with tempfile.TemporaryDirectory() as tmp:
            tok = mcp_server.ensure_token(Path(tmp) / "mcp-token")
            srv = mcp_server.create_http_server(lambda: tv, tok, "127.0.0.1", 0)
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            port = srv.server_address[1]
            try:
                # 1. Missing/wrong token -> 401
                c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                c.request("POST", "/mcp", body=b'{"jsonrpc":"2.0","id":1,"method":"ping"}',
                          headers={"Content-Type": "application/json", "Authorization": "Bearer wrong"})
                self.assertEqual(c.getresponse().status, 401)
                c.close()

                # 2. Valid token -> 200
                c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                c.request("POST", "/mcp", body=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}',
                          headers={"Content-Type": "application/json", "Authorization": f"Bearer {tok}"})
                r = c.getresponse()
                self.assertEqual(r.status, 200)
                data = json.loads(r.read())
                self.assertTrue(len(data["result"]["tools"]) >= 7)
                c.close()
            finally:
                srv.shutdown()


if __name__ == "__main__":
    unittest.main()
