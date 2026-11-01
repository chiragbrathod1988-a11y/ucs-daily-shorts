"""Generate the YouTube title/description and Instagram caption for a day's Short.

Usage: python3 scripts/post_text.py            (reads src/dailyData.ts, prints JSON)
Output JSON: {"title": ..., "description": ..., "instagram_caption": ..., "tags": [...]}
"""
import json, datetime, os

here = os.path.dirname(os.path.abspath(__file__))
ts = open(os.path.join(here, "..", "src", "dailyData.ts"), encoding="utf-8").read()
d = json.loads(ts[ts.index("{"): ts.rindex("}") + 1])
L = d["levels"]
f = lambda n: f"{int(round(n)):,}"
td = datetime.date.fromisoformat(d["date"])
day_mon = td.strftime("%-d %b")
full = td.strftime("%-d %b %Y")
weekday = td.strftime("%A")
up = d["up"]
bear_first = d["bearFirst"]

# Title (GROWTH.md): short, searched keyword first, one curiosity hook, one emoji, no hashtag clutter (<= 60 chars).
a, b = (L['S1'], L['R1']) if bear_first else (L['R1'], L['S1'])
title = f"Nifty Prediction {day_mon} 🔥 {f(a)} Todega ya {f(b)}?"

move = f"{'+' if up else '−'}{abs(L['change']):,.2f} ({'+' if up else '−'}{abs(L['changePct'])}%)"
bull = f"📈 Bullish: {f(L['CPRhi'])} ke upar tike → {f(L['R1'])} test ho sakta hai"
bear = f"📉 Bearish: {f(L['P'])} ke neeche gaya → {f(L['S1'])} tak dabaav"
if bear_first:
    bear = f"📉 Bearish: {f(L['P'])} ke neeche raha → {f(L['S1'])} test ho sakta hai"
    bull = f"📈 Bullish: {f(L['CPRhi'])} ke upar nikla → {f(L['R1'])} tak recovery"
scen = [bear, bull] if bear_first else [bull, bear]

COURSES = """🔥 Enroll in these premium trading courses:

💥 Intraday Options Mastery:
https://www.upsurge.club/course/intraday-stocks-options-strategy-by-chirag-rathod?invite=CHIR-RTHD

💥 Swing Trading Mastery:
https://www.upsurge.club/course/swing-trading-in-stocks-and-futures?invite=CHIR-RTHD

💥 Advanced Swing Trading Mastery (4 Bullish + 4 Bearish Setups):
https://www.upsurge.club/course/advanced-swing-trading-in-stocks-and-futures?invite=CHIR-RTHD

💥 BTST Trading in Stocks, Options & Futures:
https://www.upsurge.club/course/btst-trading-in-stock-options-and-futures?invite=CHIR-RTHD"""

LINKS = """📲 FREE Telegram Channel — daily levels & market updates:
https://t.me/uppercircuitstocksbychiragrathod

🤖 AI DASHBOARD — Stock Screeners, Heat Map, Nifty Overview & detailed Stock Research:
https://app.uppercircuitstocks.com"""

DISCLAIMER = ("⚠️ For educational purposes only. Not investment advice. Levels are calculated pivot points, "
              "not buy/sell recommendations. Market risks apply — do your own research.")

body = f"""Nifty prediction for today — support & resistance levels {full}.
🔥 Aaj Nifty kya karega? Market khulne se pehle ye levels SAVE kar lo! 📌

📊 NIFTY 50 LEVELS — {full} ({weekday})
Previous close: {L['close']:,.2f} {move}

🔴 R2: {f(L['R2'])}
🔴 R1: {f(L['R1'])}
🟡 Pivot: {f(L['P'])}  |  CPR: {f(L['CPRlo'])} – {f(L['CPRhi'])}
🟢 S1: {f(L['S1'])}
🟢 S2: {f(L['S2'])}

{scen[0]}
{scen[1]}

👇 Comment karo — aaj Nifty UPAR jayega ya NEECHE?"""

description = f"""{body}

{LINKS}

{COURSES}

🔔 Roz subah Nifty levels — SUBSCRIBE karo & bell icon dabao!
UpperCircuitStocks by Chirag Rathod

{DISCLAIMER}

#nifty #niftyprediction #stockmarket"""

instagram_caption = f"""{body}
👉 Save karo & follow @uppercircuitstocks — roz subah levels!

{LINKS}

{COURSES}

{DISCLAIMER}

#nifty50 #stockmarketindia #intradaytrading #niftylevels #uppercircuitstocks"""

tags = ["nifty prediction", "nifty prediction for tomorrow", "nifty levels today", "nifty support and resistance",
        "nifty 50", "nifty analysis", "nifty kal kya karega", "nifty tomorrow", "stock market", "share market",
        "intraday trading", "trading for beginners", "pivot points", "cpr trading", "stock market india",
        "uppercircuitstocks", "chirag rathod"]

assert len(title) <= 60, len(title)
assert len(description) <= 5000, len(description)
assert len(instagram_caption) <= 2200, len(instagram_caption)
print(json.dumps({"title": title, "description": description, "instagram_caption": instagram_caption, "tags": tags},
                 ensure_ascii=False, indent=1))
