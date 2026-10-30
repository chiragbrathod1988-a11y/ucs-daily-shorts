"""Generate the daily voice-over with Microsoft neural TTS (edge-tts) — runs in GitHub Actions
(the build sandbox cannot reach the TTS service). One MP3 per script line, so caption timing stays exact.

Usage: python3 scripts/tts_edge.py data/YYYY-MM-DD.json
Writes tts/YYYY-MM-DD/<tag>.mp3 and tts/YYYY-MM-DD/manifest.json ({voice, rate, lines:[{tag,text}]}).
"""
import asyncio, json, os, subprocess, sys

import edge_tts

VOICE = os.environ.get("UCS_EDGE_VOICE", "hi-IN-SwaraNeural")   # clear adult female Hindi neural voice
RATE = os.environ.get("UCS_EDGE_RATE", "+4%")
PITCH = os.environ.get("UCS_EDGE_PITCH", "-2Hz")

src = sys.argv[1]
D = json.load(open(src))["tradeDate"]
out = os.path.join("tts", D)
os.makedirs(out, exist_ok=True)
lines = json.loads(subprocess.run([sys.executable, "scripts/build_audio.py", src, "--dump-script"],
                                  check=True, capture_output=True, text=True).stdout)


async def main():
    for ln in lines:
        path = os.path.join(out, ln["tag"] + ".mp3")
        for attempt in range(4):
            try:
                await edge_tts.Communicate(ln["text"], VOICE, rate=RATE, pitch=PITCH).save(path)
                if os.path.getsize(path) > 2000:
                    break
            except Exception as e:  # transient service errors
                print("retry", ln["tag"], e, file=sys.stderr)
            await asyncio.sleep(3)
        else:
            sys.exit(f"TTS failed for {ln['tag']}")
        print("ok", ln["tag"], os.path.getsize(path))

asyncio.run(main())
json.dump({"voice": VOICE, "rate": RATE, "pitch": PITCH, "lines": lines},
          open(os.path.join(out, "manifest.json"), "w"), ensure_ascii=False, indent=1)
