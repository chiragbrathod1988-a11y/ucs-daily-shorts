// Real 5-minute candles for the plan's charts (GitHub Actions; needs UCS_DASH_TOKEN).
// Usage: node scripts/dash/charts.mjs dash/D/<slot>-plan.json  ->  dash/D/<slot>-charts.json
// symbol "NIFTYFUT" / "BANKNIFTYFUT" etc. resolves to the near-month futures contract (NIFTY26NOVFUT ...).
import fs from "fs";

const planPath = process.argv[2];
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const T = process.env.UCS_DASH_TOKEN;
const API = "https://api.uppercircuitstocks.com/api/charts/";
const MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
const istDate = (t) => new Date((t + 19800) * 1000).toISOString().slice(0, 10);

async function candles(sym) {
  const r = await fetch(API + encodeURIComponent(sym) + "?tf=5", { headers: { Authorization: "Bearer " + T } });
  const j = await r.json().catch(() => ({}));
  return j.success ? j.candles : null;
}
function futSyms(root, D) {
  const d = new Date(D + "T00:00:00Z"), out = [];
  for (let k = 0; k < 3; k++) {
    const m = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + k, 1));
    out.push(`${root}${String(m.getUTCFullYear()).slice(2)}${MON[m.getUTCMonth()]}FUT`);
  }
  return out;
}

const out = {};
for (const c of plan.charts || []) {
  try {
    const syms = c.symbol.endsWith("FUT") && !/\d/.test(c.symbol) ? futSyms(c.symbol.replace(/FUT$/, ""), plan.date) : [c.symbol];
    let got = null;
    for (const s of syms) {
      const cs = await candles(s);
      if (!cs || !cs.length) continue;
      const days = [...new Set(cs.map((x) => istDate(x.t)))].sort();
      const day = c.when === "prev" ? days.filter((x) => x < plan.date).filter((x) => cs.filter((y) => istDate(y.t) === x).length >= 40).pop()
                                    : days.includes(plan.date) ? plan.date : null;
      if (!day) continue;
      got = { symbol: s, date: day, candles: cs.filter((x) => istDate(x.t) === day).map((x) => [x.t, x.o, x.h, x.l, x.c]) };
      break;
    }
    if (got) { out[c.key] = got; console.log("chart ok", c.key, got.symbol, got.date, got.candles.length); }
    else console.log("chart miss", c.key, c.symbol);
  } catch (e) { console.log("chart error", c.key, String(e).slice(0, 120)); }
}
fs.writeFileSync(planPath.replace("-plan.json", "-charts.json"), JSON.stringify(out));
