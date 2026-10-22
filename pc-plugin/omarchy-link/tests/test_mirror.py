"""Mirror credits: the TV shows exactly what an Omarchy bar widget shows."""
import json
import os
import shutil
import subprocess
import time
import unittest
from pathlib import Path

import helpers
from helpers import cli
from mock_tv import MockTV
from omarchy_link import ai, clis, config, widgets
from omarchy_link.ai.providers import mirror

PLUGINS = helpers.HOME / ".config/omarchy/plugins"
STATE = helpers.HOME / ".local/state/omarchy"
BIN = helpers.TMP / "mirrorbin"
ARGV_LOG = helpers.TMP / "omacash-argv.log"

SNAPSHOT = {
    "schemaVersion": 1, "generatedAt": "2026-10-18T22:40:00Z", "totalRemainingUsd": "118.90", "anyEstimated": True,
    "attention": "openrouter",
    "providers": [
        {"id": "openrouter", "name": "OpenRouter", "status": "ok", "source": "credits",
         "balance": {"remaining": "23.40", "funded": "120.00", "spent": "96.60", "currency": "USD", "estimated": False},
         "percentRemaining": 0.195, "severity": "low", "resetsAt": None, "detail": "$96.60 used of $120.00",
         "fetchedAt": "2026-10-18T22:39:58Z", "stale": False, "error": None, "hint": None},
        {"id": "elevenlabs", "name": "ElevenLabs", "status": "ok", "source": "subscription",
         "balance": {"remaining": "71000", "funded": "100000", "spent": "29000", "currency": "credits", "estimated": False},
         "percentRemaining": 0.71, "severity": "ok", "resetsAt": "2026-11-01T00:00:00Z", "detail": "29k of 100k credits",
         "fetchedAt": "2026-10-18T22:39:58Z", "stale": False, "error": None, "hint": None},
        {"id": "vercel-ai", "name": "Vercel AI Gateway", "status": "error", "source": "credits", "balance": None,
         "percentRemaining": None, "severity": "unknown", "resetsAt": None, "detail": "", "fetchedAt": None,
         "stale": False, "error": {"kind": "auth", "message": "key rejected", "hint": "set the key again"}, "hint": None},
        {"id": "anthropic-api", "name": "Anthropic API", "status": "unconfigured", "source": "ledger", "balance": None,
         "percentRemaining": None, "severity": "unknown", "resetsAt": None, "detail": "", "fetchedAt": None,
         "stale": False, "error": None, "hint": "Run: python3 omacash key set anthropic-api"}]}


def plugin(pid, name, description="", with_bin=None):
    d = PLUGINS / pid
    d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.json").write_text(json.dumps({"schemaVersion": 1, "id": pid, "name": name, "description": description,
                                                 "kinds": ["bar-widget"], "barWidget": {"category": "AI"}}))
    if with_bin:
        (d / "bin").mkdir(exist_ok=True)
        (d / "bin" / with_bin[0]).write_text(with_bin[1])
    return d


def stub(name, body):
    BIN.mkdir(parents=True, exist_ok=True)
    p = BIN / name
    p.write_text(body)
    p.chmod(0o755)


class Mirror(unittest.TestCase):
    def setUp(self):
        helpers.reset_pc_state()
        for d in (PLUGINS, STATE, BIN, helpers.HOME / ".config/omarchy/shell.json"):
            shutil.rmtree(d, ignore_errors=True) if d.is_dir() else d.unlink(missing_ok=True)
        ARGV_LOG.unlink(missing_ok=True)
        self.old_path = os.environ["PATH"]
        os.environ["PATH"] = f"{BIN}:{self.old_path}"
        clis.clear_cache()

    def tearDown(self):
        os.environ["PATH"] = self.old_path
        shutil.rmtree(BIN, ignore_errors=True)
        helpers.reset_pc_state()

    def omacash(self, snapshot=SNAPSHOT):
        body = ("import json, sys\n"
                f"open({str(ARGV_LOG)!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
                f"print(json.dumps({json.dumps(snapshot)!r} and json.loads({json.dumps(json.dumps(snapshot))})))\n")
        return plugin("io.github.baranskyi.omacash", "Omacash", "Remaining money on AI services", ("omacash", body))

    def collect(self, cfg=None):
        return ai.collect(cfg if cfg is not None else {"providers": []}, helpers.TMP / "absent.json")["ai"]

    # ---------------------------------------------------------- omacash
    def test_omacash_mirrored_exactly(self):
        self.omacash()
        # a signed-in Claude Code is on PATH too: mirroring must not add or recompute anything
        stub("claude", "#!/bin/sh\necho 'Current session: 99% used'\n")
        (helpers.HOME / ".claude").mkdir(exist_ok=True)
        (helpers.HOME / ".claude/.credentials.json").write_text("{}")
        self.assertEqual(widgets.default_preset(), "omacash")  # only widget present: still auto-detected
        rows = self.collect()
        self.assertEqual([r["name"] for r in rows], ["OpenRouter", "ElevenLabs", "Vercel AI Gateway"])  # unconfigured hidden
        orr, el, ver = rows
        self.assertEqual((orr["used"], orr["limit"], orr["remaining"], orr["unit"]), (96.6, 120.0, 23.4, "$"))
        self.assertEqual(orr["detail"], "$96.60 used of $120.00")
        self.assertEqual(orr["updatedAt"], "2026-10-18T22:39:58Z")
        self.assertEqual((el["unit"], el["remaining"], el["resetsAt"]), ("credits", 71000.0, "2026-11-01T00:00:00Z"))
        self.assertEqual((ver["status"], ver["error"], ver["used"]), ("error", "key rejected", None))
        self.assertEqual(ARGV_LOG.read_text().split(), ["status"])  # read-only verb, never "sync"

    def test_omacash_include_order_total_and_file_fallback(self):
        d = self.omacash()
        rows = self.collect({"providers": [{"type": "mirror", "preset": "omacash", "include": ["elevenlabs", "OpenRouter"]}]})
        self.assertEqual([r["name"] for r in rows], ["ElevenLabs", "OpenRouter"])
        rows = self.collect({"providers": [{"type": "mirror", "preset": "omacash", "total": True}]})
        self.assertEqual((rows[0]["name"], rows[0]["remaining"]), ("AI total", 118.9))
        shutil.rmtree(d / "bin")  # no CLI: read its snapshot.json (owner-checked, no symlinks)
        s = STATE / "io.github.baranskyi.omacash"
        s.mkdir(parents=True)
        (s / "snapshot.json").write_text(json.dumps(SNAPSHOT))
        self.assertEqual(self.collect()[0]["remaining"], 23.4)

    def test_real_omacash_cli_if_available(self):
        src = Path(os.environ.get("OMACASH_SRC", "/tmp/omacash"))
        if not (src / "bin/omacash").is_file():
            self.skipTest("set OMACASH_SRC to a checkout of github.com/baranskyi/omacash")
        dst = PLUGINS / "io.github.baranskyi.omacash"
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"))
        s = STATE / "io.github.baranskyi.omacash"
        s.mkdir(parents=True, mode=0o700)
        os.chmod(s, 0o700)
        (s / "snapshot.json").write_text(json.dumps(SNAPSHOT))
        os.chmod(s / "snapshot.json", 0o600)
        rows = self.collect()
        self.assertEqual([r["name"] for r in rows][:2], ["OpenRouter", "ElevenLabs"])
        self.assertEqual(rows[0]["remaining"], 23.4)

    def test_tv_gets_the_same_numbers(self):
        self.omacash()
        tv = MockTV(helpers.TMP / "tv-mirror", code="123456").start()
        try:
            cli("pair", f"127.0.0.1:{tv.port}", "--code", "123456")
            cli("push-ai")  # no ai.json at all: Omacash is detected and mirrored
            items = json.loads((helpers.TMP / "tv-mirror/files/omarchytv.json").read_text())["ai"]
            self.assertEqual([(i["name"], i["used"], i["limit"], i["unit"]) for i in items if i["status"] == "ok"],
                             [("OpenRouter", 96.6, 120.0, "$"), ("ElevenLabs", 29000.0, 100000.0, "credits")])
        finally:
            tv.close()

    # ---------------------------------------------------------- omarchy agents
    def write_agents(self):
        usage = STATE / "agents/usage"
        usage.mkdir(parents=True)
        soon = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(time.time() + 7200))
        (usage / "claude.json").write_text(json.dumps({"id": "claude", "name": "Claude", "tierLabel": "Max",
            "limits": [{"label": "Session (5-hour)", "percent": 0.314, "resetsAt": soon},
                       {"label": "Weekly (7-day)", "percent": 0.42, "resetsAt": "2020-01-01T00:00:00+00:00"}],
            "limitsFetchedAt": 1790000000000}))
        (usage / "codex.json").write_text(json.dumps({"id": "codex", "name": "Codex",
            "limits": [{"label": "Weekly (7-day)", "percent": 0.18, "resetsAt": soon}]}))
        (usage / "fireworks.json").write_text(json.dumps({"id": "fireworks", "name": "Fireworks", "limits": [],
            "balance": {"remaining": 12.5, "funded": 20, "spent": 7.5, "currency": "USD", "estimated": True}}))
        (STATE / "agents/order.json").write_text('["fireworks", "claude"]\n')
        return usage

    def test_omarchy_agents_like_the_panel(self):
        self.write_agents()
        (helpers.HOME / ".config/omarchy").mkdir(parents=True, exist_ok=True)
        (helpers.HOME / ".config/omarchy/shell.json").write_text(json.dumps({"bar": {"layout": {"right": [
            {"id": "omarchy.agents", "providers": {"codex": {"enabled": False}}}]}}}))
        self.assertEqual(widgets.default_preset(), "omarchy-agents")  # in the bar, no Omacash
        rows = self.collect()
        self.assertEqual([r["name"] for r in rows], ["Fireworks balance", "Claude Session", "Claude Weekly"])
        self.assertEqual((rows[0]["remaining"], rows[0]["limit"], rows[0]["estimated"]), (12.5, 20.0, True))
        self.assertEqual(rows[1]["used"], 31)            # rounded like the panel
        self.assertEqual(rows[2]["used"], 0)             # window past its reset reads 0 like the panel
        self.assertEqual(rows[1]["updatedAt"], "2026-09-21T14:13:20Z")
        weekly = self.collect({"providers": [{"type": "mirror", "preset": "agent-usage"}]})
        self.assertEqual([r["name"] for r in weekly], ["Claude Weekly"])

    def test_agents_preferred_over_omacash(self):
        self.omacash()
        self.write_agents()
        (helpers.HOME / ".config/omarchy").mkdir(parents=True, exist_ok=True)
        # Omacash even sits in the bar: the built-in Agents panel still wins
        (helpers.HOME / ".config/omarchy/shell.json").write_text(json.dumps({"bar": {"layout": {"right": [
            {"id": "io.github.baranskyi.omacash"}]}}}))
        self.assertEqual(widgets.default_preset(), "omarchy-agents")
        rows = self.collect()  # no ai.json
        self.assertEqual([r["name"] for r in rows], ["Fireworks balance", "Claude Session", "Claude Weekly", "Codex Weekly"])
        self.assertTrue(all(r.get("source") == "omarchy agents" for r in rows))
        self.assertFalse(ARGV_LOG.exists())  # Omacash not even run
        cli("ai", "setup", "--yes")
        saved = json.loads(config.AI_FILE.read_text())
        self.assertEqual(saved["providers"], [{"type": "mirror", "preset": "omarchy-agents"}])

    # ---------------------------------------------------------- source switches
    def test_sources_cli_opt_in_omacash(self):
        self.omacash()
        self.write_agents()
        from omarchy_link.ai import sources
        self.assertEqual([(x["id"], x["enabled"]) for x in sources.listing()],
                         [("omarchy-agents", True), ("omacash", False)])  # Omacash off by default
        cli("ai", "sources", "enable", "omacash")
        self.assertEqual(sources.enabled(), ["omarchy-agents", "omacash"])
        names = [r["name"] for r in ai.collect()["ai"]]
        self.assertEqual(names[-3:], ["OpenRouter", "ElevenLabs", "Vercel AI Gateway"])
        self.assertIn("Claude Session", names)
        # options survive switching off and on again; other providers are untouched
        saved = json.loads(config.AI_FILE.read_text())
        saved["providers"][1]["include"] = ["openrouter"]
        saved["providers"].append({"type": "manual", "name": "SuperGrok", "used": 3, "limit": 10, "unit": "%"})
        config.write_json_private(config.AI_FILE, saved)
        cli("ai", "sources", "disable", "omacash")
        saved = json.loads(config.AI_FILE.read_text())
        self.assertEqual(saved["providers"][1], {"type": "mirror", "preset": "omacash", "include": ["openrouter"], "enabled": False})
        self.assertEqual(saved["providers"][2]["type"], "manual")
        self.assertNotIn("OpenRouter", [r["name"] for r in ai.collect()["ai"]])
        cli("ai", "sources", "enable", "omacash")
        self.assertEqual([r["name"] for r in ai.collect()["ai"]][-2:], ["OpenRouter", "SuperGrok"])
        self.assertEqual(cli("ai", "sources", "enable", "nope", check=False).returncode, 1)
        # same result through setup
        cli("ai", "setup", "--use", "omarchy-agents,omacash")
        self.assertEqual(sources.enabled(), ["omarchy-agents", "omacash"])
        self.assertIn("[x] omacash", cli("ai", "sources").stdout)

    def test_tv_switches_sources(self):
        self.omacash()
        self.write_agents()
        tvdir = helpers.TMP / "tv-sources"
        tv = MockTV(tvdir, code="123456").start()
        self.addCleanup(tv.close)
        cli("pair", f"127.0.0.1:{tv.port}", "--code", tv.code)
        sess = subprocess.Popen([helpers.CLI, "session"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True)
        conf = lambda: json.loads((tvdir / "files/omarchytv.json").read_text())
        def wait(pred):
            for _ in range(100):
                try:
                    if tv.clients and pred(conf()):
                        return conf()
                except (OSError, ValueError):
                    pass
                time.sleep(0.1)
            self.fail(f"TV never got it: {conf()}")
        try:
            c = wait(lambda j: j.get("aiSources"))
            self.assertEqual([(x["id"], x["enabled"]) for x in c["aiSources"]], [("omarchy-agents", True), ("omacash", False)])
            self.assertNotIn("OpenRouter", [e["name"] for e in c["ai"]])
            r = tv.set_ai_sources(["omarchy-agents", "omacash"])
            self.assertEqual(r["type"], "ai_sources_ok", r)
            self.assertEqual(r["data"]["enabled"], ["omarchy-agents", "omacash"])
            c = wait(lambda j: "OpenRouter" in [e["name"] for e in j["ai"]])
            self.assertTrue(all(x["enabled"] for x in c["aiSources"]))
            # the TV can only switch known, installed widgets: no commands, files or keys
            for bad, code in ((["claudebar"], "not_installed"), (["rm -rf"], "unknown_source"), ("omacash", "bad_request")):
                r = tv.set_ai_sources(bad)
                self.assertEqual((r["type"], r["data"]["error"]), ("ai_sources_error", code))
            r = tv.set_ai_sources([])
            self.assertEqual(r["data"]["enabled"], [])
            wait(lambda j: j["ai"] == [] and not any(x["enabled"] for x in j["aiSources"]))
        finally:
            sess.stdin.close()
            sess.wait(5)
            sess.stdout.close()

    # ---------------------------------------------------------- other widgets
    def test_claudebar_and_ai_usagebar(self):
        stub("claudebar", "#!/bin/sh\n[ \"$1\" = --json ] || exit 3\ncat <<'E'\n" + json.dumps({
            "schema_version": 2, "error": None, "windows": [
                {"id": "five_hour", "label": "Session", "group": "", "used_pct": 37, "reset_at_unix": 1790003600},
                {"id": "fable_week", "label": "Weekly", "group": "Fable", "used_pct": 12, "reset_at": None}],
            "extra_usage": {"used_credit_cents": 1250, "available_credit_cents": 3750, "funded_credit_cents": 5000,
                            "monthly_limit_cents": 10000}}) + "\nE\n")
        rows = self.collect({"providers": [{"type": "mirror", "preset": "claudebar"}]})
        self.assertEqual([r["name"] for r in rows], ["Claude Session", "Claude Fable Weekly", "Claude extra usage"])
        self.assertEqual((rows[0]["used"], rows[0]["resetsAt"]), (37.0, "2026-09-21T15:13:20Z"))
        self.assertEqual((rows[2]["used"], rows[2]["limit"], rows[2]["remaining"]), (12.5, 50.0, 37.5))
        stub("ai-usagebar", "#!/bin/sh\ncat <<'E'\n" + json.dumps({"primary": "claude", "entries": [
            {"id": "claude", "display_name": "Claude", "sections": [
                {"type": "metric", "label": "Session", "percent": 20, "value": "20%", "reset_at": "2026-10-19T05:00:00Z"},
                {"type": "text", "label": "Plan", "value": "Max"}]},
            {"id": "glm", "name": "Z.AI", "error": "token expired", "sections": []}]}) + "\nE\n")
        rows = self.collect({"providers": [{"type": "mirror", "preset": "ai-usagebar"}]})
        self.assertEqual([(r["name"], r.get("used")) for r in rows], [("Claude Session", 20.0), ("Z.AI", None)])
        self.assertEqual(rows[1]["status"], "error")

    def test_generic_json_text_waybar(self):
        stub("myusage", "#!/bin/sh\necho '{\"agents\":[{\"title\":\"Grok\",\"frac\":0.25,\"ends\":1790000000},{\"title\":\"Kimi\",\"frac\":0.5}]}'\n")
        rows = self.collect({"providers": [{"type": "mirror", "source": {"command": ["myusage"]}, "items": "$.agents[*]",
                                             "fields": {"name": "$.title", "used": "$.frac", "unit": "=%", "resetsAt": "$.ends"},
                                             "scale": {"used": 100}, "include": ["Kimi", "Grok"]}]})
        self.assertEqual([(r["name"], r["used"], r["limit"]) for r in rows], [("Kimi", 50.0, 100.0), ("Grok", 25.0, 100.0)])
        f = helpers.TMP / "usage.txt"
        f.write_text("claude 41% weekly\ncodex 7% weekly\n")
        rows = self.collect({"providers": [{"type": "mirror", "source": {"file": str(f)}, "format": "text",
                                             "regex": r"(?P<name>\w+) (?P<used>\d+)%"}]})
        self.assertEqual([(r["name"], r["used"]) for r in rows], [("claude", 41.0), ("codex", 7.0)])
        stub("wb", "#!/bin/sh\necho '{\"text\":\"󰚩 63%\",\"tooltip\":\"x\",\"class\":\"high\"}'\n")
        rows = self.collect({"providers": [{"type": "mirror", "name": "Bar AI", "format": "waybar",
                                             "source": {"command": ["wb"]}}]})
        self.assertEqual((rows[0]["name"], rows[0]["used"]), ("Bar AI", 63.0))
        bad = self.collect({"providers": [{"type": "mirror", "source": {"command": "rm -rf /"}}]})
        self.assertEqual(bad[0]["status"], "error")

    def test_jpath(self):
        doc = {"a": [{"b": 1}, {"b": 2}], "c d": {"e": 3}}
        self.assertEqual(mirror.jpath(doc, "$.a[*].b"), [1, 2])
        self.assertEqual(mirror.jpath(doc, "$.a[1].b"), [2])
        self.assertEqual(mirror.jpath(doc, "$['c d'].e"), [3])
        self.assertEqual(mirror.jpath(doc, "$.nope"), [])

    # ---------------------------------------------------------- setup
    def test_setup_lists_candidates_and_writes_choice(self):
        self.omacash()
        self.write_agents()
        plugin("someone.token-meter", "Token Meter", "Shows Claude token usage in the bar")
        plugin("someone.weather", "Weather", "Forecast in the bar")
        cands = json.loads(cli("ai", "setup", "--json").stdout)
        ids = [c["id"] for c in cands["candidates"]]
        self.assertEqual(ids, ["omarchy.agents", "io.github.baranskyi.omacash", "someone.token-meter"])
        self.assertIsNone(cands["candidates"][2]["preset"])
        self.assertEqual(cands["default"], "omarchy-agents")
        out = cli("ai", "setup", "--list").stdout
        self.assertIn("Omacash", out)
        cli("ai", "setup", "--use", "omacash,omarchy-agents", "--include", "OpenRouter,Claude Session")
        saved = json.loads(config.AI_FILE.read_text())
        self.assertFalse(saved["autoDetect"])
        self.assertEqual([p["preset"] for p in saved["providers"]], ["omacash", "omarchy-agents"])
        self.assertTrue(config.is_private_file(config.AI_FILE))
        rows = ai.collect()["ai"]
        self.assertEqual([r["name"] for r in rows], ["OpenRouter", "Claude Session"])
        r = cli("ai", "setup", "--use", "nope", check=False)
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
