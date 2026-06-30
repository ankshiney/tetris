#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v java &>/dev/null; then
  echo "JDK 17 required. Install: sudo apt-get install openjdk-17-jdk"
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3.11 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install "Cython<3.0" "setuptools<71" buildozer

export PATH="$(pwd)/.venv/bin:$PATH"
buildozer -v android debug

echo ""
echo "APK ready in bin/"
ls -la bin/*.apk