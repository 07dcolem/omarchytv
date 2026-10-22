"""AI credit providers against a local fake of each provider's documented API."""
import json
import os
import stat
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import helpers
from helpers import cli
from mock_tv import MockTV
from omarchy_link import ai, config

SEEN = []


class FakeProviders(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        SEEN.append((u.path, dict(self.headers)))
        if u.path == "/v1/organization/costs":
            if self.headers.get("Authorization") != "Bearer sk-admin-openai":
                return self._send({"error": {"message": "bad key"}}, 401)
            if "page" not in q:
                return self._send({"data": [{"results": [{"amount": {"value": 1.25, "currency": "usd"}}]}],
                                   "has_more": True, "next_page": "p2"})
            return self._send({"data": [{"results": [{"amount": {"value": 2.5, "currency": "usd"}}]}], "has_more": False})
        if u.path == "/v1/organizations/cost_report":
            assert self.headers.get("x-api-key") == "sk-ant-admin-x"
            assert self.headers.get("anthropic-version") == "2023-06-01"
            return self._send({"data": [{"results": [{"amount": "1234.5", "currency": "USD"}]},
                                        {"results": [{"amount": "100", "currency": "USD"}]}], "has_more": False})
        if u.path == "/v1/billing/teams/team-1/prepaid/balance":
            return self._send({"changes": [{"changeOrigin": "PURCHASE", "amount": {"val": "-2500"}},
                                           {"changeOrigin": "SPEND", "amount": {"val": "700"}}],
                               "total": {"val": "-1800"}})
        if u.path == "/v1/billing/teams/team-1/postpaid/invoice/preview":
            return self._send({"coreInvoice": {"amountAfterVat": "350"}, "effectiveSpendingLimit": "20000"})
        if u.path == "/api/v1/key":
            return self._send({"data": {"limit": 10, "limit_remaining": 7.5, "limit_reset": "monthly", "usage": 40,
                                        "effective_budget": {"resets_at": "2026-11-01T00:00:00Z"}}})
        if u.path == "/api/v1/credits":
            return self._send({"data": {"total_credits": 100.5, "total_usage": 25.75}})
        if u.path == "/user/balance":
            return self._send({"is_available": True, "balance_infos": [{"currency": "USD", "total_balance": "4.20"}]})
        self._send({"error": "nope"}, 404)


class AiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), FakeProviders)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        helpers.reset_pc_state()
        os.environ["OPENAI_ADMIN_KEY"] = "sk-admin-openai"
        keyfile = helpers.TMP / "anthropic.key"
        keyfile.write_text("sk-ant-admin-x\n")
        os.chmod(keyfile, 0o600)
        script = helpers.TMP / "my-credits"
        script.write_text('#!/bin/sh\necho \'{"ai":[{"name":"Local LLM","used":12,"limit":100,"unit":"%"}]}\'\n')
        os.chmod(script, 0o755)
        self.cfg = {"providers": [
            {"type": "openai", "baseUrl": self.base, "budget": 20},
            {"type": "anthropic", "baseUrl": self.base, "key": f"file:{keyfile}", "budget": 50},
            {"type": "xai", "baseUrl": self.base, "key": "cmd:echo xai-mgmt", "teamId": "team-1", "postpaid": True},
            {"type": "openrouter", "baseUrl": self.base, "key": "env:OPENAI_ADMIN_KEY"},
            {"type": "openrouter", "name": "OpenRouter account", "baseUrl": self.base, "key": "cmd:echo m", "management": True},
            {"type": "deepseek", "baseUrl": self.base, "key": "cmd:echo d"},
            {"type": "manual", "name": "Claude Max week", "used": 42, "limit": 100, "unit": "%", "resetsAt": "2026-10-23T09:00:00Z"},
            {"type": "command", "exec": [str(script)]},
            {"type": "nope"},
            {"type": "openai", "name": "OpenAI bad key", "baseUrl": self.base, "key": "cmd:echo wrong"},
        ]}

    def test_collect(self):
        res = {e["name"]: e for e in ai.collect(self.cfg, helpers.TMP / "absent.json")["ai"]}
        self.assertEqual((res["OpenAI API"]["used"], res["OpenAI API"]["limit"], res["OpenAI API"]["unit"]), (3.75, 20.0, "$"))
        self.assertTrue(res["OpenAI API"]["resetsAt"].endswith("01T00:00:00Z"))
        self.assertEqual(res["Claude API"]["used"], 13.345)
        self.assertEqual((res["Grok API"]["used"], res["Grok API"]["limit"], res["Grok API"]["remaining"]), (7.0, 25.0, 18.0))
        self.assertEqual((res["Grok API postpaid"]["used"], res["Grok API postpaid"]["limit"]), (3.5, 200.0))
        self.assertEqual((res["OpenRouter"]["used"], res["OpenRouter"]["limit"]), (2.5, 10.0))
        self.assertEqual(res["OpenRouter account"]["used"], 25.75)
        self.assertEqual((res["DeepSeek"]["used"], res["DeepSeek"]["remaining"]), (None, 4.2))
        self.assertEqual(res["Claude Max week"]["status"], "manual")
        self.assertEqual(res["Local LLM"]["unit"], "%")
        self.assertEqual(res["nope"]["status"], "error")
        self.assertIn("401", res["OpenAI bad key"]["error"])
        for e in res.values():
            for k in ("name", "used", "limit", "unit", "resetsAt", "updatedAt"):
                self.assertIn(k, e)
            self.assertNotIn("sk-", json.dumps(e))  # no key ever ends up in what the TV gets

    def test_inline_key_needs_private_file(self):
        cfg = {"providers": [{"type": "deepseek", "baseUrl": self.base, "key": "sk-inline"}]}
        f = helpers.TMP / "ai.json"
        f.write_text(json.dumps(cfg))
        os.chmod(f, 0o644)
        self.assertIn("chmod 600", ai.collect(cfg, f)["ai"][0]["error"])
        os.chmod(f, 0o600)
        self.assertEqual(ai.collect(cfg, f)["ai"][0]["status"], "ok")

    def test_key_file_must_be_private(self):
        keyfile = helpers.TMP / "loose.key"
        keyfile.write_text("k")
        os.chmod(keyfile, 0o644)
        cfg = {"providers": [{"type": "deepseek", "baseUrl": self.base, "key": f"file:{keyfile}"}]}
        self.assertIn("chmod 600", ai.collect(cfg, helpers.TMP / "absent.json")["ai"][0]["error"])

    def test_https_only(self):
        cfg = {"providers": [{"type": "deepseek", "baseUrl": "http://example.com", "key": "cmd:echo k"}]}
        self.assertIn("https", ai.collect(cfg, helpers.TMP / "absent.json")["ai"][0]["error"])

    def test_push_to_tv(self):
        tv = MockTV(helpers.TMP / "tv-ai", code="123456").start()
        try:
            cli("pair", f"127.0.0.1:{tv.port}", "--code", "123456")
            config.write_json_private(config.AI_FILE, {"providers": self.cfg["providers"][6:8]})
            cli("push-ai")
            items = json.loads((helpers.TMP / "tv-ai/files/omarchytv.json").read_text())["ai"]
            self.assertEqual([i["name"] for i in items], ["Claude Max week", "Local LLM"])
        finally:
            tv.close()


if __name__ == "__main__":
    unittest.main()
