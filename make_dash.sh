#!/usr/bin/env bash
# Build a dashboard video: ./make_dash.sh YYYY-MM-DD morning|evening  ->  videos/dash/D-slot.mp4 (+ thumbnail, check frames)
set -e
D=$1; S=$2
CH=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell 2>/dev/null | head -1)
B=${CH:+--browser-executable=$CH}
python3 scripts/dash/build.py $D $S
mkdir -p out videos/dash out/check-$S
npx remotion render DashShort out/dash-silent.mp4 --muted --concurrency=$(nproc) --crf=18 $B --log=error
ffmpeg -v error -y -i out/dash-silent.mp4 -i public/dash/mix.wav -map 0:v -map 1:a -c:v libx264 -crf 21 -preset medium -pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart videos/dash/$D-$S.mp4
npx remotion still DashShort videos/dash/$D-$S-thumb.jpg --frame=40 --jpeg-quality=90 $B --log=error
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 videos/dash/$D-$S.mp4)
for f in 0.03 0.15 0.3 0.45 0.6 0.75 0.88 0.97; do
  t=$(python3 -c "print($DUR*$f)"); ffmpeg -v error -y -ss $t -i videos/dash/$D-$S.mp4 -frames:v 1 -vf scale=540:-1 out/check-$S/$f.png
done
echo "built videos/dash/$D-$S.mp4 ($DUR s)"
