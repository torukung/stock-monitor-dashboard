"""Rewrite recap.js to this week's Thematic Brief (2026-06-21) + v5.0 watchlist.
Narrative from the brief; country prices from data.json/us_top10.json; moving-in/out
applies the v5.0 rotation with dated persistence (out keeps its since-date)."""
import json, datetime as dt
GEN = "2026-06-20 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
wl = {h["ticker"]: h for h in json.load(open("data.json"))["holdings"]}
us = {n["ticker"]: n for n in json.load(open("us_top10.json"))["names"]}
def us1m(n):
    s = n.get("spark") or []
    return round((n["last"]/s[-5]-1)*100,1) if len(s)>=5 and n.get("last") else None
def trend(c): return "up" if (c or 0)>1 else "down" if (c or 0)<-1 else "flat"
R = json.load(open("recap.json"))

R["meta"]["generated"] = GEN
R["meta"]["asof"] = "2026-06-20"
R["meta"]["source"] = "scheduled-task weekly-us-china-thematic-brief (Thematic Brief 2026-06-21) + 02_WATCHLIST v5.0"

R["recap"]["headline"] = ("Warsh's first FOMC was a hawkish hold — no cut, hike-skewed dots — so AI's risk shifts from "
  "'ROI doubt' to 'rates + valuation/supply' (SpaceX→Cursor $60B, NVDA's $25B bond), while China self-sufficiency and batteries keep compounding.")
R["recap"]["bullets"] = [
  "Hawkish hold: rates held 3.50-3.75%, but 9 of 18 members now pencil a 2026 HIKE (6 see two); the statement was gutted to 130 words and Warsh withheld his dot. Stocks fell into the Jun 17 close (Nasdaq -1.34%, S&P -1.21%; Dow at a record). The rate-cut cushion under high-multiple AI is gone.",
  "AI went full capital-markets: days after the largest-ever IPO (SpaceX ~$85.7B, >$2T), SpaceX bought Cursor for $60B all-stock and NVDA priced its biggest-ever $25B bond (~$210.69 close). A ~$3.6T AI-IPO pipeline now looms as a supply risk.",
  "China softened on geopolitics, not fundamentals: Hang Seng -1.59% to ~23,925 as US-Iran talks in Switzerland were cancelled and Brent firmed toward ~$80. Self-sufficiency (Cambricon/SMIC, Huawei Ascend) and batteries (CATL/BYD) compound underneath. Power-for-AI screens as the cleanest risk/reward.",
]
R["recap"]["catalysts"] = [
  {"title":"Warsh FOMC — hawkish hold, hike-skewed dots (130-word statement)","theme":"Rates / multiples","horizon":"now","flow":"flow"},
  {"title":"SpaceX IPO -> $60B Cursor; ~$3.6T AI-IPO pipeline","theme":"AI capital markets / supply","horizon":"1-6 mo","flow":"show -> flow"},
  {"title":"NVDA's record $25B bond funds the AI buildout","theme":"US semis","horizon":"3-12 mo","flow":"flow"},
  {"title":"China self-sufficiency: Cambricon/SMIC + Huawei Ascend (DeepSeek-V4)","theme":"China AI","horizon":"3-12 mo","flow":"flow"},
  {"title":"US-Iran talks cancelled; Brent firms ~$80","theme":"Oil / energy premium","horizon":"days-wk","flow":"flow"},
  {"title":"Power-for-AI (CEG/VST/OKLO) — megawatts the bottleneck","theme":"Power for AI","horizon":"3-36 mo","flow":"flow"},
]
R["outlook"]["bull_1m"] = 45
R["outlook"]["bull_6m"] = 55
R["outlook"]["bull_3y"] = 66
R["outlook"]["note"] = ("Hawkish hold (no cut, possible 2026 hike) removes the cheapest tailwind under high-multiple AI and "
  "lengthens duration risk; AI is now a rates/valuation/supply story. Power-for-AI is the cleanest risk/reward; China "
  "self-sufficiency + batteries compound independent of US rates; oil ideas whipsaw on on-off Iran talks.")

# sector trends by region (-3..+3), refreshed to the brief
R["sectors_by_region"] = [
 {"region":"TH","name":"Thailand","sectors":[
   {"name":"Data center / industrial estate","t1m":2,"t6m":3,"t3y":3},
   {"name":"Construction / infrastructure","t1m":2,"t6m":2,"t3y":2},
   {"name":"Power & utilities","t1m":2,"t6m":2,"t3y":3},
   {"name":"Oil & gas (E&P)","t1m":-2,"t6m":-1,"t3y":0},
   {"name":"Property","t1m":-2,"t6m":-1,"t3y":0}]},
 {"region":"HK","name":"Hong Kong","sectors":[
   {"name":"Semis / foundry (SMIC)","t1m":1,"t6m":2,"t3y":3},
   {"name":"China tech / AI (pullback)","t1m":-1,"t6m":1,"t3y":2},
   {"name":"Batteries / storage (CATL)","t1m":2,"t6m":2,"t3y":3},
   {"name":"Oil & gas","t1m":-2,"t6m":0,"t3y":0},
   {"name":"Construction / BRI","t1m":-2,"t6m":0,"t3y":1}]},
 {"region":"CN","name":"China A","sectors":[
   {"name":"AI chips (Cambricon)","t1m":3,"t6m":3,"t3y":3},
   {"name":"Rare earth (improving)","t1m":1,"t6m":2,"t3y":3},
   {"name":"Batteries / storage","t1m":2,"t6m":2,"t3y":3}]},
 {"region":"US","name":"United States","sectors":[
   {"name":"AI / semis (Fed re-rate)","t1m":0,"t6m":2,"t3y":3},
   {"name":"Power for AI / nuclear","t1m":2,"t6m":2,"t3y":3},
   {"name":"AI IPOs / capital markets","t1m":1,"t6m":1,"t3y":2},
   {"name":"Software / cloud","t1m":0,"t6m":1,"t3y":2}]},
 {"region":"SG","name":"Singapore","sectors":[
   {"name":"Defense / engineering (S63)","t1m":2,"t6m":2,"t3y":2},
   {"name":"Power / renewables (Sembcorp)","t1m":1,"t6m":2,"t3y":2},
   {"name":"Data-center REIT","t1m":-1,"t6m":1,"t3y":2},
   {"name":"Shipbuilding (stop hit)","t1m":-2,"t6m":0,"t3y":1}]},
]

# refresh country-group prices/status from data.json + us_top10.json
for c in R["countries"]:
    for s in c["stocks"]:
        tk = s["ticker"]; src = wl.get(tk)
        if src:
            s["last"] = src.get("last"); s["status"] = src.get("status")
            s["chg_1m"] = src.get("chg_1m"); s["trend"] = trend(src.get("chg_1m"))
        elif tk in us:
            n = us[tk]; s["last"] = n.get("last"); cm = us1m(n)
            s["chg_1m"] = cm; s["trend"] = trend(cm); s["status"] = "Monitor"

# add Tencent/CATL/China Mobile to the HK group (now watchlist names) if missing
hk = next(c for c in R["countries"] if c["code"]=="HK")
have = {s["ticker"] for s in hk["stocks"]}
for tk,sec in [("0700","China tech / AI"),("3750","Batteries / storage"),("0941","Telecom / AI-compute")]:
    if tk not in have and tk in wl:
        h = wl[tk]
        hk["stocks"].append({"ticker":tk,"name":h["name"],"sector":sec,"last":h.get("last"),
            "currency":h.get("currency","HKD"),"chg_1m":h.get("chg_1m"),"status":h.get("status"),"trend":trend(h.get("chg_1m"))})

# moving-in / moving-out (v5.0 rotation, dated persistence)
def mom(tk): return (wl.get(tk) or {}).get("chg_1m")
R["moving_in"] = [
 {"ticker":"STECON","country":"TH","sector":"Construction / DC unit","since":"2026-06-06","mom_1m":mom("STECON"),
  "why":"Winner — through 6-mo target, 7-day +10%; new DC unit + PPP/Land-Bridge bids. Trim into strength but trend up."},
 {"ticker":"0981","country":"HK","sector":"China foundry / semis","since":"2026-06-20","mom_1m":mom("0981"),
  "why":"Graduated off the drop alert — +11.4% 1-mo; self-sufficiency thesis converting (capacity doubling). Upgrade to accumulate."},
 {"ticker":"0700","country":"HK","sector":"China tech / AI","since":"2026-06-15","mom_1m":mom("0700"),
  "why":"Top Idea #1 — cheapest large China-AI proxy, no US-chip dependency. Accumulate <HK$455 (now ~440)."},
 {"ticker":"3750","country":"HK","sector":"Batteries / storage","since":"2026-06-15","mom_1m":mom("3750"),
  "why":"Top Idea #2 — storage super-cycle + ~37% share + JPM upgrade; +7% 7-day. Momentum add."},
 {"ticker":"0941","country":"HK","sector":"Telecom / AI-compute","since":"2026-06-20","mom_1m":mom("0941"),
  "why":"New defensive watch — East-Data-West-Compute capex + ~5% dividend, ~10x P/E; low-beta China-AI into a hawkish Fed."},
]
R["moving_out"] = [
 {"ticker":"9988","country":"HK","sector":"China tech / AI","since":"2026-06-06","mom_1m":mom("9988"),
  "why":"REMOVED — within ~5% of HK$100 stop (-22% vs entry). H200-import flow dead; theme rotated to domestic suppliers."},
 {"ticker":"BS6","country":"SG","sector":"Shipbuilding","since":"2026-06-20","mom_1m":None,
  "why":"REMOVED — broke S$3.90 stop to ~S$3.60 on weak order momentum (~-22% off peak). Honor stop."},
 {"ticker":"0883","country":"HK","sector":"Oil major","since":"2026-06-20","mom_1m":mom("0883"),
  "why":"De-elevated / dropped from ideas — -16% 1-mo as Brent fades ~$80 and US-Iran talks are cancelled."},
]
# note: 600111 (CNRE) removed from moving-out this week — momentum turning up (+8% 7-day), graduated.

open("recap.json","w").write(json.dumps(R, ensure_ascii=False, indent=2))
open("recap.js","w").write("window.RECAP = "+json.dumps(R, ensure_ascii=False)+";\n")
print("recap rewritten", GEN, "| asof", R["meta"]["asof"])
print("moving_in:", [m["ticker"] for m in R["moving_in"]], "| moving_out:", [m["ticker"] for m in R["moving_out"]])
print("HK group:", [s["ticker"] for s in hk["stocks"]])
