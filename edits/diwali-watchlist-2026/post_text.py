import json, os, sys
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(here, "..", "..", "scripts"))
from channel_links import CHANNEL_BLOCK
title = "Diwali Breakout Stocks 2026 🪔 ICICI Bank & Kotak Bank"
body = """Diwali breakout stocks 2026 — ICICI Bank and Kotak Mahindra Bank monthly chart breakout + fundamentals.
🪔 Diwali Breakout Watchlist — 2 bade Bank stocks ne monthly chart pe lamba consolidation tod diya!

📊 ICICI BANK (Monthly chart)
Range: 1,195 – 1,505 → breakout above 1,505, now ~1,576 (+12.7% this month)
Chart projection zone: 2,358
Q2 FY27: Net profit ₹14,843 Cr (+20% YoY) • NIM 4.18% • Net NPA 0.30% • Loans +30% YoY
Holding (Sep-26): Mutual funds ~29.4% • FII stake increased vs Jun-26

📊 KOTAK MAHINDRA BANK (Monthly chart)
Range: 317 – 450 → breakout above 450, now ~480
Chart projection zone: 699
Q2 FY27: Net profit ₹4,212 Cr (+29% YoY) • NIM 4.31% • Net NPA 0.24% • CAR 21.9%
Holding (Sep-26): DII 38.5% (up from 37.7%) • Promoter 25.9%

⚠️ Breakout tabhi strong jab price breakout level ke upar tike.

👇 Comment karo — aapki Diwali watchlist mein kaunsa stock hai?"""
DIS = ("⚠️ Educational chart study only — not a buy/sell recommendation or investment advice. Projection zones are chart-pattern "
       "levels, not targets or guarantees. Chirag Rathod is not a SEBI-registered research analyst. Data: company Q2 FY27 results, "
       "Sep-2026 shareholding (Trendlyne/Upstox). Market risks apply — do your own research.")
description = f"""{body}

{CHANNEL_BLOCK}

🔔 SUBSCRIBE karo & bell icon dabao!
UpperCircuitStocks by Chirag Rathod
Happy Diwali 🪔

{DIS}

#diwali #stockmarket #icicibank"""
DIS_IG = "⚠️ Educational chart study only — not investment advice or a buy/sell call. Projection zones are not targets. Chirag Rathod is not SEBI-registered. Do your own research."
caption = f"""{body}
👉 Save karo & follow @uppercircuitstocks

{CHANNEL_BLOCK}

{DIS_IG}

#diwali2026 #icicibank #kotakbank #stockmarketindia #uppercircuitstocks"""
tags = ["diwali stocks 2026", "diwali breakout stocks", "muhurat trading 2026", "icici bank share", "kotak bank share",
        "icici bank breakout", "kotak mahindra bank", "bank stocks", "breakout stocks", "monthly chart breakout",
        "banking stocks india", "icici bank q2 results", "kotak bank q2 results", "stock market", "share market",
        "technical analysis", "stock market india", "uppercircuitstocks", "chirag rathod"]
assert len(title) <= 60 and len(description) <= 5000 and len(caption) <= 2200, (len(title), len(description), len(caption))
assert CHANNEL_BLOCK in description and CHANNEL_BLOCK in caption
print(json.dumps({"title": title, "description": description, "instagram_caption": caption, "tags": tags}, ensure_ascii=False, indent=1))
