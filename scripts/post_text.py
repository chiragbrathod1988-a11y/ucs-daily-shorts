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

# Title: a question built from today's real levels (hook), date, keywords. YouTube max 100 chars.
if bear_first:
    hook = f"Nifty {f(L['S1'])} Todega ya {f(L['R1'])} Wapas? 🔥"
else:
    hook = f"Nifty {f(L['R1'])} Todega ya {f(L['S1'])} Aayega? 🔥"
title = f"{hook} Nifty Levels {day_mon} | Support & Resistance #shorts"
if len(title) > 100:
    title = f"{hook} Nifty Levels {day_mon} #shorts"

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

🤖 AI DASHBOARD — live signals & 1-click trade:
https://app.uppercircuitstocks.com"""

DISCLAIMER = ("⚠️ For educational purposes only. Not investment advice. Levels are calculated pivot points, "
              "not buy/sell recommendations. Market risks apply — do your own research.")

body = f"""🔥 Aaj Nifty kya karega? Market khulne se pehle ye levels SAVE kar lo! 📌

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

#nifty #nifty50 #niftylevels #stockmarketindia #intradaytrading #shorts"""

instagram_caption = f"""{body}
👉 Save karo & follow @uppercircuitstocks — roz subah levels!

{LINKS}

{COURSES}

{DISCLAIMER}

#nifty50 #stockmarketindia #intradaytrading #niftylevels #uppercircuitstocks"""

tags = ["nifty levels today", "nifty support and resistance", "nifty prediction", "nifty 50", "nifty analysis",
        "pivot points", "cpr", "stock market india", "intraday trading", "uppercircuitstocks", "chirag rathod"]

assert len(title) <= 100, len(title)
assert len(description) <= 5000, len(description)
assert len(instagram_caption) <= 2200, len(instagram_caption)
print(json.dumps({"title": title, "description": description, "instagram_caption": instagram_caption, "tags": tags},
                 ensure_ascii=False, indent=1))
