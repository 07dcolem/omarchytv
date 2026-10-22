#!/usr/bin/env bash
# Before/after memory comparison of two snapshots from tools/backup-state.sh (local files only, read-only).
# Usage: tools/mem-compare.sh backup/state-<before> backup/reboot-<stamp>/after
set -euo pipefail
cd "$(dirname "$0")/.."
A="${1:?usage: mem-compare.sh <before dir> <after dir>}" B="${2:?usage: mem-compare.sh <before dir> <after dir>}"
[ -f "$A/meminfo.txt" ] && [ -f "$B/meminfo.txt" ] || { echo "no meminfo.txt in $A or $B (older backup?)"; exit 0; }
kb() { awk -v k="$1:" '$1==k {print $2}' "$2"; }
printf '%-14s %12s %12s %10s\n' "/proc/meminfo" "before MB" "after MB" "delta MB"
for k in MemTotal MemFree MemAvailable Cached SwapFree; do
  a=$(kb "$k" "$A/meminfo.txt") b=$(kb "$k" "$B/meminfo.txt")
  [ -n "$a" ] && [ -n "$b" ] || continue
  printf '%-14s %12d %12d %+10d\n' "$k" $((a/1024)) $((b/1024)) $(((b-a)/1024))
done
if [ -s "$A/dumpsys-meminfo.txt" ] || [ -s "$B/dumpsys-meminfo.txt" ]; then
  echo "dumpsys meminfo (before):"; sed 's/^ */  /' "$A/dumpsys-meminfo.txt" 2>/dev/null | grep -E 'Free RAM|Used RAM' || true
  echo "dumpsys meminfo (after):";  sed 's/^ */  /' "$B/dumpsys-meminfo.txt" 2>/dev/null | grep -E 'Free RAM|Used RAM' || true
fi
echo "(right after a boot, caches are cold: MemAvailable is the fairest number to compare)"
