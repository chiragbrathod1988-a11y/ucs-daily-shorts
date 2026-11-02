#!/usr/bin/env python3
"""Nifty gap-up pattern Short/Reel from the 2026-11-02 21:56 Zoom recording.
1080x1920, Hindi AI voice (Matilda), English captions, black/gold, webcam/face/dialog/blank screens removed.
Usage: build.py SRC.mp4 OUT.mp4 MUSIC.wav DASH_FRAME.png"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

SRC, OUT, MUSIC, DASH = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 25
GOLD, BLACK, WHITE = "#D4AF37", "#0A0A0A", "#FFFFFF"
FONT_B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
VO = [f"{HERE}/voice/v{i}.mp3" for i in range(1, 7)]
TMP = f"{HERE}/tmp"; os.makedirs(TMP, exist_ok=True)
CHART = (70, 120, 1830, 1584)  # x, y, w, h of the chart area (excludes watchlist + webcam)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
D = [dur(v) for v in VO]

def run(a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

def canvas(inner, d):
    return (f"{inner};color=c={BLACK}:s={W}x{H}:r={FPS}:d={d:.3f}[bg];"
            f"[c]pad=iw+10:ih+10:5:5:color={GOLD}[cf];[bg][cf]overlay=(W-w)/2:(H-h)/2-40:shortest=1,format=yuv420p[v]")

def enc(out, d): return ["-map", "[v]", "-t", f"{d:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out]

def frame_at(ss):
    p = f"{TMP}/f_{ss}.png"
    if not os.path.exists(p): run(["-ss", f"{ss}", "-i", SRC, "-frames:v", "1", p])
    return Image.open(p)

def highlight(im, box, label=None):
    """gold ellipse (+ label) on a full-frame PIL image; box in full-frame coords"""
    d = ImageDraw.Draw(im); d.ellipse(box, outline=GOLD, width=10)
    if label:
        f = ImageFont.truetype(FONT_B, 54); x0, y0, x1, y1 = box
        tw = d.textlength(label, font=f)
        d.rounded_rectangle((x0 - 20, y0 - 110, x0 + tw + 40, y0 - 30), 16, fill=GOLD)
        d.text((x0 + 10, y0 - 100), label, font=f, fill=BLACK)
    return im

def still_clip(im, crop, d, out, zoom=1.12, pan=None):
    """im: full-frame PIL; crop=(x,y,w,h); zoom-in, or pan=(x0,x1) horizontal window"""
    x, y, w, h = crop
    c = im.crop((x, y, x + w, y + h)); p = f"{out}.png"; c.save(p)
    sw = 1000
    if pan:
        win = pan[2]; sh = int(h * sw / win) // 2 * 2; span = w - win
        inner = f"[0:v]crop={win}:{h}:'{pan[0]}+({pan[1]}-{pan[0]})*min(1,t/{d-1:.2f})':0,scale={sw}:{sh}[c]"
    else:
        sh = int(h * sw / w) // 2 * 2; n = int(d * FPS)
        inner = f"[0:v]scale={sw*2}:{sh*2},zoompan=z='1+({zoom}-1)*on/{n}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s={sw}x{sh}:fps={FPS}[c]"
    run(["-loop", "1", "-t", f"{d+0.2:.3f}", "-i", p, "-filter_complex", canvas(inner, d), *enc(out, d)])

def video_clip(ss, d, crop, out):
    x, y, w, h = crop; sw = 1000; sh = int(h * sw / w) // 2 * 2
    inner = f"[0:v]trim=duration={d:.3f},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale={sw}:{sh}[c]"
    run(["-ss", f"{ss}", "-t", f"{d+0.2:.3f}", "-i", SRC, "-filter_complex", canvas(inner, d), *enc(out, d)])

clips = []
# 1. Hook: today's chart, gap-up candle circled, zoom toward it
f5 = frame_at(5.0)
im1 = highlight(f5.copy(), (1560, 420, 1700, 620), "GAP-UP")
c1 = f"{TMP}/c1.mp4"; still_clip(im1, (700, 120, 1200, 1584), D[0], c1, zoom=1.18); clips.append(c1)
# 2. Close above Bollinger band + momentum cross: tall crop of candle + oscillator
im2 = highlight(f5.copy(), (1560, 420, 1700, 620))
im2 = highlight(im2, (1540, 1270, 1720, 1420), "MOMENTUM")
c2 = f"{TMP}/c2.mp4"; still_clip(im2, (900, 120, 1000, 1584), D[1], c2, zoom=1.10); clips.append(c2)
# 3. Bullish view: live chart motion (zoomed-out view with cursor)
c3 = f"{TMP}/c3.mp4"; video_clip(38.0, D[2], CHART, c3); clips.append(c3)
# 4. Aug 2021: same pattern — breakout candles circled, pan left->right along the rally
f85 = frame_at(85.0)
im4 = highlight(f85.copy(), (470, 820, 640, 1060), "AUG 2021")
im4 = highlight(im4, (1580, 150, 1760, 420), "18,600")
c4 = f"{TMP}/c4.mp4"; still_clip(im4, (70, 120, 1830, 1400), D[3], c4, pan=(0, 630, 1200)); clips.append(c4)
# 5. Pattern repeats: Oct 2021 top with the line (live motion)
c5 = f"{TMP}/c5.mp4"; video_clip(96.0, D[4], CHART, c5); clips.append(c5)

# 6. CTA: real dashboard frame (5 s) then enrol slides
def slide(name, lines, badge=None, steps=None, tagline=None, sub=None):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
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
            d.ellipse((120, y, 220, y + 100), fill=col); d.text((170, y + 50), str(i), font=fb(52), fill=BLACK, anchor="mm")
            d.text((260, y + 2), title, font=fb(50), fill=tcol); d.text((260, y + 66), desc, font=fm(32), fill=("#CFCFCF" if on else "#4a4a4a"))
            y += 190
    if tagline: d.multiline_text((W / 2, H - 600), tagline, font=fb(50), fill=GOLD, anchor="ma", align="center", spacing=14)
    if sub: d.multiline_text((W / 2, H - 300), sub, font=fm(28), fill="#9a9a9a", anchor="ma", align="center")
    d.text((W / 2, H - 120), "UpperCircuitStocks  •  AI Dashboard", font=fm(32), fill=GOLD, anchor="ma")
    p = f"{TMP}/{name}.png"; im.save(p); return p

STEPS = [("Open the app", "app.uppercircuitstocks.com"), ("Sign up", "Create your free login"), ("Choose your Plan", "Tap Plans - pick a plan - done")]
on = lambda k: [(t, s, i < k) for i, (t, s) in enumerate(STEPS)]
dash = Image.open(DASH)
cA = f"{TMP}/cA.mp4"; still_clip(dash, (0, 790, 1440, 914), 5.5, cA, zoom=1.12)
sB1 = slide("sB1", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=on(1)); sB2 = slide("sB2", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=on(2)); sB3 = slide("sB3", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=on(3))
sC = slide("sC", [("LINK IN BIO", 96, GOLD), ("app.uppercircuitstocks.com", 46, WHITE)], tagline="Like  •  Share\nComment: kal Nifty\nUPAR ya NEECHE?",
           sub="Information & education only. Not investment advice.\nViews are the educator's opinion; market risks apply.")
parts = [cA]
for i, (img, d) in enumerate([(sB1, 3.6), (sB2, 2.4), (sB3, 3.4), (sC, D[5] - 5.5 - 9.4)]):
    p = f"{TMP}/e{i}.mp4"; run(["-loop", "1", "-t", f"{d:.3f}", "-i", img, "-vf", "fade=t=in:st=0:d=0.3,format=yuv420p", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", p]); parts.append(p)
c6 = f"{TMP}/c6.mp4"
open(f"{TMP}/c6.txt", "w").write("".join(f"file '{p}'\n" for p in parts)); run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/c6.txt", "-c", "copy", c6]); clips.append(c6)

open(f"{TMP}/all.txt", "w").write("".join(f"file '{p}'\n" for p in clips)); run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/all.txt", "-c", "copy", f"{TMP}/video.mp4"])
open(f"{TMP}/vo.txt", "w").write("".join(f"file '{p}'\n" for p in VO)); run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/vo.txt", "-ar", "48000", "-ac", "2", f"{TMP}/voice.wav"])
total = sum(D); starts = [sum(D[:i]) for i in range(6)]

HEAD = ["NIFTY GAP-UP PATTERN", "ABOVE BOLLINGER + MOMENTUM UP", "VIEW: BULLISH FOR TOMORROW", "SAME PATTERN • AUG 2021", "PATTERNS REPEAT", ""]
SUBS = [
    [("Nifty made a GAP-UP candle today —", 0.33), ("and this candle never comes alone.", 0.22), ("Chirag sir's observation: this pattern", 0.22), ("comes in a set of 3 or 5 gap-ups.", 0.23)],
    [("Look closely — price closed ABOVE the Bollinger band,", 0.36), ("and the momentum indicator crossed above zero.", 0.30), ("So this is only the FIRST gap-up —", 0.17), ("two more can follow.", 0.17)],
    [("So the view for tomorrow is BULLISH —", 0.55), ("watch the upside setups, not the downside.", 0.45)],
    [("And this isn't the first time. August 2021 —", 0.35), ("exactly the same pattern.", 0.17), ("Gap-up, gap-up, gap-up —", 0.24), ("and Nifty went straight to 18,600.", 0.24)],
    [("Patterns repeat — you just need to recognise them.", 0.5), ("Save this chart and watch tomorrow's market closely.", 0.5)],
    [("Setups like this show up every morning at 9:20", 0.20), ("on the AI Dashboard — as per scanner rules, automatic.", 0.22), ("Step 1 — open app.uppercircuitstocks.com", 0.14),
     ("Step 2 — Sign up", 0.08), ("Step 3 — choose your Plan", 0.11), ("Link in bio & description.", 0.09), ("Like, share — and comment: Nifty UP or DOWN tomorrow?", 0.16)],
]
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Head,Poppins,60,&H0037AFD4,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,3,0,8,40,40,230,1",
       "Style: Sub,Poppins,46,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,3,10,0,2,60,60,330,1",
       "Style: Foot,Poppins,30,&H0037AFD4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,40,40,120,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i in range(6):
    s0, d = starts[i], D[i]
    if HEAD[i]:
        ass.append(f"Dialogue: 0,{ts(s0)},{ts(s0+d)},Head,,0,0,0,,{{\\fad(200,200)}}{HEAD[i]}")
        ass.append(f"Dialogue: 0,{ts(s0)},{ts(s0+d)},Foot,,0,0,0,,app.uppercircuitstocks.com")
    t = s0
    for txt, frac in SUBS[i]:
        e = t + frac * d
        if i < 5 or t < s0 + 5.5: ass.append(f"Dialogue: 0,{ts(t)},{ts(e)},Sub,,0,0,0,,{txt}")
        t = e
open(f"{TMP}/subs.ass", "w", encoding="utf-8").write("\n".join(ass) + "\n")
run(["-i", f"{TMP}/video.mp4", "-i", f"{TMP}/voice.wav", "-i", MUSIC, "-filter_complex",
     f"[0:v]subtitles={TMP}/subs.ass:fontsdir=/usr/share/fonts/truetype/google-fonts[v];[1:a]anull[vo];[2:a]volume=0.10,atrim=0:{total:.3f},afade=t=out:st={total-2:.2f}:d=2[m];[vo][m]amix=inputs=2:duration=first:normalize=0[a]",
     "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT])

# thumbnail / cover
cov = Image.new("RGB", (W, H), BLACK); ch = im1.crop((700, 120, 1900, 1704)).resize((1000, 1320)); cov.paste(ch, (40, 420))
d = ImageDraw.Draw(cov); d.rectangle((35, 415, 1045, 1745), outline=GOLD, width=8)
d.text((W/2, 110), "NIFTY GAP-UP", font=ImageFont.truetype(FONT_B, 120), fill=GOLD, anchor="ma")
d.text((W/2, 250), "3 ya 5 gap-ups?", font=ImageFont.truetype(FONT_B, 80), fill=WHITE, anchor="ma")
d.rounded_rectangle((240, 1770, 840, 1860), 20, fill=GOLD); d.text((W/2, 1815), "2021 JAISA RALLY?", font=ImageFont.truetype(FONT_B, 48), fill=BLACK, anchor="mm")
cov.save(OUT.replace(".mp4", "-thumb.jpg"), quality=90)
print("done", OUT, round(total, 2))
