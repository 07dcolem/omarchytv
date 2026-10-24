#!/usr/bin/env python3
"""
End-to-end integration test suite for OmarchyTV Mobile (com.omarchytv.mobile v2.11.0-beta):
1. Pure-Java Wireless ADB over TCP (AdbTcpClient) against a mock Android TV adbd server (:15555)
2. Pure-Java OmarchyLinkClient (HMAC-SHA256 OTV1 + X-Omarchy-Signature) against mock omarchy-link (:18999)
3. Dual-Mirror GitLab + GitHub & Dual-Platform (.apk + .ipk) release resolver (GitLabReleaseClient)
4. Built-in WebOsBridgeServer (:18765) serving /v1/status, /v1/themes, /tv (Universal HTML5/Canvas TV),
   real .ipk Debian ar + appinfo.json validator, and Samsung Tizen :8001 /api/v2/ SmartView launcher!
"""
import hashlib
import hmac
import http.server
import json
import os
import socket
import struct
import subprocess
import tempfile
import threading
import urllib.request

CMD_SYNC = 0x434E5953
CMD_CNXN = 0x4E584E43
CMD_AUTH = 0x48545541
CMD_OPEN = 0x4E45504F
CMD_OKAY = 0x59414B4F
CMD_CLSE = 0x45534C43
CMD_WRTE = 0x45545257


def make_adb_packet(cmd, arg0, arg1, payload=b""):
    checksum = sum(payload) & 0xFFFFFFFF
    magic = cmd ^ 0xFFFFFFFF
    hdr = struct.pack("<6I", cmd, arg0, arg1, len(payload), checksum, magic)
    return hdr + payload


def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError("socket closed")
        buf.extend(chunk)
    return bytes(buf)


def read_adb_packet(sock):
    hdr = recv_exact(sock, 24)
    cmd, arg0, arg1, length, checksum, magic = struct.unpack("<6I", hdr)
    payload = recv_exact(sock, length) if length > 0 else b""
    return cmd, arg0, arg1, payload


class MockAdbdServer:
    def __init__(self, port=15555):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", port))
        self.sock.listen(8)
        self.running = True
        self.received_pubkeys = []
        self.shell_commands = []
        self.pushed_files = {}
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        while self.running:
            try:
                conn, _ = self.sock.accept()
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, conn):
        with conn:
            # 1. Expect CNXN
            cmd, version, maxdata, banner = read_adb_packet(conn)
            assert cmd == CMD_CNXN, f"Expected CNXN, got {hex(cmd)}"
            # 2. Send AUTH_TOKEN
            token = b"0123456789abcdef0123"
            conn.sendall(make_adb_packet(CMD_AUTH, 1, 0, token))
            # 3. Expect AUTH_SIGNATURE (2)
            cmd, auth_type, _, sig_payload = read_adb_packet(conn)
            assert cmd == CMD_AUTH and auth_type == 2 and len(sig_payload) == 256
            # 4. Ask for AUTH_RSAPUBLICKEY (3) by sending another AUTH_TOKEN
            conn.sendall(make_adb_packet(CMD_AUTH, 1, 0, token))
            cmd, auth_type, _, pub_payload = read_adb_packet(conn)
            assert cmd == CMD_AUTH and auth_type == 3
            assert b"omarchytv@mobile" in pub_payload
            self.received_pubkeys.append(pub_payload)
            # 5. Accept connection with CNXN
            conn.sendall(make_adb_packet(CMD_CNXN, 0x01000001, 256 * 1024, b"device::ro.product.name=bravia_atv3\0"))

            # Stream loop
            sync_mode = False
            sync_buf = bytearray()
            sync_local_id = 0
            sync_remote_id = 99
            while True:
                try:
                    cmd, arg0, arg1, payload = read_adb_packet(conn)
                except EOFError:
                    break
                if cmd == CMD_OPEN:
                    local_id = arg0
                    dest = payload.rstrip(b"\x00").decode("utf-8", errors="replace")
                    if dest.startswith("shell:"):
                        cmdline = dest[len("shell:"):]
                        self.shell_commands.append(cmdline)
                        conn.sendall(make_adb_packet(CMD_OKAY, 42, local_id))
                        if "pm install" in cmdline:
                            out = b"Success\n"
                        elif "set-home-activity" in cmdline:
                            out = b"Home activity set\n"
                        elif "disable-user" in cmdline:
                            pkg = cmdline.split()[-1]
                            out = f"Package {pkg} new state: disabled-user\n".encode()
                        elif "pm enable" in cmdline:
                            pkg = cmdline.split()[-1]
                            out = f"Package {pkg} new state: enabled\n".encode()
                        elif "pm list packages -d" in cmdline:
                            out = b"package:tv.samba.ssm\npackage:com.sony.dtv.promos\n"
                        else:
                            out = b"OK\n"
                        conn.sendall(make_adb_packet(CMD_WRTE, 42, local_id, out))
                        conn.sendall(make_adb_packet(CMD_CLSE, 42, local_id))
                    elif dest == "sync:":
                        sync_mode = True
                        sync_buf.clear()
                        sync_local_id = local_id
                        conn.sendall(make_adb_packet(CMD_OKAY, sync_remote_id, sync_local_id))
                elif cmd == CMD_WRTE and sync_mode:
                    sync_buf.extend(payload)
                    conn.sendall(make_adb_packet(CMD_OKAY, sync_remote_id, sync_local_id))
                    if b"DONE" in sync_buf:
                        # Parse SEND + DATA chunks + DONE
                        pos = 0
                        assert sync_buf[pos:pos + 4] == b"SEND"
                        path_len = struct.unpack("<I", sync_buf[pos + 4:pos + 8])[0]
                        path_spec = sync_buf[pos + 8:pos + 8 + path_len].decode("utf-8")
                        remote_path = path_spec.split(",")[0]
                        pos += 8 + path_len
                        file_bytes = bytearray()
                        while pos + 8 <= len(sync_buf):
                            tag = bytes(sync_buf[pos:pos + 4])
                            sz = struct.unpack("<I", sync_buf[pos + 4:pos + 8])[0]
                            pos += 8
                            if tag == b"DATA":
                                file_bytes.extend(sync_buf[pos:pos + sz])
                                pos += sz
                            elif tag == b"DONE":
                                break
                        self.pushed_files[remote_path] = bytes(file_bytes)
                        conn.sendall(make_adb_packet(CMD_WRTE, sync_remote_id, sync_local_id, b"OKAY\x00\x00\x00\x00"))
                elif cmd == CMD_CLSE:
                    sync_mode = False
                    conn.sendall(make_adb_packet(CMD_CLSE, arg1, arg0))

    def stop(self):
        self.running = False
        self.sock.close()


class MockHttpState:
    requests = []
    tizen_launches = []
    apk_bytes = b"PK\x03\x04MOCK_OMARCHYTV_2_11_0_BETA_APK_PAYLOAD" * 64
    apk_sha256 = hashlib.sha256(apk_bytes).hexdigest()


class MockOmarchyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _read_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length) if length > 0 else b""

    def _verify_sig(self, body):
        auth = self.headers.get("Authorization", "")
        sig_hdr = self.headers.get("X-Omarchy-Signature", "")
        ts = self.headers.get("X-Omarchy-Timestamp", "")
        nonce = self.headers.get("X-Omarchy-Nonce", "")
        assert auth.startswith("OTV1 "), f"Missing OTV1 Authorization header: {auth}"
        assert sig_hdr.startswith("sha256="), f"Missing X-Omarchy-Signature header: {sig_hdr}"
        canonical = f"OTV1\n{self.command}\n{self.path}\n{ts}\n{nonce}\n{hashlib.sha256(body).hexdigest()}".encode()
        expected = hmac.new(b"test-secret-key", canonical, hashlib.sha256).hexdigest()
        assert sig_hdr == f"sha256={expected}", f"HMAC mismatch: {sig_hdr} != sha256={expected}"

    def do_GET(self):
        body = self._read_body()
        if self.path in ("/ping", "/v1/status"):
            self._verify_sig(body)
            MockHttpState.requests.append(("GET", self.path))
            resp = json.dumps({
                "ok": True,
                "name": "Sony Bravia XR-65A95L",
                "version": "2.11.0-beta",
                "versionCode": 21100,
                "theme": "tokyo-night"
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        elif self.path == "/gitlab/releases":
            resp = json.dumps([
                {
                    "tag_name": "v2.11.0-testing-webos",
                    "name": "OmarchyTV v2.11.0-testing (LG webOS)",
                    "description": "LG webOS release",
                    "assets": {"links": [{"name": "omarchytv-webos-2.11.0-testing.ipk", "direct_asset_url": f"http://127.0.0.1:{self.server.server_port}/downloads/omarchytv-webos.ipk"}]}
                },
                {
                    "tag_name": "v2.11.0-beta",
                    "name": "OmarchyTV v2.11.0-beta (Android TV)",
                    "description": f"SHA-256: `{MockHttpState.apk_sha256}`",
                    "assets": {"links": [{"name": "omarchytv-release-2.11.0.apk", "direct_asset_url": f"http://127.0.0.1:{self.server.server_port}/downloads/omarchytv.apk"}]}
                }
            ]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        elif self.path == "/github/releases":
            resp = json.dumps([
                {
                    "tag_name": "v2.11.0-beta",
                    "name": "OmarchyTV v2.11.0-beta",
                    "body": f"SHA-256: {MockHttpState.apk_sha256}",
                    "assets": [{"name": "omarchytv-release-2.11.0.apk", "browser_download_url": f"http://127.0.0.1:{self.server.server_port}/downloads/omarchytv.apk"}]
                }
            ]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        elif self.path == "/downloads/omarchytv.apk":
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.android.package-archive")
            self.send_header("Content-Length", str(len(MockHttpState.apk_bytes)))
            self.end_headers()
            self.wfile.write(MockHttpState.apk_bytes)
        elif self.path == "/api/v2/":
            resp = json.dumps({"device": {"name": "Samsung QN90C Neo QLED", "modelName": "QN65QN90C"}}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        body = self._read_body()
        self._verify_sig(body)
        MockHttpState.requests.append(("PUT", self.path, len(body)))
        resp = json.dumps({"ok": True, "sha256": hashlib.sha256(body).hexdigest()}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def do_POST(self):
        body = self._read_body()
        if self.path == "/api/v2/applications/org.tizen.browser":
            MockHttpState.tizen_launches.append(json.loads(body.decode()))
            resp = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
            return
        self._verify_sig(body)
        MockHttpState.requests.append(("POST", self.path, json.loads(body.decode())))
        resp = b'{"ok":true}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)


def main():
    adb_srv = MockAdbdServer(15555)
    http_srv = http.server.ThreadingHTTPServer(("127.0.0.1", 18999), MockOmarchyHandler)
    threading.Thread(target=http_srv.serve_forever, daemon=True).start()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            harness_java = os.path.join(tmpdir, "MobileIntegrationTest.java")
            with open(harness_java, "w", encoding="utf-8") as f:
                f.write("""
import com.omarchytv.mobile.*;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class MobileIntegrationTest {
    public static void main(String[] args) throws Exception {
        File tmpDir = new File(args[0]);

        // 1. Test DebloatProfiles safety denylist & brand profiles
        assert DebloatProfiles.isProtected("com.google.android.tungsten.setupwraith");
        assert DebloatProfiles.isProtected("com.google.android.gms");
        assert DebloatProfiles.isProtected("com.google.android.apps.mediashell");
        assert DebloatProfiles.isProtected("com.sony.dtv.tvx");
        assert !DebloatProfiles.isProtected("tv.samba.ssm");
        assert DebloatProfiles.allProfiles().size() >= 6;
        System.out.println("[PASS] DebloatProfiles safety denylist & 6 brand profiles verified");

        // 2. Test Dual-Mirror Release Resolver & SHA-256 Downloader
        String glUrl = "http://127.0.0.1:18999/gitlab/releases";
        String ghUrl = "http://127.0.0.1:18999/github/releases";
        GitLabReleaseClient rc = new GitLabReleaseClient(glUrl, ghUrl, glUrl, ghUrl);
        GitLabReleaseClient.DualPlatformCatalog cat = rc.fetchDualPlatformReleases();
        assert cat.androidTvApk != null : "Missing Android TV APK release";
        assert cat.lgWebOsIpk != null : "Missing LG webOS IPK release";
        assert "v2.11.0-beta".equals(cat.androidTvApk.tagName);
        assert "v2.11.0-testing-webos".equals(cat.lgWebOsIpk.tagName);

        File downloadedApk = new File(tmpDir, "downloaded.apk");
        rc.downloadAndVerifyAsset(cat.androidTvApk, downloadedApk, null);
        assert downloadedApk.isFile() && downloadedApk.length() > 100;
        System.out.println("[PASS] GitLab + GitHub dual-mirror & dual-platform (.apk + .ipk) release verification passed");

        // 3. Test AdbTcpClient handshake, SYNC push, pm install -r, Home pin, and safe debloat
        try (AdbTcpClient adb = AdbTcpClient.connect("127.0.0.1", 15555, tmpDir, 5000, null)) {
            String res = adb.installAndPinHome(downloadedApk, true, null);
            assert res.contains("Success") : "Unexpected install output: " + res;
            String disOut = adb.disablePackageUser0("tv.samba.ssm");
            assert disOut.contains("disabled-user");
            String enOut = adb.enablePackage("tv.samba.ssm");
            assert enOut.contains("enabled");
            Set<String> disabled = adb.listDisabledPackages();
            assert disabled.contains("tv.samba.ssm");

            boolean blockedProtected = false;
            try {
                adb.disablePackageUser0("com.google.android.tungsten.setupwraith");
            } catch (Exception expected) {
                blockedProtected = true;
            }
            assert blockedProtected : "Protected package must throw SecurityException";
        }
        System.out.println("[PASS] AdbTcpClient RSA handshake, SYNC APK push, pm install, Home pin & safe debloat passed");

        // 4. Test OmarchyLinkClient HMAC-SHA256 protocol
        OmarchyLinkClient link = new OmarchyLinkClient("127.0.0.1", 18999, "omarchymobile01", "test-secret-key");
        OmarchyLinkClient.PingResult pr = link.ping();
        assert pr.ok && pr.tvName.contains("Sony Bravia");

        List<ThemeCatalog.ThemeEntry> themes;
        try (FileInputStream fis = new FileInputStream("/workspace/omarchytv-app/mobile-companion/app/src/main/assets/omarchy_themes.json")) {
            themes = ThemeCatalog.loadFromStream(fis);
        }
        assert themes.size() >= 23;
        link.switchTheme(themes.get(1));
        link.sendRemoteKey("up");
        link.sendPromptOrCommand("neofetch");
        link.pushWallpaperJpeg(new byte[]{(byte)0xFF, (byte)0xD8, (byte)0xFF, (byte)0xD9});
        link.pushAppBannerPng("com.netflix.ninja", new byte[]{(byte)0x89, 0x50, 0x4E, 0x47});
        System.out.println("[PASS] OmarchyLinkClient HMAC-SHA256 ping, theme switch, remote key, prompt, wallpaper & banner passed");

        // 5. Test WebOsBridgeServer (:18765) for LG webOS + Samsung Tizen / Universal WebTV + .ipk validator
        File realIpk = new File("/workspace/omarchytv-webos/omarchytv-webos-2.11.0-testing.ipk");
        WebOsBridgeServer.IpkMetadata meta = WebOsBridgeServer.inspectIpkPackage(realIpk);
        assert meta.valid : "IPK validation failed: " + meta.error;
        assert "com.omarchytv.home".equals(meta.appId);
        assert "2.11.0".equals(meta.version);

        try (WebOsBridgeServer bridge = new WebOsBridgeServer(themes)) {
            bridge.setServedIpkFile(realIpk);
            bridge.setActiveTheme("catppuccin", themes.get(1).rawColors);
            bridge.queueRemoteKey("right");
            int port = bridge.start(18765);

            // Check /v1/status
            HttpURLConnection c1 = (HttpURLConnection) new URL("http://127.0.0.1:" + port + "/v1/status").openConnection();
            assert c1.getResponseCode() == 200;
            assert "*".equals(c1.getHeaderField("Access-Control-Allow-Origin"));
            String statusJson = new String(c1.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            assert statusJson.contains("catppuccin") && statusJson.contains("remoteKeySeq");

            // Check /tv (Universal HTML5/Canvas Smart TV Launcher)
            HttpURLConnection cTv = (HttpURLConnection) new URL("http://127.0.0.1:" + port + "/tv").openConnection();
            assert cTv.getResponseCode() == 200;
            String tvHtml = new String(cTv.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            assert tvHtml.contains("OmarchyTV") && tvHtml.contains("app.js");

            // Check Samsung Tizen :8001 SmartView launcher
            String launchMsg = WebOsBridgeServer.launchOnSamsungTizenOrSmartTv("127.0.0.1", 18999, "http://127.0.0.1:" + port + "/tv");
            assert launchMsg.contains("Samsung QN90C Neo QLED");
        }
        System.out.println("[PASS] WebOsBridgeServer (:18765), LG webOS .ipk inspector, Universal /tv WebTV & Samsung Tizen launcher passed");
    }
}
""")
            java_home = "/workspace/toolchain/jdk-17.0.20.1+1"
            android_jar = "/workspace/toolchain/android-sdk/platforms/android-34/android.jar"
            classes_dir = "/workspace/omarchytv-app/mobile-companion/build/classes"
            subprocess.check_call([
                f"{java_home}/bin/javac",
                "-cp", f"{classes_dir}:{android_jar}",
                "-d", tmpdir,
                harness_java
            ])
            subprocess.check_call([
                f"{java_home}/bin/java",
                "-ea",
                "-cp", f"{tmpdir}:{classes_dir}:/home/box/.gradle/caches/modules-2/files-2.1/org.json/json/20231013/e22e0c040fe16f04ffdb85d851d77b07fc05ea52/json-20231013.jar:{android_jar}",
                "MobileIntegrationTest",
                tmpdir
            ])

        assert "/data/local/tmp/omarchytv.apk" in adb_srv.pushed_files
        pushed_sha = hashlib.sha256(adb_srv.pushed_files["/data/local/tmp/omarchytv.apk"]).hexdigest()
        assert pushed_sha == MockHttpState.apk_sha256, f"Pushed APK SHA mismatch: {pushed_sha}"
        assert len(MockHttpState.tizen_launches) == 1
        print("[ALL INTEGRATION TESTS PASSED PERFECTLY]")
    finally:
        adb_srv.stop()
        http_srv.shutdown()


if __name__ == "__main__":
    main()
