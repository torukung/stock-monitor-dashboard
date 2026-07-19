"""Sync the Watchlist tab (data.js/json + watchlist.json) to 02_WATCHLIST v4.0:
new targets/stops/conviction/status for existing names, de-elevate PTTEP/CNOOC,
add Tencent (0700.HK) and CATL (3750.HK). Prices already at Jun-12 closes."""
import json, datetime as dt
GEN = "2026-06-15 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
def r2(x): return round(x, 2) if x is not None else None
def ema(v, span):
    if not v: return None
    k = 2/(span+1); e = v[0]
    for x in v[1:]: e = x*k + e*(1-k)
    return e
def interp3(t1, t6):
    if not t1 or not t6 or t1 <= 0 or t6 <= 0: return None
    return t1*(t6/t1)**0.4

CH = {
 "AMATA": dict(t=[27,30,33], stop=22, conv=5, status="Trim", note="⚠️ Take profit — hit 6-mo target in 1mo; trim ⅓, raise stop, ride DC capex tail."),
 "WHA": dict(t=[5.10,5.50,6.00], stop=4.30, conv=4, status="Trim", note="⚠️ Take profit — through 12-mo target; trim, trail stop. DC + utilities strong."),
 "STECON": dict(t=[17,18,19], stop=14, conv=4, status="Trim", note="⚠️ Take profit — at KGI TP; new DC unit; PPP bids. Trim, raise stop to 14."),
 "GULF": dict(t=[66,70,75], stop=54, conv=4, status="Hold", note="Near 52wk high. THB140bn AI/DC + renewables. Lower gas cost (oil↓) tailwind."),
 "CK": dict(t=[19.5,21,23], stop=15, conv=3, status="Hold", note="Near 52wk high. PPP motorway bids; Land Bridge optionality."),
 "688256": dict(t=[1400,1600,1500], stop=1050, conv=3, status="Trim", note="🔍 Round-tripped a spike. 500k-accelerator ramp gated by SMIC yields. Trim; ≤5-10%."),
 "600111": dict(t=[54,60,62], stop=42, conv=4, status="Reduce", note="⚠️ Divergence. Q2 concentrate +44.6% QoQ. Hold reduced for Nov Wave-2 only."),
 "9988": dict(t=[120,135,140], stop=100, conv=2, status="Reduce", note="🚨 7-day −10%. Cloud show not converting; H200 zero-shipped. Reduce to ≤2-3%."),
 "0981": dict(t=[75,85,95], stop=64, conv=3, status="Watch", note="🔍 Below entry on Stock-Connect outflow; self-sufficiency thesis strengthening. Add on stabilisation."),
 "BS6": dict(stop=3.90, status="Hold", last=4.22, note="Slipped just below entry; Seaspan stake intact. SGX price approx."),
 "S63": dict(stop=9.80, status="Hold", last=11.00, note="Ex-div Jun 11; $4.8b 1Q wins. SGX price approx."),
 "U96": dict(status="Watch", last=6.20, note="⭐ Top Idea #3 — power-for-AI + renewables, ~3% yield. Accumulate ~S$6.10-6.30."),
 "AJBU": dict(status="Watch", last=2.28, note="DC REIT; not triggered (yield ~4.6%). Rate-sensitive into hawkish FOMC."),
 "PTTEP": dict(status="Watch", note="DE-ELEVATED — oil leverage now a headwind as Brent fades <$86.5. Re-engage only if Iran talks collapse."),
 "0883": dict(status="Watch", note="DE-ELEVATED — oil beneficiary fading (~HK$24.92)."),
}
NEW = [
 dict(ticker="0700", name="Tencent Holdings", exchange="HKEX", symbol="0700.HK", currency="HKD", tier=3,
      theme="China tech / AI / cloud", conviction=4, note="⭐ Top Idea #1 — China-AI self-sufficiency at a cheap multiple (P/E ~15.7). Accumulate <HK$455.",
      spark=[547.5,508,493.4,489.2,504.5,510.5,493.4,467.8,471.4,456.4,441.4,427.2,453.2,463.6]),
 dict(ticker="3750", name="CATL (HK)", exchange="HKEX", symbol="3750.HK", currency="HKD", tier=3,
      theme="EV battery / storage", conviction=3, note="⭐ Top Idea #2 — storage-boom re-rating + JPM upgrade. Momentum add, size small (rich multiple).",
      spark=[621,698,634,627.5,681.5,692,695,608,651,680,686,744.5,711,672.5]),
]

d = json.load(open("data.json")); wl = json.load(open("watchlist.json"))
wlmap = {h["ticker"]: h for h in wl["holdings"]}

def recompute(h, last, t1, t6, t12, stop, cagr):
    h["last"] = r2(last); h["error"] = None
    entry = h.get("entry")
    h["pct_vs_entry"] = round((last/entry-1)*100, 1) if entry else None
    h["dist_to_stop"] = round((last/stop-1)*100, 1) if stop else None
    h["suggest_entry"] = r2(max(stop*1.02, last*0.93)) if stop else None
    targets = [t for t in (t1, t6, t12) if t]
    above = [t for t in targets if t > last]
    if above: h["suggest_exit"] = r2(min(above)); h["targets_met"] = False
    elif targets: h["suggest_exit"] = r2(max(targets)); h["targets_met"] = True
    else: h["suggest_exit"] = None; h["targets_met"] = None
    h["reward_risk"] = round((t12-last)/(last-stop), 2) if (t12 and stop and last > stop) else None
    t3 = interp3(t1, t6); g = cagr or 0
    h["upside"] = {
        "3mo": round((t3/last-1)*100, 1) if t3 else None,
        "6mo": round((t6/last-1)*100, 1) if t6 else None,
        "12mo": round((t12/last-1)*100, 1) if t12 else None,
        "3yr": round((t12*(1+g)**2/last-1)*100, 1) if t12 else None,
        "5yr": round((t12*(1+g)**4/last-1)*100, 1) if t12 else None,
    }

for h in d["holdings"]:
    tk = h["ticker"]
    if tk not in CH: continue
    c = CH[tk]; w = wlmap.get(tk, {})
    cagr = w.get("cagr_long", 0)
    if "conv" in c: h["conviction"] = c["conv"]
    if "status" in c: h["status"] = c["status"]
    if "note" in c: h["note"] = c["note"]
    if "stop" in c: h["stop"] = c["stop"]
    t = c.get("t")
    if t:
        t1, t6, t12 = t
        if tk in wlmap: wlmap[tk]["target_1mo"], wlmap[tk]["target_6mo"], wlmap[tk]["target_12mo"] = t1, t6, t12
    else:
        t1, t6, t12 = w.get("target_1mo"), w.get("target_6mo"), w.get("target_12mo")
    stop = c.get("stop", h.get("stop"))
    last = c.get("last", h.get("last"))
    if last is not None: recompute(h, last, t1, t6, t12, stop, cagr)
    if tk in wlmap:
        wm = wlmap[tk]
        for k in ("conv", "status", "note", "stop"):
            if k in c: wm["conviction" if k == "conv" else k] = c[k]

def chg3(s): return round((s[-1]/s[0]-1)*100, 2)
for nx in NEW:
    s = nx["spark"]; last = s[-1]; e = ema(s, 50)
    d["holdings"].append({
        "ticker": nx["ticker"], "name": nx["name"], "exchange": nx["exchange"], "currency": nx["currency"],
        "tier": nx["tier"], "theme": nx["theme"], "conviction": nx["conviction"], "status": "Watch", "note": nx["note"],
        "source": "eodhd", "symbol": nx["symbol"], "entry": None, "stop": None, "entry_date": None, "entry_date_fmt": None,
        "condition_since": "2026-06-15", "condition_since_fmt": "15-Jun-26", "days_on_condition": 0,
        "last": r2(last), "spark": s, "error": None, "spark_from": "09-Mar-26", "spark_to": "08-Jun-26", "spark_tf": "3M",
        "chg_1d": round((last/s[-2]-1)*100, 2), "chg_1m": round((last/s[-5]-1)*100, 2), "chg_3m": chg3(s),
        "ema50": r2(e), "trend_up": last >= e, "hi_52w": r2(max(s)), "lo_52w": r2(min(s)),
        "range_pos": round((last-min(s))/(max(s)-min(s))*100, 0), "pct_vs_entry": None, "dist_to_stop": None,
        "suggest_entry": None, "suggest_exit": None, "targets_met": None, "reward_risk": None,
        "upside": {"3mo": None, "6mo": None, "12mo": None, "3yr": None, "5yr": None}})
    wl["holdings"].append({"ticker": nx["ticker"], "name": nx["name"], "exchange": nx["exchange"], "source": "eodhd",
        "symbol": nx["symbol"], "currency": nx["currency"], "tier": nx["tier"], "theme": nx["theme"],
        "conviction": nx["conviction"], "status": "Watch", "entry": None, "stop": None, "target_1mo": None,
        "target_6mo": None, "target_12mo": None, "cagr_long": 0.10, "entry_date": None, "condition_since": "2026-06-15", "note": nx["note"]})

scored = [h for h in d["holdings"] if h.get("chg_3m") is not None]
scored.sort(key=lambda h: h["chg_3m"]); n = len(scored)
for i, h in enumerate(scored): h["rs"] = round(i/max(n-1, 1)*99 + 1)
for h in d["holdings"]: h.setdefault("rs", None)
d["meta"]["generated"] = GEN
json.dump(d, open("data.json", "w"), indent=2)
open("data.js", "w").write("window.DASHBOARD_DATA = " + json.dumps(d) + ";\n")
json.dump(wl, open("watchlist.json", "w"), indent=2)
print("v4.0 sync done", GEN, "| holdings", len(d["holdings"]))
