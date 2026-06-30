#!/usr/bin/env bash
# Patch pyjnius 1.6.x jnius_utils.pxi: replace Python 2 `long` with `int` for Py3.10 builds.
set -euo pipefail

ROOT="${1:-${HOME}/.buildozer}"
if [ ! -d "$ROOT" ]; then
  echo "No buildozer cache at: $ROOT"
  exit 0
fi

mapfile -t files < <(find "$ROOT" -name 'jnius_utils.pxi' 2>/dev/null || true)
if [ "${#files[@]}" -eq 0 ]; then
  echo "No jnius_utils.pxi found under: $ROOT"
  exit 0
fi

for f in "${files[@]}"; do
  sed -i 's/isinstance(arg, long)/isinstance(arg, int)/g' "$f"
  sed -i 's/(isinstance(arg, int) and arg < 2147483648)/isinstance(arg, int)/g' "$f"
  echo "Patched: $f"
done