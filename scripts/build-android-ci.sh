#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CACHE_DIR=".buildozer-global"
mkdir -p "$CACHE_DIR" bin
: > buildozer.log

run_build() {
  docker pull kivy/buildozer
  docker run --rm \
    -v "$ROOT/$CACHE_DIR:/home/user/.buildozer" \
    -v "$ROOT:/home/user/hostcwd" \
    -w /home/user/hostcwd \
    kivy/buildozer \
    -v android debug 2>&1 | tee -a buildozer.log
  return "${PIPESTATUS[0]}"
}

collect_apk() {
  local apk
  apk="$(find . -name '*debug*.apk' -type f | head -1 || true)"
  if [ -z "$apk" ]; then
    echo "No APK found. Last 100 log lines:"
    tail -n 100 buildozer.log || true
    find . -name '*.apk' -type f || true
    return 1
  fi
  cp "$apk" bin/tetris-debug.apk
  ls -la bin/
}

if ! run_build; then
  echo "=== Build failed; patching pyjnius long→int and retrying ==="
  bash "$ROOT/scripts/patch-pyjnius.sh" "$ROOT/$CACHE_DIR"
  run_build || {
    echo "=== Build failed after pyjnius patch ==="
    tail -n 100 buildozer.log || true
    exit 1
  }
fi

collect_apk