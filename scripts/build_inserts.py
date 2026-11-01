"""Build the AI Dashboard inserts for a long-form edit and splice them into the source video.

Usage: python3 scripts/build_inserts.py edits/<name>/plan.json SOURCE.mp4 OUT.mp4
plan.json: {"name": "<tts folder>", "dashUrl": "...", "telegram": "...",
            "inserts": [{"kind": "intro", "at": 52.7, "lines": ["a1","a2","a3"]}, ... {"kind": "end", "at": "end", ...}]}
Voice lines come from tts/<name>/<tag>.mp3 (Microsoft neural TTS, made by .github/workflows/tts.yml).
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf

plan_path, SRC, OUT = sys.argv[1:4]
plan = json.load(open(plan_path))
ROOT = os.path.join(os.path.dirname(__file__), "..")
TTS = os.path.join(ROOT, "tts", plan["name"])
WORK = os.path.join(ROOT, "out", "inserts", plan["name"])
os.makedirs(WORK, exist_ok=True)
SR = 48000
run = lambda *a: subprocess.run(list(a), check=True)


def load(tag):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(TTS, tag + ".mp3"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    env = np.convolve(np.abs(a), np.ones(480) / 480, "same")
    nz = np.where(env > 0.004)[0]
    return a[max(0, nz[0] - 960): nz[-1] + 3600] if len(nz) else a


src_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                               check=True, capture_output=True, text=True).stdout)
clips = []
for i, ins in enumerate(plan["inserts"]):
    lead = 0.9 if ins["kind"] != "end" else 0.6
    t, parts, marks = lead, [np.zeros(int(lead * SR), np.float32)], {}
    for tag in ins["lines"]:
        a = load(tag)
        marks[tag] = round(t, 3)
        parts += [a, np.zeros(int(0.3 * SR), np.float32)]
        t += len(a) / SR + 0.3
    tail = ins.get("tail", 0.9)
    parts.append(np.zeros(int(tail * SR), np.float32))
    voice = np.concatenate(parts)
    dur = len(voice) / SR
    base = os.path.join(WORK, f"ins{i}")
    sf.write(base + "_voice.wav", voice, SR)
    run(sys.executable, os.path.join(ROOT, "scripts", "music.py"), base + "_music.wav", str(dur + 0.5))
    run("ffmpeg", "-v", "error", "-y", "-i", base + "_voice.wav", "-i", base + "_music.wav", "-filter_complex",
        f"[0:a]highpass=f=80,acompressor=threshold=-22dB:ratio=2:attack=15:release=200,loudnorm=I=-16:TP=-1.5:LRA=7,aformat=channel_layouts=stereo,asplit=2[v1][v2];"
        f"[1:a]atrim=0:{dur:.3f},volume=0.30,afade=t=in:d=0.4,afade=t=out:st={dur-0.6:.3f}:d=0.6[m];"
        f"[m][v1]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=400[md];[md][v2]amix=inputs=2:normalize=0,alimiter=limit=0.9[o]",
        "-map", "[o]", "-ar", str(SR), "-ac", "2", base + "_mix.wav")
    props = {"kind": ins["kind"], "duration": round(dur, 3), "marks": marks, "dashUrl": plan["dashUrl"], "telegram": plan["telegram"]}
    json.dump(props, open(base + "_props.json", "w"))
    clips.append((ins["at"], base, dur))
    print("insert", i, ins["kind"], f"{dur:.1f}s", marks, flush=True)

browser = subprocess.run("ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1",
                         shell=True, capture_output=True, text=True).stdout.strip()
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "25", "-vf", "scale=1280:720,setsar=1",
       "-c:a", "aac", "-b:a", "160k", "-ar", str(SR), "-ac", "2"]
for at, base, dur in clips:
    if os.path.exists(base + ".mp4") and os.path.getmtime(base + ".mp4") > os.path.getmtime(base + "_props.json") \
            and os.path.getmtime(base + ".mp4") > os.path.getmtime(os.path.join(ROOT, "src", "DashInsert.tsx")):
        continue   # already rendered and up to date
    cmd = ["npx", "remotion", "render", "DashInsert", base + "_silent.mp4", f"--props={base}_props.json", "--muted", "--crf=16", f"--concurrency={os.cpu_count()}", "--log=error"]
    if browser:
        cmd.append(f"--browser-executable={browser}")
    subprocess.run(cmd, check=True, cwd=ROOT)
    run("ffmpeg", "-v", "error", "-y", "-i", base + "_silent.mp4", "-i", base + "_mix.wav", "-map", "0:v", "-map", "1:a", *ENC, "-shortest", base + ".mp4")

# splice: cut the source into pieces at the insert points (re-encoded to the same parameters), then concat-copy
pts = sorted(float(c[0]) for c in clips if c[0] != "end")
bounds = [0.0] + pts + [src_dur]
by_at = {(src_dur if c[0] == "end" else float(c[0])): c for c in clips}
seq, out_map, t = [], [], 0.0
for k in range(len(bounds) - 1):
    a, b = bounds[k], bounds[k + 1]
    piece = os.path.join(WORK, f"src{k}.mp4")
    if not os.path.exists(piece):
        run("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", SRC, *ENC, piece)
    seq.append(piece); t += b - a
    if b in by_at:
        seq.append(by_at[b][1] + ".mp4"); out_map.append(round(t, 2)); t += by_at[b][2]
lst = os.path.join(WORK, "concat.txt")
open(lst, "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in seq))
run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", OUT)
json.dump({"insertStarts": out_map, "duration": round(t, 2)}, open(os.path.join(WORK, "timeline.json"), "w"))
print("done", OUT, out_map, round(t, 2))
