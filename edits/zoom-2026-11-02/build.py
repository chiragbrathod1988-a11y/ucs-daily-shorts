#!/usr/bin/env python3
"""Build the 2026-11-02 Zoom demo reel: 1080x1920, Hindi AI voice (Matilda), English subtitles,
black/gold UCS theme, face segment removed, enrol ending. Usage: build.py SRC.mp4 OUT.mp4"""
import os, subprocess, sys, json
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 25
GOLD, BLACK, WHITE = "#D4AF37", "#0A0A0A", "#FFFFFF"
FONT_B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
VO = [f"{HERE}/voice/v{i}.mp3" for i in range(1, 8)]
MUSIC = sys.argv[3] if len(sys.argv) > 3 else None
TMP = f"{HERE}/tmp"; os.makedirs(TMP, exist_ok=True)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))

D = [dur(v) for v in VO]

def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

# common tail: pad the cropped region with a gold frame, place on black canvas
def canvas(inner, d, out):
    """inner = filter chain producing [c]; result centred on black 1080x1920 for d seconds"""
    fc = (f"{inner};color=c={BLACK}:s={W}x{H}:r={FPS}:d={d:.3f}[bg];"
          f"[c]pad=iw+10:ih+10:5:5:color={GOLD}[cf];[bg][cf]overlay=(W-w)/2:(H-h)/2-40:shortest=1,format=yuv420p[v]")
    return fc

def seg_video(ss, t, crop_chain, d, out, extra_in=None):
    inner = f"[0:v]trim=start=0:duration={t:.3f},setpts=PTS-STARTPTS,{crop_chain}[c]"
    run(["-ss", f"{ss}", "-t", f"{t + 0.2:.3f}", "-i", SRC, "-filter_complex", canvas(inner, d, out), "-map", "[v]",
         "-t", f"{d:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out])

def seg_still(ss, crop_box, d, out, zoom=1.12):
    x, y, w, h = crop_box
    frame = f"{TMP}/still_{ss}.png"
    run(["-ss", f"{ss}", "-i", SRC, "-frames:v", "1", frame])
    im = Image.open(frame).crop((x, y, x + w, y + h)); sw = 1000; sh = int(h * sw / w) // 2 * 2
    im = im.resize((sw, sh), Image.LANCZOS); still = f"{TMP}/still_{ss}_c.png"; im.save(still)
    n = int(d * FPS)
    inner = (f"[0:v]scale={sw*2}:{sh*2},zoompan=z='1+({zoom}-1)*on/{n}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
             f":s={sw}x{sh}:fps={FPS}[c]")
    run(["-loop", "1", "-t", f"{d + 0.2:.3f}", "-i", still, "-filter_complex", canvas(inner, d, out), "-map", "[v]",
         "-t", f"{d:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out])

def seg_still_pan(ss, crop_box, win, d, out):
    """still frame, crop_box=(x,y,w,h) strip; a `win`-wide window pans left->right over it"""
    x, y, w, h = crop_box
    frame = f"{TMP}/still_{ss}.png"
    run(["-ss", f"{ss}", "-i", SRC, "-frames:v", "1", frame])
    im = Image.open(frame).crop((x, y, x + w, y + h)); still = f"{TMP}/still_{ss}_p.png"; im.save(still)
    sw = 1000; sh = int(h * sw / win) // 2 * 2
    n = int(d * FPS); span = w - win
    inner = (f"[0:v]crop={win}:{h}:'min({span},{span}*t/{d-1.5:.2f})':0,scale={sw}:{sh}[c]")
    run(["-loop", "1", "-t", f"{d + 0.2:.3f}", "-i", still, "-filter_complex", canvas(inner, d, out), "-map", "[v]",
         "-t", f"{d:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out])

clips = []
# 1. Four options signals: pan across the 4 cards (stats row with ₹ excluded)
c1 = f"{TMP}/c1.mp4"
seg_still_pan(6.0, (0, 790, 2880, 914), 1300, D[0], c1); clips.append(c1)
# 2. One card: entry / target / SL / exit rule, slow zoom
c2 = f"{TMP}/c2.mp4"
n2 = int(D[1] * FPS)
seg_video(14.0, D[1], f"crop=900:884:100:820,scale=1000:-2,zoompan=z='1+0.18*on/{n2}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s=1000x982:fps={FPS}", D[1], c2); clips.append(c2)
# 3. Buy on Fyers / Zerodha / Dhan — slowed scroll
c3 = f"{TMP}/c3.mp4"; seg_still(27.0, (0, 1000, 1440, 704), D[2], c3, zoom=1.15); clips.append(c3)
# 4. Ask the Scanner AI (still, zoom)
c4 = f"{TMP}/c4.mp4"; seg_still(34.0, (0, 1180, 1500, 524), D[3], c4); clips.append(c4)
# 5. Options -> Futures pan, then the broker order popup
c5a, c5b, c5 = f"{TMP}/c5a.mp4", f"{TMP}/c5b.mp4", f"{TMP}/c5.mp4"
da = D[4] - 3.0
seg_video(50.0, da, f"crop=1440:1144:'min(1440,1440*t/{da-1:.2f})':560,scale=1000:-2", da, c5a)
seg_video(69.6, 3.0, "crop=1550:700:400:170,scale=1000:-2", 3.0, c5b)
with open(f"{TMP}/c5.txt", "w") as f: f.write(f"file '{c5a}'\nfile '{c5b}'\n")
run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/c5.txt", "-c", "copy", c5]); clips.append(c5)
# 6. Phone alerts bar (still, zoom)
c6 = f"{TMP}/c6.mp4"; seg_still(96.0, (0, 150, 1500, 560), D[5], c6, zoom=1.10); clips.append(c6)

# 7. Ending slides (enrol in 3 steps)
def slide(name, lines, sub=None, badge=None, steps=None, tagline=None):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    # subtle gold frame + corner accents
    d.rectangle((40, 40, W - 40, H - 40), outline=GOLD, width=3)
    fb = lambda s: ImageFont.truetype(FONT_B, s); fm = lambda s: ImageFont.truetype(FONT_M, s)
    y = 300
    if badge:
        bw = d.textlength(badge, font=fb(34)) + 80
        d.rounded_rectangle(((W - bw) / 2, y, (W + bw) / 2, y + 70), 35, fill=GOLD)
        d.text((W / 2, y + 35), badge, font=fb(34), fill=BLACK, anchor="mm"); y += 130
    for ln, size, col in lines:
        d.text((W / 2, y), ln, font=fb(size), fill=col, anchor="ma"); y += size + 24
    if steps:
        y += 40
        for i, (title, desc, on) in enumerate(steps, 1):
            col = GOLD if on else "#4a4a4a"; tcol = WHITE if on else "#4a4a4a"
            d.ellipse((120, y, 220, y + 100), fill=col)
            d.text((170, y + 50), str(i), font=fb(52), fill=BLACK, anchor="mm")
            d.text((260, y + 2), title, font=fb(50), fill=tcol)
            d.text((260, y + 66), desc, font=fm(32), fill=("#CFCFCF" if on else "#4a4a4a"))
            y += 190
    if tagline:
        d.multiline_text((W / 2, H - 560), tagline, font=fb(52), fill=GOLD, anchor="ma", align="center", spacing=14)
    if sub:
        d.text((W / 2, H - 300), sub, font=fm(30), fill="#9a9a9a", anchor="ma")
    d.text((W / 2, H - 120), "UpperCircuitStocks  •  AI Dashboard", font=fm(32), fill=GOLD, anchor="ma")
    p = f"{TMP}/{name}.png"; im.save(p); return p

STEPS = [("Open the app", "app.uppercircuitstocks.com"), ("Sign up", "Create your free login"), ("Choose your Plan", "Tap Plans - pick a plan - done")]
def steps_on(k): return [(t, dsc, i < k) for i, (t, dsc) in enumerate(STEPS)]
sA = slide("sA", [("AI DASHBOARD", 92, GOLD), ("Enroll in 3 easy steps", 60, WHITE)], badge="ENROLL TODAY")
sB1 = slide("sB1", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=steps_on(1))
sB2 = slide("sB2", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=steps_on(2))
sB3 = slide("sB3", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=steps_on(3))
sC = slide("sC", [("LINK IN BIO", 96, GOLD), ("app.uppercircuitstocks.com", 46, WHITE)], tagline="Start today.\nKal ka market kisi ka\nintezaar nahi karta.",
           sub="Information & education only. Not investment advice.\nSignals are generated as per scanner rules.")
# timing inside the 24.5 s ending voice
end_parts = [(sA, 4.6), (sB1, 3.6), (sB2, 2.6), (sB3, 5.2), (sC, D[6] - 16.0)]
parts = []
for i, (img, d) in enumerate(end_parts):
    p = f"{TMP}/e{i}.mp4"
    run(["-loop", "1", "-t", f"{d:.3f}", "-i", img, "-vf", f"fade=t=in:st=0:d=0.3,format=yuv420p", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", p]); parts.append(p)
c7 = f"{TMP}/c7.mp4"
with open(f"{TMP}/c7.txt", "w") as f: f.write("".join(f"file '{p}'\n" for p in parts))
run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/c7.txt", "-c", "copy", c7]); clips.append(c7)

# ---- concat video, voice, music ----
with open(f"{TMP}/all.txt", "w") as f: f.write("".join(f"file '{p}'\n" for p in clips))
run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/all.txt", "-c", "copy", f"{TMP}/video.mp4"])
with open(f"{TMP}/vo.txt", "w") as f: f.write("".join(f"file '{p}'\n" for p in VO))
run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/vo.txt", "-ar", "48000", "-ac", "2", f"{TMP}/voice.wav"])
total = sum(D)

# ---- subtitles (ASS): headline per segment on top, English captions at bottom ----
starts = [sum(D[:i]) for i in range(7)]
HEAD = ["4 OPTIONS SIGNALS @ 9:20 AM", "ENTRY • TARGET • STOP LOSS", "BUY ON FYERS • ZERODHA • DHAN",
        "ASK THE SCANNER AI", "OPTIONS ⇄ FUTURES • 1-TAP ORDER", "SIGNAL ALERTS ON YOUR PHONE", ""]
SUBS = [
    [("At 9:20 AM, right at the open,", 0.28), ("this AI Dashboard generated 4 stock options signals —", 0.30),
     ("TATA STEEL, BANK OF BARODA, TMPV & HINDPETRO", 0.24), ("All as per scanner rules. Fully automatic.", 0.18)],
    [("Every card gives you entry price,", 0.26), ("target, stop loss and a clear exit rule —", 0.30),
     ("\"exit if a 5-min candle closes below this level\"", 0.30), ("No guesswork.", 0.14)],
    [("And the best part — see the signal,", 0.22), ("tap \"Buy on Fyers\" directly.", 0.22),
     ("Fyers, Zerodha or Dhan — your broker, your control.", 0.30), ("The order is placed in YOUR broker account.", 0.26)],
    [("Got a question? Just type in \"Ask the Scanner AI\" —", 0.55), ("e.g. \"show stocks with RS above 80\"", 0.45)],
    [("One click: switch from Options to Futures —", 0.36), ("same setup, with futures levels.", 0.30), ("And the order? Right here, in one tap.", 0.34)],
    [("Every new signal comes to your phone as an alert —", 0.62), ("even when the app is closed.", 0.38)],
    [("All of this can be yours from today.", 0.14), ("Enrolling is very easy.", 0.10), ("Step 1 — open app.uppercircuitstocks.com", 0.16),
     ("Step 2 — Sign up", 0.10), ("Step 3 — go to Plans and choose your plan", 0.17), ("That's it — your AI Dashboard is ready.", 0.12),
     ("Link in bio. Start today —", 0.11), ("the market won't wait for anyone.", 0.10)],
]
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Head,Poppins,62,&H0037AFD4,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,3,0,8,40,40,250,1",
       "Style: Sub,Poppins,46,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,3,10,0,2,60,60,330,1",
       "Style: Foot,Poppins,30,&H0037AFD4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,40,40,120,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i in range(7):
    s0, d = starts[i], D[i]
    if HEAD[i]:
        ass.append(f"Dialogue: 0,{ts(s0)},{ts(s0+d)},Head,,0,0,0,,{{\\fad(200,200)}}{HEAD[i]}")
        ass.append(f"Dialogue: 0,{ts(s0)},{ts(s0+d)},Foot,,0,0,0,,app.uppercircuitstocks.com")
    t = s0
    for txt, frac in SUBS[i]:
        e = t + frac * d
        if i < 6:  # ending slides carry their own text; keep captions only on demo segments
            ass.append(f"Dialogue: 0,{ts(t)},{ts(e)},Sub,,0,0,0,,{txt}")
        t = e
open(f"{TMP}/subs.ass", "w", encoding="utf-8").write("\n".join(ass) + "\n")

ins = ["-i", f"{TMP}/video.mp4", "-i", f"{TMP}/voice.wav"]
if MUSIC:
    ins += ["-i", MUSIC]
    amix = f"[1:a]volume=1.0[vo];[2:a]volume=0.10,atrim=0:{total:.3f},afade=t=out:st={total-2:.2f}:d=2[m];[vo][m]amix=inputs=2:duration=first:normalize=0[a]"
else:
    amix = "[1:a]anull[a]"
run([*ins, "-filter_complex", f"[0:v]subtitles={TMP}/subs.ass:fontsdir=/usr/share/fonts/truetype/google-fonts[v];{amix}",
     "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT])
print("done", OUT, round(total, 2), "s")
