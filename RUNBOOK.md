# Daily Nifty Levels Short — runbook

Fully automatic. Chirag does not review or approve; never ask him to. He is **not** a SEBI-registered
Research Analyst: never call him one or add RA wording. All content is educational: calculated pivot
levels, never buy/sell calls, targets or guarantees.

Everything runs in IST (Asia/Kolkata). `D` = today's date (the trading day the levels are for), `YYYY-MM-DD`.

## 0. Should today run?
1. Get today's date (`current_time` tool).
2. If `posted/D.json` already exists and lists both a YouTube and an Instagram result → already done today, stop
   silently. If it lists only one, do just the missing platform in step 4.
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
If `data/D.json` and `videos/D.mp4` already exist in the repo (built ahead of time), skip steps 1–3 and go to 4.

**Voice (Microsoft neural TTS, hi-IN-SwaraNeural — clear adult AI voice).** The sandbox cannot reach the TTS
service, so the voice is made by GitHub Actions (`.github/workflows/tts.yml`):
1. `git add data/D.json && git commit -m "Data D" && git push origin HEAD:main` — this push triggers the workflow
   (or trigger it with `actions_run_trigger`, workflow `tts.yml`, inputs `{"date":"D"}`).
2. Wait (git fetch every ~15 s, up to ~6 min) until `tts/D/manifest.json` is on origin/main, then `git pull`.
3. Read `tts/D/transcript.txt` (speech-to-text of the voice): every level number should be heard correctly
   (speech-to-text is imperfect on English words; numbers are what matter). If the workflow failed, re-trigger once;
   if it fails again → Failure. Never fall back to another voice.
```
./setup.sh            # first time on this machine
./make_video.sh D     # writes videos/D.mp4 and check frames in out/check/ (fails if tts/D does not match the script)
```
Then **look at every image in `out/check/`** with the Read tool. Confirm: logo intro, previous close card with the
right close, chart with PIVOT/R1/R2/S1/S2 labels that match the levels printed by the script, captions readable,
nothing overlapping or cut off. If something is wrong, fix it (data or code) and rebuild. Never post a broken video.

## 3. Publish the file
```
git add data/D.json videos/D.mp4 tts/D && git commit -m "Nifty Short D" && git push origin HEAD:main
```
Public URL: `https://raw.githubusercontent.com/chiragbrathod1988-a11y/ucs-daily-shorts/main/videos/D.mp4`
(wait ~30 s after the push; it must return HTTP 200).

## 4. Post
Generate the exact post text — never write it by hand:
```
python3 scripts/post_text.py > out/post.json   # title, description, instagram_caption, tags
```
`post.json` already contains everything Chirag requires: the engaging hook title built from today's levels, the
levels, Telegram channel link, AI Dashboard link, the four Upsurge course links (exact text), subscribe CTA,
disclaimer and hashtags. Use its fields verbatim. (If `src/dailyData.ts` is not today's, run `./make_video.sh D` first.)

**YouTube Shorts — Metricool** (`mcp__Metricool_Social_Media_Management__createScheduledPost`)
- blogId `7738599` (brand linked to YouTube channel Upper circuit Stocks, UCvcxTPpZiYBtJ8UaxTR3VVQ), timezone Asia/Calcutta.
- date: now + 5 minutes (ISO with +05:30). info JSON:
  - providers `[{"network":"youtube"}]`, media `[<public URL>]`, autoPublish true, draft false
  - text = `post.json.description`
  - youtubeData `{"title": post.json.title, "type":"short", "privacy":"public", "madeForKids": false, "category":"EDUCATION", "tags": post.json.tags, "isAiGeneratedContent": false}`

**Instagram Reel — vidIQ**
1. `vidiq_video_upload` with `url` = public URL (title "Nifty Short D") → hosted `videoUrl`.
2. `vidiq_instagram_publish_reel` with platformAccountId `27871127732565506` (@uppercircuitstocks), that `videoUrl`,
   and caption = `post.json.instagram_caption`; follow its mcpJobId / containerId continuation until PUBLISHED.
   Do not set isAiGenerated.

## 5. Record and report
Write `posted/D.json` with `{"youtube": <Metricool plannerUrl or error>, "instagram": <permalink or error>}`,
commit and push. Then send Chirag one short message (SendUserMessage): "✅ Nifty Short posted — YouTube: … | Instagram: …".

## Failure
If data can't be verified, a build fails twice, or a post fails: post nothing more, and send Chirag one short message
saying what failed today (no questions, no action needed from him). Don't retry paid steps in a loop.

## Housekeeping
Keep only the last 30 videos in `videos/` and voice folders in `tts/` (git rm older ones in the daily commit) so the repo stays small.
