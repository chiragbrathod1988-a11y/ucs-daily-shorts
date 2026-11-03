// High-res scroll recordings of AI Dashboard feature pages for the UGC explainer (GitHub Actions; needs UCS_DASH_TOKEN).
// Usage: node rec.mjs ugc/pages.json ugc/out   -> ugc/out/<name>.mp4 (1440x2560, 30 fps) + <name>.jpg (first frame)
import fs from "fs";
import path from "path";
import { execFileSync } from "child_process";
import { chromium } from "playwright";
const [cfgPath, outDir] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
fs.mkdirSync(outDir, { recursive: true });
const T = process.env.UCS_DASH_TOKEN;
const VW = 412, VH = 732, DSF = 1440 / 412;
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: VW, height: VH }, deviceScaleFactor: DSF, isMobile: true, hasTouch: true,
  userAgent: "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36" });
await ctx.addInitScript((tok) => { try { localStorage.setItem("pt_token", tok); localStorage.setItem("push_asked", "1"); } catch (e) {} }, T);
const page = await ctx.newPage();
const log = {};
for (const p of cfg.pages) {
  const tmp = fs.mkdtempSync("/tmp/rec-");
  try {
    await page.goto(cfg.base + p.url, { waitUntil: "networkidle", timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(p.wait ?? 7000);
    await page.addStyleTag({ content: "[class*=telegram i],[class*=tg-float i],.uc-help,#uc-help,[class*=toast i]{display:none!important} html{scroll-behavior:auto!important} ::-webkit-scrollbar{display:none}" }).catch(() => {});
    if (p.click) { await page.getByText(p.click, { exact: false }).first().click({ timeout: 5000 }).catch(() => {}); await page.waitForTimeout(3000); }
    const maxY = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
    const y0 = p.from ?? 0, y1 = Math.max(y0, Math.min(p.to ?? 900, maxY));
    const N = Math.round((p.secs ?? 4.5) * 30);
    for (let i = 0; i < N; i++) {
      const k = i / (N - 1), e = k < 0.12 ? 0 : k > 0.88 ? 1 : (1 - Math.cos(Math.PI * (k - 0.12) / 0.76)) / 2;
      await page.evaluate((y) => window.scrollTo(0, y), Math.round(y0 + (y1 - y0) * e));
      await page.screenshot({ path: path.join(tmp, String(i).padStart(4, "0") + ".jpg"), type: "jpeg", quality: 92 });
    }
    execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", "30", "-i", path.join(tmp, "%04d.jpg"), "-vf", "scale=1440:2560:force_original_aspect_ratio=decrease,pad=1440:2560:(ow-iw)/2:0:color=0x050505",
      "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p", path.join(outDir, p.name + ".mp4")]);
    fs.copyFileSync(path.join(tmp, "0000.jpg"), path.join(outDir, p.name + ".jpg"));
    log[p.name] = { ok: true, maxY, y0, y1 };
    console.log("ok", p.name, y0, y1);
  } catch (e) { log[p.name] = { ok: false, err: String(e).slice(0, 200) }; console.log("miss", p.name, String(e).slice(0, 200)); }
  fs.rmSync(tmp, { recursive: true, force: true });
}
fs.writeFileSync(path.join(outDir, "log.json"), JSON.stringify(log, null, 1));
await browser.close();
