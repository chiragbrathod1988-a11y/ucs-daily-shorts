"""Build voice (Microsoft neural TTS files from tts/D/, made by GitHub Actions), captions timing, music and SFX for the daily Nifty Short.

Usage: python3 build_audio.py levels.json OUT_PUBLIC_DIR OUT_TS_FILE
levels.json: {"tradeDate":"2026-10-30","prevDate":"2026-10-29","open":..,"high":..,"low":..,"close":..,"change":..,"changePct":..}
"""
import json, sys, os, subprocess, wave, datetime, re
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
from hindi_num import words as hw

SR = 24000

lv = json.load(open(sys.argv[1]))
DUMP = len(sys.argv) > 2 and sys.argv[2] == "--dump-script"
if not DUMP:
    out_dir = sys.argv[2]
    ts_out = sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)

H, L, C = lv["high"], lv["low"], lv["close"]
P = (H + L + C) / 3
R1, S1 = 2 * P - L, 2 * P - H
R2, S2 = P + (H - L), P - (H - L)
BC = (H + L) / 2
TC = 2 * P - BC
cpr_lo, cpr_hi = min(TC, BC), max(TC, BC)
r = lambda x: int(round(x))
lev = dict(P=r(P), R1=r(R1), R2=r(R2), S1=r(S1), S2=r(S2), CPRlo=r(cpr_lo), CPRhi=r(cpr_hi),
           close=round(C, 2), closeR=r(C), open=lv["open"], high=H, low=L,
           change=round(lv["change"], 2), changePct=round(lv["changePct"], 2))
up = lv["change"] >= 0
above_cpr = C >= cpr_hi
below_cpr = C < cpr_lo

td = datetime.date.fromisoformat(lv["tradeDate"])
MONTH_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
DAY_HI = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
MONTH_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
prev_word = "कल" if (td - datetime.date.fromisoformat(lv["prevDate"])).days == 1 else "पिछले सेशन में"
prev_word_en = "Kal" if prev_word == "कल" else "Pichhle session mein"
fmt = lambda n: f"{n:,}"

# (tag, spoken text for TTS in Devanagari — casual Hinglish, all numbers spoken in English — , roman caption; *word* = gold)
from english_num import words as ew
bull = ("bull",
        f"अगर निफ़्टी {ew(lev['CPRhi'])} के ऊपर होल्ड करता है, तो {ew(lev['R1'])} टेस्ट हो सकता है।",
        f"*{fmt(lev['CPRhi'])}* ke upar hold kiya toh *{fmt(lev['R1'])}* test ho sakta hai")
bear = ("bear",
        f"लेकिन अगर {ew(lev['P'])} के नीचे फिसला, तो {ew(lev['S1'])} तक प्रेशर आ सकता है।",
        f"*{fmt(lev['P'])}* ke neeche fisla toh *{fmt(lev['S1'])}* tak pressure")
if below_cpr:
    bear = ("bear",
            f"अगर निफ़्टी {ew(lev['P'])} के नीचे ही रहता है, तो प्रेशर बना रहेगा, और {ew(lev['S1'])} टेस्ट हो सकता है।",
            f"*{fmt(lev['P'])}* ke neeche raha toh *pressure* — *{fmt(lev['S1'])}* test ho sakta hai")
    bull = ("bull",
            f"लेकिन अगर {ew(lev['CPRhi'])} के ऊपर निकला, तो {ew(lev['R1'])} तक रिकवरी आ सकती है।",
            f"*{fmt(lev['CPRhi'])}* ke upar nikla toh *{fmt(lev['R1'])}* tak recovery")

MARKS = {"dash": [("screener", "स्क्रीनर्स"), ("heatmap", "हीट मैप"), ("overview", "ओवरव्यू"), ("research", "रिसर्च")]}
prev_hi = "कल" if prev_word == "कल" else "लास्ट सेशन में"

S = [
    ("intro", f"हेलो ट्रेडर्स! {ew(td.day)} {MONTH_HI[td.month-1]} के निफ़्टी लेवल्स, चलो देखते हैं।",
     f"Hello traders! *{td.day} {MONTH_EN[td.month-1]}* ke *Nifty levels* — chalo dekhte hain"),
    ("prev", f"{prev_hi} निफ़्टी {ew(abs(lev['change']))} पॉइंट्स {'ऊपर' if up else 'नीचे'}, {ew(lev['closeR'])} पे क्लोज़ हुआ।",
     f"{prev_word_en} Nifty *{fmt(r(abs(lev['change'])))} points {'upar' if up else 'neeche'}* — *{fmt(lev['closeR'])}* pe close"),
    ("pivot", f"आज का पिवट है, {ew(lev['P'])}।", f"Aaj ka *pivot* hai *{fmt(lev['P'])}*"),
    ("r1", f"ऊपर फर्स्ट रेज़िस्टेंस, {ew(lev['R1'])},", f"Upar first *resistance* — *{fmt(lev['R1'])}*"),
    ("r2", f"उसके बाद, {ew(lev['R2'])}।", f"uske baad *{fmt(lev['R2'])}*"),
    ("s1", f"नीचे फर्स्ट सपोर्ट, {ew(lev['S1'])},", f"Neeche first *support* — *{fmt(lev['S1'])}*"),
    ("s2", f"और फिर, {ew(lev['S2'])}।", f"aur phir *{fmt(lev['S2'])}*"),
    *( [bear, bull] if below_cpr else [bull, bear] ),
    ("dash", "और हाँ, अपर सर्किट स्टॉक्स के ए आई डैशबोर्ड पे मिलेंगे, स्टॉक स्क्रीनर्स, हीट मैप, निफ़्टी ओवरव्यू, और डिटेल्ड स्टॉक रिसर्च।",
     "*UpperCircuitStocks AI Dashboard* pe — *Stock Screeners* *Heat Map* *Nifty Overview* aur *detailed research*"),
    ("dash2", "लिंक डिस्क्रिप्शन में है, एक बार ज़रूर चेक करो।", "Link *description* mein — *ek baar zaroor check karo*"),
    ("cta", "लेवल्स सेव कर लो, और रोज़ सुबह के लिए फॉलो करो, अपर सर्किट स्टॉक्स।",
     "Levels *save* karo — roz subah *follow* karo *UpperCircuitStocks*"),
]

if DUMP:
    print(json.dumps([{"tag": tag, "text": dev} for tag, dev, _ in S], ensure_ascii=False))
    sys.exit(0)

# Voice: per-line MP3s from Microsoft neural TTS (scripts/tts_edge.py, run by .github/workflows/tts.yml).
# The text in the manifest must match today's script exactly — never fall back to a different voice.
TTS_DIR = os.path.join(os.path.dirname(__file__), "..", "tts", lv["tradeDate"])
man = json.load(open(os.path.join(TTS_DIR, "manifest.json")))
want = [{"tag": tag, "text": dev} for tag, dev, _ in S]
assert man["lines"] == want, "tts/<date>/manifest.json does not match today's script — re-run the TTS workflow"

def synth(tag):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(TTS_DIR, tag + ".mp3"), "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

LEAD = 0.30
GAP_COMMA, GAP_STOP = 0.10, 0.22   # short natural pauses so the voice flows unbroken
pieces, timeline, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
for tag, dev, rom in S:
    a = synth(tag)
    # gentle trim: keep soft word endings (no clipping), only drop long silence
    env = np.convolve(np.abs(a), np.ones(240) / 240, "same")
    nz = np.where(env > 0.004)[0]
    if len(nz):
        a = a[max(0, nz[0] - 480): min(len(a), nz[-1] + 1800)]
    fade = int(0.012 * SR)
    a[:fade] *= np.linspace(0, 1, fade); a[-fade:] *= np.linspace(1, 0, fade)
    d = len(a) / SR
    seg = {"tag": tag, "start": round(t, 3), "end": round(t + d, 3), "text": rom}
    # sub-marks inside a sentence (e.g. each dashboard feature) by character position
    for key, word in MARKS.get(tag, []):
        pos = dev.find(word)
        if pos >= 0:
            seg.setdefault("marks", {})[key] = round(t + d * pos / max(1, len(dev)), 3)
    timeline.append(seg)
    pieces.append(a)
    gap = GAP_COMMA if dev.rstrip().endswith(",") else GAP_STOP
    pieces.append(np.zeros(int(gap * SR), np.float32))
    t += d + gap

END_HOLD = 1.9
pieces.append(np.zeros(int(END_HOLD * SR), np.float32))
voice = np.concatenate(pieces)
total = len(voice) / SR
sf.write(os.path.join(out_dir, "voice_raw.wav"), voice, SR)

# caption chunks: split each sentence into <= ~26 visible chars, timed by character share
def chunks(text, maxlen=26):
    # tokens: a *highlighted phrase* stays together as one unit
    toks = re.findall(r"\*[^*]+\*|[^\s*]+", text)
    out, cur = [], []
    for tk in toks:
        trial = " ".join(cur + [tk])
        if tk == "," and cur:
            cur[-1] += ","; continue
        if tk in ("—", "-") and cur:
            cur.append(tk); continue
        if cur and len(trial.replace("*", "")) > maxlen:
            out.append(" ".join(cur)); cur = [tk]
        else:
            cur.append(tk)
    if cur: out.append(" ".join(cur))
    return out
caps = []
for seg in timeline:
    cs = chunks(seg["text"])
    wts = np.array([max(4, len(c.replace("*", ""))) for c in cs], float)
    b = seg["start"] + np.concatenate([[0], np.cumsum(wts) / wts.sum()]) * (seg["end"] - seg["start"])
    for i, c in enumerate(cs):
        caps.append({"text": c, "start": round(b[i], 3), "end": round(b[i + 1] + (0.12 if i == len(cs) - 1 else 0), 3)})

# music (original synth) + sfx
here = os.path.dirname(__file__)
subprocess.run([sys.executable, os.path.join(here, "music.py"), os.path.join(out_dir, "music.wav"), str(total + 0.5)], check=True)
ev = {s["tag"]: s["start"] for s in timeline}
sfx_events = [(0.05, "whoosh"), (ev["prev"], "coin"), (ev["pivot"], "pop"), (ev["r1"], "pop"), (ev["r2"], "pop"),
              (ev["s1"], "pop"), (ev["s2"], "pop"), (ev["bull"], "whoosh"), (ev["bear"], "whoosh"), (ev["dash"], "whoosh"), *[(v, "pop") for v in timeline[[x["tag"] for x in timeline].index("dash")].get("marks", {}).values()],  (ev["cta"], "whoosh"),
              (total - END_HOLD + 0.1, "whoosh")]
json.dump(sfx_events, open(os.path.join(out_dir, "sfx.json"), "w"))
subprocess.run([sys.executable, os.path.join(here, "sfx.py"), os.path.join(out_dir, "sfx.json"), os.path.join(out_dir, "sfx.wav"), str(total + 0.5)], check=True)

D = f"{total:.3f}"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(out_dir, "voice_raw.wav"),
                "-af", "highpass=f=80,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=2:attack=15:release=200:makeup=1.5,loudnorm=I=-15:TP=-1.5:LRA=7",
                "-ar", "48000", "-ac", "1", os.path.join(out_dir, "voice.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(out_dir, "music.wav"), "-i", os.path.join(out_dir, "voice.wav"),
                "-i", os.path.join(out_dir, "sfx.wav"), "-filter_complex",
                f"[0:a]atrim=0:{D},highpass=f=60,lowpass=f=9000,equalizer=f=2800:t=q:w=1.4:g=-6,volume=0.42[m];"
                f"[1:a]aformat=channel_layouts=stereo,apad=whole_dur={D},asplit=2[v1][v2];"
                f"[m][v1]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450:makeup=1[md];"
                f"[md][v2][2:a]amix=inputs=3:weights='1 1 1':normalize=0,afade=t=out:st={total-1.2:.2f}:d=1.2,loudnorm=I=-14:TP=-1.0:LRA=11[out]",
                "-map", "[out]", "-ar", "48000", "-t", D, os.path.join(out_dir, "mix.wav")], check=True)

data = {"date": lv["tradeDate"], "prevDate": lv["prevDate"], "dayEn": DAY_EN[td.weekday()], "dateLabel": f"{td.day} {MONTH_EN[td.month-1][:3].upper()} {td.year}",
        "levels": lev, "up": up, "bearFirst": bool(below_cpr), "timeline": timeline, "captions": caps, "duration": round(total, 3)}
open(ts_out, "w").write("// AUTO-GENERATED by scripts/build_audio.py — do not edit by hand.\nexport const DAILY = " + json.dumps(data, ensure_ascii=False, indent=1) + " as const;\n")
print(json.dumps({"duration": total, "levels": lev, "timeline": [(s["tag"], s["start"]) for s in timeline]}, ensure_ascii=False))
