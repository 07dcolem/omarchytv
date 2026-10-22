#!/usr/bin/env bash
# OPTIONAL, opt-in only: set Android Private DNS (DNS-over-TLS) to a hostname, e.g. dns.adguard-dns.com.
# Not part of any default flow: nothing here runs unless you pass --private-dns <host> or --restore.
# Android 9+ only (ro.build.version.sdk >= 28). The previous values are saved first and --restore puts
# them back exactly (deleted again if they were unset; mode "off" if no backup exists).
#
# Usage: TV_HOST=192.168.1.50 tools/private-dns.sh                          # show current values (read-only)
#        TV_HOST=192.168.1.50 tools/private-dns.sh --private-dns <host>     # ask, back up, apply
#        TV_HOST=192.168.1.50 tools/private-dns.sh --restore                # ask, put the saved values back
set -euo pipefail
cd "$(dirname "$0")/.."
PY=tools/venv/bin/python
[ -x "$PY" ] || PY=tools/venv/Scripts/python.exe
export MSYS_NO_PATHCONV=1
[ -x "$PY" ] || { echo "run: python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt"; exit 1; }
tv() { "$PY" -I tools/tv.py "$@" | tr -d '\r\n'; }
SAVE=backup/private-dns-before.txt
mode=$(tv 'settings get global private_dns_mode') spec=$(tv 'settings get global private_dns_specifier')
echo "current: private_dns_mode=$mode private_dns_specifier=$spec"
case "${1:-}" in
  "") exit 0 ;;
  --private-dns)
    HOST="${2:?--private-dns needs a hostname, e.g. dns.adguard-dns.com}"
    [[ "$HOST" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$ ]] || { echo "not a hostname: $HOST"; exit 1; }
    sdk=$(tv 'getprop ro.build.version.sdk')
    [ "${sdk:-0}" -ge 28 ] || { echo "Android SDK $sdk: Private DNS needs Android 9 (SDK 28) or newer; nothing changed"; exit 1; }
    read -r -p "Set Private DNS to $HOST (replaces the current setting above)? [y/N] " ok
    case "$ok" in y|Y|yes) ;; *) echo "nothing changed"; exit 0 ;; esac
    mkdir -p backup
    [ -f "$SAVE" ] || printf 'private_dns_mode=%s\nprivate_dns_specifier=%s\n' "$mode" "$spec" > "$SAVE"
    tv "settings put global private_dns_specifier $HOST" >/dev/null
    tv 'settings put global private_dns_mode hostname' >/dev/null
    echo "now:     private_dns_mode=$(tv 'settings get global private_dns_mode') private_dns_specifier=$(tv 'settings get global private_dns_specifier')"
    echo "saved the previous values in $SAVE (undo: tools/private-dns.sh --restore)" ;;
  --restore)
    if [ -f "$SAVE" ]; then
      pm_=$(sed -n 's/^private_dns_mode=//p' "$SAVE") ps_=$(sed -n 's/^private_dns_specifier=//p' "$SAVE")
    else pm_=off ps_=null; echo "no $SAVE: resetting to mode off"; fi
    read -r -p "Restore private_dns_mode=$pm_ private_dns_specifier=$ps_? [y/N] " ok
    case "$ok" in y|Y|yes) ;; *) echo "nothing changed"; exit 0 ;; esac
    if [ "$ps_" = null ] || [ -z "$ps_" ]; then tv 'settings delete global private_dns_specifier' >/dev/null
    else tv "settings put global private_dns_specifier $ps_" >/dev/null; fi
    if [ "$pm_" = null ] || [ -z "$pm_" ]; then tv 'settings delete global private_dns_mode' >/dev/null
    else tv "settings put global private_dns_mode $pm_" >/dev/null; fi
    rm -f "$SAVE"
    echo "now:     private_dns_mode=$(tv 'settings get global private_dns_mode') private_dns_specifier=$(tv 'settings get global private_dns_specifier')" ;;
  *) echo "unknown option $1 (use --private-dns <host> or --restore)"; exit 1 ;;
esac
