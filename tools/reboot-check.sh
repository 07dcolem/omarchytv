#!/usr/bin/env bash
# Post-install reboot check: snapshot (read-only), reboot the TV, wait for boot, then verify
#  - the home activity is still com.omarchytv.home (cmd package resolve-activity HOME),
#  - no disabled package (stock Sony/Google launchers, debloated apps) was re-enabled by a boot receiver
#    or an update: `pm list packages -d` is compared with the snapshot taken just before the reboot,
#    and with an older backup (BASELINE=backup/state-…, default backup/state-latest) if there is one,
#  - every package in the debloat list (optional argument) is still disabled,
#  - Private DNS (mode / specifier) is unchanged. Read-only: this script never writes private_dns_*.
#  - memory: free / available memory now vs the baseline (your pre-debloat backup-state.sh) and vs before
#    the reboot (/proc/meminfo + dumpsys meminfo summary), printed as a before/after table.
# Nothing is fixed automatically: diffs are reported, exit code 1 if any. Re-apply with tools/disable.sh.
#
# Usage: TV_HOST=192.168.1.50 tools/reboot-check.sh [debloat list] [--yes]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=tools/venv/bin/python
[ -x "$PY" ] || PY=tools/venv/Scripts/python.exe
export MSYS_NO_PATHCONV=1
[ -x "$PY" ] || { echo "run: python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt"; exit 1; }
HOME_PKG=com.omarchytv.home
LIST="" YES=0
for a in "$@"; do case "$a" in --yes) YES=1 ;; *) LIST="$a" ;; esac; done
BASELINE="${BASELINE:-backup/state-latest}"
tv() { "$PY" -I tools/tv.py "$@"; }

STAMP=$(date +%Y%m%d-%H%M%S)
PRE="backup/reboot-$STAMP/before" POST="backup/reboot-$STAMP/after"
echo "== snapshot before reboot (read-only)"
tools/backup-state.sh "$PRE" >/dev/null
echo "home: $(cat "$PRE/home.txt")"
if [ "$YES" != 1 ]; then
  read -r -p "Reboot the TV now? Whatever is playing stops. [y/N] " ok
  case "$ok" in y|Y|yes) ;; *) echo "not rebooted"; exit 0 ;; esac
fi
echo "== rebooting"
timeout 20 "$PY" -I tools/tv.py 'reboot' >/dev/null 2>&1 || true
sleep 20
echo -n "== waiting for boot"
booted=0
for _ in $(seq 1 60); do   # up to ~10 min (Sony boots slowly, ADB comes back late)
  if [ "$(timeout 15 "$PY" -I tools/tv.py 'getprop sys.boot_completed' 2>/dev/null | tr -d '\r\n')" = 1 ]; then booted=1; break; fi
  echo -n "."; sleep 10
done
echo
[ "$booted" = 1 ] || { echo "TV did not come back over ADB in time (is network ADB still on?)"; exit 1; }
sleep 30   # let boot receivers (updaters, setup wizards) run before comparing
tools/backup-state.sh "$POST" >/dev/null

fail=0
home=$(cat "$POST/home.txt")
if [ "${home%%/*}" = "$HOME_PKG" ]; then echo "OK   home is $home"
else echo "FAIL home is now '$home' (expected $HOME_PKG). Fix: cmd package set-home-activity --user 0 $HOME_PKG/.MainActivity"; fail=1; fi

compare() {   # $1 = reference dir, $2 = label
  local re new
  re=$(comm -23 "$1/disabled.txt" "$POST/disabled.txt" | sed 's/^package://')
  new=$(comm -13 "$1/disabled.txt" "$POST/disabled.txt" | sed 's/^package://')
  if [ -n "$re" ]; then echo "FAIL re-enabled since $2:"; echo "$re" | sed 's/^/       /'; fail=1
  else echo "OK   nothing re-enabled since $2"; fi
  [ -z "$new" ] || { echo "NOTE newly disabled since $2:"; echo "$new" | sed 's/^/       /'; }
}
compare "$PRE" "before the reboot"
[ -d "$BASELINE" ] && [ "$BASELINE" != "$PRE" ] && compare "$BASELINE" "$BASELINE"

if [ -n "$LIST" ]; then
  missing=$(grep -vE '^\s*(#|$)' "$LIST" | sed -E 's/\s+#.*$//' | while read -r p; do
    grep -qx "package:$p" "$POST/disabled.txt" || { grep -qx "package:$p" "$POST/packages.txt" && echo "$p"; }; done || true)
  if [ -n "$missing" ]; then echo "FAIL enabled again from $LIST:"; echo "$missing" | sed 's/^/       /'; fail=1
  else echo "OK   every package in $LIST is still disabled (or not installed)"; fi
fi

if diff -q "$PRE/private-dns.txt" "$POST/private-dns.txt" >/dev/null; then echo "OK   Private DNS unchanged: $(tr '\n' ' ' < "$POST/private-dns.txt")"
else echo "NOTE Private DNS changed across the reboot:"; diff "$PRE/private-dns.txt" "$POST/private-dns.txt" | sed 's/^/       /' || true; fi

if [ -d "$BASELINE" ] && [ "$BASELINE" != "$PRE" ]; then echo "== memory: $BASELINE (before debloat) vs after reboot"; tools/mem-compare.sh "$BASELINE" "$POST"; fi
echo "== memory: before reboot vs after reboot"; tools/mem-compare.sh "$PRE" "$POST"

echo "snapshots: backup/reboot-$STAMP/"
[ "$fail" = 0 ] && echo "reboot check passed" || echo "reboot check found differences (nothing was changed; re-apply with tools/disable.sh)"
exit "$fail"
