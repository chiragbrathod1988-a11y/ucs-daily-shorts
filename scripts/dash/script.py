"""Build the voice script + scene plan for the daily AI Dashboard videos from real dashboard data.

Usage: python3 scripts/dash/script.py dash/D/<slot>-raw.json  ->  writes dash/D/<slot>-plan.json
slot = morning (market overview + feature of the day) | evening (today's selected signals).

Rules (Chirag): Hindi voice, English subtitles. Never speak about profit / rupees. Evening shows 2-3 signals that
reached target plus 1 that hit SL (labelled "selected signals"); if fewer than 2 real target hits exist, the evening
video becomes a feature spotlight instead. Nothing is invented: every number comes from the raw dashboard data.
"""
import json, os, sys, datetime, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from english_num import words as ew  # spoken English numbers in Devanagari (verified clear with the Hindi voice)

raw_path = sys.argv[1]
raw = json.load(open(raw_path))
D, slot = raw["date"], raw["slot"]
out_path = raw_path.replace("-raw.json", "-plan.json")
td = datetime.date.fromisoformat(D)
APP = "https://app.uppercircuitstocks.com"
fmt = lambda n: f"{int(round(float(n))):,}"
pct = lambda x: f"{float(x):+.2f}%"

# ---------------------------------------------------------------- features (one a day, rotating)
FEATURES = [
    dict(key="star", name="Star Setup", url="/research.html?page=star",
         hi=["Star Setup, stock options के लिए live scanner है।", "Entry, stop loss और दोनों targets, signal के साथ ही card पे दिखते हैं।"],
         en=["Star Setup — a live scanner for stock options.", "Entry, SL and both targets show on the card instantly."]),
    dict(key="trap", name="Intraday Trap", url="/research.html?page=trap",
         hi=["Intraday Trap scanner, fake breakout और fake breakdown पकड़ता है।", "जहाँ बाकी traders फँसते हैं, वहाँ से reversal का setup मिलता है।"],
         en=["Intraday Trap catches fake breakouts and breakdowns.", "Where others get trapped, you see the reversal setup."]),
    dict(key="heatmap", name="Sector Heat Map", url="/research.html?p=heatmap",
         hi=["Heat Map में एक नज़र में दिखता है, कौन सा sector strong है और कौन सा weak।", "Sector rotation, बाकी traders से पहले पकड़ो।"],
         en=["Heat Map: strong and weak sectors at a glance.", "Spot sector rotation before others do."]),
    dict(key="ohl", name="Open High / Low", url="/research.html?page=ohl",
         hi=["Open High Low screen, सुबह नौ बीस से दस बजे तक चलता है।", "Open equals high या open equals low वाले stocks, अपने आप list हो जाते हैं।"],
         en=["Open High/Low screen runs 9:20 to 10:00 AM.", "Open = High / Open = Low stocks, listed automatically."]),
    dict(key="idx", name="Index Options", url="/research.html?page=idx",
         hi=["Index Options में Nifty और Bank Nifty के setups, trigger level के साथ मिलते हैं।", "Signal armed होते ही, आपको पता होता है कहाँ entry और कहाँ SL।"],
         en=["Index Options: NIFTY & BANKNIFTY setups with trigger levels.", "Know the entry and SL the moment it's armed."]),
    dict(key="report", name="AI Stock Reports", url="/equity-report.html",
         hi=["AI Stock Report में, किसी भी NSE stock के fundamentals, technicals, shareholding और peers, एक ही page पे।", "AI सब कुछ आसान भाषा में summarise करता है।"],
         en=["AI Stock Reports: fundamentals, technicals, shareholding & peers.", "Summarised by AI in plain language."]),
    dict(key="cas", name="CAS Expiry", url="/research.html?page=cas",
         hi=["Expiry के दिन, CAS Expiry बताता है किस strike में premium तेज़ी से भाग सकता है।", "Spot driven move है या gamma spike, ये भी दिखता है।"],
         en=["CAS Expiry: strikes where premium can ignite on expiry day.", "Shows spot-driven move vs gamma spike."]),
    dict(key="btst", name="BTST / STBT", url="/research.html?page=btst",
         hi=["BTST और STBT screen, overnight setups देता है।", "अगली सुबह, हर setup का result भी track होता है।"],
         en=["BTST/STBT: overnight setups.", "Every setup is tracked the next morning."]),
    dict(key="oi", name="OI Spikes", url="/oi-spikes.html",
         hi=["OI Spikes, index और stock options में अचानक बढ़ा open interest दिखाता है।", "बड़े players कहाँ position बना रहे हैं, live पता चलता है।"],
         en=["OI Spikes: sudden open-interest jumps in options.", "See where big players are building positions — live."]),
    dict(key="optan", name="Options Analytics", url="/options-analytics.html",
         hi=["Options Analytics में option chain, OI build up और PCR, सब एक screen पे।", "Support और resistance, option data से समझो।"],
         en=["Options Analytics: option chain, OI build-up, PCR.", "Read support & resistance from option data."]),
    dict(key="futrev", name="Futures Reversal Breakout", url="/research.html?page=futrev",
         hi=["Futures Trade section में, Reversal Breakout और Momentum scanners live चलते हैं।", "Futures के setups, बिना chart खोले मिल जाते हैं।"],
         en=["Futures: Reversal Breakout & Momentum scanners, live.", "Futures setups without opening a single chart."]),
    dict(key="track", name="Track Record", url="/research.html?page=track",
         hi=["Track Record में, हर signal का result public रहता है — जीत भी, और loss भी।", "भरोसा, data से बनता है।"],
         en=["Track Record: every signal's result stays visible — wins and losses.", "Trust built on data."]),
    dict(key="algo", name="Build Your Algo", url="/research.html?p=algo",
         hi=["Algo Trade में, अपनी strategy simple English में लिखो।", "Backtest seconds में, फिर paper पे forward test।"],
         en=["Algo Trade: describe your strategy in plain English.", "Backtest in seconds, then forward-test on paper."]),
    dict(key="terminal", name="Paper Trading Terminal", url="/terminal.html",
         hi=["Terminal में, live NSE prices पे virtual capital से F and O practice करो।", "Zero risk, पर experience असली।"],
         en=["Terminal: practise F&O on live NSE prices with virtual capital.", "Zero risk, real experience."]),
    dict(key="ipo", name="IPO Centre", url="/ipo.html",
         hi=["IPO Centre में हर Mainboard और SME IPO, GMP trend और subscription के साथ।", "RHP financials और AI view भी।"],
         en=["IPO Centre: every Mainboard & SME IPO with GMP & subscription.", "Plus RHP financials and an AI view."]),
    dict(key="mf", name="Mutual Funds", url="/mf.html",
         hi=["Mutual Funds section में, सत्रह सौ से ज़्यादा schemes का data।", "Returns, risk, holdings, और SIP calculator।"],
         en=["Mutual Funds: 1,700+ schemes.", "Returns, risk, holdings and a SIP calculator."]),
    dict(key="commod", name="Commodities Scanner", url="/commodities.html",
         hi=["Commodities scanner में MCX crude, gold, silver और natural gas के setups।", "Hourly volume spurt भी तुरंत दिखता है।"],
         en=["Commodities scanner: MCX crude, gold, silver, natural gas.", "Hourly volume spurts flagged instantly."]),
    dict(key="journal", name="Trade Journal", url="/journal.html",
         hi=["Trade Journal में हर trade का mood, setup और rating लिखो।", "अपनी गलतियाँ, data में दिखने लगती हैं।"],
         en=["Trade Journal: log mood, setup and rating for every trade.", "Your mistakes become visible in the data."]),
]
day_no = (td - datetime.date(2026, 11, 2)).days
feature = FEATURES[(day_no if slot == "morning" else day_no + 7) % len(FEATURES)]

lines, scenes, shots = [], [], []
def say(tag, hi, en, scene=None):
    lines.append({"tag": tag, "text": hi, "en": en})
    if scene is not None:
        scene = dict(scene); scene["tags"] = scene.get("tags", []) + [tag]
        scenes.append(scene)
def shot(name, url, kind="page", match=None, clip=None):
    shots.append({"name": name, "url": APP + url, "kind": kind, "match": match or [], "clip": clip})
    return name + ".png"

mode = slot
meta = {}

# ---------------------------------------------------------------- MORNING
if slot == "morning":
    snap, mkt = raw["snapshot"], raw["market"]
    ni, bn, vix = snap["indices"]["nifty"], snap["indices"]["bankNifty"], snap["indices"]["vix"]
    br = mkt["breadth"]
    secs = sorted([s for s in mkt.get("sectors", []) if s.get("total_stocks", 0) >= 4], key=lambda s: float(s["today_pct"]))
    weak, strong = secs[0], secs[-1]
    upn = ni["ch"] >= 0
    s_snap = shot("snapshot", "/snapshot.html")
    s_heat = shot("heatmap", "/research.html?p=heatmap")
    s_feat = shot("feature", feature["url"])
    say("hook", "Market खुलने से पहले, ये एक screen देख लो, बाकी traders से आगे रहोगे।",
        "Check this ONE screen before 9:15 — stay ahead of other traders.",
        {"kind": "hook", "title": "9:15 SE PEHLE", "sub": "Nifty + Sectors · ek screen"})
    say("nifty", f"पिछले session में Nifty {ew(ni['ltp'])} पे close हुआ, और Bank Nifty {ew(bn['ltp'])} पे।",
        f"Last session: Nifty closed at {fmt(ni['ltp'])}, Bank Nifty at {fmt(bn['ltp'])}.",
        {"kind": "screen", "shot": s_snap, "scroll": [0.18, 0.30],
         "stats": [["NIFTY 50", fmt(ni["ltp"]), pct(ni["chp"])], ["BANK NIFTY", fmt(bn["ltp"]), pct(bn["chp"])], ["INDIA VIX", f"{vix['ltp']:.2f}", pct(vix["chp"])]]})
    say("breadth", f"Market breadth रहा {br['mood_label']}, {ew(br['advancing'])} stocks ऊपर, और {ew(br['declining'])} नीचे।",
        f"Breadth: {br['mood_label']} — {br['advancing']:,} up, {br['declining']:,} down.",
        {"kind": "screen", "shot": s_snap, "scroll": [0.30, 0.45],
         "badge": [br["mood_label"].upper(), f"{br['advancing']:,} ▲  ·  {br['declining']:,} ▼"]})
    say("sectors", f"सबसे strong sector रहा {strong['sector']}, और सबसे weak रहा {weak['sector']}।",
        f"Strongest: {strong['sector']} ({pct(strong['today_pct'])}) · Weakest: {weak['sector']} ({pct(weak['today_pct'])}).",
        {"kind": "screen", "shot": s_heat, "scroll": [0.10, 0.35],
         "sectors": [[strong["sector"], pct(strong["today_pct"])], [weak["sector"], pct(weak["today_pct"])]]})
    say("ahead", "नौ पंद्रह के बाद यही सब live update होता है, तो आप market के साथ नहीं, market से आगे चलते हो।",
        "After 9:15 it all updates live — you move ahead of the market, not behind it.",
        {"kind": "screen", "shot": s_heat, "scroll": [0.35, 0.55]})
    say("feat1", f"आज का feature: {feature['hi'][0]}", f"Feature of the day — {feature['en'][0]}",
        {"kind": "feature", "shot": s_feat, "name": feature["name"], "scroll": [0.0, 0.25]})
    say("feat2", feature["hi"][1], feature["en"][1], {"kind": "feature", "shot": s_feat, "name": feature["name"], "scroll": [0.25, 0.45]})
    meta = {"nifty": ni, "bankNifty": bn, "vix": vix, "breadth": {k: br[k] for k in ("advancing", "declining", "mood_label")},
            "strong": [strong["sector"], strong["today_pct"]], "weak": [weak["sector"], weak["today_pct"]], "feature": feature["name"],
            "marketDate": mkt.get("date", "")[:10]}

# ---------------------------------------------------------------- EVENING
else:
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    def hhmm(iso):
        t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(IST)
        return t.strftime("%H:%M"), t.hour, t.minute
    def spoken_time(h, m):
        return f"{ew(h)} {ew(m)}" if m else f"{ew(h)}"
    def strike_words(k):
        f = float(k)
        return ew(int(f)) if f == int(f) else None

    LOGIC = [  # (regex on reason, hindi, english)
        (r"5d/5h high break", "पाँच दिन और पाँच घंटे का high break", "5-day & 5-hour high break"),
        (r"5d/5h low break", "पाँच दिन और पाँच घंटे का low break", "5-day & 5-hour low break"),
        (r"above 20 SMA", "price बीस SMA के ऊपर", "price above 20 SMA"),
        (r"below 20 SMA", "price बीस SMA के नीचे", "price below 20 SMA"),
        (r"ORB", "opening range breakout", "Opening Range Breakout"),
        (r"premium at ATH", "premium अपने high पे", "premium at its high"),
    ]
    def logic_of(sig):
        if sig["src"] == "trap":
            setup = sig.get("setup", "")
            tf = "पंद्रह minute" if str(sig.get("tf")) == "15" else "एक घंटे"
            tfe = "15-min" if str(sig.get("tf")) == "15" else "1-hour"
            if "Bull" in setup:
                return f"{tf} पे Bull Trap, breakout fail हुआ", f"Bull Trap on {tfe} — breakout failed"
            return f"{tf} पे Bear Trap, breakdown fail हुआ", f"Bear Trap on {tfe} — breakdown failed"
        if sig["src"] == "index":
            return "gap के बाद candle और volume में mismatch", "Gap + candle/volume mismatch"
        hi, en = [], []
        for rx, h, e in LOGIC:
            if re.search(rx, sig.get("reason") or "", re.I) and len(hi) < 2:
                hi.append(h); en.append(e)
        if not hi:
            return "scanner के सारे rules match हुए", "All scanner rules matched"
        return " और ".join(hi), " + ".join(en)

    pool = []
    for s in raw["options"].get("signals", []):
        pool.append(dict(src="star", page="/research.html?page=star", name=s["underlying"], side=s["side"], strike=s["strike"],
                         ts=s["ts"], reason=s.get("reason"), outcome=s.get("outcome") or "", t1=s.get("t1_hit"),
                         entry=s["entry_premium"], sl=s["stop_loss"], tgt=[s["t1"], s["t2"]], exitp=s.get("exit_premium")))
    for a in (raw["trap"].get("algos") or {}).values():
        for s in a.get("closed", []):
            if s.get("trade_date") != raw["tradeDate"]:
                continue
            win = s.get("exit_reason") in ("TRAIL", "TARGET", "T1", "T2") and float(s.get("pnl_gross") or 0) > 0
            pool.append(dict(src="trap", page="/research.html?page=trap", name=s["underlying"], side=s["side"], strike=s["strike"],
                             ts=s["entry_time"], setup=s.get("setup"), tf=s.get("tf"), outcome=("TRAIL" if win else s.get("exit_reason") or ""),
                             entry=s["entry_premium"], sl=s.get("sl_level"), tgt=[], exitp=s.get("exit_premium")))
    for s in raw["index"].get("signals", []):
        if (s.get("trade_date") or "")[:10] != raw["tradeDate"] or s.get("status") != "closed":
            continue
        pool.append(dict(src="index", page="/research.html?page=idx", name=s["index_name"], side=s["side"], strike=s["strike"],
                         ts=s.get("activated_at") or s["ts"], reason=s.get("reason"), outcome=s.get("outcome") or "",
                         entry=s.get("entry_premium"), sl=s.get("sl_px"), tgt=[s.get("t1_index"), s.get("t2_index")], exitp=s.get("exit_premium")))
    NAMES = raw.get("names", {})
    IDX = {"NIFTY": "Nifty", "BANKNIFTY": "Bank Nifty", "FINNIFTY": "Fin Nifty", "MIDCPNIFTY": "Midcap Nifty", "SENSEX": "Sensex"}
    def spoken_name(t):
        if t in IDX:
            return IDX[t]
        n = NAMES.get(t) or t
        n = re.sub(r"\s*(Limited|Ltd\.?|\(India\))\s*$", "", n.strip(), flags=re.I)
        return n
    rank = {"T2": 0, "T1": 1, "TRAIL": 2}
    for p in pool:
        if p["outcome"] not in rank and p.get("t1"):
            p["outcome"] = "T1"
    ordered = sorted([p for p in pool if p["outcome"] in rank], key=lambda p: (rank[p["outcome"]], p["ts"]))
    winners, seen = [], set()
    for p in ordered:                       # prefer variety: one per scanner/setup first, then fill
        key = (p["src"], p.get("setup") or p["side"])
        if key not in seen:
            winners.append(p); seen.add(key)
    for p in ordered:
        if len(winners) >= 3: break
        if p not in winners: winners.append(p)
    winners = sorted(winners[:3], key=lambda p: p["ts"])
    sls = [p for p in pool if p["outcome"] == "SL"]
    loser = sorted(sls, key=lambda p: ((p.get("setup") or p["side"]) in {w.get("setup") or w["side"] for w in winners}, p["ts"]))[0] if sls else None
    meta = {"poolSize": len(pool), "winners": len(winners), "slHits": len(sls)}

    if len(winners) < 2:
        mode = "spotlight"
        s_feat = shot("feature", feature["url"])
        s_home = shot("brokers", "/home.html", kind="match", match=["TRADE FROM SIGNAL CARDS"])
        say("hook", f"आज AI Dashboard का एक खास feature देखते हैं, {feature['name']}।",
            f"Today's AI Dashboard spotlight: {feature['name']}.", {"kind": "hook", "title": feature["name"].upper(), "sub": "AI Dashboard spotlight"})
        say("feat1", feature["hi"][0], feature["en"][0], {"kind": "feature", "shot": s_feat, "name": feature["name"], "scroll": [0.0, 0.25]})
        say("feat2", feature["hi"][1], feature["en"][1], {"kind": "feature", "shot": s_feat, "name": feature["name"], "scroll": [0.25, 0.5]})
    else:
        picks = winners + ([loser] if loser else [])
        s_home = shot("brokers", "/home.html", kind="match", match=["TRADE FROM SIGNAL CARDS"])
        n_ok = len(winners)
        say("hook", "आज AI Dashboard ने क्या पकड़ा? कुछ selected signals देखो।",
            "What did the AI Dashboard catch today? A few selected signals.",
            {"kind": "hook", "title": "AAJ KE SIGNALS", "sub": "Selected signals · " + td.strftime("%-d %b"),
             "chips": ["✅"] * n_ok + (["❌"] if loser else [])})
        OUT = {"T1": ("TARGET 1 HIT ✅", "Target one hit हुआ।", "Target 1 hit."),
               "T2": ("TARGET 2 HIT ✅", "Target two तक गया।", "Target 2 hit."),
               "TRAIL": ("TRAILING EXIT ✅", "Trailing stop से move पकड़ा।", "Move captured with a trailing stop."),
               "SL": ("SL HIT ❌", "ये वाला stop loss hit हुआ, इसीलिए SL हमेशा ज़रूरी है।", "This one hit SL — that's why SL always matters.")}
        for i, p in enumerate(picks, 1):
            tm, h, m = hhmm(p["ts"])
            sw = strike_words(p["strike"])
            opt_hi = ("Call" if p["side"] == "CE" else "Put")
            lhi, len_ = logic_of(p)
            label, out_hi, out_en = OUT[p["outcome"]]
            card = shot(f"sig{i}", p["page"], kind="card", match=[p["name"], "ENTRY"]) if p["src"] in ("star", "index") else \
                   shot(f"sig{i}", p["page"], kind="card", match=[p["name"]])
            sk = f"{fmt(p['strike'])}" if float(p["strike"]) == int(float(p["strike"])) else str(p["strike"])
            sc = {"kind": "signal", "shot": card, "n": i, "name": p["name"], "contract": f"{p['name']} {sk} {p['side']}",
                  "time": tm, "logic": len_, "label": label, "win": p["outcome"] != "SL", "scanner": {"star": "Star Setup", "trap": "Intraday Trap", "index": "Index Options"}[p["src"]],
                  "entry": p.get("entry"), "sl": p.get("sl"), "tgt": [t for t in p.get("tgt", []) if t]}
            say(f"s{i}a", f"{spoken_name(p['name'])} {opt_hi}, {lhi}।",
                f"{p['name']} {sk} {p['side']} — {len_}.", sc)
            say(f"s{i}b", out_hi, out_en, dict(sc, phase="result"))
        say("ahead", "Signal आते ही phone पे alert आता है, और एक tap में अपने broker पे order, Fyers, Zerodha या Dhan।",
            "Instant phone alert the moment a signal appears — one tap to your broker: Fyers, Zerodha or Dhan.",
            {"kind": "ahead", "shot": s_home})
        meta["picks"] = [{k: p[k] for k in ("src", "name", "side", "strike", "outcome", "ts")} for p in picks]

say("cta", "बाकी traders से आगे रहना है? AI Dashboard का link description में है। Follow करो, Upper Circuit Stocks।",
    "Want to stay ahead? AI Dashboard link in the description. Follow UpperCircuitStocks!",
    {"kind": "cta"})

plan = {"date": D, "slot": slot, "mode": mode, "feature": feature["name"], "lines": lines, "scenes": scenes, "shots": shots, "meta": meta}
json.dump(plan, open(out_path, "w"), ensure_ascii=False, indent=1)
print(json.dumps({"mode": mode, "lines": len(lines), "shots": [s["name"] for s in shots], "meta": meta}, ensure_ascii=False))
