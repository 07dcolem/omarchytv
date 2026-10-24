"""APK / IPK update:
- Android TV (.apk): same signing certificate, higher versionCode, `adb install -r` only (never uninstall).
- LG webOS (.ipk): validates Debian ar + data.tar.* + appinfo.json (id == com.omarchytv.home), installs via `ares-install`.
"""
import io, json, os, re, shutil, subprocess, tarfile
from .i18n import t

PACKAGE = "com.omarchytv.home"
CERT_SHA256 = "90aa68d9f45e623eadfd349ab1eb66042356f95ff6347a4568c3f3a78f8ea33d"


def apk_cert(apk: str) -> str | None:
    tool = shutil.which("apksigner") or os.environ.get("APKSIGNER")
    if not tool:
        return None
    out = subprocess.run([tool, "verify", "--print-certs", apk], text=True, capture_output=True).stdout
    m = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-f]{64})", out)
    return m.group(1) if m else None


def apk_version(apk: str) -> int | None:
    tool = shutil.which("aapt") or os.environ.get("AAPT")
    if not tool:
        return None
    args = [tool, "dump", "badging", apk]
    out = subprocess.run(args, text=True, capture_output=True).stdout
    m = re.search(r"versionCode='(\d+)'", out)
    return int(m.group(1)) if m else None


def tv_version(serial: str) -> int | None:
    try:
        out = subprocess.run(["adb", "-s", serial, "shell", "dumpsys", "package", PACKAGE], text=True,
                             capture_output=True, timeout=30).stdout
    except subprocess.TimeoutExpired:
        return None
    m = re.search(r"versionCode=(\d+)", out)
    return int(m.group(1)) if m else None


def check(apk_cert_sha: str | None, apk_vc: int | None, tv_vc: int | None) -> str | None:
    """None if OK, else the reason to refuse."""
    if apk_cert_sha is None:
        return t("update.no_cert")
    if apk_cert_sha != CERT_SHA256:
        return t("update.bad_cert")
    if apk_vc is None:
        return t("update.no_vc")
    if tv_vc is not None and apk_vc <= tv_vc:
        return t("update.not_newer", apk=apk_vc, tv=tv_vc)
    return None


def ipk_info(ipk: str) -> dict | None:
    """Parse an LG webOS .ipk (ar archive) and return its appinfo.json dict, or None if invalid."""
    try:
        with open(ipk, "rb") as f:
            if f.read(8) != b"!<arch>\n":
                return None
            while True:
                hdr = f.read(60)
                if len(hdr) < 60:
                    break
                name = hdr[:16].decode("ascii", errors="replace").strip().rstrip("/")
                size = int(hdr[48:58].decode("ascii", errors="replace").strip() or "0")
                payload = f.read(size)
                if size % 2 == 1:
                    f.read(1)
                if name.startswith("data.tar"):
                    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as tf:
                        for member in tf.getmembers():
                            if member.name.endswith("/appinfo.json") or member.name == "appinfo.json":
                                ex = tf.extractfile(member)
                                if ex:
                                    return json.loads(ex.read().decode("utf-8"))
    except (OSError, ValueError, tarfile.TarError, json.JSONDecodeError):
        return None
    return None


def check_ipk(info: dict | None) -> str | None:
    """None if the LG webOS .ipk is a valid OmarchyTV package, else the reason to refuse."""
    if not isinstance(info, dict):
        return t("ipk.invalid")
    if info.get("id") != PACKAGE:
        return t("ipk.bad_id", got=info.get("id"), want=PACKAGE)
    if not info.get("version"):
        return t("ipk.no_version")
    return None


def update_ipk(ipk: str, device: str | None = None, dry_run: bool = False, yes: bool = False) -> int:
    from . import ui
    info = ipk_info(ipk)
    why = check_ipk(info)
    if why:
        ui.say(t("update.cancelled", why=why))
        ui.notify(t("update.cancelled", why=why), "critical")
        return 1
    ver = info.get("version", "?")
    ui.say(t("ipk.info", id=info.get("id"), ver=ver))
    if dry_run:
        ui.say(t("update.no_changes"))
        return 0
    tool = shutil.which("ares-install")
    if not tool:
        ui.say(t("ipk.no_ares"))
        return 1
    target_label = device or "default"
    if not (yes or ui.confirm(t("ipk.confirm", ipk=ipk, ver=ver, device=target_label))):
        ui.say(t("update.no_changes"))
        return 0
    cmd = [tool] + (["--device", device] if device else []) + [ipk]
    r = subprocess.run(cmd)
    if r.returncode == 0:
        ui.notify(t("ipk.done", ver=ver))
        launch_tool = shutil.which("ares-launch")
        if launch_tool:
            subprocess.run([launch_tool] + (["--device", device] if device else []) + [PACKAGE], capture_output=True)
    return r.returncode


def update(apk: str, serial: str | None = None, dry_run: bool = False, yes: bool = False) -> int:
    if apk and apk.lower().endswith(".ipk"):
        return update_ipk(apk, serial, dry_run=dry_run, yes=yes)
    from . import ui
    if serial is None:
        serial = ui.ask("TV (ip:5555)")
    if not shutil.which("adb"):
        ui.say(t("update.no_adb")); return 1
    if ":" in serial:   # network TV (ip:5555); a local serial such as emulator-5554 needs no connect
        try:
            subprocess.run(["adb", "connect", serial], capture_output=True, timeout=15)
        except subprocess.TimeoutExpired:
            ui.say(t("update.no_answer", serial=serial)); return 1
    cert, vc, tvc = apk_cert(apk), apk_version(apk), tv_version(serial)
    ui.say(t("update.info", vc=vc, tvc=tvc, cert=cert or '?'))
    why = check(cert, vc, tvc)
    if why:
        ui.say(t("update.cancelled", why=why)); ui.notify(t("update.cancelled", why=why), "critical"); return 1
    if dry_run or not (yes or ui.confirm(t("update.confirm", apk=apk, serial=serial))):
        ui.say(t("update.no_changes")); return 0
    r = subprocess.run(["adb", "-s", serial, "install", "-r", apk])   # never -d, never uninstall
    if r.returncode == 0:
        ui.notify(t("update.done", vc=tv_version(serial)))
    return r.returncode
