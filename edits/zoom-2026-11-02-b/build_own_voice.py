#!/usr/bin/env python3
"""Nifty gap-up pattern Short/Reel — Chirag's OWN voice kept continuous; visuals replaced where the screen
showed the Go-to dialog, a blank chart or the webcam. AI (Matilda) enrol ending appended after he finishes.
Usage: build_own_voice.py SRC.mp4 OUT.mp4 MUSIC.wav DASH_FRAME.png"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

SRC, OUT, MUSIC, DASH = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 25
GOLD, BLACK, WHITE = "#D4AF37", "#0A0A0A", "#FFFFFF"
FONT_B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
TMP = f"{HERE}/tmp2"; os.makedirs(TMP, exist_ok=True)
CHART = (70, 215, 1830, 1489)
A0, A1 = 2.5, 112.2            # his audio window (source time)
END_VO = f"{HERE}/voice/v6.mp3"  # AI enrol ending

def dur(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
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
    d = ImageDraw.Draw(im); d.ellipse(box, outline=GOLD, width=10)
    if label:
        f = ImageFont.truetype(FONT_B, 54); x0, y0, *_ = box; tw = d.textlength(label, font=f)
        d.rounded_rectangle((x0 - 20, y0 - 110, x0 + tw + 40, y0 - 30), 16, fill=GOLD); d.text((x0 + 10, y0 - 100), label, font=f, fill=BLACK)
    return im
def still_clip(im, crop, d, out, zoom=1.10):
    x, y, w, h = crop; c = im.crop((x, y, x + w, y + h)); p = f"{out}.png"; c.save(p)
    sw = 1000; sh = int(h * sw / w) // 2 * 2; n = int(d * FPS)
    inner = f"[0:v]scale={sw*2}:{sh*2},zoompan=z='1+({zoom}-1)*on/{n}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s={sw}x{sh}:fps={FPS}[c]"
    run(["-loop", "1", "-t", f"{d+0.2:.3f}", "-i", p, "-filter_complex", canvas(inner, d), *enc(out, d)])
def video_clip(ss, d, crop, out):
    x, y, w, h = crop; sw = 1000; sh = int(h * sw / w) // 2 * 2
    inner = f"[0:v]trim=duration={d:.3f},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale={sw}:{sh}[c]"
    run(["-ss", f"{ss}", "-t", f"{d+0.2:.3f}", "-i", SRC, "-filter_complex", canvas(inner, d), *enc(out, d)])

# ---- visual timeline over his audio (source times) ----
clips = []
f5 = frame_at(5.0)
hook = highlight(f5.copy(), (1560, 420, 1700, 620), "GAP-UP")
c0 = f"{TMP}/c0.mp4"; still_clip(hook, (700, 300, 1200, 1300), 6.0, c0, zoom=1.15); clips.append(c0)          # 2.5–8.5 hook zoom
c1 = f"{TMP}/c1.mp4"; video_clip(8.5, 62.0, CHART, c1); clips.append(c1)                                        # 8.5–70.5 live
f85 = frame_at(85.0); im4 = highlight(f85.copy(), (470, 820, 640, 1060), "AUG 2021"); im4 = highlight(im4, (1580, 150, 1760, 420))
c2 = f"{TMP}/c2.mp4"; still_clip(im4, (70, 100, 1830, 1400), 10.5, c2, zoom=1.12); clips.append(c2)             # 70.5–81 dialog → 2021 still
c3 = f"{TMP}/c3.mp4"; video_clip(81.0, 20.5, CHART, c3); clips.append(c3)                                       # 81–101.5 live
dash = Image.open(DASH)
c4 = f"{TMP}/c4.mp4"; still_clip(dash, (0, 790, 1440, 914), A1 - 101.5, c4, zoom=1.12); clips.append(c4)        # 101.5–end blank/face → dashboard
own_len = A1 - A0

# ---- AI enrol ending ----
def slide(name, lines, steps=None, tagline=None, sub=None):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im); d.rectangle((40, 40, W - 40, H - 40), outline=GOLD, width=3)
    fb = lambda s: ImageFont.truetype(FONT_B, s); fm = lambda s: ImageFont.truetype(FONT_M, s); y = 300
    for ln, size, col in lines: d.text((W / 2, y), ln, font=fb(size), fill=col, anchor="ma"); y += size + 24
    if steps:
        y += 40
        for i, (title, desc, on) in enumerate(steps, 1):
            col = GOLD if on else "#4a4a4a"; tcol = WHITE if on else "#4a4a4a"
            d.ellipse((120, y, 220, y + 100), fill=col); d.text((170, y + 50), str(i), font=fb(52), fill=BLACK, anchor="mm")
            d.text((260, y + 2), title, font=fb(50), fill=tcol); d.text((260, y + 66), desc, font=fm(32), fill=("#CFCFCF" if on else "#4a4a4a")); y += 190
    if tagline: d.multiline_text((W / 2, H - 600), tagline, font=fb(50), fill=GOLD, anchor="ma", align="center", spacing=14)
    if sub: d.multiline_text((W / 2, H - 300), sub, font=fm(28), fill="#9a9a9a", anchor="ma", align="center")
    d.text((W / 2, H - 120), "UpperCircuitStocks  •  AI Dashboard", font=fm(32), fill=GOLD, anchor="ma")
    p = f"{TMP}/{name}.png"; im.save(p); return p
STEPS = [("Open the app", "app.uppercircuitstocks.com"), ("Sign up", "Create your free login"), ("Choose your Plan", "Tap Plans - pick a plan - done")]
on = lambda k: [(t, s, i < k) for i, (t, s) in enumerate(STEPS)]
DE = dur(END_VO)
cA = f"{TMP}/cA.mp4"; still_clip(dash, (0, 560, 1440, 1144), 5.5, cA, zoom=1.12)
imgs = [(slide("sB1", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=on(1)), 3.6), (slide("sB2", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=on(2)), 2.4),
        (slide("sB3", [("ENROLL IN 3 STEPS", 70, GOLD)], steps=on(3)), 3.4),
        (slide("sC", [("LINK IN BIO", 96, GOLD), ("app.uppercircuitstocks.com", 46, WHITE)], tagline="Like  •  Share\nComment: kal Nifty\nUPAR ya NEECHE?",
               sub="Information & education only. Not investment advice.\nViews are the educator's opinion; market risks apply."), DE - 5.5 - 9.4)]
parts = [cA]
for i, (img, d) in enumerate(imgs):
    p = f"{TMP}/e{i}.mp4"; run(["-loop", "1", "-t", f"{d:.3f}", "-i", img, "-vf", "fade=t=in:st=0:d=0.3,format=yuv420p", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", p]); parts.append(p)
clips += parts
open(f"{TMP}/all.txt", "w").write("".join(f"file '{p}'\n" for p in clips)); run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/all.txt", "-c", "copy", f"{TMP}/video.mp4"])

# ---- audio: his voice (cleaned + normalised) then AI ending ----
run(["-ss", f"{A0}", "-to", f"{A1}", "-i", SRC, "-vn", "-af", "highpass=f=90,lowpass=f=9000,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.3", "-ar", "48000", "-ac", "2", f"{TMP}/own.wav"])
run(["-i", END_VO, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", f"{TMP}/end.wav"])
open(f"{TMP}/a.txt", "w").write(f"file '{TMP}/own.wav'\nfile '{TMP}/end.wav'\n"); run(["-f", "concat", "-safe", "0", "-i", f"{TMP}/a.txt", f"{TMP}/voice.wav"])
total = own_len + DE

# ---- on-screen text: phase headlines over his voice, captions on the AI ending ----
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Head,Poppins,60,&H0037AFD4,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,3,0,8,40,40,230,1",
       "Style: Sub,Poppins,46,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,3,10,0,2,60,60,330,1",
       "Style: Foot,Poppins,30,&H0037AFD4,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,2,0,2,40,40,120,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
# (start, end) in OUTPUT time = source - A0
heads = [(0, 34, "NIFTY GAP-UP PATTERN"), (34, 68, "3 YA 5 GAP-UPS? VIEW: BULLISH"), (68, 99, "SAME PATTERN • AUG–OCT 2021"), (99, own_len, "LIKE • SHARE • SAVE")]
subs = [(0, 6, "Nifty made a GAP-UP candle today"), (6, 14, "Chirag Rathod explains the pattern (own voice, Hindi)"),
        (34, 42, "His observation: 3 or 5 gap-ups come in a set"), (68, 78.5, "Aug 2021: gap-up, gap-up, gap-up → 18,600"),
        (99, own_len, "Pattern repeats — save this chart")]
for s, e, t in heads:
    ass.append(f"Dialogue: 0,{ts(s)},{ts(e)},Head,,0,0,0,,{{\\fad(200,200)}}{t}")
ass.append(f"Dialogue: 0,{ts(0)},{ts(own_len)},Foot,,0,0,0,,app.uppercircuitstocks.com")
for s, e, t in subs: ass.append(f"Dialogue: 0,{ts(s)},{ts(e)},Sub,,0,0,0,,{t}")
end_subs = [("Setups like this show up every morning at 9:20", 0.20), ("on the AI Dashboard — as per scanner rules, automatic.", 0.22), ("Step 1 — open app.uppercircuitstocks.com", 0.14),
            ("Step 2 — Sign up", 0.08), ("Step 3 — choose your Plan", 0.11), ("Link in bio & description.", 0.09), ("Like, share — and comment: Nifty UP or DOWN tomorrow?", 0.16)]
t = own_len
for txt, fr in end_subs[:2]:
    ass.append(f"Dialogue: 0,{ts(t)},{ts(t+fr*DE)},Sub,,0,0,0,,{txt}"); t += fr * DE
open(f"{TMP}/subs.ass", "w", encoding="utf-8").write("\n".join(ass) + "\n")
run(["-i", f"{TMP}/video.mp4", "-i", f"{TMP}/voice.wav", "-i", MUSIC, "-filter_complex",
     f"[0:v]subtitles={TMP}/subs.ass:fontsdir=/usr/share/fonts/truetype/google-fonts[v];[1:a]anull[vo];[2:a]volume=0.07,aloop=loop=-1:size=2e9,atrim=0:{total:.3f},afade=t=out:st={total-2:.2f}:d=2[m];[vo][m]amix=inputs=2:duration=first:normalize=0[a]",
     "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT])
cov = Image.new("RGB", (W, H), BLACK); ch = hook.crop((700, 120, 1900, 1704)).resize((1000, 1320)); cov.paste(ch, (40, 420))
d = ImageDraw.Draw(cov); d.rectangle((35, 415, 1045, 1745), outline=GOLD, width=8)
d.text((W/2, 110), "NIFTY GAP-UP", font=ImageFont.truetype(FONT_B, 120), fill=GOLD, anchor="ma")
d.text((W/2, 250), "3 ya 5 gap-ups?", font=ImageFont.truetype(FONT_B, 80), fill=WHITE, anchor="ma")
d.rounded_rectangle((240, 1770, 840, 1860), 20, fill=GOLD); d.text((W/2, 1815), "2021 JAISA RALLY?", font=ImageFont.truetype(FONT_B, 48), fill=BLACK, anchor="mm")
cov.save(OUT.replace(".mp4", "-thumb.jpg"), quality=90)
print("done", OUT, round(total, 2))
