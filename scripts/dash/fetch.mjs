// Fetch the day's AI Dashboard data (GitHub Actions; needs secret UCS_DASH_TOKEN).
// Usage: node scripts/dash/fetch.mjs YYYY-MM-DD morning|evening   ->  dash/D/<slot>-raw.json
import fs from "fs";

const [D, slot] = process.argv.slice(2);
const T = process.env.UCS_DASH_TOKEN;
if (!T) throw new Error("UCS_DASH_TOKEN secret is missing");
const API = "https://api.uppercircuitstocks.com/api/";
const get = async (p) => {
  for (let i = 0; i < 3; i++) {
    const r = await fetch(API + p, { headers: { Authorization: "Bearer " + T } });
    if (r.status === 401) throw new Error("Dashboard token rejected (401) — renew UCS_DASH_TOKEN");
    if (r.ok) return r.json();
    await new Promise((s) => setTimeout(s, 3000));
  }
  throw new Error("API failed: " + p);
};

const raw = { date: D, slot, tradeDate: D };
if (slot === "morning") {
  raw.snapshot = await get("research/snapshot");
  raw.market = await get("research/market");
  raw.sectors = await get("heatmap/sectors");
} else {
  raw.options = await get("research/options-signals");
  raw.trap = await get("research/trap-algo");
  raw.index = await get("research/index-signals");
  const tick = new Set([
    ...(raw.options.signals || []).map((s) => s.underlying),
    ...Object.values(raw.trap.algos || {}).flatMap((a) => (a.closed || []).map((s) => s.underlying)),
  ]);
  raw.names = {};
  for (const t of tick) {
    try {
      const j = await get("research/search?q=" + encodeURIComponent(t));
      const hit = (j.results || []).find((r) => r.symbol === t);
      if (hit) raw.names[t] = hit.long_name;
    } catch (e) { /* name is optional */ }
  }
}
fs.mkdirSync(`dash/${D}`, { recursive: true });
fs.writeFileSync(`dash/${D}/${slot}-raw.json`, JSON.stringify(raw));
console.log("saved", `dash/${D}/${slot}-raw.json`);
