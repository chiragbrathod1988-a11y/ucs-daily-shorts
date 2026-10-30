#!/usr/bin/env bash
# One-time (per fresh machine) setup for the daily Nifty Short pipeline.
set -euo pipefail
cd "$(dirname "$0")"
pip install --break-system-packages -q soundfile numpy scipy 2>&1 | grep -v WARNING || true
# Voice comes from tts/<date>/ (Microsoft neural TTS, made by .github/workflows/tts.yml) — no local TTS model.
[ -d node_modules ] || npm install --no-audit --no-fund --loglevel=error
which ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
echo "setup ok"
