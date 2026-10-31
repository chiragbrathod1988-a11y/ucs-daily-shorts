import { AbsoluteFill, Audio, Composition, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/fonts";
import { DASH } from "./dashData";

for (const weight of ["500", "700", "800"]) {
  loadFont({ family: "Poppins", url: staticFile(`fonts/poppins-latin-${weight}-normal.woff2`), weight });
  loadFont({ family: "PoppinsExt", url: staticFile(`fonts/poppins-latin-ext-${weight}-normal.woff2`), weight });
}
loadFont({ family: "Cinzel", url: staticFile("fonts/cinzel-latin-700-normal.woff2"), weight: "700" });
const SANS = "Poppins, PoppinsExt, 'Noto Color Emoji', sans-serif";
const SERIF = "Cinzel, serif";
const GOLD = "#F5C451";
const CREAM = "#FFF1C9";
const GREEN = "#22C55E";
const RED = "#EF4444";
const TG = "#2AABEE";
const GOLD_GRAD = "linear-gradient(180deg,#FFF7D1 0%,#F5C451 42%,#B8801A 72%,#FFE08A 100%)";
const FPS = 30;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outExpo = Easing.bezier(0.16, 1, 0.3, 1);
const spring = (d = 12) => Easing.spring({ damping: d });

/* eslint-disable @typescript-eslint/no-explicit-any */
const DATA: any = DASH;
const TL: { tag: string; start: number; end: number; en: string }[] = DATA.timeline;
const SC: any[] = DATA.scenes;
const SHOTS: Record<string, { w: number; h: number }> = DATA.shots;
const TOTAL: number = DATA.duration;
const dateLabel = (() => {
  const d = new Date(DATA.date + "T00:00:00");
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" }).toUpperCase();
})();

// group consecutive lines that share the same visual into one scene block
type Block = { sc: any; start: number; end: number; parts: { sc: any; start: number; end: number }[] };
const BLOCKS: Block[] = [];
TL.forEach((l, i) => {
  const sc = SC[i];
  const key = `${sc.kind}|${sc.shot ?? sc.chart ?? ""}|${sc.n ?? ""}`;
  const last = BLOCKS[BLOCKS.length - 1];
  if (last && `${last.sc.kind}|${last.sc.shot ?? last.sc.chart ?? ""}|${last.sc.n ?? ""}` === key) {
    last.end = l.end;
    last.parts.push({ sc, start: l.start, end: l.end });
  } else BLOCKS.push({ sc, start: l.start, end: l.end, parts: [{ sc, start: l.start, end: l.end }] });
});
BLOCKS.forEach((b, i) => { b.start = i === 0 ? 0 : b.start - 0.18; b.end = i < BLOCKS.length - 1 ? BLOCKS[i + 1].start - 0.18 : TOTAL; });

const Gold: React.FC<{ size: number; children: React.ReactNode; font?: string; style?: React.CSSProperties }> = ({ size, children, font, style }) => (
  <span style={{ fontFamily: font ?? SANS, fontWeight: 800, fontSize: size, backgroundImage: GOLD_GRAD, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", ...style }}>{children}</span>
);

const Chrome: React.FC<{ t: number }> = ({ t }) => (
  <>
    <div style={{ position: "absolute", inset: 22, border: "2px solid rgba(201,138,14,0.55)", borderRadius: 20 }} />
    <div style={{ position: "absolute", left: 40, right: 40, top: 205, height: 8, borderRadius: 4, backgroundColor: "rgba(255,255,255,0.12)" }}>
      <div style={{ height: "100%", borderRadius: 4, backgroundImage: GOLD_GRAD, width: `${(t / TOTAL) * 100}%` }} />
    </div>
    <div style={{ position: "absolute", left: 40, top: 70, display: "flex", alignItems: "center", gap: 20 }}>
      <Img src={staticFile("dash/logo.png")} style={{ width: 104, height: 104, borderRadius: 22, border: `3px solid #B8801A`, objectFit: "cover" }} />
      <div>
        <div style={{ fontFamily: SERIF, color: CREAM, fontSize: 26, letterSpacing: 5 }}>UPPERCIRCUITSTOCKS</div>
        <Gold size={52}>AI DASHBOARD</Gold>
      </div>
    </div>
    <div style={{ position: "absolute", right: 40, top: 88, textAlign: "right" }}>
      <div style={{ display: "inline-block", padding: "8px 20px", borderRadius: 999, border: `2px solid ${GOLD}`, color: GOLD, fontFamily: SANS, fontWeight: 800, fontSize: 28 }}>{dateLabel}</div>
      <div style={{ marginTop: 8, color: CREAM, fontFamily: SANS, fontWeight: 700, fontSize: 24, letterSpacing: 3, opacity: 0.85 }}>
        {DATA.slot === "morning" ? "MORNING BRIEF" : DATA.mode === "spotlight" ? "FEATURE SPOTLIGHT" : "SIGNAL REVIEW"}
      </div>
    </div>
  </>
);

const Phone: React.FC<{ shot?: string; t: number; start: number; end: number; scroll?: number[]; top?: number; height?: number }> = ({ shot, t, start, end, scroll, top = 250, height = 1150 }) => {
  const W = 640;
  const p = interpolate(t, [start, start + 0.5], [0, 1], { ...clamp, easing: outExpo });
  const info = shot ? SHOTS[shot] : undefined;
  const imgH = info ? (info.h * W) / info.w : 0;
  const maxOff = Math.max(0, imgH - (height - 36));
  const [a, b] = scroll ?? [0, 0.3];
  const off = maxOff * interpolate(t, [start + 0.4, end], [Math.min(a, 1), Math.min(b, 1)], { ...clamp, easing: Easing.inOut(Easing.quad) }) / 1;
  return (
    <div style={{ position: "absolute", left: (1080 - W - 36) / 2, top, width: W + 36, height, borderRadius: 64, padding: 18, boxSizing: "border-box", background: "linear-gradient(160deg,#2a2112,#0b0905)", border: `3px solid ${GOLD}`, boxShadow: "0 30px 80px rgba(0,0,0,0.7), 0 0 60px rgba(245,196,81,0.25)", opacity: p, transform: `translateY(${(1 - p) * 80}px) scale(${0.94 + 0.06 * p})` }}>
      <div style={{ width: W, height: height - 36, borderRadius: 48, overflow: "hidden", backgroundColor: "#000", position: "relative" }}>
        {info ? (
          <Img src={staticFile("dash/" + shot)} style={{ position: "absolute", left: 0, top: -Math.min(off, maxOff), width: W, height: imgH }} />
        ) : (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 20 }}>
            <Img src={staticFile("dash/logo.png")} style={{ width: 220, borderRadius: 30 }} />
            <Gold size={40}>app.uppercircuitstocks.com</Gold>
          </div>
        )}
        <div style={{ position: "absolute", top: 12, left: "50%", width: 120, height: 30, marginLeft: -60, borderRadius: 20, backgroundColor: "#000" }} />
      </div>
    </div>
  );
};

const Hook: React.FC<{ b: Block; t: number }> = ({ b, t }) => {
  const sc = b.sc;
  const s = interpolate(t, [0, 0.5], [0.6, 1], { ...clamp, easing: spring(10) });
  const chips: string[] = sc.chips ?? [];
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 330, height: 1000, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <div style={{ scale: `${s}` }}>
        <Gold size={sc.title.length > 14 ? 104 : 132} style={{ lineHeight: 1.05, display: "block" }}>{sc.title}</Gold>
      </div>
      <div style={{ marginTop: 26, color: CREAM, fontFamily: SANS, fontWeight: 700, fontSize: 46, opacity: interpolate(t, [0.3, 0.7], [0, 1], clamp) }}>{sc.sub}</div>
      {chips.length ? (
        <div style={{ marginTop: 50, display: "flex", gap: 22 }}>
          {chips.map((c, i) => {
            const a = interpolate(t, [0.5 + i * 0.18, 0.8 + i * 0.18], [0, 1], { ...clamp, easing: spring(9) });
            return <div key={i} style={{ width: 150, height: 150, borderRadius: 34, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 84, backgroundColor: c === "❌" ? "rgba(239,68,68,0.18)" : "rgba(34,197,94,0.18)", border: `4px solid ${c === "❌" ? RED : GREEN}`, scale: `${a}` }}>{c}</div>;
          })}
        </div>
      ) : (
        <div style={{ marginTop: 50, padding: "18px 40px", borderRadius: 999, backgroundImage: GOLD_GRAD, color: "#0a0a0a", fontFamily: SANS, fontWeight: 800, fontSize: 44, scale: `${interpolate(t, [0.6, 1.0], [0, 1], { ...clamp, easing: spring(10) })}` }}>
          {DATA.slot === "morning" ? "Traders se aage raho 🚀" : "Ab dekho 👇"}
        </div>
      )}
    </div>
  );
};

const StatRow: React.FC<{ stats: string[][]; t: number; at: number }> = ({ stats, t, at }) => (
  <div style={{ position: "absolute", left: 50, right: 50, top: 1215, display: "flex", gap: 16, justifyContent: "center" }}>
    {stats.map(([k, v, c], i) => {
      const a = interpolate(t, [at + i * 0.2, at + 0.4 + i * 0.2], [0, 1], { ...clamp, easing: spring(11) });
      const up = c.startsWith("+");
      return (
        <div key={k} style={{ flex: 1, padding: "16px 10px", borderRadius: 22, textAlign: "center", background: "linear-gradient(180deg,#191207,#070604)", border: `3px solid ${GOLD}`, scale: `${a}`, boxShadow: "0 12px 30px rgba(0,0,0,0.7)" }}>
          <div style={{ color: CREAM, fontFamily: SANS, fontWeight: 700, fontSize: 22, letterSpacing: 2 }}>{k}</div>
          <div style={{ color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 40 }}>{v}</div>
          <div style={{ color: up ? GREEN : RED, fontFamily: SANS, fontWeight: 800, fontSize: 28 }}>{up ? "▲ " : "▼ "}{c}</div>
        </div>
      );
    })}
  </div>
);

const Pill: React.FC<{ t: number; at: number; children: React.ReactNode; top: number; color?: string }> = ({ t, at, children, top, color }) => {
  const a = interpolate(t, [at, at + 0.35], [0, 1], { ...clamp, easing: spring(11) });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top, display: "flex", justifyContent: "center" }}>
      <div style={{ scale: `${a}`, padding: "16px 34px", borderRadius: 24, backgroundColor: "rgba(8,8,8,0.94)", border: `3px solid ${color ?? GOLD}`, color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 40, boxShadow: "0 12px 40px rgba(0,0,0,0.7)", textAlign: "center" }}>{children}</div>
    </div>
  );
};

const ScreenScene: React.FC<{ b: Block; t: number }> = ({ b, t }) => (
  <>
    <Phone shot={b.sc.shot} t={t} start={b.start} end={b.end} scroll={[b.parts[0].sc.scroll?.[0] ?? 0, b.parts[b.parts.length - 1].sc.scroll?.[1] ?? 0.4]} top={250} height={940} />
    {b.parts.map((p, i) => (
      <div key={"o" + i} style={{ opacity: interpolate(t, [p.start, p.start + 0.3, (b.parts[i + 1]?.start ?? b.end) - 0.1, b.parts[i + 1]?.start ?? b.end], [0, 1, 1, 0], clamp) }}>
        {p.sc.stats ? <StatRow stats={p.sc.stats} t={t} at={p.start + 0.2} /> : null}
        {p.sc.badge ? <Pill t={t} at={p.start + 0.2} top={1230} color={p.sc.badge[0].includes("BEAR") ? RED : GREEN}>{p.sc.badge[0]}<div style={{ fontSize: 32, color: CREAM }}>{p.sc.badge[1]}</div></Pill> : null}
        {p.sc.sectors ? (
          <div style={{ position: "absolute", left: 50, right: 50, top: 1225, display: "flex", gap: 16 }}>
            {p.sc.sectors.map(([n, c]: string[], k: number) => (
              <div key={n} style={{ flex: 1, padding: "14px 12px", borderRadius: 22, textAlign: "center", backgroundColor: "rgba(8,8,8,0.94)", border: `3px solid ${k === 0 ? GREEN : RED}`, scale: `${interpolate(t, [p.start + 0.2 + k * 0.25, p.start + 0.6 + k * 0.25], [0, 1], { ...clamp, easing: spring(11) })}` }}>
                <div style={{ color: k === 0 ? GREEN : RED, fontFamily: SANS, fontWeight: 800, fontSize: 24, letterSpacing: 2 }}>{k === 0 ? "STRONGEST" : "WEAKEST"}</div>
                <div style={{ color: "white", fontFamily: SANS, fontWeight: 800, fontSize: n.length > 16 ? 30 : 36, lineHeight: 1.1 }}>{n}</div>
                <div style={{ color: k === 0 ? GREEN : RED, fontFamily: SANS, fontWeight: 800, fontSize: 30 }}>{c}</div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    ))}
  </>
);

const FeatureScene: React.FC<{ b: Block; t: number }> = ({ b, t }) => (
  <>
    <Phone shot={b.sc.shot} t={t} start={b.start} end={b.end} scroll={[b.parts[0].sc.scroll?.[0] ?? 0, b.parts[b.parts.length - 1].sc.scroll?.[1] ?? 0.4]} top={330} height={1070} />
    <Pill t={t} at={b.start + 0.1} top={238}>
      <span style={{ color: CREAM, fontSize: 26, letterSpacing: 3 }}>FEATURE OF THE DAY</span>
      <div><Gold size={44}>{b.sc.name}</Gold></div>
    </Pill>
  </>
);

const SignalScene: React.FC<{ b: Block; t: number }> = ({ b, t }) => {
  const sc = b.sc;
  const res = b.parts.find((p) => p.sc.phase === "result");
  const info = SHOTS[sc.shot];
  const p = interpolate(t, [b.start, b.start + 0.45], [0, 1], { ...clamp, easing: outExpo });
  const stamp = res ? interpolate(t, [res.start, res.start + 0.4], [0, 1], { ...clamp, easing: spring(8) }) : 0;
  const W = 900;
  const H = info ? Math.min(760, (info.h * W) / info.w) : 200 + 110 * [sc.entry, sc.sl, (sc.tgt ?? []).length ? 1 : null].filter(Boolean).length;
  const col = sc.win ? GREEN : RED;
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, top: 245, textAlign: "center", opacity: p }}>
        <span style={{ padding: "10px 28px", borderRadius: 999, border: `2px solid ${GOLD}`, color: GOLD, fontFamily: SANS, fontWeight: 800, fontSize: 30, letterSpacing: 2 }}>
          SIGNAL {sc.n} · {sc.scanner.toUpperCase()} · {sc.time}
        </span>
      </div>
      <div style={{ position: "absolute", left: (1080 - W) / 2, top: 330, width: W, height: H, borderRadius: 30, overflow: "hidden", border: `4px solid ${stamp > 0.5 ? col : GOLD}`, boxShadow: `0 0 ${40 + 40 * stamp}px ${stamp > 0.5 ? col + "88" : "rgba(245,196,81,0.35)"}`, opacity: p, transform: `translateY(${(1 - p) * 70}px)`, backgroundColor: "#0b0905" }}>
        {info ? (
          <Img src={staticFile("dash/" + sc.shot)} style={{ width: W, height: (info.h * W) / info.w }} />
        ) : (
          <div style={{ padding: 50, fontFamily: SANS, color: "white" }}>
            <Gold size={70}>{sc.contract}</Gold>
            {[["ENTRY", sc.entry], ["SL", sc.sl], ["TARGET", (sc.tgt ?? []).join(" / ")]].filter(([, v]) => v).map(([k, v]) => (
              <div key={k} style={{ marginTop: 36, display: "flex", justifyContent: "space-between", fontSize: 50, fontWeight: 800 }}>
                <span style={{ color: CREAM, opacity: 0.8 }}>{k}</span><span>{v}</span>
              </div>
            ))}
          </div>
        )}
        {stamp > 0 ? (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: `rgba(0,0,0,${0.35 * stamp})` }}>
            <div style={{ scale: `${0.4 + 0.6 * stamp}`, rotate: "-8deg", padding: "22px 48px", borderRadius: 26, border: `8px solid ${col}`, backgroundColor: "rgba(5,5,5,0.92)", color: col, fontFamily: SANS, fontWeight: 800, fontSize: 70 }}>{sc.label}</div>
          </div>
        ) : null}
      </div>
      <div style={{ position: "absolute", left: 60, right: 60, top: 330 + H + 30, display: "flex", justifyContent: "center", opacity: interpolate(t, [b.start + 0.5, b.start + 0.9], [0, 1], clamp) }}>
        <div style={{ padding: "16px 30px", borderRadius: 22, backgroundColor: "rgba(8,8,8,0.94)", border: `3px solid ${GOLD}`, fontFamily: SANS, fontWeight: 800, fontSize: 34, color: "white", textAlign: "center", maxWidth: 940 }}>
          <span style={{ color: GOLD }}>LOGIC · </span>{sc.logic}
        </div>
      </div>
    </>
  );
};

const AheadScene: React.FC<{ b: Block; t: number }> = ({ b, t }) => {
  const n = interpolate(t, [b.start + 0.5, b.start + 0.9], [-260, 0], { ...clamp, easing: spring(12) });
  return (
    <>
      <Phone shot={b.sc.shot} t={t} start={b.start} end={b.end} scroll={[0, 0]} top={300} height={1100} />
      <div style={{ position: "absolute", left: 230, right: 230, top: 340, transform: `translateY(${n}px)`, opacity: n > -250 ? 1 : 0 }}>
        <div style={{ display: "flex", gap: 16, alignItems: "center", padding: "18px 22px", borderRadius: 26, backgroundColor: "rgba(28,28,30,0.97)", boxShadow: "0 18px 40px rgba(0,0,0,0.7)", border: "1px solid rgba(255,255,255,0.15)" }}>
          <Img src={staticFile("dash/logo.png")} style={{ width: 64, height: 64, borderRadius: 14 }} />
          <div style={{ fontFamily: SANS, color: "white" }}>
            <div style={{ fontWeight: 800, fontSize: 26 }}>🔔 New signal · UpperCircuit</div>
            <div style={{ fontSize: 22, opacity: 0.85 }}>Entry, SL & targets ready — tap to trade</div>
          </div>
        </div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1240, display: "flex", justifyContent: "center", gap: 18 }}>
        {["FYERS", "ZERODHA", "DHAN"].map((x, i) => (
          <div key={x} style={{ scale: `${interpolate(t, [b.start + 1.2 + i * 0.25, b.start + 1.55 + i * 0.25], [0, 1], { ...clamp, easing: spring(11) })}`, padding: "14px 30px", borderRadius: 18, backgroundColor: "#0b0b0b", border: `3px solid ${GOLD}`, color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 38 }}>{x}</div>
        ))}
      </div>
    </>
  );
};


const IST = (t: number) => { const d = new Date((t + 19800) * 1000); return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}`; };
const isoToSec = (iso?: string) => (iso ? Math.floor(new Date(iso).getTime() / 1000) : 0);
const fmtP = (n: number) => n >= 1000 ? Math.round(n).toLocaleString("en-IN") : n.toFixed(n >= 100 ? 1 : 2);

const ChartScene: React.FC<{ b: Block; t: number }> = ({ b, t }) => {
  const sc = b.sc;
  const ch = DATA.charts?.[sc.chart];
  const X0 = 70, X1 = 930, Y0 = 360, Y1 = 1140;
  const p = interpolate(t, [b.start, b.start + 0.4], [0, 1], { ...clamp, easing: outExpo });
  if (!ch) {
    if (sc.mode === "signal") return <SignalScene b={b} t={t} />;
    return <Pill t={t} at={b.start} top={700}>{sc.title}</Pill>;
  }
  const cs: number[][] = ch.candles;
  const n = cs.length;
  const hi = Math.max(...cs.map((c) => c[2])), lo = Math.min(...cs.map((c) => c[3]));
  const pad = (hi - lo) * 0.08;
  const yv = (v: number) => Y1 - ((v - (lo - pad)) / (hi - lo + 2 * pad)) * (Y1 - Y0);
  const step = (X1 - X0) / n;
  const res = b.parts.find((q) => q.sc.phase === "result");
  const revealEnd = res ? res.start : b.start + 0.3 + Math.max(1.6, (b.end - b.start) * 0.62);
  const reveal = interpolate(t, [b.start + 0.3, revealEnd], [0, n], { ...clamp, easing: Easing.inOut(Easing.quad) });
  const shown = Math.floor(reveal);
  const last = cs[Math.max(0, Math.min(n - 1, shown - 1))];
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((k) => lo - pad + k * (hi - lo + 2 * pad));
  const idxOf = (sec: number) => { if (!sec) return -1; let k = cs.findIndex((c) => c[0] > sec) - 1; if (k < -1) k = n - 1; return Math.max(0, k === -2 ? n - 1 : k); };
  const si = sc.mode === "signal" ? idxOf(isoToSec(sc.sigTs)) : -1;
  const xi = sc.mode === "signal" ? idxOf(isoToSec(sc.exitTs)) : -1;
  const done = shown >= n;
  const col = sc.win ? GREEN : RED;
  const stamp = sc.mode === "signal" ? interpolate(t, [revealEnd, revealEnd + 0.4], [0, 1], { ...clamp, easing: spring(8) }) : 0;
  const card = sc.shot ? SHOTS[sc.shot] : undefined;
  const inset = card ? interpolate(t, [b.start + 0.4, b.start + 0.8, revealEnd - 0.3, revealEnd], [0, 1, 1, 0], clamp) : 0;
  const hiI = cs.findIndex((c) => c[2] === hi), loI = cs.findIndex((c) => c[3] === lo);
  return (
    <div style={{ opacity: p }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 245, textAlign: "center" }}>
        <span style={{ padding: "10px 28px", borderRadius: 999, border: `2px solid ${GOLD}`, color: GOLD, fontFamily: SANS, fontWeight: 800, fontSize: 30, letterSpacing: 2 }}>
          {sc.mode === "signal" ? sc.title : `${sc.title} · ${new Date(ch.date + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "short" }).toUpperCase()}`}
        </span>
      </div>
      <div style={{ position: "absolute", left: 40, top: 320, width: 1000, height: 860, borderRadius: 30, background: "linear-gradient(180deg,#0e0b06,#050403)", border: `3px solid rgba(245,196,81,0.55)`, boxShadow: "0 20px 60px rgba(0,0,0,0.7)" }} />
      <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0 }}>
        {ticks.map((v, k) => (
          <g key={k}>
            <line x1={X0} x2={X1} y1={yv(v)} y2={yv(v)} stroke="rgba(255,241,201,0.10)" strokeWidth={2} />
            <text x={X1 + 12} y={yv(v) + 9} fill={CREAM} opacity={0.7} fontFamily={SANS} fontSize={24} fontWeight={600}>{fmtP(v)}</text>
          </g>
        ))}
        {[0, Math.floor(n / 3), Math.floor((2 * n) / 3), n - 1].map((k) => (
          <text key={k} x={X0 + k * step} y={Y1 + 34} fill={CREAM} opacity={0.6} fontFamily={SANS} fontSize={22} textAnchor="middle">{IST(cs[k][0])}</text>
        ))}
        {si >= 0 && xi >= 0 && shown > si ? (
          <rect x={X0 + si * step} y={Y0} width={Math.max(step, (Math.min(xi, shown - 1) - si + 1) * step)} height={Y1 - Y0} fill={shown > xi && done ? col : GOLD} opacity={0.10} />
        ) : null}
        {cs.slice(0, shown).map((c, k) => {
          const up = c[4] >= c[1];
          const x = X0 + k * step + step / 2;
          const bw = Math.max(3, step * 0.62);
          return (
            <g key={k}>
              <line x1={x} x2={x} y1={yv(c[2])} y2={yv(c[3])} stroke={up ? GREEN : RED} strokeWidth={Math.max(1.5, step * 0.12)} />
              <rect x={x - bw / 2} y={yv(Math.max(c[1], c[4]))} width={bw} height={Math.max(2, Math.abs(yv(c[1]) - yv(c[4])))} fill={up ? GREEN : RED} rx={1.5} />
            </g>
          );
        })}
        {shown > 0 ? (
          <g>
            <line x1={X0} x2={X1} y1={yv(last[4])} y2={yv(last[4])} stroke={GOLD} strokeWidth={2} strokeDasharray="10 8" />
            <rect x={X1 - 8} y={yv(last[4]) - 22} width={138} height={44} rx={8} fill={GOLD} />
            <text x={X1 + 61} y={yv(last[4]) + 9} fill="#0a0a0a" fontFamily={SANS} fontSize={24} fontWeight={800} textAnchor="middle">{fmtP(last[4])}</text>
          </g>
        ) : null}
        {sc.mode === "session" && done ? (
          <g fontFamily={SANS} fontWeight={800} fontSize={26}>
            <text x={X0 + hiI * step + step / 2} y={yv(hi) - 16} fill={GREEN} textAnchor="middle">H {fmtP(hi)}</text>
            <text x={X0 + loI * step + step / 2} y={yv(lo) + 40} fill={RED} textAnchor="middle">L {fmtP(lo)}</text>
          </g>
        ) : null}
        {si >= 0 && shown > si ? (
          <g fontFamily={SANS} fontWeight={800}>
            <line x1={X0 + si * step + step / 2} x2={X0 + si * step + step / 2} y1={Y0} y2={Y1} stroke={GOLD} strokeWidth={3} />
            <rect x={X0 + si * step + step / 2 - 90} y={Y0 + 8} width={180} height={46} rx={10} fill={GOLD} />
            <text x={X0 + si * step + step / 2} y={Y0 + 40} fill="#0a0a0a" fontSize={24} textAnchor="middle">SIGNAL {IST(cs[si][0])}</text>
          </g>
        ) : null}
        {xi >= 0 && shown > xi ? (
          <g fontFamily={SANS} fontWeight={800}>
            <line x1={X0 + xi * step + step / 2} x2={X0 + xi * step + step / 2} y1={Y0 + 60} y2={Y1} stroke={col} strokeWidth={3} strokeDasharray="8 6" />
            <rect x={X0 + xi * step + step / 2 - 70} y={Y1 - 56} width={140} height={46} rx={10} fill={col} />
            <text x={X0 + xi * step + step / 2} y={Y1 - 24} fill="#fff" fontSize={24} textAnchor="middle">EXIT {IST(cs[xi][0])}</text>
          </g>
        ) : null}
      </svg>
      {stamp > 0 ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 620, display: "flex", justifyContent: "center" }}>
          <div style={{ scale: `${0.4 + 0.6 * stamp}`, rotate: "-7deg", padding: "20px 44px", borderRadius: 26, border: `8px solid ${col}`, backgroundColor: "rgba(5,5,5,0.9)", color: col, fontFamily: SANS, fontWeight: 800, fontSize: 66 }}>{sc.label}</div>
        </div>
      ) : null}
      {sc.mode === "signal" ? (
        <div style={{ position: "absolute", left: 50, right: 50, top: 1196, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <div style={{ color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 40 }}><Gold size={40}>{sc.contract}</Gold></div>
          <div style={{ padding: "10px 24px", borderRadius: 18, backgroundColor: "rgba(8,8,8,0.94)", border: `3px solid ${GOLD}`, fontFamily: SANS, fontWeight: 800, fontSize: 30, color: "white" }}><span style={{ color: GOLD }}>LOGIC · </span>{sc.logic}</div>
        </div>
      ) : null}
      {inset > 0 && card ? (
        <div style={{ position: "absolute", left: 90, top: 380, width: 470, borderRadius: 20, overflow: "hidden", border: `3px solid ${GOLD}`, boxShadow: "0 18px 50px rgba(0,0,0,0.8)", opacity: inset, transform: `translateY(${(1 - inset) * -30}px)` }}>
          <Img src={staticFile("dash/" + sc.shot)} style={{ width: 470, height: (card.h * 470) / card.w, display: "block" }} />
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "4px 0", textAlign: "center", backgroundColor: "rgba(0,0,0,0.75)", color: GOLD, fontFamily: SANS, fontWeight: 800, fontSize: 18, letterSpacing: 2 }}>LIVE CARD · AI DASHBOARD</div>
        </div>
      ) : null}
      <div style={{ position: "absolute", right: 70, top: 330, color: CREAM, opacity: 0.45, fontFamily: SANS, fontSize: 18 }}>Data: UpperCircuit AI Dashboard</div>
    </div>
  );
};

const CtaScene: React.FC<{ b: Block; t: number }> = ({ b, t }) => {
  const p = interpolate(t, [b.start, b.start + 0.5], [0, 1], { ...clamp, easing: spring(12) });
  const pulse = 1 + 0.03 * Math.sin((t - b.start) * Math.PI * 2);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 300, display: "flex", flexDirection: "column", alignItems: "center", opacity: p }}>
      <Img src={staticFile("dash/logo.png")} style={{ width: 300, borderRadius: 40, scale: `${0.8 + 0.2 * p}`, boxShadow: "0 0 80px rgba(245,196,81,0.4)" }} />
      <div style={{ marginTop: 30 }}><Gold size={84}>AI DASHBOARD</Gold></div>
      <div style={{ marginTop: 10, color: CREAM, fontFamily: SANS, fontWeight: 700, fontSize: 40 }}>Traders se ek kadam aage 🚀</div>
      <div style={{ marginTop: 40, scale: `${pulse}`, padding: "20px 44px", borderRadius: 999, backgroundImage: GOLD_GRAD, color: "#0a0a0a", fontFamily: SANS, fontWeight: 800, fontSize: 46, boxShadow: "0 0 50px rgba(245,196,81,0.5)" }}>app.uppercircuitstocks.com</div>
      <div style={{ marginTop: 26, padding: "12px 30px", borderRadius: 16, border: `3px solid ${GREEN}`, color: GREEN, fontFamily: SANS, fontWeight: 800, fontSize: 38 }}>3-DAY FREE TRIAL</div>
      <div style={{ marginTop: 34, display: "flex", gap: 18 }}>
        {["LIKE", "SHARE", "FOLLOW"].map((x, i) => (
          <div key={x} style={{ scale: `${interpolate(t, [b.start + 0.5 + i * 0.2, b.start + 0.85 + i * 0.2], [0, 1], { ...clamp, easing: spring(11) })}`, padding: "12px 28px", borderRadius: 16, border: `3px solid ${GOLD}`, color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 36 }}>{x}</div>
        ))}
      </div>
    </div>
  );
};

const Subs: React.FC<{ t: number }> = ({ t }) => {
  const s = (DATA.subs as { text: string; start: number; end: number }[]).find((x) => t >= x.start && t < x.end);
  if (!s) return null;
  const age = t - s.start;
  const pop = interpolate(age, [0, 0.15], [0.85, 1], { ...clamp, easing: Easing.bezier(0.34, 1.56, 0.64, 1) });
  return (
    <div style={{ position: "absolute", left: 50, right: 50, top: 1418, height: 190, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <div style={{ scale: `${pop}`, opacity: interpolate(age, [0, 0.08], [0, 1], clamp), fontFamily: SANS, fontWeight: 800, fontSize: 58, lineHeight: 1.15, color: "white", WebkitTextStroke: "9px #000", paintOrder: "stroke fill", textShadow: "0 6px 18px rgba(0,0,0,0.85)" }}>{s.text}</div>
    </div>
  );
};

const TelegramBar: React.FC = () => (
  <div style={{ position: "absolute", left: 50, right: 50, top: 1700, height: 110, borderRadius: 26, display: "flex", alignItems: "center", gap: 20, padding: "0 26px", backgroundColor: "rgba(10,10,10,0.95)", border: `3px solid ${TG}`, boxShadow: "0 0 30px rgba(42,171,238,0.35)" }}>
    <svg width={70} height={70} viewBox="0 0 24 24" style={{ flexShrink: 0 }}>
      <circle cx="12" cy="12" r="12" fill={TG} />
      <path d="M5.4 11.7l11.1-4.3c.5-.2 1 .1.8.9l-1.9 8.9c-.1.6-.5.8-1 .5l-2.9-2.1-1.4 1.3c-.2.2-.3.3-.6.3l.2-2.9 5.3-4.8c.2-.2 0-.3-.3-.1l-6.6 4.1-2.8-.9c-.6-.2-.6-.6.1-.9z" fill="white" />
    </svg>
    <div style={{ lineHeight: 1.15, fontFamily: SANS }}>
      <div style={{ color: TG, fontSize: 28, fontWeight: 800, letterSpacing: 2 }}>JOIN FREE TELEGRAM</div>
      <div style={{ color: "white", fontSize: 31, fontWeight: 700 }}>t.me/uppercircuitstocksbychiragrathod</div>
    </div>
  </div>
);

export const DashShort: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const b = BLOCKS.find((x) => t >= x.start && t < x.end) ?? BLOCKS[BLOCKS.length - 1];
  const fade = interpolate(t, [b.start, b.start + 0.25], [0, 1], clamp);
  const k = b.sc.kind;
  return (
    <AbsoluteFill style={{ backgroundColor: "#050505", backgroundImage: "radial-gradient(circle at 50% 45%, rgba(245,196,81,0.18) 0%, rgba(184,128,26,0.06) 40%, rgba(0,0,0,0) 70%)", fontFamily: SANS }}>
      <Audio src={staticFile("dash/mix.wav")} />
      <Chrome t={t} />
      <div style={{ opacity: fade }}>
        {k === "hook" ? <Hook b={b} t={t} /> : null}
        {k === "screen" ? <ScreenScene b={b} t={t} /> : null}
        {k === "feature" ? <FeatureScene b={b} t={t} /> : null}
        {k === "signal" ? <SignalScene b={b} t={t} /> : null}
        {k === "ahead" ? <AheadScene b={b} t={t} /> : null}
        {k === "cta" ? <CtaScene b={b} t={t} /> : null}
        {k === "chart" ? <ChartScene b={b} t={t} /> : null}
      </div>
      <Subs t={t} />
      <div style={{ position: "absolute", left: 60, right: 60, top: 1622, textAlign: "center", color: CREAM, opacity: 0.6, fontFamily: SANS, fontSize: 21, fontWeight: 500, lineHeight: 1.3 }}>
        {DATA.slot === "evening" && DATA.mode !== "spotlight" ? "Selected signals from the dashboard, shown for education. " : ""}Information & education only — not investment advice.
      </div>
      <TelegramBar />
    </AbsoluteFill>
  );
};

export const DashShortComposition = () => (
  <Composition id="DashShort" component={DashShort} durationInFrames={Math.ceil(TOTAL * FPS)} fps={FPS} width={1080} height={1920} />
);
