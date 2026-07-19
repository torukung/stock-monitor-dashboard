"""Rebuild the Watchlist tab (data.js/json + watchlist.json) from 02_WATCHLIST v5.0
(2026-06-20). Fresh EODHD weekly closes (to Fri Jun 19 / Thu Jun 18) embedded below;
SGX names web-approx (no series). Two removals -> Avoid (Alibaba, BS6); SMIC/CNRE
upgraded; China Mobile 0941 added as defensive watch."""
import json, datetime as dt
ASOF = dt.date(2026, 6, 19)
GEN = "2026-06-20 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def fmt(d):
    if not d: return None
    y, m, da = map(int, d.split("-")); return f"{da:02d}-{MON[m-1]}-{str(y)[2:]}"
def r2(x): return round(x, 2) if x is not None else None
def ema(v, span):
    if not v: return None
    k = 2/(span+1); e = v[0]
    for x in v[1:]: e = x*k + e*(1-k)
    return e
def interp3(t1, t6):
    if not t1 or not t6 or t1 <= 0 or t6 <= 0: return None
    return t1*(t6/t1)**0.4

# fresh weekly closes (ascending; week-of 2026-03-09 .. 2026-06-15 = close to Jun 19/18)
S = {
 "AMATA.BK":[18.3,19,18.9,19.1,19.7,20.5,20.3,20.6,20.8,21.4,25,24.5,26,26.25,26.5],
 "WHA.BK":[4.06,4.1,4.12,4.22,4.28,4.4,4.38,4.48,4.7,4.68,5,4.9,5.05,4.98,5],
 "STECON.BK":[12.5,11.5,11,12.3,11.9,12,11.5,12,13.9,13.1,14.2,15.7,16.2,17,18.7],
 "GULF.BK":[56.25,56.75,58.25,59.25,59.5,57.75,56,57.5,60,59.75,60.75,62,67,64,64],
 "CK.BK":[15.5,15.5,14.7,16,16.6,17.2,16.5,17,18.9,17.8,18.2,18,18.9,18.8,20.2],
 "PTTEP.BK":[146.5,154,159.5,157,151.5,145,149.5,154,148.5,150,151,141.5,144.5,142.5,134],
 "SIRI.BK":[1.51,1.43,1.36,1.4,1.42,1.41,1.41,1.4,1.41,1.42,1.43,1.43,1.4,1.41,1.44],
 "SPALI.BK":[17.4,16.8,16.3,16.4,16.4,16.5,16.7,16.2,15.3,15.4,15.5,15.5,15.6,15.6,15.7],
 "PROUD.BK":[1,0.99,1,0.99,1.01,1.03,1.04,0.98,0.96,0.95,0.92,0.95,0.93,0.94,1.02],
 "0700.HK":[547.5,508,493.4,489.2,504.5,510.5,493.4,467.8,471.4,456.4,441.4,427.2,453.2,463.6,440.2],
 "3750.HK":[621,698,634,627.5,681.5,692,695,608,651,680,686,744.5,711,672.5,708.5],
 "0941.HK":[79.95,78.8,78.05,80.05,81.1,81.45,83.9,84.6,85.45,86.2,85.5,85.15,82.4,81.8,80.1],
 "0981.HK":[62.2,56.9,52.5,51,58.25,59.35,64.3,70.9,73.35,71.15,79.85,81.6,75.65,71.65,76.5],
 "9988.HK":[132.5,123.7,122.6,118.5,125.5,136.4,131.8,126,139,132.3,127,120.9,122.4,110.2,104.9],
 "0883.HK":[29.76,30.38,29.06,27.02,26.52,26.98,27.9,29.38,26.44,26.42,27.44,26.4,26.54,24.92,22.38],
 "3311.HK":[9.38,8.87,8.49,8.45,8.67,8.69,8.92,9.07,9.38,9.34,8.9,8.75,8.98,8.76,7.59],
 "688256.SHG":[1096.1,1025,1024,1025.7,1210.7,1334,1352.5,1699.96,1182.53,1209,1286,1310,1299.2,1240,1507.46],
 "600111.SHG":[50.82,46,47.27,47.61,51.75,49.22,47.24,53.04,54.75,53.78,51.09,48.62,49.66,49.43,51.4],
}
SPARK_FROM, SPARK_TO = "09-Mar-26", "19-Jun-26"

# v5.0 config. t = [t1,t6,t12] or None; approx = web price for SGX (no series)
CFG = [
 # Tier 1
 dict(tk="AMATA",nm="Amata Corporation",ex="SET",sym="AMATA.BK",cur="THB",tier=1,th="Thai industrial estate / data-center capex",
   conv=5,st="Trim",entry=19.30,stop=23,t=[27,30,33],cagr=0.14,ed="2026-05-15",cs="2026-05-15",
   note="⚠️ TAKE PROFIT — at 1-mo target (+23% 1-mo). Trim ⅓, ride DC-capex tail, stop raised to 23."),
 dict(tk="WHA",nm="WHA Corporation",ex="SET",sym="WHA.BK",cur="THB",tier=1,th="Industrial land + utilities / data-center",
   conv=4,st="Trim",entry=3.98,stop=4.50,t=[5.10,5.50,6.00],cagr=0.12,ed="2026-05-15",cs="2026-05-15",
   note="⚠️ TAKE PROFIT — at 1-mo target 5.10. DC + utilities strong. Trim, trail stop 4.50."),
 dict(tk="STECON",nm="Stecon Group",ex="SET",sym="STECON.BK",cur="THB",tier=1,th="Construction / new data-center unit",
   conv=4,st="Trim",entry=13.10,stop=16,t=[18,20,22],cagr=0.10,ed="2026-05-15",cs="2026-06-06",
   note="⚠️ TAKE PROFIT — through 6-mo target; 7-day +10%. New DC unit; PPP bids. Trim, raise stop to 16; targets bumped."),
 dict(tk="GULF",nm="Gulf Development",ex="SET",sym="GULF.BK",cur="THB",tier=1,th="Power / AI-DC + renewables",
   conv=4,st="Hold",entry=59.25,stop=56,t=[66,70,75],cagr=0.13,ed="2026-05-15",cs="2026-05-15",
   note="Steady. THB140bn AI/DC + renewables plan; lower oil = lower gas-cost tailwind. Stop raised to 56."),
 dict(tk="CK",nm="CH. Karnchang",ex="SET",sym="CK.BK",cur="THB",tier=1,th="Construction / PPP + Land Bridge",
   conv=4,st="Hold",entry=17.70,stop=17,t=[21,23,25],cagr=0.12,ed="2026-05-15",cs="2026-05-15",
   note="Through 1-mo target; 7-day +7.4%. Breaking out with STECON on PPP/Land-Bridge. Upgraded ⭐⭐⭐→⭐⭐⭐⭐; stop to 17."),
 dict(tk="BS6",nm="Yangzijiang Shipbuilding",ex="SGX",sym="BS6.SI",cur="SGD",tier=1,th="Shipbuilding / order backlog",
   conv=2,st="Avoid",entry=4.31,stop=3.90,t=None,cagr=0.10,ed="2026-05-15",cs="2026-06-20",approx=3.60,
   note="🚨 REMOVED v5.0 — broke S$3.90 stop to ~S$3.60 on weak order momentum. Honor stop / exit. SGX price approx — verify."),
 dict(tk="S63",nm="ST Engineering",ex="SGX",sym="S63.SI",cur="SGD",tier=1,th="Defense / engineering",
   conv=4,st="Hold",entry=11.00,stop=9.90,t=[11.50,12.00,12.20],cagr=0.09,ed="2026-05-15",cs="2026-05-15",approx=10.83,
   note="Roughly flat (ex-div). Record S$33.2bn order book; defense backlog intact. SGX price approx."),
 # Tier 2
 dict(tk="688256",nm="Cambricon Technologies",ex="SSE",sym="688256.SHG",cur="CNY",tier=2,th="China AI chips",
   conv=3,st="Trim",entry=1209.0,stop=1250,t=[1550,1800,1700],cagr=0.15,ed="2026-05-15",cs="2026-06-06",
   note="⚠️ TAKE PROFIT — +21.6% one-session spike on Q1 (rev +160%, profit +185%). Through ¥1,500 base. Trim, ≤5-7% max; stop up to 1,250."),
 dict(tk="600111",nm="China Rare Earth (CNRE)",ex="SSE",sym="600111.SHG",cur="CNY",tier=2,th="Rare earth / Nov Wave-2 catalyst",
   conv=4,st="Hold",entry=53.27,stop=44,t=[54,60,62],cagr=0.10,ed="2026-05-14",cs="2026-06-20",
   note="↗️ IMPROVING — +8.2% in 7 days, divergence narrowing. Q2 concentrate +44.6% QoQ. Hold for Nov Wave-2; stop up to 44."),
 dict(tk="0981",nm="SMIC",ex="HKEX",sym="0981.HK",cur="HKD",tier=2,th="China foundry / semi self-sufficiency",
   conv=4,st="Hold",entry=79.45,stop=66,t=[82,90,100],cagr=0.12,ed="2026-05-15",cs="2026-06-20",
   note="↗️ GRADUATED off alert — +11.4% 1-mo recovery; self-sufficiency thesis converting (capacity doubling). Accumulate on dips. ⭐⭐⭐→⭐⭐⭐⭐."),
 dict(tk="9988",nm="Alibaba Group",ex="HKEX",sym="9988.HK",cur="HKD",tier=2,th="China tech / AI (Qwen) / cloud",
   conv=1,st="Avoid",entry=135.10,stop=100,t=None,cagr=0.12,ed="2026-05-15",cs="2026-06-20",
   note="🚨 REMOVED v5.0 — within ~5% of HK$100 stop. H200-import flow dead, theme rotated to domestic suppliers. Exit into any bounce."),
 # Tier 3 — watch (trigger-based, no entry/targets)
 dict(tk="0700",nm="Tencent Holdings",ex="HKEX",sym="0700.HK",cur="HKD",tier=3,th="China tech / AI / cloud",
   conv=4,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-15",
   note="⭐ TOP IDEA #1 — cheapest large China-AI proxy, no US-chip dependency (P/E ~16, net cash, buyback). Accumulate <HK$455."),
 dict(tk="3750",nm="CATL (HK)",ex="HKEX",sym="3750.HK",cur="HKD",tier=3,th="EV battery / storage",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-15",
   note="⭐ TOP IDEA #2 — storage/ESS super-cycle + ~37% global share + JPM upgrade; +7% 7-day. Momentum add, size moderate (rich multiple)."),
 dict(tk="U96",nm="Sembcorp Industries",ex="SGX",sym="U96.SI",cur="SGD",tier=3,th="Power-for-AI / renewables",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-15",approx=6.31,
   note="⭐ TOP IDEA #3 — power-for-AI + renewables, ~3% yield, P/E ~9, TP ~6.89. Accumulate ~S$6.10-6.35. SGX price approx."),
 dict(tk="0941",nm="China Mobile",ex="HKEX",sym="0941.HK",cur="HKD",tier=3,th="China AI-compute / dividend",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-20",
   note="⭐ NEW WATCH — 'East-Data-West-Compute' AI-capex + ~5% dividend, ~10x P/E (approx). Low-beta China-AI into a hawkish Fed."),
 dict(tk="AJBU",nm="Keppel DC REIT",ex="SGX",sym="AJBU.SI",cur="SGD",tier=3,th="Data-center REIT",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",approx=2.27,
   note="NOT triggered — wants yield >5% or price <S$2.10 (now ~2.27). Rate-sensitive into a hawkish dot-plot. SGX approx."),
 dict(tk="PTTEP",nm="PTT Exploration & Prod.",ex="SET",sym="PTTEP.BK",cur="THB",tier=3,th="Oil & gas / E&P",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="DE-ELEVATED — oil leverage a headwind as Brent fades ~$80 (−12.7% 1-mo). Re-engage only if Iran talks collapse into a Hormuz shock."),
 dict(tk="0883",nm="CNOOC",ex="HKEX",sym="0883.HK",cur="HKD",tier=3,th="Oil major",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="DE-ELEVATED / dropped from ideas — ~HK$22.38, −16% 1-mo. Re-engage only if oil re-rates up."),
 dict(tk="3311",nm="China State Constr. Intl",ex="HKEX",sym="3311.HK",cur="HKD",tier=3,th="Construction / BRI",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="−13% on the week; needs a fresh Belt-and-Road mega-project win. Keep on watch, no action."),
 dict(tk="SIRI",nm="Sansiri",ex="SET",sym="SIRI.BK",cur="THB",tier=3,th="Property",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="Thai property cycle still weak — not yet. Monitor for a sector turn."),
 dict(tk="PROUD",nm="Proud Real Estate",ex="SET",sym="PROUD.BK",cur="THB",tier=3,th="Small-cap property",
   conv=1,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="Thin small-cap; property cycle weak. Watch only."),
 dict(tk="SPALI",nm="Supalai",ex="SET",sym="SPALI.BK",cur="THB",tier=3,th="Property",
   conv=1,st="Avoid",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="AVOID (yield trap) — 35% EPS decline in 2025; Thai property weak. Not a buy."),
]

def build(c):
    sym = c["sym"]; ser = S.get(sym)
    h = {"ticker":c["tk"],"name":c["nm"],"exchange":c["ex"],"currency":c["cur"],"tier":c["tier"],
         "theme":c["th"],"conviction":c["conv"],"status":c["st"],"note":c["note"],
         "source":"eodhd" if sym in S else "yahoo","symbol":sym,
         "entry":c["entry"],"stop":c["stop"],"entry_date":c["ed"],"entry_date_fmt":fmt(c["ed"]),
         "condition_since":c["cs"],"condition_since_fmt":fmt(c["cs"]),
         "days_on_condition":(ASOF - dt.date(*map(int,c["cs"].split("-")))).days if c.get("cs") else 0}
    if ser:
        last = ser[-1]; e = ema(ser, 50)
        h.update(last=r2(last),spark=ser,error=None,spark_from=SPARK_FROM,spark_to=SPARK_TO,spark_tf="3M",
                 chg_1d=round((last/ser[-2]-1)*100,2),chg_1m=round((last/ser[-5]-1)*100,2),chg_3m=round((last/ser[0]-1)*100,2),
                 ema50=r2(e),trend_up=last>=e,hi_52w=r2(max(ser)),lo_52w=r2(min(ser)),
                 range_pos=round((last-min(ser))/(max(ser)-min(ser))*100,0) if max(ser)>min(ser) else 50)
    else:  # SGX web-approx: price, no chart
        last = c.get("approx")
        h.update(last=r2(last),spark=[],error=None,spark_from=None,spark_to=None,spark_tf=None,
                 chg_1d=None,chg_1m=None,chg_3m=None,ema50=None,trend_up=None,hi_52w=None,lo_52w=None,range_pos=None)
    entry, stop = c["entry"], c["stop"]; t = c["t"] or []
    t1 = t[0] if len(t)>0 else None; t6 = t[1] if len(t)>1 else None; t12 = t[2] if len(t)>2 else None
    h["pct_vs_entry"] = round((last/entry-1)*100,1) if (entry and last) else None
    h["dist_to_stop"] = round((last/stop-1)*100,1) if (stop and last) else None
    h["suggest_entry"] = r2(max(stop*1.02,last*0.93)) if (stop and last and c["st"] not in ("Avoid",)) else None
    above = [x for x in (t1,t6,t12) if x and last and x>last]
    if above: h["suggest_exit"]=r2(min(above)); h["targets_met"]=False
    elif t1: h["suggest_exit"]=r2(max([x for x in (t1,t6,t12) if x])); h["targets_met"]=True
    else: h["suggest_exit"]=None; h["targets_met"]=None
    h["reward_risk"] = round((t12-last)/(last-stop),2) if (t12 and stop and last and last>stop) else None
    t3 = interp3(t1,t6); g = c["cagr"] or 0
    h["upside"] = {"3mo":round((t3/last-1)*100,1) if (t3 and last) else None,
                   "6mo":round((t6/last-1)*100,1) if (t6 and last) else None,
                   "12mo":round((t12/last-1)*100,1) if (t12 and last) else None,
                   "3yr":round((t12*(1+g)**2/last-1)*100,1) if (t12 and last) else None,
                   "5yr":round((t12*(1+g)**4/last-1)*100,1) if (t12 and last) else None}
    return h

holds = [build(c) for c in CFG]
scored = sorted([h for h in holds if h.get("chg_3m") is not None], key=lambda h:h["chg_3m"]); n=len(scored)
for i,h in enumerate(scored): h["rs"]=round(i/max(n-1,1)*99+1)
for h in holds: h.setdefault("rs",None)

awaiting = sum(1 for h in holds if not h["spark"])
data = {"meta":{"title":"STOCK Monitor — Daily","generated":GEN,"asof":"2026-06-19",
                "version":"v5.0","awaiting_sync":awaiting,"count":len(holds),
                "note":"Prices: EODHD main-board closes — TH Fri Jun 19; HK/China-A Thu Jun 18. SGX web-approx (labelled). NOT financial advice."},
        "holdings":holds}
json.dump(data, open("data.json","w"), ensure_ascii=False, indent=2)
open("data.js","w").write("window.DASHBOARD_DATA = "+json.dumps(data, ensure_ascii=False)+";\n")

# regenerate watchlist.json config from CFG
wl = {"meta":{"title":"STOCK Monitor — Daily","owner":"ToR","schema_version":2,"source_version":"v5.0 (2026-06-20)",
              "note":"Absolute price targets. Upside computed live vs latest close. NOT financial advice."},
      "holdings":[{"ticker":c["tk"],"name":c["nm"],"exchange":c["ex"],"source":"eodhd" if c["sym"] in S else "yahoo",
                   "symbol":c["sym"],"currency":c["cur"],"tier":c["tier"],"theme":c["th"],"conviction":c["conv"],
                   "status":c["st"],"entry":c["entry"],"stop":c["stop"],
                   "target_1mo":(c["t"] or [None])[0] if c["t"] else None,
                   "target_6mo":c["t"][1] if c["t"] else None,"target_12mo":c["t"][2] if c["t"] else None,
                   "cagr_long":c["cagr"],"entry_date":c["ed"],"condition_since":c["cs"],"note":c["note"]} for c in CFG]}
json.dump(wl, open("watchlist.json","w"), ensure_ascii=False, indent=2)
print("v5.0 sync done", GEN, "| holdings", len(holds), "| awaiting", awaiting)
print("status counts:", {s:sum(1 for h in holds if h["status"]==s) for s in ["Hold","Trim","Reduce","Watch","Avoid"]})
