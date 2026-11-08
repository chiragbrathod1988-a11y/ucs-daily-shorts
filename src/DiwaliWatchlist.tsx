import { AbsoluteFill, Composition, Easing, Img, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/fonts";
import { DIWALI } from "./diwaliData";

for (const w of ["500", "700", "800"]) {
  loadFont({ family: "Poppins", url: staticFile(`fonts/poppins-latin-${w}-normal.woff2`), weight: w });
  loadFont({ family: "PoppinsExt", url: staticFile(`fonts/poppins-latin-ext-${w}-normal.woff2`), weight: w });
}
for (const w of ["700", "900"]) loadFont({ family: "Cinzel", url: staticFile(`fonts/cinzel-latin-${w}-normal.woff2`), weight: w });

const SANS = "Poppins, PoppinsExt, sans-serif";
const SERIF = "Cinzel, serif";
const GOLD = "#F5C451";
const CREAM = "#FFF1C9";
const GREEN = "#2BD46A";
const ORANGE = "#FF8A1F";
const GOLD_GRAD = "linear-gradient(180deg,#FFF7D1 0%,#F5C451 42%,#B8801A 72%,#FFE08A 100%)";
const FPS = 30;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outExpo = Easing.bezier(0.16, 1, 0.3, 1);
const outBack = Easing.bezier(0.34, 1.56, 0.64, 1);

const TL = DIWALI.timeline;
const S = Object.fromEntries(TL.map((x) => [x.tag, x.start])) as Record<string, number>;
const E = Object.fromEntries(TL.map((x) => [x.tag, x.end])) as Record<string, number>;
const TOTAL = DIWALI.total;

// scene windows
const SC = {
  intro: [0, S.i1 - 0.15],
  icici: [S.i1 - 0.15, S.if1 - 0.15],
  iciciF: [S.if1 - 0.15, S.k1 - 0.15],
  kotak: [S.k1 - 0.15, S.kf1 - 0.15],
  kotakF: [S.kf1 - 0.15, S.risk - 0.15],
  risk: [S.risk - 0.15, S.cta - 0.15],
  end: [S.cta - 0.15, TOTAL],
} as const;
const vis = (t: number, [a, b]: readonly [number, number]) => interpolate(t, [a, a + 0.3, b - 0.25, b], [0, 1, 1, 0], clamp);
const pop = (t: number, at: number, d = 0.5) => interpolate(t, [at, at + d], [0, 1], { ...clamp, easing: outBack });
const rise = (t: number, at: number, d = 0.6) => interpolate(t, [at, at + d], [0, 1], { ...clamp, easing: outExpo });

const Gold: React.FC<{ size: number; font?: string; children: React.ReactNode; style?: React.CSSProperties }> = ({ size, font, children, style }) => (
  <span style={{ fontFamily: font ?? SERIF, fontWeight: 900, fontSize: size, backgroundImage: GOLD_GRAD, backgroundClip: "text", WebkitBackgroundClip: "text", color: "transparent", ...style }}>{children}</span>
);

// ---------- Diwali decorations ----------
const Bg: React.FC<{ t: number }> = ({ t }) => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 30%, #3A1A05 0%, #1A0A02 45%, #070302 100%)" }}>
    <svg width={1080} height={1920} style={{ position: "absolute" }}>
      {/* faint rangoli mandala */}
      <g transform={`translate(540 980) rotate(${t * 4})`} opacity={0.07}>
        {Array.from({ length: 16 }, (_, i) => (
          <g key={i} transform={`rotate(${i * 22.5})`}>
            <ellipse cx={0} cy={-300} rx={46} ry={130} fill="none" stroke={GOLD} strokeWidth={3} />
            <circle cx={0} cy={-470} r={18} fill={GOLD} />
          </g>
        ))}
        <circle r={180} fill="none" stroke={GOLD} strokeWidth={4} />
        <circle r={520} fill="none" stroke={GOLD} strokeWidth={2} />
      </g>
    </svg>
  </AbsoluteFill>
);

const Sparkles: React.FC<{ t: number }> = ({ t }) => (
  <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
    {Array.from({ length: 70 }, (_, i) => {
      const x = random(`sx${i}`) * 1080;
      const sp = 20 + random(`ss${i}`) * 50;
      const y = (((random(`sy${i}`) * 2000 - t * sp) % 2000) + 2000) % 2000 - 40;
      const tw = 0.35 + 0.65 * Math.abs(Math.sin(t * (1.5 + random(`st${i}`) * 3) + i));
      const r = 1.5 + random(`sr${i}`) * 3.5;
      return <circle key={i} cx={x + Math.sin(t + i) * 12} cy={y} r={r} fill={i % 3 ? GOLD : "#FFD9A0"} opacity={0.55 * tw} />;
    })}
  </svg>
);

const Toran: React.FC<{ t: number }> = ({ t }) => {
  const n = 23;
  return (
    <svg width={1080} height={200} style={{ position: "absolute", top: 0, left: 0 }}>
      <path d="M0 18 Q540 138 1080 18" stroke="#7A4A10" strokeWidth={4} fill="none" />
      {Array.from({ length: n }, (_, i) => {
        const u = i / (n - 1);
        const x = u * 1080;
        const y = 18 + 4 * 30 * u * (1 - u) * 2;
        const sw = Math.sin(t * 2 + i * 0.7) * 3;
        const c = i % 2 ? ORANGE : "#FFC21A";
        return (
          <g key={i} transform={`translate(${x} ${y}) rotate(${sw})`}>
            <line x1={0} y1={0} x2={0} y2={i % 3 === 0 ? 46 : 28} stroke="#7A4A10" strokeWidth={2} />
            <circle cy={i % 3 === 0 ? 46 : 28} r={i % 3 === 0 ? 16 : 12} fill={c} />
            <circle cy={i % 3 === 0 ? 46 : 28} r={i % 3 === 0 ? 8 : 6} fill="#E85D04" opacity={0.6} />
            {i % 2 === 0 && <path d={`M-14 8 L0 22 L14 8 Z`} fill="#3E8E2F" />}
          </g>
        );
      })}
    </svg>
  );
};

const Diya: React.FC<{ x: number; y: number; s?: number; t: number; seed: number }> = ({ x, y, s = 1, t, seed }) => {
  const fl = 1 + 0.12 * Math.sin(t * 13 + seed) + 0.06 * Math.sin(t * 29 + seed * 2);
  return (
    <svg width={160 * s} height={170 * s} viewBox="0 0 160 170" style={{ position: "absolute", left: x - 80 * s, top: y - 120 * s, overflow: "visible" }}>
      <defs>
        <radialGradient id={`glow${seed}`}><stop offset="0" stopColor="#FFD36B" stopOpacity={0.85} /><stop offset="1" stopColor="#FF8A1F" stopOpacity={0} /></radialGradient>
        <linearGradient id={`clay${seed}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#E0782C" /><stop offset="1" stopColor="#8A3A0E" /></linearGradient>
      </defs>
      <circle cx={80} cy={70} r={70 * fl} fill={`url(#glow${seed})`} />
      <path d={`M80 ${88 - 46 * fl} C ${96} ${70}, ${92} ${92}, 80 96 C 68 92, 64 70, 80 ${88 - 46 * fl} Z`} fill="#FFB52E" />
      <path d={`M80 ${90 - 28 * fl} C 88 80, 86 93, 80 95 C 74 93, 72 80, 80 ${90 - 28 * fl} Z`} fill="#FFF3B0" />
      <path d="M14 100 Q80 92 146 100 Q140 150 80 152 Q20 150 14 100 Z" fill={`url(#clay${seed})`} />
      <path d="M14 100 Q80 110 146 100" stroke="#FFC46B" strokeWidth={4} fill="none" />
      {[40, 62, 80, 98, 120].map((cx) => <circle key={cx} cx={cx} cy={126} r={4} fill="#FFD36B" />)}
    </svg>
  );
};

const Burst: React.FC<{ t: number; at: number; x: number; y: number; color: string; seed: number; size?: number }> = ({ t, at, x, y, color, seed, size = 1 }) => {
  const k = (t - at) / 1.5;
  if (k < 0 || k > 1) return null;
  const r = interpolate(k, [0, 1], [0, 230 * size], { easing: outExpo });
  const o = interpolate(k, [0, 0.6, 1], [1, 0.8, 0]);
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
      {Array.from({ length: 24 }, (_, i) => {
        const a = (i / 24) * Math.PI * 2 + seed;
        const rr = r * (0.8 + 0.3 * random(`b${seed}${i}`));
        const cx = x + Math.cos(a) * rr, cy = y + Math.sin(a) * rr + k * k * 60;
        return (
          <g key={i} opacity={o}>
            <line x1={x + Math.cos(a) * rr * 0.6} y1={y + Math.sin(a) * rr * 0.6 + k * k * 40} x2={cx} y2={cy} stroke={color} strokeWidth={3} strokeLinecap="round" />
            <circle cx={cx} cy={cy} r={5} fill={i % 2 ? "#FFF6D0" : color} />
          </g>
        );
      })}
    </svg>
  );
};

const Fireworks: React.FC<{ t: number }> = ({ t }) => {
  const shots: [number, number, number, string][] = [
    [0.2, 220, 420, "#FFC21A"], [0.7, 860, 360, "#FF5DA2"], [1.4, 540, 300, "#5DD8FF"], [2.6, 180, 520, "#FF8A1F"], [3.4, 900, 560, "#FFC21A"],
    [S.i2 + 0.2, 880, 470, "#2BD46A"], [S.i2 + 0.6, 700, 400, "#FFC21A"],
    [S.k2 + 0.2, 880, 470, "#2BD46A"], [S.k2 + 0.6, 700, 400, "#FFC21A"],
    [S.cta2, 220, 420, "#FFC21A"], [S.cta2 + 0.5, 860, 380, "#FF5DA2"], [S.cta2 + 1.1, 540, 330, "#5DD8FF"], [S.cta2 + 1.8, 260, 560, "#FF8A1F"], [S.cta2 + 2.5, 840, 560, "#FFC21A"],
  ];
  return <>{shots.map(([at, x, y, c], i) => <Burst key={i} t={t} at={at} x={x} y={y} color={c} seed={i} />)}</>;
};

// ---------- UI pieces ----------
const Header: React.FC = () => (
  <div style={{ position: "absolute", top: 175, left: 60, right: 60, display: "flex", alignItems: "center", gap: 22 }}>
    <Img src={staticFile("diwali/logo.png")} style={{ width: 96, height: 96, borderRadius: 18, border: `2px solid ${GOLD}` }} />
    <div style={{ display: "flex", flexDirection: "column" }}>
      <Gold size={40}>UPPERCIRCUITSTOCKS</Gold>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, color: "#FFB52E", letterSpacing: 2 }}>DIWALI BREAKOUT WATCHLIST</div>
    </div>
  </div>
);

const Disclaimer: React.FC = () => (
  <div style={{ position: "absolute", bottom: 62, left: 70, right: 70, textAlign: "center", fontFamily: SANS, fontWeight: 500, fontSize: 21, lineHeight: 1.35, color: "rgba(255,241,201,0.72)" }}>
    Educational chart study only — not a buy/sell recommendation or investment advice. Chirag Rathod is not a SEBI-registered research analyst. Do your own research.
  </div>
);

const Caption: React.FC<{ t: number }> = ({ t }) => {
  const cur = TL.find((x) => t >= x.start - 0.1 && t < x.end + 0.2);
  if (!cur) return null;
  const k = rise(t, cur.start - 0.1, 0.35);
  return (
    <div style={{ position: "absolute", top: 1560, left: 60, right: 60, display: "flex", justifyContent: "center" }}>
      <div style={{ opacity: k, transform: `translateY(${(1 - k) * 24}px)`, fontFamily: SANS, fontWeight: 800, fontSize: 46, lineHeight: 1.22, color: "#FFFFFF", textAlign: "center", textShadow: "0 4px 18px rgba(0,0,0,0.9)", padding: "14px 26px", borderRadius: 22, background: "rgba(20,8,0,0.55)", border: "1px solid rgba(245,196,81,0.35)" }}>
        {cur.cap}
      </div>
    </div>
  );
};

const Pill: React.FC<{ k: number; label: string; value: string; color?: string }> = ({ k, label, value, color = GOLD }) => (
  <div style={{ opacity: Math.min(1, k * 1.5), transform: `scale(${0.6 + 0.4 * k})`, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 28px", borderRadius: 20, background: "rgba(30,12,0,0.85)", border: `2px solid ${color}`, boxShadow: `0 0 24px ${color}44` }}>
    <span style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, color: CREAM, letterSpacing: 1 }}>{label}</span>
    <span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 40, color }}>{value}</span>
  </div>
);

const ChartScene: React.FC<{ t: number; img: string; num: string; name: string; at: [number, number, number]; pills: [string, string, string?][]; zoomOrigin: string }> = ({ t, img, num, name, at, pills, zoomOrigin }) => {
  const zoom = interpolate(t, [at[1], at[1] + 1.4, at[2] + 0.2, at[2] + 1.6], [1, 1.32, 1.32, 1.0], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const ink = rise(t, at[0] - 0.1);
  return (
    <>
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, textAlign: "center", opacity: ink, transform: `translateY(${(1 - ink) * 30}px)` }}>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: "#FFB52E", letterSpacing: 4 }}>{num} • MONTHLY CHART • NSE</div>
        <Gold size={96}>{name}</Gold>
      </div>
      <div style={{ position: "absolute", top: 520, left: 40, width: 1000, height: 513, borderRadius: 22, overflow: "hidden", border: `3px solid ${GOLD}`, boxShadow: "0 0 50px rgba(245,196,81,0.35)", background: "#fff", opacity: ink }}>
        <Img src={staticFile(`diwali/${img}`)} style={{ width: 1000, height: 513, transform: `scale(${zoom})`, transformOrigin: zoomOrigin }} />
      </div>
      <div style={{ position: "absolute", top: 1080, left: 70, right: 70, display: "flex", flexDirection: "column", gap: 18 }}>
        {pills.map(([l, v, c], i) => <Pill key={i} k={pop(t, at[i])} label={l} value={v} color={c} />)}
      </div>
    </>
  );
};

const Card: React.FC<{ k: number; label: string; value: string; sub: string; color?: string }> = ({ k, label, value, sub, color = GOLD }) => (
  <div style={{ opacity: Math.min(1, k * 1.5), transform: `translateY(${(1 - k) * 40}px) scale(${0.85 + 0.15 * k})`, width: 455, padding: "22px 26px", borderRadius: 24, background: "linear-gradient(160deg, rgba(60,25,2,0.95), rgba(18,7,0,0.95))", border: `2px solid ${color}88`, boxShadow: `0 0 28px ${color}33` }}>
    <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 25, color: "#FFB52E", letterSpacing: 1.5 }}>{label}</div>
    <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 52, color, lineHeight: 1.15 }}>{value}</div>
    <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 23, color: CREAM, opacity: 0.85 }}>{sub}</div>
  </div>
);

const FundScene: React.FC<{ t: number; name: string; start: number; cards: [number, string, string, string, string?][]; source: string }> = ({ t, name, start, cards, source }) => {
  const ink = rise(t, start - 0.1);
  return (
    <>
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, textAlign: "center", opacity: ink }}>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: "#FFB52E", letterSpacing: 4 }}>FUNDAMENTALS • Q2 FY27</div>
        <Gold size={name.length > 12 ? 66 : 84}>{name}</Gold>
      </div>
      <div style={{ position: "absolute", top: 520, left: 50, right: 50, display: "flex", flexWrap: "wrap", gap: 20, justifyContent: "center" }}>
        {cards.map(([at, l, v, s, c], i) => <Card key={i} k={pop(t, at, 0.55)} label={l} value={v} sub={s} color={c} />)}
      </div>
      <div style={{ position: "absolute", top: 1490, left: 60, right: 60, textAlign: "center", fontFamily: SANS, fontWeight: 500, fontSize: 20, color: "rgba(255,241,201,0.6)", opacity: ink }}>{source}</div>
    </>
  );
};

export const DiwaliWatchlist: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const tIntro = rise(t, 0.1, 0.9);
  const tEnd = rise(t, SC.end[0] + 0.1, 0.8);
  return (
    <AbsoluteFill style={{ backgroundColor: "#070302" }}>
      <Bg t={t} />
      <Sparkles t={t} />
      <Fireworks t={t} />

      {/* INTRO */}
      <AbsoluteFill style={{ opacity: vis(t, SC.intro) }}>
        <div style={{ position: "absolute", top: 230, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <Img src={staticFile("diwali/logo.png")} style={{ width: 300, height: 300, borderRadius: 40, border: `3px solid ${GOLD}`, boxShadow: "0 0 80px rgba(255,180,60,0.6)", transform: `scale(${0.6 + 0.4 * tIntro})`, opacity: tIntro }} />
          <div style={{ marginTop: 40, opacity: tIntro }}><Gold size={110}>HAPPY</Gold></div>
          <div style={{ marginTop: -10, opacity: tIntro }}><Gold size={150}>DIWALI</Gold></div>
          <div style={{ marginTop: 30, fontFamily: SANS, fontWeight: 800, fontSize: 52, color: "#FFFFFF", opacity: rise(t, S.hook2 - 0.4), letterSpacing: 2 }}>BREAKOUT WATCHLIST</div>
          <div style={{ marginTop: 34, display: "flex", gap: 26 }}>
            {["ICICI BANK", "KOTAK BANK"].map((n, i) => {
              const k = pop(t, S.hook2 - 0.2 + i * 0.25);
              return <div key={n} style={{ opacity: Math.min(1, k * 1.5), transform: `scale(${0.6 + 0.4 * k})`, padding: "18px 34px", borderRadius: 999, border: `3px solid ${GOLD}`, background: "rgba(40,16,0,0.85)", fontFamily: SANS, fontWeight: 800, fontSize: 40, color: GOLD }}>{n}</div>;
            })}
          </div>
          <div style={{ marginTop: 26, fontFamily: SANS, fontWeight: 700, fontSize: 32, color: "#FFB52E", opacity: rise(t, S.hook2 + 0.4) }}>Monthly consolidation → breakout</div>
        </div>
        {[150, 345, 540, 735, 930].map((x, i) => <Diya key={i} x={x} y={1440} s={i === 2 ? 1.25 : 1} t={t} seed={i + 1} />)}
      </AbsoluteFill>

      {/* ICICI chart */}
      <AbsoluteFill style={{ opacity: vis(t, SC.icici) }}>
        <Header />
        <ChartScene t={t} img="icici.png" num="#1" name="ICICI BANK" at={[S.i1 + 0.8, S.i2 + 0.6, S.i3 + 0.3]} zoomOrigin="78% 45%"
          pills={[["RANGE", "1,195 – 1,505"], ["BREAKOUT ↑ NOW", "1,576  +12.7%", GREEN], ["PROJECTION ZONE", "2,358"]]} />
      </AbsoluteFill>

      {/* ICICI fundamentals */}
      <AbsoluteFill style={{ opacity: vis(t, SC.iciciF) }}>
        <Header />
        <FundScene t={t} name="ICICI BANK" start={S.if1}
          cards={[
            [S.if1 + 1.0, "NET PROFIT", "₹14,843 Cr", "+20% YoY (standalone)", GREEN],
            [S.if1 + 1.6, "LOAN GROWTH", "+30% YoY", "Advances, Q2 FY27"],
            [S.if2 + 0.3, "NET INTEREST MARGIN", "4.18%", "Q2 FY27"],
            [S.if2 + 1.6, "NET NPA", "0.30%", "Gross NPA 1.20%", GREEN],
            [S.if3 + 0.4, "MUTUAL FUNDS", "29.4%", "Sep-26 shareholding"],
            [S.if3 + 1.8, "FII STAKE", "Increased ↑", "Sep-26 vs Jun-26", GREEN],
          ]}
          source="Source: ICICI Bank Q2 FY27 results (17 Oct 2026); Sep-2026 shareholding via Trendlyne/Upstox" />
      </AbsoluteFill>

      {/* KOTAK chart */}
      <AbsoluteFill style={{ opacity: vis(t, SC.kotak) }}>
        <Header />
        <ChartScene t={t} img="kotak.png" num="#2" name="KOTAK BANK" at={[S.k1 + 0.8, S.k2 + 0.2, S.k2 + 2.6]} zoomOrigin="72% 50%"
          pills={[["RANGE", "317 – 450"], ["BREAKOUT ↑ NOW", "480", GREEN], ["PROJECTION ZONE", "699"]]} />
      </AbsoluteFill>

      {/* KOTAK fundamentals */}
      <AbsoluteFill style={{ opacity: vis(t, SC.kotakF) }}>
        <Header />
        <FundScene t={t} name="KOTAK MAHINDRA BANK" start={S.kf1}
          cards={[
            [S.kf1 + 1.0, "NET PROFIT", "₹4,212 Cr", "+29% YoY (standalone)", GREEN],
            [S.kf1 + 1.6, "ADVANCES", "+25% YoY", "₹5.77 lakh Cr"],
            [S.kf2 + 0.2, "NET INTEREST MARGIN", "4.31%", "Q2 FY27"],
            [S.kf2 + 1.4, "NET NPA", "0.24%", "Gross NPA 1.04%", GREEN],
            [S.kf3 + 0.3, "DII HOLDING", "38.5% ↑", "from 37.7% (Jun-26)", GREEN],
            [S.kf3 + 1.6, "PROMOTER", "25.9%", "0% pledged"],
          ]}
          source="Source: Kotak Q2 FY27 results (24 Oct 2026); Sep-2026 shareholding via Trendlyne. CAR 21.9% (standalone)" />
      </AbsoluteFill>

      {/* RISK note */}
      <AbsoluteFill style={{ opacity: vis(t, SC.risk) }}>
        <Header />
        <div style={{ position: "absolute", top: 520, left: 70, right: 70, padding: 44, borderRadius: 30, background: "rgba(30,12,0,0.9)", border: `3px solid ${GOLD}`, transform: `scale(${0.85 + 0.15 * pop(t, S.risk)})` }}>
          <Gold size={60}>YAAD RAKHO</Gold>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 40, color: CREAM, marginTop: 20, lineHeight: 1.3 }}>Breakout tabhi strong jab price breakout level ke upar tike</div>
          <div style={{ marginTop: 34, display: "flex", flexDirection: "column", gap: 18 }}>
            <Pill k={pop(t, S.risk + 1.2)} label="ICICI BANK breakout" value="1,505" />
            <Pill k={pop(t, S.risk + 1.8)} label="KOTAK BANK breakout" value="450" />
          </div>
        </div>
      </AbsoluteFill>

      {/* END */}
      <AbsoluteFill style={{ opacity: vis(t, SC.end) }}>
        <div style={{ position: "absolute", top: 220, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", opacity: tEnd }}>
          <Img src={staticFile("diwali/chirag.png")} style={{ width: 300, height: 300, borderRadius: "50%", objectFit: "cover", border: `5px solid ${GOLD}`, boxShadow: "0 0 70px rgba(255,180,60,0.55)" }} />
          <div style={{ marginTop: 24 }}><Gold size={64}>CHIRAG RATHOD</Gold></div>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, color: "#FFB52E", letterSpacing: 3 }}>UPPERCIRCUITSTOCKS</div>
          <div style={{ marginTop: 40, padding: "22px 34px", borderRadius: 24, border: `2px solid ${GOLD}`, background: "rgba(30,12,0,0.85)", textAlign: "center" }}>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 40, color: GOLD }}>AI DASHBOARD • STOCK SCREENERS</div>
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, color: CREAM }}>app.UpperCircuitStocks.com</div>
          </div>
          <div style={{ marginTop: 40, opacity: rise(t, S.cta2 - 0.2) }}><Gold size={110}>HAPPY DIWALI</Gold></div>
          <div style={{ marginTop: 26, display: "flex", gap: 22, opacity: rise(t, S.cta2 + 1.0) }}>
            {["SAVE", "SHARE", "FOLLOW"].map((n) => <div key={n} style={{ padding: "16px 34px", borderRadius: 999, background: GOLD_GRAD, fontFamily: SANS, fontWeight: 800, fontSize: 36, color: "#2A1400" }}>{n}</div>)}
          </div>
        </div>
        {[150, 345, 540, 735, 930].map((x, i) => <Diya key={i} x={x} y={1500} s={i === 2 ? 1.2 : 0.95} t={t} seed={i + 11} />)}
      </AbsoluteFill>

      <Toran t={t} />
      <Caption t={t} />
      <Disclaimer />
    </AbsoluteFill>
  );
};

export const DiwaliWatchlistComposition = () => (
  <Composition id="DiwaliWatchlist" component={DiwaliWatchlist} durationInFrames={Math.ceil(TOTAL * FPS)} fps={FPS} width={1080} height={1920} />
);
