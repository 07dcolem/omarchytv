"""APK update over adb: same signing certificate, higher versionCode, `adb install -r` only (never uninstall)."""
import os, re, shutil, subprocess
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


def update(apk: str, serial: str | None = None, dry_run: bool = False, yes: bool = False) -> int:
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
