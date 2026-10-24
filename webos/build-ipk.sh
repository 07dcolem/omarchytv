#!/usr/bin/env bash
# Build OmarchyTV for LG webOS (omarchytv-webos-2.11.0-testing.ipk)
# Synchronizes shared fonts, themes, MIT wordmark wallpapers, and tte.js screensaver
# assets from ../launcher/app/src/main/ before running ares-package.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/webos/app"
ANDROID_MAIN="$ROOT/launcher/app/src/main"

if [ -d "$ANDROID_MAIN" ]; then
  mkdir -p "$APP/fonts" "$APP/wallpapers" "$APP/licenses" "$APP/saver"
  cp -f "$ANDROID_MAIN/res/font/caskaydia_mono_regular.ttf" "$APP/fonts/"
  cp -f "$ANDROID_MAIN/res/font/caskaydia_mono_bold.ttf" "$APP/fonts/"
  cp -f "$ANDROID_MAIN/assets/omarchy_themes.json" "$APP/omarchy_themes.json"
  cp -rf "$ANDROID_MAIN/assets/wallpapers/"* "$APP/wallpapers/"
  cp -rf "$ANDROID_MAIN/assets/licenses/"* "$APP/licenses/"
  cp -f "$ANDROID_MAIN/assets/saver/tte-bundle.js" "$APP/saver/tte-bundle.js"
  cp -f "$ANDROID_MAIN/assets/saver/screensaver-tv.txt" "$APP/saver/screensaver-tv.txt"
  cp -rf "$ANDROID_MAIN/assets/saver/tte-js" "$APP/saver/"
fi

OUT_DIR="${1:-$ROOT/webos/releases}"
mkdir -p "$OUT_DIR"
ares-package "$APP" -o "$OUT_DIR"
mv -f "$OUT_DIR/com.omarchytv.home_2.11.0_all.ipk" "$OUT_DIR/omarchytv-webos-2.11.0-testing.ipk"
sha256sum "$OUT_DIR/omarchytv-webos-2.11.0-testing.ipk"
