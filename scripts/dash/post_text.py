"""Title / description / Instagram caption / tags for a dashboard video. Reads src/dashData.ts; prints JSON."""
import json, os, datetime
here = os.path.dirname(os.path.abspath(__file__))
ts = open(os.path.join(here, "..", "..", "src", "dashData.ts"), encoding="utf-8").read()
d = json.loads(ts[ts.index("{"): ts.rindex("}") + 1])
td = datetime.date.fromisoformat(d["date"]); dm = td.strftime("%-d %b")
m, feat = d.get("meta", {}), d["feature"]

COURSES = """🔥 Enroll in these premium trading courses:

💥 Intraday Options Mastery:
https://www.upsurge.club/course/intraday-stocks-options-strategy-by-chirag-rathod?invite=CHIR-RTHD

💥 Swing Trading Mastery:
https://www.upsurge.club/course/swing-trading-in-stocks-and-futures?invite=CHIR-RTHD

💥 Advanced Swing Trading Mastery (4 Bullish + 4 Bearish Setups):
https://www.upsurge.club/course/advanced-swing-trading-in-stocks-and-futures?invite=CHIR-RTHD

💥 BTST Trading in Stocks, Options & Futures:
https://www.upsurge.club/course/btst-trading-in-stock-options-and-futures?invite=CHIR-RTHD"""
LINKS = """🤖 AI DASHBOARD — Scanners, Heat Map, Nifty Overview, Stock Research (3-day free trial):
https://app.uppercircuitstocks.com

📲 FREE Telegram Channel — daily levels & market updates:
https://t.me/uppercircuitstocksbychiragrathod"""
DIS = "⚠️ For information and education only. Not investment advice. Signals shown are selected examples from the dashboard, not recommendations; past results do not guarantee future results. Market risks apply — do your own research."

if d["slot"] == "morning":
    title = f"9:15 Se Pehle Ye Screen Dekho! 📊 Nifty + Sectors Ek Jagah | {feat} | {dm} #shorts"
    sec = f"💪 Strongest: {m['strong'][0]}  |  🩸 Weakest: {m['weak'][0]}"
    body = f"""📊 Market khulne se pehle — Nifty, Bank Nifty, VIX, breadth aur sectors, sab EK dashboard pe!

Last session: Nifty {m['nifty']['ltp']:,.0f} · Bank Nifty {m['bankNifty']['ltp']:,.0f} · VIX {m['vix']['ltp']:.2f}
Breadth: {m['breadth']['mood_label']} ({m['breadth']['advancing']:,} ▲ / {m['breadth']['declining']:,} ▼)
{sec}

⭐ Feature of the day: {feat}

👇 Comment karo — aap market se pehle kya check karte ho?"""
    tags = ["ai dashboard", "nifty today", "sector heat map", "stock market india", "market breadth", "trading tools", "nifty bank nifty", "uppercircuitstocks", "chirag rathod", feat.lower()]
    hashtags = "#nifty #stockmarketindia #trading #aidashboard #shorts"
elif d["mode"] == "spotlight":
    title = f"Ye Feature Traders Ko Aage Rakhta Hai! 🚀 {feat} | AI Dashboard #shorts"
    body = f"""🚀 AI Dashboard Spotlight: {feat}

Har din ek naya feature — dekho kaise ye aapko baaki traders se aage rakhta hai.

👇 Comment karo — kaunsa feature aapko sabse useful laga?"""
    tags = ["ai dashboard", "trading tools", "stock market india", "options trading", "uppercircuitstocks", "chirag rathod", feat.lower()]
    hashtags = "#stockmarketindia #trading #aidashboard #shorts"
else:
    picks = m.get("picks", [])
    names = ", ".join(p["name"] for p in picks)
    title = f"Aaj AI Dashboard Ne Kya Pakda? ✅ {len([p for p in picks if p['outcome']!='SL'])} Targets + 1 SL | {dm} #shorts"
    if not any(p["outcome"] == "SL" for p in picks):
        title = f"Aaj AI Dashboard Ne Kya Pakda? ✅ Signal Review | {dm} #shorts"
    body = f"""⚡ Aaj ke selected AI Dashboard signals — logic ke saath!
📌 {names}

✅ Target hit · ❌ SL hit — har signal kaam nahi karta, isliye SL zaroori hai.
🔔 Signal aate hi phone pe alert + one-tap order (Fyers / Zerodha / Dhan).

👇 Comment karo — aap kaunsa setup trade karte ho?"""
    tags = ["ai dashboard", "option signals", "intraday trap", "star setup", "stock options", "stock market india", "intraday trading", "uppercircuitstocks", "chirag rathod"]
    hashtags = "#optionstrading #intradaytrading #stockmarketindia #aidashboard #shorts"
if len(title) > 100:
    title = title.replace(" | Support & Resistance", "")[:97].rstrip() + "…"

description = f"""{body}

{LINKS}

{COURSES}

🔔 SUBSCRIBE karo & bell icon dabao — roz subah aur shaam!
UpperCircuitStocks by Chirag Rathod

{DIS}

{hashtags}"""
caption = f"""{body}
👉 Save karo & follow @uppercircuitstocks

{LINKS}

{COURSES}

{DIS}

{hashtags.replace(' #shorts', ' #uppercircuitstocks')}"""
assert len(title) <= 100 and len(description) <= 5000 and len(caption) <= 2200
print(json.dumps({"title": title, "description": description, "instagram_caption": caption, "tags": tags}, ensure_ascii=False, indent=1))
