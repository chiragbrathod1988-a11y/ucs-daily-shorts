"""Assemble audio (Hindi neural voice + music + sfx), English subtitles and src/dashData.ts for a dashboard video.
Usage: python3 scripts/dash/build.py D slot      (needs dash/D/<slot>-plan.json, -tts/, screenshots from dash.yml)
"""
import json, os, sys, subprocess, shutil, struct, re
import numpy as np, soundfile as sf

D, slot = sys.argv[1], sys.argv[2]
root = os.path.join(os.path.dirname(__file__), "..", "..")
base = os.path.join(root, "dash", D)
plan = json.load(open(os.path.join(base, f"{slot}-plan.json")))
ttsd = os.path.join(base, f"{slot}-tts")
man = json.load(open(os.path.join(ttsd, "manifest.json")))
assert [l["tag"] for l in man["lines"]] == [l["tag"] for l in plan["lines"]], "voice does not match plan — re-run dash.yml"
pub = os.path.join(root, "public", "dash")
shutil.rmtree(pub, ignore_errors=True); os.makedirs(pub)
SR = 48000

def load(tag):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ttsd, tag + ".mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    nz = np.where(np.abs(a) > 0.003)[0]
    if len(nz): a = a[max(0, nz[0] - 960): nz[-1] + 2400]
    f = int(0.01 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    return a

LEAD, GAP, SCENE_GAP, END_HOLD = 0.45, 0.16, 0.32, 1.8
pieces, t, timeline = [np.zeros(int(LEAD * SR), np.float32)], LEAD, []
prev_scene = None
for i, (ln, sc) in enumerate(zip(plan["lines"], plan["scenes"])):
    key = (sc["kind"], sc.get("shot"), sc.get("n"))
    if prev_scene is not None:
        g = GAP if key == prev_scene else SCENE_GAP
        pieces.append(np.zeros(int(g * SR), np.float32)); t += g
    a = load(ln["tag"])
    timeline.append({"tag": ln["tag"], "start": round(t, 3), "end": round(t + len(a) / SR, 3), "en": ln["en"]})
    pieces.append(a); t += len(a) / SR
    prev_scene = key
pieces.append(np.zeros(int(END_HOLD * SR), np.float32)); t += END_HOLD
total = round(t, 3)
voice = np.concatenate(pieces)
sf.write(os.path.join(base, f"{slot}-voice_raw.wav"), voice, SR)

# English subtitles: split each line into <= 32-char chunks timed by length
subs = []
for seg in timeline:
    words, chunks, cur = seg["en"].split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > 32:
            chunks.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: chunks.append(cur)
    wts = np.array([max(6, len(c)) for c in chunks], float)
    b = seg["start"] + np.concatenate([[0], np.cumsum(wts) / wts.sum()]) * (seg["end"] - seg["start"])
    for k, c in enumerate(chunks):
        subs.append({"text": c, "start": round(b[k], 3), "end": round(b[k + 1] + (0.15 if k == len(chunks) - 1 else 0), 3)})

# screenshots -> public/dash, with sizes
def png_size(p):
    with open(p, "rb") as f:
        h = f.read(24)
    return struct.unpack(">II", h[16:24])
shots = {}
for s in plan["shots"]:
    src = os.path.join(base, f"{slot}-{s['name']}.png")
    if os.path.exists(src):
        shutil.copy(src, os.path.join(pub, s["name"] + ".png"))
        w, h = png_size(src)
        shots[s["name"] + ".png"] = {"w": w, "h": h}
for f in ("logo.png", "chirag.png"):
    shutil.copy(os.path.join(root, "public", "daily", f), os.path.join(pub, f))

# music + sfx + mix
here = os.path.join(root, "scripts")
subprocess.run([sys.executable, os.path.join(here, "music.py"), os.path.join(pub, "music.wav"), str(total + 0.5)], check=True)
ev = [(0.05, "whoosh")]
for seg, sc in zip(timeline, plan["scenes"]):
    if sc.get("phase") == "result":
        ev.append((seg["start"], "ding" if sc.get("win") else "click"))
    elif sc["kind"] in ("signal", "feature", "ahead", "cta") and not seg["tag"].endswith("2"):
        ev.append((max(0, seg["start"] - 0.2), "whoosh"))
json.dump(ev, open(os.path.join(base, f"{slot}-sfx.json"), "w"))
subprocess.run([sys.executable, os.path.join(here, "sfx.py"), os.path.join(base, f"{slot}-sfx.json"), os.path.join(pub, "sfx.wav"), str(total + 0.5)], check=True)
DD = f"{total:.3f}"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(base, f"{slot}-voice_raw.wav"), "-af",
                "highpass=f=80,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=1.5,acompressor=threshold=-22dB:ratio=2:attack=15:release=200,loudnorm=I=-15:TP=-1.5:LRA=7",
                "-ar", str(SR), "-ac", "1", os.path.join(pub, "voice.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(pub, "music.wav"), "-i", os.path.join(pub, "voice.wav"), "-i", os.path.join(pub, "sfx.wav"),
                "-filter_complex",
                f"[0:a]atrim=0:{DD},highpass=f=60,lowpass=f=9000,equalizer=f=2800:t=q:w=1.4:g=-6,volume=0.36[m];"
                f"[1:a]aformat=channel_layouts=stereo,apad=whole_dur={DD},asplit=2[v1][v2];"
                f"[m][v1]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450[md];"
                f"[md][v2][2:a]amix=inputs=3:weights='1 1 0.8':normalize=0,afade=t=out:st={total-1.2:.2f}:d=1.2,loudnorm=I=-14:TP=-1.0:LRA=11[o]",
                "-map", "[o]", "-ar", str(SR), "-t", DD, os.path.join(pub, "mix.wav")], check=True)

data = {"date": D, "slot": slot, "mode": plan["mode"], "feature": plan["feature"], "duration": total,
        "timeline": timeline, "scenes": plan["scenes"], "subs": subs, "shots": shots, "meta": plan.get("meta", {})}
open(os.path.join(root, "src", "dashData.ts"), "w").write(
    "// AUTO-GENERATED by scripts/dash/build.py — do not edit.\nexport const DASH = " + json.dumps(data, ensure_ascii=False, indent=1) + " as const;\n")
print(json.dumps({"duration": total, "lines": len(timeline), "shots": list(shots)}))
