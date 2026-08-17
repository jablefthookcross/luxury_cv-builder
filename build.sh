#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "=== [VitaeCraft Build] Installing Python Dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== [VitaeCraft Build] Installing Playwright Chromium & System Dependencies ==="
python -m playwright install --with-deps chromium || python -m playwright install chromium

echo "=== [VitaeCraft Build] Build Completed Successfully ==="
