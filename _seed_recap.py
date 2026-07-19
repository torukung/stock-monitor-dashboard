"""One-off: build the initial recap.js/json for the 3rd tab (Weekly Recap),
from data.json (watchlist) + us_top10.json (US names) plus a synthesized recap,
bull outlook, sector trends, and moving-in/out lists. The weekly scraping task
(stock-thchinaus-weekly-scraping) regenerates this each Saturday."""
import json, datetime as dt

wl = json.load(open("data.json"))["holdings"]
us = json.load(open("us_top10.json"))["names"]
byT = {h["ticker"]: h for h in wl}

EXC2C = {"SET": ("TH", "Thailand", "THB"), "HKEX": ("HK", "Hong Kong", "HKD"),
         "SSE": ("CN", "China A", "CNY"), "SGX": ("SG", "Singapore", "SGD")}

def trend(x):
    return "up" if (x or 0) > 1 else "down" if (x or 0) < -1 else "flat"

def short_sector(theme):
    return theme.split(" / ")[0].split(" + ")[0].strip()

# ---- country groups from the watchlist ----
countries = {c: {"code": c, "name": n, "currency": ccy, "stocks": []}
             for c, n, ccy in [("TH","Thailand","THB"),("HK","Hong Kong","HKD"),
                               ("CN","China A","CNY"),("US","United States","USD"),
                               ("SG","Singapore","SGD")]}
for h in wl:
    c = EXC2C.get(h["exchange"])
    if not c:
        continue
    code = c[0]
    countries[code]["stocks"].append({
        "ticker": h["ticker"], "name": h["name"], "sector": short_sector(h["theme"]),
        "last": h.get("last"), "currency": h["currency"],
        "chg_1m": h.get("chg_1m"), "status": h["status"], "trend": trend(h.get("chg_1m")),
    })
# US group: top monitored mega-caps from the US Top-10 (chg_1m from spark ~4wk)
for n in sorted(us, key=lambda x: -x["cus"])[:5]:
    s = n["spark"]; m1 = round((n["last"]/s[-5]-1)*100, 1) if len(s) >= 5 else None
    countries["US"]["stocks"].append({
        "ticker": n["ticker"], "name": n["name"], "sector": n["sector"],
        "last": n["last"], "currency": "USD", "chg_1m": m1, "status": "Monitor", "trend": trend(m1),
    })

# ---- sector trends by region (t1m, t6m, t3y on a -3..+3 scale) ----
sectors_by_region = [
 {"region":"TH","name":"Thailand","sectors":[
   {"name":"Data center / industrial estate","t1m":2,"t6m":3,"t3y":3},
   {"name":"Construction / infrastructure","t1m":2,"t6m":2,"t3y":2},
   {"name":"Power & utilities","t1m":1,"t6m":2,"t3y":3},
   {"name":"Property","t1m":-2,"t6m":-1,"t3y":0}]},
 {"region":"HK","name":"Hong Kong","sectors":[
   {"name":"Semis / foundry","t1m":1,"t6m":2,"t3y":3},
   {"name":"China tech / AI","t1m":-1,"t6m":1,"t3y":2},
   {"name":"Oil & gas","t1m":2,"t6m":1,"t3y":1},
   {"name":"Construction / BRI","t1m":0,"t6m":1,"t3y":1}]},
 {"region":"CN","name":"China A","sectors":[
   {"name":"AI chips","t1m":2,"t6m":2,"t3y":3},
   {"name":"Rare earth","t1m":0,"t6m":2,"t3y":3}]},
 {"region":"US","name":"United States","sectors":[
   {"name":"AI / semis","t1m":2,"t6m":2,"t3y":3},
   {"name":"Software / cloud","t1m":1,"t6m":2,"t3y":2},
   {"name":"Healthcare / GLP-1","t1m":2,"t6m":2,"t3y":3},
   {"name":"Consumer staples","t1m":-1,"t6m":0,"t3y":1}]},
 {"region":"SG","name":"Singapore","sectors":[
   {"name":"Shipbuilding","t1m":1,"t6m":1,"t3y":2},
   {"name":"Defense / engineering","t1m":2,"t6m":2,"t3y":2},
   {"name":"Data-center REIT","t1m":0,"t6m":1,"t3y":2},
   {"name":"Utilities / renewables","t1m":1,"t6m":2,"t3y":2}]},
]

def mom(tk):  # 1-month momentum from the watchlist
    return byT.get(tk, {}).get("chg_1m")

# ---- moving IN (signal + 1m momentum both up) ----
moving_in = [
 {"ticker":"STECON","country":"TH","sector":"Construction / DC unit","since":"2026-06-06","mom_1m":mom("STECON"),"why":"Graduated off alert; KGI upgrade + new data-center unit, momentum up"},
 {"ticker":"BS6","country":"SG","sector":"Shipbuilding","since":"2026-06-06","mom_1m":mom("BS6"),"why":"Recovered above stop on US$826m Seaspan stake"},
 {"ticker":"PTTEP","country":"TH","sector":"Oil & gas","since":"2026-06-03","mom_1m":mom("PTTEP"),"why":"Elevated idea — Iran-war/oil beneficiary at trigger, 5.5% yield"},
]
# ---- moving OUT (signal + 1m momentum both down); since = date it started ----
moving_out = [
 {"ticker":"9988","country":"HK","sector":"China tech / AI","since":"2026-06-06","mom_1m":mom("9988"),"why":"Below entry; H200 flow stalled, momentum negative — probation"},
 {"ticker":"600111","country":"CN","sector":"Rare earth","since":"2026-06-06","mom_1m":mom("600111"),"why":"Divergence — stock weak while theme strengthens; reduce"},
]

payload = {
 "meta":{"title":"Weekly Recap","generated":dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
         "asof":"2026-06-06","source":"scheduled-task stock-thchinaus-weekly-scraping",
         "in_out_rule":"A name moves in only when watchlist signal AND 1-month momentum both turn up; out when both roll over. Moving-out keeps its original since-date and is removed once it moves in again."},
 "recap":{
   "headline":"AI/data-center + energy lead into an event-heavy fortnight (US CPI → FOMC, Iran).",
   "bullets":[
     "AI-semi rally broadening — Taiwan/Korea record highs; data-center capex theme intact across TH, China A and US.",
     "Iran war keeps Brent ~$94 — energy & defense names bid; watch Hormuz headlines (kill-switch risk).",
     "US May CPI (Jun 8-12) into FOMC (Jun 16-17) — rate-sensitive growth and REITs on watch."],
   "catalysts":[
     {"title":"US May CPI → FOMC","theme":"Rates / growth multiples","horizon":"1-2 wk","flow":"flow"},
     {"title":"China rare-earth Wave-2 expiry (Nov)","theme":"Rare earth","horizon":"3-6 mo","flow":"show → flow"},
     {"title":"Nvidia H200-to-China licences","theme":"China AI / Alibaba","horizon":"ongoing","flow":"show (zero chips shipped)"},
     {"title":"Tesla Robotaxi paid launch","theme":"US autonomy","horizon":"1 mo","flow":"flow"}]},
 "outlook":{"bull_1m":45,"bull_6m":58,"bull_3y":67,
   "note":"Constructive but event-heavy near-term (CPI/FOMC, Iran). Structural AI/data-center + energy tailwinds favor the 6-month and 3-year horizons."},
 "countries":[countries[c] for c in ["TH","HK","CN","US","SG"]],
 "sectors_by_region":sectors_by_region,
 "moving_in":moving_in,
 "moving_out":moving_out,
}
open("recap.json","w").write(json.dumps(payload,indent=2))
open("recap.js","w").write("window.RECAP = "+json.dumps(payload)+";\n")
print("Wrote recap.js / .json — countries:", {c["code"]:len(c["stocks"]) for c in payload["countries"]},
      "| moving_in", len(moving_in), "| moving_out", len(moving_out))
