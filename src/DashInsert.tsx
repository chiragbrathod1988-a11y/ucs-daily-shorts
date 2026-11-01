// AI Dashboard inserts for long-form (16:9) videos. Designed on a 1920x1080 stage, scaled to the composition size.
// Props come from edits/<name>/inserts.json (built by scripts/build_inserts.py). No P&L, prices or trade calls —
// only features, "signals generated as per scanner rules", and broker connectivity.
import { AbsoluteFill, Composition, Easing, Img, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/fonts";

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
const RED = "#F04D4D";
const GOLD_GRAD = "linear-gradient(180deg,#FFF7D1 0%,#F5C451 42%,#B8801A 72%,#FFE08A 100%)";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const spring = (t: number, a: number, d = 0.45) => interpolate(t, [a, a + d], [0, 1], { ...clamp, easing: Easing.spring({ damping: 12 }) });

export type InsertProps = { kind: "intro" | "screener" | "signals" | "end"; duration: number; marks: Record<string, number>; dashUrl: string; telegram: string };

const Gold: React.FC<{ size: number; font?: string; children: React.ReactNode }> = ({ size, font, children }) => (
  <span style={{ fontFamily: font ?? SERIF, fontWeight: 900, fontSize: size, backgroundImage: GOLD_GRAD, backgroundClip: "text", WebkitBackgroundClip: "text", color: "transparent" }}>{children}</span>
);

const Candles: React.FC<{ t: number }> = ({ t }) => (
  <svg width={1920} height={1080} style={{ position: "absolute", inset: 0 }}>
    {Array.from({ length: 30 }, (_, i) => {
      const x = random(`x${i}`) * 1920, h = 50 + random(`h${i}`) * 180, w = 14 + random(`w${i}`) * 14;
      const y = ((random(`y${i}`) * 1200 - t * (8 + random(`s${i}`) * 16)) % 1250 + 1250) % 1250 - 100;
      const up = random(`u${i}`) > 0.42;
      return (
        <g key={i} opacity={0.05 + random(`o${i}`) * 0.09}>
          <line x1={x} x2={x} y1={y - h * 0.35} y2={y + h * 1.35} stroke={GOLD} strokeWidth={2} />
          <rect x={x - w / 2} y={y} width={w} height={h} fill={up ? GOLD : "none"} stroke={GOLD} strokeWidth={2} rx={2} />
        </g>
      );
    })}
  </svg>
);

const Card: React.FC<{ t: number; at: number; active?: boolean; w: number; h: number; title: string; sub: string; children: React.ReactNode }> = ({ t, at, active, w, h, title, sub, children }) => {
  const s = spring(t, at);
  return (
    <div style={{ width: w, height: h, borderRadius: 28, padding: "24px 28px", boxSizing: "border-box", background: "linear-gradient(180deg,#191207 0%,#070604 100%)", border: `${active ? 4 : 2}px solid ${active ? GOLD : "rgba(245,196,81,0.45)"}`, boxShadow: active ? "0 0 60px rgba(245,196,81,0.4)" : "0 10px 30px rgba(0,0,0,0.6)", opacity: s, scale: `${(0.86 + 0.14 * s) * (active ? 1.02 : 1)}` }}>
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 36, color: active ? GOLD : CREAM, lineHeight: 1.1 }}>{title}</div>
      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 22, color: CREAM, opacity: 0.75, marginTop: 4, marginBottom: 16 }}>{sub}</div>
      {children}
    </div>
  );
};

const Chips: React.FC<{ items: string[]; filled?: number }> = ({ items, filled = -1 }) => (
  <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
    {items.map((c, i) => (
      <span key={c} style={{ padding: "6px 14px", borderRadius: 999, border: `2px solid ${GOLD}`, backgroundColor: i === filled ? GOLD : "transparent", color: i === filled ? "#0A0A0A" : GOLD, fontFamily: SANS, fontWeight: 700, fontSize: 19 }}>{c}</span>
    ))}
  </div>
);
const Rows: React.FC<{ n?: number }> = ({ n = 4 }) => (
  <div>
    {[0.9, 0.7, 0.8, 0.6, 0.75, 0.65].slice(0, n).map((w, i) => (
      <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 13 }}>
        <div style={{ width: 28, height: 28, borderRadius: 7, backgroundColor: "rgba(245,196,81,0.25)" }} />
        <div style={{ height: 15, width: `${w * 60}%`, borderRadius: 8, backgroundColor: "rgba(255,241,201,0.28)" }} />
        <div style={{ marginLeft: "auto", height: 15, width: 60, borderRadius: 8, backgroundColor: i % 3 === 1 ? "rgba(240,77,77,0.6)" : "rgba(43,212,106,0.6)" }} />
      </div>
    ))}
  </div>
);
const HEAT = [["IT", 0.6], ["BANK", 0.9], ["AUTO", -0.4], ["FMCG", 0.3], ["PHARMA", -0.7], ["METAL", 0.8], ["ENERGY", -0.2], ["REALTY", 1], ["MEDIA", -0.5]] as const;
const Heatmap: React.FC<{ cell?: number }> = ({ cell = 62 }) => (
  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 9 }}>
    {HEAT.map(([n, v]) => (
      <div key={n} style={{ height: cell, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 800, fontSize: 20, color: "white", backgroundColor: v >= 0 ? `rgba(43,212,106,${0.25 + 0.55 * v})` : `rgba(240,77,77,${0.25 + 0.55 * -v})` }}>{n}</div>
    ))}
  </div>
);
const Spark = () => (
  <svg width={400} height={110}>
    <polyline fill="none" stroke={GREEN} strokeWidth={4} points="0,90 50,84 95,94 140,66 190,72 240,48 290,56 340,30 400,18" />
  </svg>
);
const Bars = () => (
  <svg width={400} height={130}>
    {[[20, 80, 110, 1], [60, 64, 100, 1], [100, 56, 92, 0], [140, 44, 86, 1], [180, 30, 72, 1], [220, 36, 80, 0], [260, 22, 64, 1], [300, 14, 54, 1], [340, 8, 46, 1]].map(([x, top, bot, up], i) => (
      <g key={i}>
        <line x1={x} x2={x} y1={top - 8} y2={bot + 8} stroke={up ? GREEN : RED} strokeWidth={3} />
        <rect x={x - 11} y={top + 4} width={22} height={Math.max(12, bot - top - 8)} fill={up ? GREEN : RED} rx={3} />
      </g>
    ))}
  </svg>
);

const Title: React.FC<{ t: number; sub?: string }> = ({ t, sub }) => (
  <div style={{ position: "absolute", top: 46, left: 0, right: 0, textAlign: "center", scale: `${spring(t, 0.05, 0.6)}` }}>
    <div style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 30, letterSpacing: 8 }}>UPPERCIRCUITSTOCKS</div>
    <div style={{ marginTop: -8 }}><Gold size={92}>AI DASHBOARD</Gold></div>
    {sub ? <div style={{ fontFamily: SANS, fontWeight: 700, color: CREAM, fontSize: 30, marginTop: -4, opacity: 0.9 }}>{sub}</div> : null}
  </div>
);
const Pill: React.FC<{ t: number; at: number; text: string; top: number; size?: number }> = ({ t, at, text, top, size = 42 }) => {
  const s = spring(t, at, 0.4);
  const pulse = 1 + 0.025 * Math.sin((t - at) * Math.PI * 2);
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: s }}>
      <div style={{ scale: `${s * pulse}`, padding: "16px 44px", borderRadius: 999, backgroundImage: GOLD_GRAD, color: "#0A0A0A", fontFamily: SANS, fontWeight: 800, fontSize: size, boxShadow: "0 0 50px rgba(245,196,81,0.5)" }}>{text}</div>
    </div>
  );
};

// ---- scenes ----
const IntroScene: React.FC<{ t: number; p: InsertProps }> = ({ t, p }) => {
  const m = p.marks;
  const feats = ["Stock Screeners", "Heat Map", "Nifty Overview", "Stock Research"];
  const at = (i: number) => m.a2 + 0.25 + i * Math.max(0.9, (m.a3 - m.a2 - 0.6) / 4);
  const act = (i: number) => t >= at(i) && (i === 3 ? t < m.a3 + 0.2 : t < at(i + 1));
  const show = (i: number) => Math.min(at(i), m.a1 + 1.4 + i * 0.35);
  return (
    <>
      <Title t={t} sub="Ek chhota sa break" />
      <div style={{ position: "absolute", top: 270, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 26 }}>
        <Card t={t} at={show(0)} active={act(0)} w={420} h={520} title={feats[0]} sub="Filter stocks in seconds"><Chips items={["Breakout", "Volume", "52W High"]} /><Rows n={6} /></Card>
        <Card t={t} at={show(1)} active={act(1)} w={420} h={520} title={feats[1]} sub="Sector-wise market view"><Heatmap cell={96} /></Card>
        <Card t={t} at={show(2)} active={act(2)} w={420} h={520} title={feats[2]} sub="Index at a glance"><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 46, color: GOLD }}>NIFTY 50</div><Spark /><Rows n={3} /></Card>
        <Card t={t} at={show(3)} active={act(3)} w={420} h={520} title={feats[3]} sub="Detailed analysis per stock"><Chips items={["Technicals", "Fundamentals", "News"]} filled={0} /><Bars /><Rows n={2} /></Card>
      </div>
      <Pill t={t} at={m.a3} text={`${p.dashUrl}  ·  Link in description`} top={860} size={40} />
    </>
  );
};

const ScreenerScene: React.FC<{ t: number; p: InsertProps }> = ({ t, p }) => {
  const m = p.marks;
  const chipAt = (i: number) => m.b2 + 0.2 + i * 0.9;
  const filled = t >= chipAt(2) ? 2 : t >= chipAt(1) ? 1 : t >= chipAt(0) ? 0 : -1;
  const heat = m.b2 + (p.duration - m.b2) * 0.45;
  return (
    <>
      <Title t={t} sub="Aise setups dhoondhne ke liye" />
      <div style={{ position: "absolute", top: 280, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 40 }}>
        <Card t={t} at={m.b1 + 0.6} active={t < heat} w={820} h={600} title="Stock Screeners" sub="Stocks filter in seconds">
          <Chips items={["Breakout", "Volume", "52W High", "RSI"]} filled={filled} />
          <Rows n={6} />
        </Card>
        <Card t={t} at={heat} active={t >= heat} w={620} h={600} title="Heat Map" sub="Poora sector view ek nazar mein"><Heatmap cell={120} /></Card>
      </div>
    </>
  );
};

const SIG = [
  ["NIFTY", "Futures", "RSI Reversal · 1D + 1H"],
  ["BANKNIFTY", "Options", "Breakout + Volume"],
  ["RELIANCE", "Futures", "RSI Reversal · 1D + 1H"],
  ["HDFCBANK", "Options", "52W High Breakout"],
] as const;
const SignalsScene: React.FC<{ t: number; p: InsertProps }> = ({ t, p }) => {
  const m = p.marks;
  const conn = spring(t, m.c2 + 0.9, 0.5);
  return (
    <>
      <Title t={t} sub="Options & Futures" />
      <div style={{ position: "absolute", top: 280, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 40 }}>
        <Card t={t} at={m.c1 + 0.3} active={t < m.c2} w={980} h={560} title="F&O Signals" sub="Generated as per scanner rules">
          <div style={{ display: "grid", gridTemplateColumns: "230px 170px 1fr 220px", rowGap: 14, fontFamily: SANS, fontSize: 24, color: CREAM, alignItems: "center" }}>
            {["Symbol", "Segment", "Scanner rule", "Status"].map((h) => <div key={h} style={{ fontWeight: 700, opacity: 0.6, fontSize: 20 }}>{h}</div>)}
            {SIG.map(([s, seg, rule], i) => {
              const r = spring(t, m.c1 + 1.0 + i * 0.55, 0.35);
              const cells = [
                <div key="s" style={{ fontWeight: 800, color: GOLD }}>{s}</div>,
                <div key="g" style={{ fontWeight: 700 }}>{seg}</div>,
                <div key="r" style={{ fontWeight: 500, opacity: 0.9 }}>{rule}</div>,
                <div key="st"><span style={{ padding: "5px 14px", borderRadius: 999, border: `2px solid ${GOLD}`, color: GOLD, fontWeight: 700, fontSize: 19 }}>Signal generated</span></div>,
              ];
              return cells.map((c, j) => <div key={`${i}${j}`} style={{ opacity: r, translate: `${(1 - r) * 30}px 0` }}>{c}</div>);
            })}
          </div>
          <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 18, color: CREAM, opacity: 0.5, marginTop: 22 }}>Illustrative screen · rule-based scanner output</div>
        </Card>
        <Card t={t} at={m.c2} active={t >= m.c2} w={500} h={560} title="Broker Connect" sub="Apna broker account link karo">
          <svg width={440} height={250} viewBox="0 0 440 250">
            <rect x={20} y={70} width={150} height={110} rx={20} fill="none" stroke={GOLD} strokeWidth={4} />
            <text x={95} y={133} textAnchor="middle" fill={CREAM} fontFamily="Poppins" fontWeight={800} fontSize={24}>AI Dash</text>
            <rect x={270} y={70} width={150} height={110} rx={20} fill="none" stroke={GOLD} strokeWidth={4} />
            <text x={345} y={133} textAnchor="middle" fill={CREAM} fontFamily="Poppins" fontWeight={800} fontSize={24}>Broker</text>
            <line x1={170} x2={170 + 100 * conn} y1={125} y2={125} stroke={GREEN} strokeWidth={6} strokeDasharray="12 8" />
          </svg>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 6 }}>
            <div style={{ width: 92, height: 48, borderRadius: 999, backgroundColor: conn > 0.5 ? GREEN : "rgba(255,241,201,0.25)", position: "relative" }}>
              <div style={{ position: "absolute", top: 5, left: 5 + 44 * conn, width: 38, height: 38, borderRadius: "50%", backgroundColor: "white" }} />
            </div>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: conn > 0.5 ? GREEN : CREAM }}>{conn > 0.5 ? "Connected" : "Connect"}</div>
          </div>
        </Card>
      </div>
      <div style={{ position: "absolute", top: 900, left: 0, right: 0, textAlign: "center", fontFamily: SANS, fontWeight: 600, fontSize: 26, color: CREAM, opacity: interpolate(t, [m.c3, m.c3 + 0.4], [0.55, 1], clamp) }}>
        Educational purpose only · Not investment advice · Signals follow scanner rules, not recommendations
      </div>
    </>
  );
};

const EndScene: React.FC<{ t: number; p: InsertProps }> = ({ t, p }) => {
  const m = p.marks;
  const ring = spring(t, 0.2, 0.7);
  return (
    <>
      <div style={{ position: "absolute", left: 170, top: 190, width: 520, height: 520, borderRadius: "50%", padding: 12, background: GOLD_GRAD, scale: `${ring}`, boxShadow: "0 0 90px rgba(245,196,81,0.5)" }}>
        <Img src={staticFile("daily/chirag.png")} style={{ width: 496, height: 496, borderRadius: "50%", objectFit: "cover", objectPosition: "50% 22%" }} />
      </div>
      <div style={{ position: "absolute", left: 120, width: 620, top: 750, textAlign: "center" }}>
        <Gold size={64}>CHIRAG RATHOD</Gold>
        <div style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 30, letterSpacing: 6 }}>UPPERCIRCUITSTOCKS</div>
      </div>
      <div style={{ position: "absolute", left: 820, right: 90, top: 200 }}>
        <div style={{ opacity: spring(t, 0.4) }}>
          <div style={{ fontFamily: SERIF, fontWeight: 700, color: CREAM, fontSize: 30, letterSpacing: 6 }}>TRY THE</div>
          <Gold size={100}>AI DASHBOARD</Gold>
        </div>
        {[
          ["DASHBOARD", p.dashUrl, m.d1 + 0.2],
          ["TELEGRAM", p.telegram.replace("https://", ""), m.d1 + 2.2],
        ].map(([ic, txt, at]) => (
          <div key={txt as string} style={{ marginTop: 34, display: "flex", alignItems: "center", gap: 18, opacity: spring(t, at as number), scale: `${0.9 + 0.1 * spring(t, at as number)}`, transformOrigin: "left center" }}>
            <div style={{ width: 190, fontFamily: SANS, fontWeight: 800, fontSize: 26, color: GOLD, letterSpacing: 2 }}>{ic}</div>
            <div style={{ padding: "14px 30px", borderRadius: 999, backgroundImage: GOLD_GRAD, color: "#0A0A0A", fontFamily: SANS, fontWeight: 800, fontSize: (txt as string).length > 30 ? 30 : 38 }}>{txt}</div>
          </div>
        ))}
        <div style={{ marginTop: 56, display: "flex", gap: 18, opacity: spring(t, m.d2) }}>
          {["LIKE", "SHARE", "SUBSCRIBE"].map((x, i) => (
            <div key={x} style={{ padding: "16px 30px", borderRadius: 16, border: `3px solid ${i === 2 ? RED : GOLD}`, backgroundColor: i === 2 ? RED : "transparent", color: i === 2 ? "white" : GOLD, fontFamily: SANS, fontWeight: 800, fontSize: 32, scale: `${1 + (i === 2 ? 0.04 * Math.sin((t - m.d2) * Math.PI * 2) : 0)}` }}>{x}</div>
          ))}
        </div>
      </div>
    </>
  );
};

export const DashInsert: React.FC<InsertProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const t = frame / fps;
  const fadeIn = interpolate(t, [0, 0.3], [0, 1], clamp);
  const fadeOut = interpolate(t, [p.duration - 0.35, p.duration], [1, 0], clamp);
  const k = width / 1920;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: "0 0", opacity: fadeIn * fadeOut, overflow: "hidden", backgroundColor: "#040302", backgroundImage: "radial-gradient(circle at 50% 40%, rgba(245,196,81,0.2) 0%, rgba(176,122,18,0.07) 42%, rgba(0,0,0,0) 72%)" }}>
        <Candles t={t} />
        <div style={{ position: "absolute", inset: 0, boxShadow: "inset 0 0 220px rgba(0,0,0,0.9)" }} />
        <div style={{ position: "absolute", inset: 22, border: "2px solid rgba(245,196,81,0.55)", borderRadius: 18 }} />
        {p.kind === "intro" && <IntroScene t={t} p={p} />}
        {p.kind === "screener" && <ScreenerScene t={t} p={p} />}
        {p.kind === "signals" && <SignalsScene t={t} p={p} />}
        {p.kind === "end" && <EndScene t={t} p={p} />}
      </div>
    </AbsoluteFill>
  );
};

const DEFAULT: InsertProps = { kind: "intro", duration: 12, marks: { a1: 0.3, a2: 3, a3: 9 }, dashUrl: "app.uppercircuitstocks.com", telegram: "https://t.me/uppercircuitstocksbychiragrathod" };
export const DashInsertComposition = () => (
  <Composition id="DashInsert" component={DashInsert} durationInFrames={300} fps={25} width={1280} height={720} defaultProps={DEFAULT}
    calculateMetadata={({ props }) => ({ durationInFrames: Math.ceil(props.duration * 25) })} />
);
