#!/usr/bin/env bash
# One-time (per fresh machine) setup for the daily Nifty Short pipeline.
set -euo pipefail
cd "$(dirname "$0")"
pip install --break-system-packages -q piper-tts soundfile numpy scipy 2>&1 | grep -v WARNING || true
VOICE=vits-piper-hi_IN-pratham-medium
if [ ! -f ".piper/$VOICE/hi_IN-pratham-medium.onnx" ]; then
  mkdir -p .piper
  curl -sL -m 600 -o ".piper/$VOICE.tar.bz2" "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/$VOICE.tar.bz2"
  tar xjf ".piper/$VOICE.tar.bz2" -C .piper && rm ".piper/$VOICE.tar.bz2"
fi
[ -d node_modules ] || npm install --no-audit --no-fund --loglevel=error
which ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
echo "setup ok"
