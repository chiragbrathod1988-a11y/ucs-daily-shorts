"""Build voice (Piper hi_IN-pratham), captions timing, music and SFX for the daily Nifty Short.

Usage: python3 build_audio.py levels.json OUT_PUBLIC_DIR OUT_TS_FILE
levels.json: {"tradeDate":"2026-10-30","prevDate":"2026-10-29","open":..,"high":..,"low":..,"close":..,"change":..,"changePct":..}
"""
import json, sys, os, subprocess, wave, datetime, re
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
from hindi_num import words as hw

VOICE_DIR = os.environ.get("PIPER_DIR", os.path.join(os.path.dirname(__file__), "..", ".piper", "vits-piper-hi_IN-pratham-medium"))
VOICE = "hi_IN-pratham-medium"
SR = 22050

lv = json.load(open(sys.argv[1]))
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

# (tag, devanagari for TTS, roman caption — *word* = gold highlight)
bull = ("bull",
        f"अगर निफ़्टी {hw(lev['CPRhi'])} के ऊपर टिकता है, तो बायस पॉज़िटिव रहेगा, और {hw(lev['R1'])} का लेवल टेस्ट हो सकता है।",
        f"*{fmt(lev['CPRhi'])}* ke upar tike toh bias *positive* — *{fmt(lev['R1'])}* test ho sakta hai")
bear = ("bear",
        f"और अगर {hw(lev['P'])} के नीचे गया, तो {hw(lev['S1'])} तक दबाव आ सकता है।",
        f"*{fmt(lev['P'])}* ke neeche gaya toh *{fmt(lev['S1'])}* tak dabaav")
if below_cpr:
    bear = ("bear",
            f"अगर निफ़्टी {hw(lev['P'])} के नीचे रहता है, तो दबाव बना रह सकता है, और {hw(lev['S1'])} का लेवल टेस्ट हो सकता है।",
            f"*{fmt(lev['P'])}* ke neeche raha toh *pressure* — *{fmt(lev['S1'])}* test ho sakta hai")
    bull = ("bull",
            f"और अगर {hw(lev['CPRhi'])} के ऊपर निकला, तो {hw(lev['R1'])} तक रिकवरी आ सकती है।",
            f"*{fmt(lev['CPRhi'])}* ke upar nikla toh *{fmt(lev['R1'])}* tak recovery")

S = [
    ("intro", f"नमस्ते ट्रेडर्स! {hw(td.day)} {MONTH_HI[td.month-1]} के निफ़्टी लेवल्स।",
     f"Namaste traders! *{td.day} {MONTH_EN[td.month-1]}* ke *Nifty levels*"),
    ("prev", f"{prev_word} निफ़्टी {hw(abs(lev['change']))} पॉइंट्स {'ऊपर' if up else 'नीचे'}, {hw(lev['closeR'])} पर बंद हुआ।",
     f"{prev_word_en} Nifty *{fmt(r(abs(lev['change'])))} points {'upar' if up else 'neeche'}* — *{fmt(lev['closeR'])}* par close"),
    ("pivot", f"आज का पिवट है, {hw(lev['P'])}।", f"Aaj ka *pivot* hai *{fmt(lev['P'])}*"),
    ("r1", f"ऊपर की तरफ़ पहला रेज़िस्टेंस, {hw(lev['R1'])},", f"Upar pehla *resistance* — *{fmt(lev['R1'])}*"),
    ("r2", f"और फिर, {hw(lev['R2'])}।", f"aur phir *{fmt(lev['R2'])}*"),
    ("s1", f"नीचे की तरफ़ पहला सपोर्ट, {hw(lev['S1'])},", f"Neeche pehla *support* — *{fmt(lev['S1'])}*"),
    ("s2", f"और फिर, {hw(lev['S2'])}।", f"aur phir *{fmt(lev['S2'])}*"),
    *( [bear, bull] if below_cpr else [bull, bear] ),
    ("cta", "लेवल्स सेव कर लीजिए, और रोज़ सुबह के लिए फ़ॉलो कीजिए, अपर सर्किट स्टॉक्स।",
     "Levels *save* karo — roz subah *follow* karo *UpperCircuitStocks*"),
]

from piper import PiperVoice
from piper.config import SynthesisConfig
pv = PiperVoice.load(f"{VOICE_DIR}/{VOICE}.onnx", config_path=f"{VOICE_DIR}/{VOICE}.onnx.json")
syn = SynthesisConfig(length_scale=0.9, noise_scale=0.6, noise_w_scale=0.8)

LEAD = 0.35
GAP_COMMA, GAP_STOP = 0.18, 0.34
pieces, timeline, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
for tag, dev, rom in S:
    tmp = os.path.join(out_dir, "_s.wav")
    with wave.open(tmp, "wb") as w:
        pv.synthesize_wav(dev, w, syn_config=syn)
    a, sr = sf.read(tmp, dtype="float32")
    assert sr == SR, sr
    # trim leading/trailing silence
    nz = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, nz[0] - 200): nz[-1] + 400] if len(nz) else a
    d = len(a) / SR
    timeline.append({"tag": tag, "start": round(t, 3), "end": round(t + d, 3), "text": rom})
    pieces.append(a)
    gap = GAP_COMMA if dev.rstrip().endswith(",") else GAP_STOP
    pieces.append(np.zeros(int(gap * SR), np.float32))
    t += d + gap
os.remove(os.path.join(out_dir, "_s.wav"))
END_HOLD = 2.4
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
        if tk in ("—", "-", ",") and cur:
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
              (ev["s1"], "pop"), (ev["s2"], "pop"), (ev["bull"], "whoosh"), (ev["bear"], "whoosh"), (ev["cta"], "ding"),
              (total - END_HOLD + 0.1, "whoosh")]
json.dump(sfx_events, open(os.path.join(out_dir, "sfx.json"), "w"))
subprocess.run([sys.executable, os.path.join(here, "sfx.py"), os.path.join(out_dir, "sfx.json"), os.path.join(out_dir, "sfx.wav"), str(total + 0.5)], check=True)

D = f"{total:.3f}"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(out_dir, "voice_raw.wav"),
                "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=8",
                "-ar", "48000", "-ac", "1", os.path.join(out_dir, "voice.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(out_dir, "music.wav"), "-i", os.path.join(out_dir, "voice.wav"),
                "-i", os.path.join(out_dir, "sfx.wav"), "-filter_complex",
                f"[0:a]atrim=0:{D},highpass=f=60,equalizer=f=2500:t=q:w=1.2:g=-4,volume=0.6[m];"
                f"[1:a]aformat=channel_layouts=stereo,apad=whole_dur={D},asplit=2[v1][v2];"
                f"[m][v1]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450:makeup=1[md];"
                f"[md][v2][2:a]amix=inputs=3:weights='1 1 1':normalize=0,afade=t=out:st={total-1.2:.2f}:d=1.2,loudnorm=I=-14:TP=-1.0:LRA=11[out]",
                "-map", "[out]", "-ar", "48000", "-t", D, os.path.join(out_dir, "mix.wav")], check=True)

data = {"date": lv["tradeDate"], "prevDate": lv["prevDate"], "dayEn": DAY_EN[td.weekday()], "dateLabel": f"{td.day} {MONTH_EN[td.month-1][:3].upper()} {td.year}",
        "levels": lev, "up": up, "bearFirst": bool(below_cpr), "timeline": timeline, "captions": caps, "duration": round(total, 3)}
open(ts_out, "w").write("// AUTO-GENERATED by scripts/build_audio.py — do not edit by hand.\nexport const DAILY = " + json.dumps(data, ensure_ascii=False, indent=1) + " as const;\n")
print(json.dumps({"duration": total, "levels": lev, "timeline": [(s["tag"], s["start"]) for s in timeline]}, ensure_ascii=False))
