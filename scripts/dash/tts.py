"""Hindi neural voice (hi-IN-SwaraNeural, the voice Chirag approved) for a dashboard video plan — GitHub Actions.
Usage: python3 scripts/dash/tts.py dash/D/<slot>-plan.json  ->  dash/D/<slot>-tts/<tag>.mp3 + manifest.json
"""
import asyncio, json, os, sys
import edge_tts

VOICE, RATE, PITCH = "hi-IN-SwaraNeural", "+6%", "-2Hz"
plan_path = sys.argv[1]
plan = json.load(open(plan_path))
out = plan_path.replace("-plan.json", "-tts")
os.makedirs(out, exist_ok=True)


async def main():
    for ln in plan["lines"]:
        path = os.path.join(out, ln["tag"] + ".mp3")
        for _ in range(4):
            try:
                await edge_tts.Communicate(ln["text"], VOICE, rate=RATE, pitch=PITCH).save(path)
                if os.path.getsize(path) > 2000:
                    break
            except Exception as e:
                print("retry", ln["tag"], e, file=sys.stderr)
            await asyncio.sleep(3)
        else:
            sys.exit("TTS failed for " + ln["tag"])
        print("ok", ln["tag"])

asyncio.run(main())
json.dump({"voice": VOICE, "rate": RATE, "pitch": PITCH, "lines": [{"tag": l["tag"], "text": l["text"]} for l in plan["lines"]]},
          open(os.path.join(out, "manifest.json"), "w"), ensure_ascii=False, indent=1)
