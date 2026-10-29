#!/usr/bin/env bash
# One-time (per fresh machine) setup for the daily Nifty Short pipeline.
set -euo pipefail
cd "$(dirname "$0")"
pip install --break-system-packages -q kokoro-onnx soundfile numpy scipy 2>&1 | grep -v WARNING || true
mkdir -p .kokoro
for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
  [ -s ".kokoro/$f" ] || curl -sL -m 900 -o ".kokoro/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
[ -d node_modules ] || npm install --no-audit --no-fund --loglevel=error
which ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
echo "setup ok"
