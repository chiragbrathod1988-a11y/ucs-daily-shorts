# Daily AI Dashboard videos — runbook (morning + evening)

Fully automatic; never ask Chirag to approve. He is **not** a SEBI-registered RA — never say so. Content is
information/education only. Never speak or write profit / ₹ amounts. Hindi voice (hi-IN-SwaraNeural), English subtitles.
`D` = today (IST, YYYY-MM-DD), `S` = `morning` or `evening`.

## 0. Should it run?
- Weekend or NSE trading holiday (web-search this year's NSE holiday list) → stop silently.
- `posted/dash/D-S.json` exists with both platforms → stop silently (if one platform is missing, do only that one in step 5).

## 1. Setup
```
git clone https://github.com/chiragbrathod1988-a11y/ucs-daily-shorts.git && cd ucs-daily-shorts && ./setup.sh
```

## 2. Data, screenshots and voice (GitHub Actions, workflow dash.yml)
The sandbox cannot reach the dashboard or the TTS service, so Actions does it:
```
mkdir -p dash/requests && echo '{"date":"D","slot":"S"}' > dash/requests/D-S.json
git add dash/requests/D-S.json && git commit -m "Dash request D S" && git push origin HEAD:main
```
Then `git pull` every ~20 s (up to 12 min) until `dash/logs/D-S.txt` ends with `OK D:S` or `FAILED D:S`.
- `FAILED` and the log mentions the token (401 / not set) → send Chirag ONE message: "Dashboard video skipped: the
  dashboard login key (GitHub secret UCS_DASH_TOKEN) has expired — please copy a fresh one (F12 → Console →
  copy(localStorage.pt_token)) into GitHub → Settings → Secrets → Actions → UCS_DASH_TOKEN." Stop.
- Other `FAILED` → delete `dash/D/S-tts` if present, re-push the request once (change a field like `"try":2`); fails again → Failure.
- Read `dash/D/S-transcript.txt`: the stock / sector names and numbers should be recognisable (speech-to-text is rough on English words).
- Read `dash/D/S-shots.json`: screenshots marked `missing` fall back to branded cards — acceptable, but note it in the status message.
- Evening `mode` (in `dash/D/evening-plan.json`) is `spotlight` when fewer than 2 real target hits exist — that is correct behaviour; never invent winners.

## 3. Build and check
```
./make_dash.sh D S        # videos/dash/D-S.mp4 + D-S-thumb.jpg + out/check-S/*.png
```
Look at every image in `out/check-S/` and the thumbnail with Read. Confirm screenshots are real dashboard screens
(no login page / error page / blank), cards readable, subtitles in English, nothing overlapping. If a screenshot shows a
login page or error, the token is bad → treat as the token failure above. Never post a broken video.

## 4. Publish files
```
git add videos/dash/D-S.mp4 videos/dash/D-S-thumb.jpg && git commit -m "Dash video D S" && git push origin HEAD:main
```
URLs: `https://raw.githubusercontent.com/chiragbrathod1988-a11y/ucs-daily-shorts/main/videos/dash/D-S.mp4` (and `-thumb.jpg`); wait until HTTP 200.

## 5. Post (use the generated text verbatim)
`python3 scripts/dash/post_text.py > out/dash-post.json`
- **YouTube Short — Metricool** `createScheduledPost`, blogId `7738599`, timezone Asia/Calcutta. date: morning → now + 5 min;
  evening → 19:00 IST today (now + 5 min if already past 18:55). info: providers `[{"network":"youtube"}]`, media `[mp4 URL]`,
  `videoThumbnailUrl` = thumb URL, autoPublish true, draft false, text = description,
  youtubeData `{"title": title, "type":"short", "privacy":"public", "madeForKids": false, "category":"EDUCATION", "tags": tags, "isAiGeneratedContent": false}`.
  If rejected with VIDEO_THUMBNAIL_NOT_APPLICABLE, send again without `videoThumbnailUrl`.
- **Instagram Reel — vidIQ**: `vidiq_video_upload` (url = mp4 URL) → `vidiq_instagram_publish_reel` with platformAccountId
  `27871127732565506`, caption = instagram_caption; follow containerId / mcpJobId continuation until PUBLISHED. Evening:
  run this at/after 19:00 IST. If vidIQ needs re-authorisation, post YouTube only and say so in the status message.

## 6. Record
Write `posted/dash/D-S.json` `{"youtube": plannerUrl|error, "instagram": permalink|error}`, commit, push. Send Chirag one
short message: "✅ AI Dashboard <morning/evening> video posted — YouTube: … | Instagram: …".
Housekeeping: keep the last 30 days of `videos/dash/` and `dash/<date>/` (git rm older).

## Failure
Data/build/post fails twice → post nothing more, send Chirag one short note of what failed. Don't loop on paid steps.
