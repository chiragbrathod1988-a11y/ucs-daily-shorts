import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/fonts";
import { DAILY } from "./dailyData";

for (const w of ["500", "700", "800"]) {
  loadFont({ family: "Poppins", url: staticFile(`fonts/poppins-latin-${w}-normal.woff2`), weight: w });
  loadFont({ family: "PoppinsExt", url: staticFile(`fonts/poppins-latin-ext-${w}-normal.woff2`), weight: w });
}
for (const w of ["700", "900"]) {
  loadFont({ family: "Cinzel", url: staticFile(`fonts/cinzel-latin-${w}-normal.woff2`), weight: w });
}
const SANS = "Poppins, PoppinsExt, sans-serif";
const SERIF = "Cinzel, serif";

// Brand palette taken from the UpperCircuitStocks emblem
const GOLD = "#F5C451";
const CREAM = "#FFF1C9";
const GREEN = "#2BD46A";
const RED = "#F04D4D";
const GOLD_GRAD = "linear-gradient(180deg,#FFF7D1 0%,#F5C451 42%,#B8801A 72%,#FFE08A 100%)";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outExpo = Easing.bezier(0.16, 1, 0.3, 1);
const ease = Easing.bezier(0.65, 0, 0.35, 1);

const T = Object.fromEntries(DAILY.timeline.map((s) => [s.tag, s.start])) as Record<string, number>;
const L = DAILY.levels;
const fmt = (n: number, d = 0) => n.toLocaleString("en-IN", { minimumFractionDigits: d, maximumFractionDigits: d });
const fade = (t: number, a: number, b: number, fi = 0.35, fo = 0.35) =>
  interpolate(t, [a, a + fi, b - fo, b], [0, 1, 1, 0], clamp);

const Gold: React.FC<{ size: number; font?: string; children: React.ReactNode; style?: React.CSSProperties }> = ({ size, font, children, style }) => (
  <span style={{ fontFamily: font ?? SERIF, fontWeight: 900, fontSize: size, backgroundImage: GOLD_GRAD, backgroundClip: "text", WebkitBackgroundClip: "text", color: "transparent", ...style }}>
    {children}
  </span>
);

// ---------- background: black, gold glow, drifting golden candlesticks, ornate frame ----------
const Candles: React.FC<{ t: number }> = ({ t }) => {
  const items = Array.from({ length: 26 }, (_, i) => {
    const x = random(`cx${i}`) * 1080;
    const h = 60 + random(`ch${i}`) * 220;
    const y0 = random(`cy${i}`) * 1920;
    const speed = 8 + random(`cs${i}`) * 18;
    const y = ((y0 - t * speed) % 2100 + 2100) % 2100 - 100;
    const up = random(`cu${i}`) > 0.42;
    return { x, h, y, up, w: 14 + random(`cw${i}`) * 16, o: 0.06 + random(`co${i}`) * 0.1 };
  });
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
      {items.map((c, i) => (
        <g key={i} opacity={c.o}>
          <line x1={c.x} x2={c.x} y1={c.y - c.h * 0.35} y2={c.y + c.h * 1.35} stroke={GOLD} strokeWidth={2} />
          <rect x={c.x - c.w / 2} y={c.y} width={c.w} height={c.h} fill={c.up ? GOLD : "none"} stroke={GOLD} strokeWidth={2} rx={2} />
        </g>
      ))}
    </svg>
  );
};

const Frame: React.FC = () => (
  <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
    <defs>
      <linearGradient id="fg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#FFE9A8" />
        <stop offset="0.5" stopColor="#B07A12" />
        <stop offset="1" stopColor="#FFD77A" />
      </linearGradient>
    </defs>
    <rect x={22} y={22} width={1036} height={1876} rx={26} fill="none" stroke="url(#fg)" strokeWidth={3} />
    <rect x={34} y={34} width={1012} height={1852} rx={20} fill="none" stroke="url(#fg)" strokeWidth={1} opacity={0.6} />
    {[
      [40, 40],
      [1040, 40],
      [40, 1880],
      [1040, 1880],
    ].map(([x, y], i) => (
      <path key={i} d={`M${x} ${y - 14} L${x + 14} ${y} L${x} ${y + 14} L${x - 14} ${y} Z`} fill="url(#fg)" />
    ))}
  </svg>
);

// ---------- persistent chrome ----------
const Header: React.FC<{ t: number }> = ({ t }) => {
  const p = interpolate(t, [3.0, 3.6], [0, 1], { ...clamp, easing: outExpo });
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 150, display: "flex", alignItems: "center", gap: 22, opacity: p, translate: `0px ${(1 - p) * -30}px` }}>
      <Img src={staticFile("daily/logo.png")} style={{ width: 128, height: 136, objectFit: "cover", borderRadius: 18, boxShadow: "0 0 30px rgba(245,196,81,0.45)" }} />
      <div style={{ flex: 1 }}>
        <Gold size={44}>UPPERCIRCUITSTOCKS</Gold>
        <div style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 24, letterSpacing: 6, marginTop: 2 }}>BY CHIRAG RATHOD</div>
        <div style={{ marginTop: 12, display: "inline-flex", gap: 12, alignItems: "center", padding: "6px 18px", borderRadius: 999, border: `2px solid ${GOLD}`, color: GOLD, fontFamily: SANS, fontWeight: 700, fontSize: 26 }}>
          {DAILY.dateLabel} · {DAILY.dayEn.toUpperCase()} · PRE-MARKET
        </div>
      </div>
    </div>
  );
};

const Progress: React.FC<{ t: number }> = ({ t }) => (
  <div style={{ position: "absolute", left: 60, right: 60, top: 100, height: 8, borderRadius: 4, backgroundColor: "rgba(245,196,81,0.18)" }}>
    <div style={{ height: "100%", width: `${Math.min(1, t / DAILY.duration) * 100}%`, borderRadius: 4, backgroundImage: GOLD_GRAD }} />
  </div>
);

// ---------- intro ----------
const Intro: React.FC<{ t: number }> = ({ t }) => {
  const p = fade(t, 0, 3.35, 0.01, 0.4);
  if (p <= 0) return null;
  const logo = interpolate(t, [0, 0.7], [0.55, 1], { ...clamp, easing: Easing.spring({ damping: 11 }) });
  const shine = interpolate(t, [0.6, 1.6], [-0.6, 1.6], clamp);
  const title = interpolate(t, [0.5, 1.0], [0, 1], { ...clamp, easing: outExpo });
  const sub = interpolate(t, [1.0, 1.5], [0, 1], { ...clamp, easing: outExpo });
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: p }}>
      <div style={{ position: "relative", width: 420, height: 445, scale: `${logo}`, borderRadius: 40, overflow: "hidden", boxShadow: "0 0 120px rgba(245,196,81,0.55)" }}>
        <Img src={staticFile("daily/logo.png")} style={{ width: 420, height: 445, objectFit: "cover" }} />
        <div style={{ position: "absolute", top: -100, bottom: -100, width: 140, left: `${shine * 100}%`, rotate: "20deg", background: "linear-gradient(90deg,rgba(255,240,190,0),rgba(255,240,190,0.65),rgba(255,240,190,0))" }} />
      </div>
      <div style={{ marginTop: 50, opacity: title, translate: `0px ${(1 - title) * 40}px` }}>
        <Gold size={150}>NIFTY 50</Gold>
      </div>
      <div style={{ marginTop: 10, opacity: sub, display: "flex", alignItems: "center", gap: 22 }}>
        <div style={{ width: 90, height: 3, backgroundImage: GOLD_GRAD }} />
        <span style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 46, letterSpacing: 4 }}>AAJ KE LEVELS</span>
        <div style={{ width: 90, height: 3, backgroundImage: GOLD_GRAD }} />
      </div>
    </AbsoluteFill>
  );
};

// ---------- previous close card ----------
const PrevClose: React.FC<{ t: number }> = ({ t }) => {
  const a = T.prev;
  const b = T.pivot;
  const p = fade(t, a - 0.1, b + 0.2, 0.4, 0.4);
  if (p <= 0) return null;
  const prevPrev = L.close - L.change;
  const n = interpolate(t, [a + 0.2, a + 1.8], [prevPrev, L.close], { ...clamp, easing: Easing.out(Easing.cubic) });
  const pill = interpolate(t, [a + 1.8, a + 2.2], [0, 1], { ...clamp, easing: Easing.spring({ damping: 11 }) });
  const col = DAILY.up ? GREEN : RED;
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: p }}>
      <div style={{ width: 900, padding: "50px 0 56px", borderRadius: 36, textAlign: "center", background: "linear-gradient(180deg,#171106 0%,#060504 100%)", border: `4px solid ${GOLD}`, boxShadow: "0 0 90px rgba(245,196,81,0.3)" }}>
        <div style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 40, letterSpacing: 6 }}>PREVIOUS CLOSE</div>
        <div style={{ marginTop: 8 }}>
          <Gold size={150} font={SANS}>{fmt(n, 2)}</Gold>
        </div>
        <div style={{ marginTop: 14, display: "inline-flex", alignItems: "center", gap: 12, scale: `${pill}`, padding: "12px 30px", borderRadius: 999, backgroundColor: DAILY.up ? "rgba(43,212,106,0.14)" : "rgba(240,77,77,0.14)", border: `3px solid ${col}`, color: col, fontFamily: SANS, fontWeight: 800, fontSize: 50 }}>
          {DAILY.up ? "▲" : "▼"} {DAILY.up ? "+" : "−"}{fmt(Math.abs(L.change), 2)} ({DAILY.up ? "+" : "−"}{Math.abs(L.changePct)}%)
        </div>
        <div style={{ marginTop: 26, display: "flex", justifyContent: "center", gap: 34, fontFamily: SANS, fontWeight: 600, fontSize: 30, color: CREAM, opacity: 0.85 }}>
          <span>H {fmt(L.high, 2)}</span>
          <span>L {fmt(L.low, 2)}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- chart with levels ----------
const CH = { x: 60, y: 360, w: 960, h: 960 };
const ChartStage: React.FC<{ t: number }> = ({ t }) => {
  const start = T.pivot - 0.15;
  const end = T.cta + 0.25;
  const p = fade(t, start, end, 0.45, 0.45);
  if (p <= 0) return null;
  const lo = Math.min(L.S2, L.low) - (L.R2 - L.S2) * 0.12;
  const hi = Math.max(L.R2, L.high) + (L.R2 - L.S2) * 0.12;
  const y = (v: number) => CH.y + 90 + (1 - (v - lo) / (hi - lo)) * (CH.h - 140);
  const candleX = 250;
  const grow = interpolate(t, [start, start + 0.9], [0, 1], { ...clamp, easing: outExpo });
  const bodyTop = y(Math.max(L.open, L.close));
  const bodyBot = y(Math.min(L.open, L.close));
  const mid = (bodyTop + bodyBot) / 2;
  const candleCol = L.close >= L.open ? GREEN : RED;

  const levels: { key: string; label: string; v: number; col: string; at: number; thick: number }[] = [
    { key: "P", label: "PIVOT", v: L.P, col: GOLD, at: T.pivot, thick: 5 },
    { key: "R1", label: "R1", v: L.R1, col: RED, at: T.r1, thick: 4 },
    { key: "R2", label: "R2", v: L.R2, col: RED, at: T.r2, thick: 4 },
    { key: "S1", label: "S1", v: L.S1, col: GREEN, at: T.s1, thick: 4 },
    { key: "S2", label: "S2", v: L.S2, col: GREEN, at: T.s2, thick: 4 },
  ];
  const cpr = interpolate(t, [T.bull - 0.2, T.bull + 0.5], [0, 1], clamp);
  const bullA = interpolate(t, [T.bull + 0.6, T.bull + 2.2], [0, 1], { ...clamp, easing: ease });
  const bearA = interpolate(t, [T.bear + 0.3, T.bear + 1.9], [0, 1], { ...clamp, easing: ease });
  const zoom = interpolate(t, [start, end], [1.0, 1.04], clamp);
  const arrow = (from: number, to: number, a: number, col: string, x: number) => {
    const y0 = y(from);
    const y1 = y0 + (y(to) - y0) * a;
    const dir = to > from ? 1 : -1; // arms point back toward the start (svg y grows down)
    return a > 0 ? (
      <g>
        <line x1={x} x2={x} y1={y0} y2={y1} stroke={col} strokeWidth={10} strokeLinecap="round" style={{ filter: `drop-shadow(0 0 12px ${col})` }} />
        <path d={`M${x - 26} ${y1 + dir * 30} L${x} ${y1} L${x + 26} ${y1 + dir * 30}`} stroke={col} strokeWidth={10} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    ) : null;
  };
  return (
    <div style={{ position: "absolute", left: CH.x, top: CH.y, width: CH.w, height: CH.h, opacity: p, scale: `${zoom}` }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: 30, background: "linear-gradient(180deg,rgba(23,17,6,0.92) 0%,rgba(6,5,4,0.95) 100%)", border: `3px solid ${GOLD}`, boxShadow: "0 0 80px rgba(245,196,81,0.25)" }} />
      <div style={{ position: "absolute", left: 34, top: 26, display: "flex", alignItems: "center", gap: 14 }}>
        <Gold size={40}>NIFTY 50</Gold>
        <span style={{ fontFamily: SANS, fontWeight: 700, color: CREAM, fontSize: 28, opacity: 0.85 }}>Support & Resistance</span>
      </div>
      <svg width={CH.w} height={CH.h} style={{ position: "absolute", left: 0, top: 0 }}>
        {/* faint grid */}
        {Array.from({ length: 7 }, (_, i) => (
          <line key={i} x1={30} x2={CH.w - 30} y1={110 + i * 130} y2={110 + i * 130} stroke="rgba(245,196,81,0.08)" strokeWidth={1} />
        ))}
        {/* CPR band */}
        <rect x={130} width={CH.w - 160} y={y(L.CPRhi) - CH.y} height={Math.max(6, y(L.CPRlo) - y(L.CPRhi))} fill="rgba(245,196,81,0.16)" opacity={cpr} />
        {/* level lines */}
        {levels.map((lv) => {
          const a = interpolate(t, [lv.at, lv.at + 0.55], [0, 1], { ...clamp, easing: outExpo });
          if (a <= 0) return null;
          const yy = y(lv.v) - CH.y;
          return (
            <g key={lv.key} opacity={a}>
              <line x1={130} x2={130 + (CH.w - 470) * a} y1={yy} y2={yy} stroke={lv.col} strokeWidth={lv.thick} strokeDasharray={lv.key === "P" ? "0" : "18 10"} style={{ filter: `drop-shadow(0 0 6px ${lv.col})` }} />
            </g>
          );
        })}
        {/* yesterday candle */}
        <g opacity={grow}>
          <line x1={candleX} x2={candleX} y1={mid + (y(L.high) - mid) * grow - CH.y} y2={mid + (y(L.low) - mid) * grow - CH.y} stroke={candleCol} strokeWidth={6} />
          <rect x={candleX - 34} width={68} y={mid + (bodyTop - mid) * grow - CH.y} height={Math.max(4, (bodyBot - bodyTop) * grow)} fill={candleCol} rx={6} />
        </g>
        {/* scenario arrows */}
        <g transform={`translate(0,${-CH.y})`}>
          {arrow(L.CPRhi, L.R1, bullA, GREEN, 520)}
          {arrow(L.P, L.S1, bearA, RED, 640)}
        </g>
      </svg>
      <div style={{ position: "absolute", left: candleX - 90, width: 180, top: y(L.low) - CH.y + 18, textAlign: "center", fontFamily: SANS, fontWeight: 700, fontSize: 24, color: CREAM, opacity: grow * 0.8 }}>
        {DAILY.prevDate.slice(8, 10)}/{DAILY.prevDate.slice(5, 7)} candle
      </div>
      {/* level labels */}
      {levels.map((lv) => {
        const a = interpolate(t, [lv.at + 0.15, lv.at + 0.6], [0, 1], { ...clamp, easing: Easing.spring({ damping: 12 }) });
        if (a <= 0) return null;
        const big = lv.key === "P";
        return (
          <div key={lv.key} style={{ position: "absolute", right: 26, top: y(lv.v) - CH.y - (big ? 38 : 33), scale: `${a}`, display: "flex", alignItems: "center", gap: 10, padding: big ? "10px 20px" : "8px 18px", borderRadius: 16, backgroundColor: big ? GOLD : "#0B0905", border: `3px solid ${lv.col}`, boxShadow: `0 0 24px ${lv.col}55` }}>
            <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: big ? 26 : 24, color: big ? "#0A0A0A" : lv.col }}>{lv.label}</span>
            <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: big ? 44 : 40, color: big ? "#0A0A0A" : "white" }}>{fmt(lv.v)}</span>
          </div>
        );
      })}
      {/* CPR label */}
      <div style={{ position: "absolute", left: 310, top: y(L.CPRlo) - CH.y + 6, fontFamily: SANS, fontWeight: 700, fontSize: 24, color: GOLD, opacity: cpr }}>
        CPR {fmt(L.CPRlo)}–{fmt(L.CPRhi)}
      </div>
      {/* scenario callouts */}
      {bullA > 0 ? (
        <div style={{ position: "absolute", left: 120, top: 104, opacity: interpolate(bullA, [0, 0.3], [0, 1], clamp), padding: "12px 22px", borderRadius: 16, backgroundColor: "rgba(43,212,106,0.14)", border: `3px solid ${GREEN}`, fontFamily: SANS, fontWeight: 800, fontSize: 30, color: "white" }}>
          <span style={{ color: GREEN }}>▲ BULLISH</span> above {fmt(L.CPRhi)} → {fmt(L.R1)}
        </div>
      ) : null}
      {bearA > 0 ? (
        <div style={{ position: "absolute", left: 120, bottom: 34, opacity: interpolate(bearA, [0, 0.3], [0, 1], clamp), padding: "12px 22px", borderRadius: 16, backgroundColor: "rgba(240,77,77,0.14)", border: `3px solid ${RED}`, fontFamily: SANS, fontWeight: 800, fontSize: 30, color: "white" }}>
          <span style={{ color: RED }}>▼ BEARISH</span> below {fmt(L.P)} → {fmt(L.S1)}
        </div>
      ) : null}
    </div>
  );
};

// ---------- outro with the human touch ----------
const Outro: React.FC<{ t: number }> = ({ t }) => {
  const a = T.cta;
  const p = interpolate(t, [a, a + 0.5], [0, 1], { ...clamp, easing: outExpo });
  if (p <= 0) return null;
  const ring = interpolate(t, [a + 0.2, a + 0.9], [0, 1], { ...clamp, easing: Easing.spring({ damping: 12 }) });
  const pulse = 1 + 0.035 * Math.sin((t - a) * Math.PI * 1.8);
  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: p, paddingBottom: 120 }}>
      <div style={{ width: 400, height: 400, borderRadius: "50%", padding: 10, background: GOLD_GRAD, scale: `${ring}`, boxShadow: "0 0 90px rgba(245,196,81,0.5)" }}>
        <Img src={staticFile("daily/chirag.png")} style={{ width: 380, height: 380, borderRadius: "50%", objectFit: "cover", objectPosition: "50% 22%" }} />
      </div>
      <div style={{ marginTop: 34 }}>
        <Gold size={66}>CHIRAG RATHOD</Gold>
      </div>
      <div style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 32, letterSpacing: 5, marginTop: 4 }}>UPPERCIRCUITSTOCKS</div>
      <div style={{ marginTop: 40, scale: `${pulse}`, display: "flex", gap: 18 }}>
        {["SAVE KARO", "FOLLOW KARO"].map((x) => (
          <div key={x} style={{ padding: "18px 34px", borderRadius: 999, backgroundImage: GOLD_GRAD, color: "#0A0A0A", fontFamily: SANS, fontWeight: 800, fontSize: 40, boxShadow: "0 0 40px rgba(245,196,81,0.45)" }}>
            {x}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 26, fontFamily: SANS, fontWeight: 700, color: CREAM, fontSize: 34, opacity: 0.9 }}>Roz subah Nifty levels</div>
    </AbsoluteFill>
  );
};

const Captions: React.FC<{ t: number }> = ({ t }) => {
  if (t >= T.cta) return null;
  const c = DAILY.captions.find((x) => t >= x.start && t < x.end);
  if (!c) return null;
  const age = t - c.start;
  const pop = interpolate(age, [0, 0.16], [0.84, 1], { ...clamp, easing: Easing.bezier(0.34, 1.56, 0.64, 1) });
  const parts = c.text.split("*");
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 1350, height: 220, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <div style={{ scale: `${pop}`, fontFamily: SANS, fontSize: 66, fontWeight: 800, lineHeight: 1.15, color: "white", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textShadow: "0 6px 18px rgba(0,0,0,0.85)" }}>
        {parts.map((s, i) => (i % 2 ? <span key={i} style={{ color: GOLD }}>{s}</span> : <span key={i}>{s}</span>))}
      </div>
    </div>
  );
};

export const NiftyShort: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{ backgroundColor: "#040302", backgroundImage: "radial-gradient(circle at 50% 38%, rgba(245,196,81,0.22) 0%, rgba(176,122,18,0.08) 40%, rgba(0,0,0,0) 70%)" }}>
      <Candles t={t} />
      <AbsoluteFill style={{ boxShadow: "inset 0 0 220px rgba(0,0,0,0.9)" }} />
      <Frame />
      <Progress t={t} />
      <Header t={t} />
      <Intro t={t} />
      <PrevClose t={t} />
      <ChartStage t={t} />
      <Outro t={t} />
      <Captions t={t} />
      <div style={{ position: "absolute", left: 80, right: 80, top: 1640, textAlign: "center", fontFamily: SANS, fontWeight: 500, fontSize: 23, lineHeight: 1.35, color: CREAM, opacity: 0.6 }}>
        Educational purpose only. Not investment advice. Levels are calculated pivot points, not buy/sell recommendations. Market risks apply.
      </div>
    </AbsoluteFill>
  );
};

export const NiftyShortComposition = () => (
  <Composition id="NiftyShort" component={NiftyShort} durationInFrames={Math.ceil(DAILY.duration * 30)} fps={30} width={1080} height={1920} />
);
