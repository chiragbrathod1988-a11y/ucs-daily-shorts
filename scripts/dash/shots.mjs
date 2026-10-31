// Real dashboard screenshots for the plan (GitHub Actions; needs UCS_DASH_TOKEN).
// Usage: node scripts/dash/shots.mjs dash/D/<slot>-plan.json  ->  dash/D/<slot>-<name>.png (1080 px wide, phone layout)
import fs from "fs";
import path from "path";
import { chromium } from "playwright";

const planPath = process.argv[2];
const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
const dir = path.dirname(planPath);
const T = process.env.UCS_DASH_TOKEN;

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 }, deviceScaleFactor: 1080 / 390, isMobile: true, hasTouch: true,
  userAgent: "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36",
});
await ctx.addInitScript((tok) => {
  try { localStorage.setItem("pt_token", tok); localStorage.setItem("push_asked", "1"); } catch (e) {}
}, T);
const page = await ctx.newPage();
const results = {};
const cache = {};

async function open(url) {
  if (page.url() === url) return;
  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(6000);
  // hide floating widgets that cover content
  await page.addStyleTag({ content: "[class*=telegram i],[class*=tg-float i],.uc-help,#uc-help{display:none!important}" }).catch(() => {});
}

for (const s of plan.shots) {
  const out = path.join(dir, `${plan.slot}-${s.name}.png`);
  try {
    await open(s.url);
    if (s.kind === "page") {
      const h = await page.evaluate(() => document.documentElement.scrollHeight);
      await page.screenshot({ path: out, fullPage: true, clip: { x: 0, y: 0, width: 390, height: Math.min(h, 4200) } });
      results[s.name] = "page";
    } else {
      // smallest element whose text contains every match string (a signal card / panel)
      const handle = await page.evaluateHandle((m) => {
        const els = [...document.querySelectorAll("div,article,section,li")].filter((e) => {
          const t = e.innerText || ""; const r = e.getBoundingClientRect();
          return r.width > 200 && r.height > 80 && m.every((x) => t.includes(x));
        });
        els.sort((a, b) => a.innerText.length - b.innerText.length);
        return els[0] || null;
      }, s.match);
      const el = handle.asElement();
      if (!el) throw new Error("not found: " + s.match.join(" + "));
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(800);
      await el.screenshot({ path: out });
      results[s.name] = "card";
    }
    console.log("ok", s.name);
  } catch (e) {
    console.log("miss", s.name, String(e).slice(0, 160));
    results[s.name] = "missing";
  }
}
fs.writeFileSync(path.join(dir, `${plan.slot}-shots.json`), JSON.stringify(results, null, 1));
await browser.close();
