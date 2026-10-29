#!/usr/bin/env bash
# Usage: ./make_video.sh YYYY-MM-DD   (needs data/YYYY-MM-DD.json with verified previous-session OHLC)
# Output: videos/YYYY-MM-DD.mp4 and check frames in out/check/
set -euo pipefail
cd "$(dirname "$0")"
D="$1"
export PIPER_DIR="$PWD/.piper/vits-piper-hi_IN-pratham-medium"
python3 scripts/build_audio.py "data/$D.json" public/daily src/dailyData.ts | tail -1
BROWSER=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell 2>/dev/null | head -1 || true)
BARG=""; [ -n "$BROWSER" ] && BARG="--browser-executable=$BROWSER"
mkdir -p out videos
npx remotion render NiftyShort out/silent.mp4 --muted --concurrency="$(nproc)" --crf=18 $BARG --log=error
ffmpeg -v error -y -i out/silent.mp4 -i public/daily/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 21 \
  -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -shortest -movflags +faststart "videos/$D.mp4"
rm -rf out/check && mkdir -p out/check
for t in 1.5 7 15 28 36 44; do ffmpeg -v error -ss $t -i "videos/$D.mp4" -frames:v 1 -vf scale=360:640 "out/check/$t.jpg" || true; done
ffprobe -v error -show_entries format=duration,size -of compact=p=0:nk=1 "videos/$D.mp4"
