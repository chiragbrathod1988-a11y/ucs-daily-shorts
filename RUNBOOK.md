# Daily Nifty Levels Short — runbook

Fully automatic. Chirag does not review or approve; never ask him to. He is **not** a SEBI-registered
Research Analyst: never call him one or add RA wording. All content is educational: calculated pivot
levels, never buy/sell calls, targets or guarantees.

Everything runs in IST (Asia/Kolkata). `D` = today's date (the trading day the levels are for), `YYYY-MM-DD`.

## 0. Should today run?
1. Get today's date (`current_time` tool).
2. If `posted/D.json` already exists in this repo → already done today, stop silently.
3. Web-search the NSE trading-holiday list for the current year. Weekend or NSE holiday → stop silently.

## 1. Verified data for the previous trading session
Find the previous session's Nifty 50 **open, high, low, close, point change, % change** with WebSearch
(mode "extended") + WebFetch. Sources that have worked: freepressjournal.in (gives O/H/L/C), upstox.com/news,
business-standard.com, 5paisa.com/blog/nifty-outlook (also gives the session before), moneycontrol,
economictimes, livemint, kotakneo.com/news.

Rules — all must pass, otherwise do NOT make or post a video (go to "Failure"):
- close matches in ≥ 2 independent sources (±0.1);
- high and low come from a source dated that session; prefer ≥ 2 sources;
- low ≤ open ≤ high and low ≤ close ≤ high;
- (close − change) equals the session-before close from another source (±0.5) when available.

Write `data/D.json`:
`{"tradeDate":"D","prevDate":"<previous session date>","open":..,"high":..,"low":..,"close":..,"change":..,"changePct":..}`
(change is signed: negative on a down day).

## 2. Build the video
```
./setup.sh            # first time on this machine
./make_video.sh D     # writes videos/D.mp4 and check frames in out/check/
```
Then **look at every image in `out/check/`** with the Read tool. Confirm: logo intro, previous close card with the
right close, chart with PIVOT/R1/R2/S1/S2 labels that match the levels printed by the script, captions readable,
nothing overlapping or cut off. If something is wrong, fix it (data or code) and rebuild. Never post a broken video.

## 3. Publish the file
```
git add data/D.json videos/D.mp4 && git commit -m "Nifty Short D" && git push origin HEAD:main
```
Public URL: `https://raw.githubusercontent.com/chiragbrathod1988-a11y/ucs-daily-shorts/main/videos/D.mp4`
(wait ~30 s after the push; it must return HTTP 200).

## 4. Post
Levels come from `src/dailyData.ts` (`DAILY.levels`). Use `{DD Mon YYYY}` for the trading day.

**YouTube Shorts — Metricool** (`mcp__Metricool_Social_Media_Management__createScheduledPost`)
- blogId `7738599` (brand linked to YouTube channel Upper circuit Stocks, UCvcxTPpZiYBtJ8UaxTR3VVQ), timezone Asia/Calcutta.
- date: now + 5 minutes (ISO with +05:30). info JSON:
  - providers `[{"network":"youtube"}]`, media `[<public URL>]`, autoPublish true, draft false
  - text = description (below)
  - youtubeData `{"title": "Nifty Levels Today {DD Mon YYYY} | Support & Resistance | Pivot Levels #shorts", "type":"short", "privacy":"public", "madeForKids": false, "category":"EDUCATION", "tags":["nifty levels today","nifty support and resistance","nifty prediction","nifty 50","pivot points","stock market india","intraday trading","uppercircuitstocks"], "isAiGeneratedContent": false}`
- Description:
  ```
  Aaj ke Nifty 50 levels ({DD Mon YYYY}) 📊
  Pivot {P} | R1 {R1} | R2 {R2} | S1 {S1} | S2 {S2}
  CPR zone {CPRlo}–{CPRhi}. {bias line in Hinglish: above CPR → R1 possible; below pivot → S1 possible}

  Roz subah Nifty levels ke liye subscribe karein — UpperCircuitStocks by Chirag Rathod.
  For educational purposes only. Not investment advice. Levels are calculated pivot points, not buy/sell recommendations. Market risks apply.

  #nifty #nifty50 #stockmarketindia #shorts
  ```

**Instagram Reel — vidIQ**
1. `vidiq_video_upload` with `url` = public URL (title "Nifty Short D") → hosted `videoUrl`.
2. `vidiq_instagram_publish_reel` with platformAccountId `27871127732565506` (@uppercircuitstocks), that `videoUrl`,
   and the caption below; follow its mcpJobId / containerId continuation until PUBLISHED. Do not set isAiGenerated.
   Caption:
   ```
   Aaj Nifty kya karega? 👇
   📊 Nifty 50 levels — {DD Mon YYYY}
   🔴 R2 {R2} | R1 {R1}
   🟡 Pivot {P} (CPR {CPRlo}–{CPRhi})
   🟢 S1 {S1} | S2 {S2}
   Save karo & follow @uppercircuitstocks — roz subah levels.
   Educational purpose only. Not investment advice. Market risks apply.
   #nifty50 #stockmarketindia #intradaytrading #niftylevels #uppercircuitstocks
   ```

## 5. Record and report
Write `posted/D.json` with `{"youtube": <Metricool plannerUrl or error>, "instagram": <permalink or error>}`,
commit and push. Then send Chirag one short message (SendUserMessage): "✅ Nifty Short posted — YouTube: … | Instagram: …".

## Failure
If data can't be verified, a build fails twice, or a post fails: post nothing more, and send Chirag one short message
saying what failed today (no questions, no action needed from him). Don't retry paid steps in a loop.

## Housekeeping
Keep only the last 30 videos in `videos/` (git rm older ones in the daily commit) so the repo stays small.
