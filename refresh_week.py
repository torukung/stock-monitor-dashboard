"""Refresh the latest weekly close for every covered name and recompute the
price-derived fields in data.js, us_top10.js, china_top10.js, th_top10.js.
Research figures (entry/targets, CUS, bull, earnings, backlog, cash, driver/risk)
are preserved. Run after fetching this week's closes."""
import json, datetime as dt

GEN = "2026-06-15 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"

FRESH = {
 # Thailand .BK
 "AMATA.BK":26.25,"WHA.BK":4.98,"STECON.BK":17,"GULF.BK":64,"CK.BK":18.8,"PTTEP.BK":142.5,
 "SPALI.BK":15.6,"SIRI.BK":1.41,"PROUD.BK":0.94,"AOT.BK":58,"CPALL.BK":45.5,"ADVANC.BK":366,
 "MINT.BK":22.2,"BBL.BK":172.5,"CPN.BK":65.5,"KTB.BK":35.25,"KBANK.BK":203,"BDMS.BK":18,
 # China A .SHG/.SHE
 "688256.SHG":1240,"600111.SHG":49.43,"601138.SHG":70.13,"300308.SHE":1149,"300502.SHE":506.46,
 "300394.SHE":280.95,"688041.SHG":280,"603986.SHG":481.47,"688981.SHG":124.88,"300750.SHE":394.85,
 "002594.SHE":91.6,
 # Hong Kong .HK
 "9988.HK":110.2,"0981.HK":71.65,"0883.HK":24.92,"3311.HK":8.76,
 # US .US
 "NVDA.US":205.19,"AAPL.US":291.13,"MSFT.US":390.74,"GOOGL.US":359.68,"AMZN.US":238.55,
 "META.US":566.98,"TSLA.US":406.43,"LLY.US":1133,"BRK-B.US":489.25,"WMT.US":121.04,
}

def r2(x): return round(x, 2)
def ema(v, span):
    if not v: return None
    k = 2.0/(span+1); e = v[0]
    for x in v[1:]: e = x*k + e*(1-k)
    return e
def interp3(t1, t6):
    if not t1 or not t6 or t1 <= 0 or t6 <= 0: return None
    return t1*(t6/t1)**((3-1)/(6-1))

# ---------------- Watchlist (data.json / data.js) ----------------
d = json.load(open("data.json"))
for h in d["holdings"]:
    sym = h.get("symbol")
    if h.get("source") != "eodhd" or sym not in FRESH:
        continue
    s = h.get("spark") or []
    if not s:
        continue
    new = FRESH[sym]; s[-1] = new
    h["spark"] = s; h["last"] = r2(new); h["error"] = None
    h["chg_1d"] = round((new/s[-2]-1)*100, 2) if len(s) > 1 else None
    if len(s) > 5: h["chg_1m"] = round((new/s[-5]-1)*100, 2)
    h["chg_3m"] = round((new/s[0]-1)*100, 2)
    e = ema(s[-50:], 50); h["ema50"] = r2(e) if e else None
    h["trend_up"] = (e is not None and new >= e)
    hi = max(s); lo = min(s); h["hi_52w"] = r2(hi); h["lo_52w"] = r2(lo)
    h["range_pos"] = round((new-lo)/(hi-lo)*100, 0) if hi > lo else None
    entry = h.get("entry"); stop = h.get("stop"); t12 = h.get("target_12mo")
    h["pct_vs_entry"] = round((new/entry-1)*100, 1) if entry else None
    h["dist_to_stop"] = round((new/stop-1)*100, 1) if stop else None
    h["suggest_entry"] = r2(max(stop*1.02, new*0.93)) if stop else None
    targets = [t for t in (h.get("target_1mo"), h.get("target_6mo"), t12) if t]
    above = [t for t in targets if t > new]
    if above: h["suggest_exit"] = r2(min(above)); h["targets_met"] = False
    elif targets: h["suggest_exit"] = r2(max(targets)); h["targets_met"] = True
    h["reward_risk"] = round((t12-new)/(new-stop), 2) if (t12 and stop and new > stop) else None
    t1 = h.get("target_1mo"); t6 = h.get("target_6mo"); t3 = interp3(t1, t6); g = h.get("cagr_long") or 0
    h["upside"] = {
        "3mo": round((t3/new-1)*100, 1) if t3 else None,
        "6mo": round((t6/new-1)*100, 1) if t6 else None,
        "12mo": round((t12/new-1)*100, 1) if t12 else None,
        "3yr": round((t12*(1+g)**2/new-1)*100, 1) if t12 else None,
        "5yr": round((t12*(1+g)**4/new-1)*100, 1) if t12 else None,
    }
# RS rank across the watchlist on 3-month return
scored = [h for h in d["holdings"] if h.get("chg_3m") is not None]
scored.sort(key=lambda h: h["chg_3m"]); n = len(scored)
for i, h in enumerate(scored): h["rs"] = round(i/max(n-1, 1)*99 + 1)
for h in d["holdings"]: h.setdefault("rs", None)
d["meta"]["generated"] = GEN
json.dump(d, open("data.json", "w"), indent=2)
open("data.js", "w").write("window.DASHBOARD_DATA = " + json.dumps(d) + ";\n")

# ---------------- Rankings (US / China / Thailand) ----------------
def us_sym(t): return t + ".US"
def cn_sym(t): return t[:-3]+".SHE" if t.endswith(".SZ") else (t[:-3]+".SHG" if t.endswith(".SH") else t)
def th_sym(t): return t + ".BK"
for fn, var, mapf in [("us_top10","US_TOP10",us_sym),("china_top10","CHINA_TOP10",cn_sym),("th_top10","TH_TOP10",th_sym)]:
    D = json.load(open(fn + ".json"))
    miss = []
    for x in D["names"]:
        sym = mapf(x["ticker"])
        if sym not in FRESH:
            miss.append(x["ticker"]); continue
        s = x["spark"]; new = FRESH[sym]; s[-1] = new
        x["spark"] = s; x["last"] = r2(new)
        x["chg_3m"] = round((new/s[0]-1)*100, 1)
        x["buy"] = r2(new*0.93)
        x["tp"] = r2(new*(1 + x["base"]["3m"]/100.0))
    D["meta"]["generated"] = GEN
    json.dump(D, open(fn + ".json", "w"), indent=2, ensure_ascii=False)
    open(fn + ".js", "w").write("window." + var + " = " + json.dumps(D, ensure_ascii=False) + ";\n")
    if miss: print(fn, "unmatched:", miss)

print("Refreshed", GEN, "— watchlist + US/China/Thailand prices.")
