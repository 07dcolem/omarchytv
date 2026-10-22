#!/usr/bin/env bash
# Read-only snapshot of the TV state, saved to backup/state-<timestamp>/ (and backup/state-latest/).
# Nothing on the TV is changed. Private DNS is only *recorded* (private_dns_mode / private_dns_specifier).
# Memory is recorded too (/proc/meminfo, dumpsys meminfo summary): run this once BEFORE debloating, so
# tools/reboot-check.sh (or tools/mem-compare.sh) can show before/after free memory.
#
# Usage: TV_HOST=192.168.1.50 tools/backup-state.sh [out-dir]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=tools/venv/bin/python
[ -x "$PY" ] || PY=tools/venv/Scripts/python.exe
export MSYS_NO_PATHCONV=1
[ -x "$PY" ] || { echo "run: python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt"; exit 1; }
tv() { "$PY" -I tools/tv.py "$@"; }
OUT="${1:-backup/state-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT"
tv 'getprop' > "$OUT/getprop.txt"
tv 'pm list packages' | sort > "$OUT/packages.txt"
tv 'pm list packages -d' | sort > "$OUT/disabled.txt"
tv 'cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME' | tail -n 1 > "$OUT/home.txt"
tv 'settings list global' > "$OUT/settings-global.txt"
tv 'settings list secure' > "$OUT/settings-secure.txt"
tv 'settings list system' > "$OUT/settings-system.txt"
tv 'cat /proc/meminfo' > "$OUT/meminfo.txt"
# dumpsys meminfo summary: the totals block at the end (Total / Free / Used / Lost RAM), not the per-process list
tv 'dumpsys meminfo' | grep -E '^ *(Total RAM|Free RAM|Used RAM|Lost RAM|ZRAM|Tuning)' > "$OUT/dumpsys-meminfo.txt" || true
{
  echo "private_dns_mode=$(tv 'settings get global private_dns_mode' | tr -d '\r\n')"
  echo "private_dns_specifier=$(tv 'settings get global private_dns_specifier' | tr -d '\r\n')"
} > "$OUT/private-dns.txt"
case "$OUT" in backup/state-2*) rm -rf backup/state-latest && cp -r "$OUT" backup/state-latest ;; esac
echo "saved $OUT ($(wc -l < "$OUT/disabled.txt") disabled packages, home: $(cat "$OUT/home.txt"))"
cat "$OUT/private-dns.txt"
