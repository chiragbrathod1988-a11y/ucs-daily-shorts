# Daily AI Dashboard videos — runbook (morning + evening)

> Titles/descriptions/hashtags follow GROWTH.md (short keyword-first titles, exactly 3 hashtags, 15–20 tags).

Fully automatic; never ask Chirag to approve. He is **not** a SEBI-registered RA — never say so. Content is
information/education only. Never speak or write profit / ₹ amounts. Voice: ElevenLabs **Matilda** via vidIQ (Chirag's choice — openly an AI voice), Hindi/Hinglish script, English subtitles.
`D` = today (IST, YYYY-MM-DD), `S` = `morning`, `evening` or `eveningyt`.

**YouTube rule (Chirag): YouTube must never show individual signals, entries, targets, SL, exits or results.**
- Morning run: one video (`S=morning`, features are signal-free) → YouTube + Instagram.
- Evening run: TWO videos. `S=eveningyt` (feature spotlight, no signals) → **YouTube only**.
  `S=evening` (selected signals with charts) → **Instagram only**. Never post the `evening` video to YouTube.
  Run steps 2–4 for both (two requests can go in one push; voice = one Matilda call each).

## 0. Should it run?
- Weekend or NSE trading holiday (web-search this year's NSE holiday list) → stop silently.
- `posted/dash/D-S.json` exists with every platform that slot posts to (morning: both; evening: instagram; eveningyt: youtube) → skip that slot.

## 1. Setup
```
git clone https://github.com/chiragbrathod1988-a11y/ucs-daily-shorts.git && cd ucs-daily-shorts && ./setup.sh
```

## 2. Data, screenshots and charts (GitHub Actions, workflow dash.yml)
The sandbox cannot reach the dashboard, so Actions does it:
```
mkdir -p dash/requests && echo '{"date":"D","slot":"S"}' > dash/requests/D-S.json
git add dash/requests/D-S.json && git commit -m "Dash request D S" && git push origin HEAD:main
```
Then `git pull` every ~20 s (up to 12 min) until `dash/logs/D-S.txt` ends with `OK D:S` or `FAILED D:S`.
- `FAILED` and the log mentions the token (401 / not set) → send Chirag ONE message: "Dashboard video skipped: the
  dashboard login key (GitHub secret UCS_DASH_TOKEN) has expired — please copy a fresh one (F12 → Console →
  copy(localStorage.pt_token)) into GitHub → Settings → Secrets → Actions → UCS_DASH_TOKEN." Stop.
- Other `FAILED` → delete `dash/D/S-plan.json` if present, re-push the request once (change a field like `"try":2`); fails again → Failure.
- Read `dash/D/S-shots.json` (screenshots marked `missing` fall back to branded cards) and `dash/D/S-charts.json` (real 5-min candles).
- Evening `mode` (in `dash/D/evening-plan.json`) is `spotlight` when fewer than 2 real target hits exist — correct; never invent winners.

## 2b. Voice — Matilda (vidIQ / ElevenLabs), one call per video
1. Script = the `text` of every line in `dash/D/S-plan.json` in order, joined with a newline (do not edit the text).
2. `vidiq_voiceover_generate` with voiceId `XrExE9yKIg1WjnnlVkGX` (Matilda) and that script; poll `vidiq_job_poll` until completed → `audioUrl`.
3. The sandbox cannot download it and the signed URL must never be committed in plain text. Encrypt it and let Actions fetch it:
```
python3 - <<'PY'
import json, subprocess
blob = json.loads(subprocess.check_output(["python3", "scripts/dash/seal.py", AUDIO_URL]))   # AUDIO_URL = the audioUrl string
json.dump([{"sealed": blob, "path": "dash/D/S-voice.mp3"}], open("fetch/D-S-voice.json", "w"))
PY
git add fetch/D-S-voice.json && git commit -m "Voice D S" && git push origin HEAD:main
```
4. `git pull` every ~15 s (up to 6 min) until `dash/D/S-voice.mp3` exists (log: `fetch/done/D-S-voice.log`). If it fails twice → Failure
   (if the log says UCS_FETCH_KEY is missing, tell Chirag that secret needs adding).

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
- **YouTube Short — Metricool** (morning video, or the `eveningyt` video in the evening — never `evening`) `createScheduledPost`, blogId `7738599`, timezone Asia/Calcutta. date: morning → now + 5 min;
  evening → 19:00 IST today (now + 5 min if already past 18:55). info: providers `[{"network":"youtube"}]`, media `[mp4 URL]`,
  `videoThumbnailUrl` = thumb URL, autoPublish true, draft false, text = description,
  youtubeData `{"title": title, "type":"short", "privacy":"public", "madeForKids": false, "category":"EDUCATION", "tags": tags, "isAiGeneratedContent": false}`.
  If rejected with VIDEO_THUMBNAIL_NOT_APPLICABLE, send again without `videoThumbnailUrl`.
- **Instagram Reel — vidIQ** (morning video, or the `evening` signals video in the evening): `vidiq_video_upload` (url = mp4 URL) → `vidiq_instagram_publish_reel` with platformAccountId
  `27871127732565506`, caption = instagram_caption; follow containerId / mcpJobId continuation until PUBLISHED. Evening:
  run this at/after 19:00 IST. If vidIQ needs re-authorisation, post YouTube only and say so in the status message.

## 6. Record
Write `posted/dash/D-S.json` `{"youtube": plannerUrl|error, "instagram": permalink|error}`, commit, push. Send Chirag one
short message: "✅ AI Dashboard <morning/evening> video posted — YouTube: … | Instagram: …".
Housekeeping: keep the last 30 days of `videos/dash/` and `dash/<date>/` (git rm older).

## Failure
Data/build/post fails twice → post nothing more, send Chirag one short note of what failed. Don't loop on paid steps.
