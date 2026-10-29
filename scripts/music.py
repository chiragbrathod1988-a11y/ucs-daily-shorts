"""Original lo-fi / corporate background bed, 92 BPM, royalty-free (synthesised here)."""
import numpy as np, soundfile as sf

SR = 48000
BPM = 98
BEAT = 60 / BPM
import sys
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)

def midi(n): return 440 * 2 ** ((n - 69) / 12)

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i] * gain

def env(n, a=0.01, d=1.0, s=0.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * (s + (1 - s) * np.exp(-t / d))
    return e

def keys(note, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(note)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.2 * t)
    s = (np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t) + 0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t/0.25))
    e = env(n, 0.012, 1.6, 0.25)
    rel = np.ones(n); r = int(0.25 * SR); rel[-r:] = np.linspace(1, 0, r)
    return s * e * trem * rel

def pad(note, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(note)
    s = sum(np.sin(2*np.pi*f*(1+dt)*t + p) for dt, p in [(0,0),(0.004,1.3),(-0.004,2.1)]) / 3
    a = np.minimum(1, t/0.6); rel = np.minimum(1, (dur - t)/0.6)
    return s * a * rel

def bass(note, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(note)
    s = np.sin(2*np.pi*f*t) + 0.2*np.sin(2*np.pi*2*f*t)
    return s * env(n, 0.005, 0.9, 0.35) * np.minimum(1, (dur - t)/0.05)

def kick():
    n = int(0.35 * SR); t = np.arange(n)/SR
    f = 50 + 90*np.exp(-t/0.04); ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-t/0.12)

def lp(x, a):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a*(v-acc); y[i] = acc
    return y

SN = int(0.25*SR)
snare_noise = rng.standard_normal(SN)
snare_noise = snare_noise - lp(snare_noise, 0.05)
def snare():
    t = np.arange(SN)/SR
    return (snare_noise*np.exp(-t/0.07)*0.6 + np.sin(2*np.pi*190*t)*np.exp(-t/0.05)*0.5)

HN = int(0.06*SR)
hat_noise = rng.standard_normal(HN); hat_noise = hat_noise - lp(hat_noise, 0.4)
def hat(open_=False):
    t = np.arange(HN)/SR
    return hat_noise*np.exp(-t/(0.03 if open_ else 0.012))

# Progression: Am7 | Fmaj7 | C | G  — each 1 bar (4 beats)
prog = [
    ([57, 60, 64, 67], 45),  # Am7
    ([53, 57, 60, 64], 41),  # Fmaj7
    ([55, 60, 64, 67], 48),  # C
    ([55, 59, 62, 67], 43),  # G
]
bar = 4 * BEAT
nbars = int(DUR / bar) + 1
melody = [76, 79, 81, 79, 76, 74, 76, 72]
for b in range(nbars):
    t0 = b * bar
    chord, bn = prog[b % 4]
    last = t0 + bar > DUR - 2.5
    # keys: chord stabs on beat 1 and the "and" of 2
    for off, g in [(0, 0.55), (1.5*BEAT, 0.35), (3*BEAT, 0.3)]:
        for k, nt in enumerate(chord):
            s = keys(nt, BEAT*1.4 if off else BEAT*1.9)
            add(L, t0+off+0.006*k, s, g*0.18*(1.05 if k % 2 else 0.95))
            add(R, t0+off+0.006*k, s, g*0.18*(0.95 if k % 2 else 1.05))
    # pad
    for nt in chord[1:3]:
        p = pad(nt+12, bar+0.5)
        add(L, t0, p, 0.045); add(R, t0, p, 0.045)
    # bass
    add(L, t0, bass(bn, 2*BEAT), 0.32); add(R, t0, bass(bn, 2*BEAT), 0.32)
    add(L, t0+2.5*BEAT, bass(bn+7, 1.4*BEAT), 0.22); add(R, t0+2.5*BEAT, bass(bn+7, 1.4*BEAT), 0.22)
    # soft pluck melody every other bar
    if b % 2 == 1 and not last:
        for i in range(4):
            nt = melody[(b//2*4 + i) % len(melody)]
            s = keys(nt+12, BEAT*0.9)
            add(L, t0+i*BEAT, s, 0.05); add(R, t0+i*BEAT+0.012, s, 0.06)
    if last or b == 0:
        continue  # first bar: no drums (soft intro); last: let it ring
    for beat in range(4):
        tb = t0 + beat*BEAT
        if beat in (0, 2):
            k = kick(); add(L, tb, k, 0.5); add(R, tb, k, 0.5)
        if beat == 2 and b % 2: add(L, tb+0.5*BEAT, kick(), 0.25); add(R, tb+0.5*BEAT, kick(), 0.25)
        if beat in (1, 3):
            s = snare(); add(L, tb, s, 0.14); add(R, tb, s, 0.14)
        for half in (0, 1):
            sw = 0.58 if half else 0.0  # swing
            h = hat(open_=(beat == 3 and half == 1))
            add(L, tb+sw*BEAT, h, 0.03*(0.8 if half else 1)); add(R, tb+sw*BEAT, h, 0.04*(0.8 if half else 1))

# simple reverb: convolve with exponentially-decaying noise
ir_n = int(1.6*SR); t = np.arange(ir_n)/SR
irL = rng.standard_normal(ir_n)*np.exp(-t/0.45); irR = rng.standard_normal(ir_n)*np.exp(-t/0.45)
irL[:int(0.02*SR)] = 0; irR[:int(0.02*SR)] = 0
def conv(x, ir):
    n = len(x)+len(ir)-1; nf = 1 << (n-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf)*np.fft.rfft(ir, nf), nf)[:len(x)]
wetL = conv(L, irL); wetR = conv(R, irR)
wetL /= np.max(np.abs(wetL)); wetR /= np.max(np.abs(wetR))
L2 = L + 0.035*wetL*np.max(np.abs(L)); R2 = R + 0.035*wetR*np.max(np.abs(R))

# fade in/out
fi = int(0.8*SR); fo = int(2.5*SR)
for x in (L2, R2):
    x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo)
st = np.stack([L2, R2], 1)
st = st/np.max(np.abs(st))*0.89
sf.write(OUT, st.astype(np.float32), SR)
print("ok", st.shape[0]/SR)
