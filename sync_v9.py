"""Rebuild the Watchlist tab from 02_WATCHLIST v9.0 (2026-07-18). Fresh EODHD weekly
closes to Fri Jul 17; SGX web-approx. v9.0 = dovish CPI (3.5% miss) + AI-chip crack:
Cambricon stop breached->Avoid, SMIC->Reduce (2.6% from stop), CK->Watch, GULF breakout
(targets/stop raised, conv5), KTB->new position, AJBU->Top Idea #2, Alibaba re-entry triggered."""
import json, datetime as dt
ASOF = dt.date(2026, 7, 17)
GEN = "2026-07-18 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def fmt(d):
    if not d: return None
    y,m,da = map(int,d.split("-")); return f"{da:02d}-{MON[m-1]}-{str(y)[2:]}"
def r2(x): return round(x,2) if x is not None else None
def ema(v,span):
    if not v: return None
    k=2/(span+1); e=v[0]
    for x in v[1:]: e=x*k+e*(1-k)
    return e
def interp3(t1,t6):
    if not t1 or not t6 or t1<=0 or t6<=0: return None
    return t1*(t6/t1)**0.4
S = {
 "AMATA.BK":[19.7,20.5,20.3,20.6,20.8,21.4,25,24.5,26,26.25,26.5,26.5,26.75,28.5,27.5],
 "WHA.BK":[4.28,4.4,4.38,4.48,4.7,4.68,5,4.9,5.05,4.98,5,5.05,5.2,5.45,5.45],
 "STECON.BK":[11.9,12,11.5,12,13.9,13.1,14.2,15.7,16.2,17,18.7,18.1,18.4,18.8,18.1],
 "CK.BK":[16.6,17.2,16.5,17,18.9,17.8,18.2,18,18.9,18.8,20.2,19.7,19.5,19.8,18.5],
 "GULF.BK":[59.5,57.75,56,57.5,60,59.75,60.75,62,67,64,64,59.75,63.5,63.5,67.5],
 "ADVANC.BK":[363,353,349,340,350,365,355,353,361,366,357,352,375,373,379],
 "BDMS.BK":[18.6,18.7,18.5,18.3,18.4,18.3,18.1,18.2,18.4,18,18.3,18.9,20.1,19.6,19.7],
 "KBANK.BK":[192,189,190,194,195,196.5,197,201,201,203,207,215,233,232,234],
 "BBL.BK":[166,164.5,158.5,162.5,163,165,168.5,173,174.5,172.5,175,176,192.5,196.5,202],
 "KTB.BK":[33,31.25,32.25,33,32.75,34.25,34.75,34.75,35.25,35.25,36,36.5,40,40.75,41.5],
 "SCB.BK":[145.5,145,129.5,131,132,133,135,134.5,141,140,141,145,153.5,156.5,157],
 "PTTEP.BK":[151.5,145,149.5,154,148.5,150,151,141.5,144.5,142.5,134,130,131.5,139.5,145.5],
 "SIRI.BK":[1.42,1.41,1.41,1.4,1.41,1.42,1.43,1.43,1.4,1.41,1.44,1.42,1.46,1.47,1.5],
 "SPALI.BK":[16.4,16.5,16.7,16.2,15.3,15.4,15.5,15.5,15.6,15.6,15.7,15.6,16.4,15.9,16],
 "PROUD.BK":[1.01,1.03,1.04,0.98,0.96,0.95,0.92,0.95,0.93,0.94,1.02,1.01,1.03,1.02,1.11],
 "0700.HK":[504.5,510.5,493.4,467.8,471.4,456.4,441.4,427.2,453.2,463.6,440.2,411.8,431.2,460.2,461.6],
 "3750.HK":[681.5,692,695,608,651,680,686,744.5,711,672.5,708.5,680.5,675.5,587,606.5],
 "0941.HK":[81.1,81.45,83.9,84.6,85.45,86.2,85.5,85.15,82.4,81.8,80.1,77.4,76.7,78.75,79.95],
 "0981.HK":[58.25,59.35,64.3,70.9,73.35,71.15,79.85,81.6,75.65,71.65,76.5,80,77.6,79.65,67.7],
 "9988.HK":[125.5,136.4,131.8,126,139,132.3,127,120.9,122.4,110.2,104.9,89.5,94.1,110.2,112.6],
 "0883.HK":[26.52,26.98,27.9,29.38,26.44,26.42,27.44,26.4,26.54,24.92,22.38,20.86,21.18,21.82,22.72],
 "3311.HK":[8.67,8.69,8.92,9.07,9.38,9.34,8.9,8.75,8.98,8.76,7.59,7.02,7.22,7.35,7.82],
 "688256.SHG":[1210.7,1334,1352.5,1699.96,1182.53,1209,1286,1310,1299.2,1240,1507.46,1458,1353,1400,1190.58],
 "600111.SHG":[51.75,49.22,47.24,53.04,54.75,53.78,51.09,48.62,49.66,49.43,51.4,47.26,48.57,42.51,37.45],
}
SPARK_FROM, SPARK_TO = "07-Apr-26", "17-Jul-26"
CFG = [
 dict(tk="AMATA",nm="Amata Corporation",ex="SET",sym="AMATA.BK",cur="THB",tier=1,th="Thai industrial estate / data-center capex",
   conv=5,st="Trim",entry=19.30,stop=25,t=[29,31,34],cagr=0.14,ed="2026-05-15",cs="2026-05-15",
   note="⚠️ TAKE PROFIT — off the high but +42.5% (1-mo +2.8%, 7-day −3.5%). Thai DC capex = haven. Hold trimmed ⅓, stop 25."),
 dict(tk="WHA",nm="WHA Corporation",ex="SET",sym="WHA.BK",cur="THB",tier=1,th="Industrial land + utilities / data-center",
   conv=4,st="Trim",entry=3.98,stop=4.80,t=[5.50,5.80,6.20],cagr=0.12,ed="2026-05-15",cs="2026-05-15",
   note="⚠️ TAKE PROFIT — at 6-mo target (1-mo +6.9%). DC + utilities. Trim, trail 4.80."),
 dict(tk="STECON",nm="Stecon Group",ex="SET",sym="STECON.BK",cur="THB",tier=1,th="Construction / new data-center unit",
   conv=4,st="Trim",entry=13.10,stop=16.5,t=[19,21,23],cagr=0.10,ed="2026-05-15",cs="2026-06-06",
   note="Cooling (1-mo +2.8%, 7-day −3.7%) but well through the 6-mo zone. DC unit + PPP/Land-Bridge bids. Keep trim, stop 16.5."),
 dict(tk="CK",nm="CH. Karnchang",ex="SET",sym="CK.BK",cur="THB",tier=1,th="Construction / PPP + Land Bridge",
   conv=3,st="Watch",entry=17.70,stop=17,t=[21,23,25],cagr=0.12,ed="2026-05-15",cs="2026-07-18",
   note="🔍 WATCH — rolled over (1-mo −5.6%, 7-day −6.6%) while the SET held. Above stop 17. Reduce if it loses 18. Cut ⭐⭐⭐⭐→⭐⭐⭐."),
 dict(tk="GULF",nm="Gulf Development",ex="SET",sym="GULF.BK",cur="THB",tier=1,th="Power / AI-DC + renewables",
   conv=5,st="Hold",entry=59.25,stop=60,t=[70,74,80],cagr=0.13,ed="2026-05-15",cs="2026-07-18",
   note="↗️ BREAKOUT — +6.3% wk, 1-mo +5.1% on power-for-AI + rate relief. THB140bn AI/DC + renewables. Raise stop to 60. Up ⭐⭐⭐⭐→⭐⭐⭐⭐⭐."),
 dict(tk="ADVANC",nm="Advanced Info Service",ex="SET",sym="ADVANC.BK",cur="THB",tier=1,th="Thai telecom / defensive dividend",
   conv=4,st="Hold",entry=375,stop=360,t=[392,420,440],cagr=0.09,ed="2026-07-05",cs="2026-07-05",
   note="Working (1-mo +5.9%). Defensive telecom + dividend. Consensus TP ~392. Hold, raise stop 360."),
 dict(tk="BDMS",nm="Bangkok Dusit Medical",ex="SET",sym="BDMS.BK",cur="THB",tier=1,th="Thai healthcare / defensive",
   conv=4,st="Hold",entry=20.10,stop=18.4,t=[21.5,24.5,26],cagr=0.10,ed="2026-07-05",cs="2026-07-05",
   note="Recovering to entry (1-mo +5.9%). Healthcare defensive, AI-immune. Strong-Buy, TP ~26. Hold, stop 18.4."),
 dict(tk="KBANK",nm="Kasikornbank",ex="SET",sym="KBANK.BK",cur="THB",tier=1,th="Thai bank / value + dividend",
   conv=4,st="Hold",entry=233,stop=218,t=[248,268,282],cagr=0.10,ed="2026-07-05",cs="2026-07-05",
   note="Consolidating a big move (1-mo +14.1%). Bank leadership on inflows + Q2 loan growth + dovish-CPI rate relief. ~P/E 8, ~4% yld. Raise stop 218."),
 dict(tk="BBL",nm="Bangkok Bank",ex="SET",sym="BBL.BK",cur="THB",tier=1,th="Thai bank / deep value + dividend",
   conv=5,st="Hold",entry=196.50,stop=185,t=[208,228,245],cagr=0.10,ed="2026-07-11",cs="2026-07-11",
   note="Working post-entry (1-mo +16.1%). Deep-value bank (P/E ~7, P/B ~0.6), ~5.4% yield, payout ~33%. Direct beneficiary of rate relief + loan growth + inflows. Raise stop 185."),
 dict(tk="KTB",nm="Krung Thai Bank",ex="SET",sym="KTB.BK",cur="THB",tier=1,th="Thai state bank / deep value",
   conv=5,st="Hold",entry=41.50,stop=37,t=[44,48,52],cagr=0.10,ed="2026-07-18",cs="2026-07-18",
   note="↗️ NEW — Top Idea #1. Deep-value state bank (P/E ~7, P/B ~0.6), ~5% yield, payout <50% (sustainable), 1-mo +16.1% breakout. Cleanest rate-relief + loan-growth beneficiary."),
 dict(tk="S63",nm="ST Engineering",ex="SGX",sym="S63.SI",cur="SGD",tier=1,th="Defense / engineering",
   conv=4,st="Hold",entry=11.00,stop=9.90,t=[11.50,12.00,12.20],cagr=0.09,ed="2026-05-15",cs="2026-05-15",approx=10.55,
   note="Below entry (ex-div). Record S$33.2bn order book (+49% new contracts). Defense backlog intact. Hold. SGX price approx."),
 dict(tk="0981",nm="SMIC",ex="HKEX",sym="0981.HK",cur="HKD",tier=2,th="China foundry / semi self-sufficiency",
   conv=2,st="Reduce",entry=79.45,stop=66,t=[None,85,95],cagr=0.12,ed="2026-05-15",cs="2026-07-18",
   note="🚨 REDUCE — −15% wk to HK$67.70, within 2.6% of the HK$66 stop (Jul-17 intraday low 66.25); 1-mo −10.6%. Global chip selloff (Meta Compute + memory) broke the re-strengthening thesis. Reduce; hard exit below 66. Cut ⭐⭐⭐⭐→⭐⭐."),
 dict(tk="688256",nm="Cambricon Technologies",ex="SSE",sym="688256.SHG",cur="CNY",tier=2,th="China AI chips",
   conv=1,st="Avoid",entry=1209.0,stop=1250,t=None,cagr=0.15,ed="2026-05-15",cs="2026-07-18",
   note="🚨 REMOVED — broke the ¥1,250 stop to ¥1,190.58; 1-mo −9.8%, 7-day −15%. AI-chip trade cracked (Meta Compute + STAR-50 reweight). Honor the stop; do not average down."),
 dict(tk="9988",nm="Alibaba Group",ex="HKEX",sym="9988.HK",cur="HKD",tier=3,th="China tech / AI (Qwen) / cloud",
   conv=3,st="Watch",entry=135.10,stop=100,t=None,cagr=0.12,ed="2026-05-15",cs="2026-07-18",
   note="↗️ RE-ENTRY TRIGGERED — 1-mo momentum turned POSITIVE (+5.3%, HK$112.6) above HK$100, the v8.0 trigger. DOJ deal + Qwen/Cloud re-rate intact; China Q2-GDP miss → late-July Politburo stimulus put. Starter ≤5%, add above HK$115, stop HK$100. Jul-17 −3.7% wobble → scale in, don't chase."),
 dict(tk="AJBU",nm="Keppel DC REIT",ex="SGX",sym="AJBU.SI",cur="SGD",tier=3,th="Data-center REIT",
   conv=4,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-07-18",approx=2.29,
   note="↗️ TOP IDEA #2 — dovish CPI relieves the rate headwind that capped it. Data-center demand structural; long leases = backlog. Strong-Buy (~14 analysts, TP ~2.63). Accumulate <S$2.35. SGX approx."),
 dict(tk="U96",nm="Sembcorp Industries",ex="SGX",sym="U96.SI",cur="SGD",tier=3,th="Power-for-AI / renewables",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-15",approx=5.60,
   note="TOP IDEA #3 candidate — power-for-AI + renewables + gas; long-dated PPAs = backlog. ~P/E 9, ~4.4% yield. Dovish CPI helps. Accumulate ~S$5.50-5.70. SGX approx."),
 dict(tk="0700",nm="Tencent Holdings",ex="HKEX",sym="0700.HK",cur="HKD",tier=3,th="China tech / AI / cloud",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-27",
   note="~HK$461.6, 1-mo +3.6%. Re-rating with the China-internet bid + stimulus hopes. Cheap (P/E ~16, net cash, buyback). Re-engage on momentum confirmation."),
 dict(tk="SCB",nm="SCB X",ex="SET",sym="SCB.BK",cur="THB",tier=3,th="Thai bank / high yield",
   conv=3,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-07-05",
   note="Value/yield backstop — ~THB 157, 1-mo +16.8%; ~8% yield but payout high (~80%) → KTB/BBL/KBANK preferred on the AMATA profile."),
 dict(tk="0941",nm="China Mobile",ex="HKEX",sym="0941.HK",cur="HKD",tier=3,th="China AI-compute / dividend",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-20",
   note="~HK$79.95, 1-mo −1.1% (bounced +1.5% wk). ~5% dividend, ~10x P/E. Accumulate only if it stops falling."),
 dict(tk="PTTEP",nm="PTT Exploration & Prod.",ex="SET",sym="PTTEP.BK",cur="THB",tier=3,th="Oil & gas / E&P",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="~THB 145.5, 1-mo +2.5%, 7-day +4.3% on an oil bounce. Re-engage only on a Hormuz/supply shock."),
 dict(tk="0883",nm="CNOOC",ex="HKEX",sym="0883.HK",cur="HKD",tier=3,th="Oil major",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="~HK$22.72, 1-mo −0.5% (bounced +4.1% wk). Re-engage only if oil re-rates up."),
 dict(tk="3311",nm="China State Constr. Intl",ex="HKEX",sym="3311.HK",cur="HKD",tier=3,th="Construction / BRI",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="~HK$7.82, 1-mo −2.0% (bounced +6.1% wk); needs a fresh Belt-and-Road mega-project win."),
 dict(tk="SIRI",nm="Sansiri",ex="SET",sym="SIRI.BK",cur="THB",tier=3,th="Property",
   conv=2,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="~1.50; dovish CPI is a mild tailwind for property. Not yet."),
 dict(tk="PROUD",nm="Proud Real Estate",ex="SET",sym="PROUD.BK",cur="THB",tier=3,th="Small-cap property",
   conv=1,st="Watch",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="Thin small-cap; popped +8.8% wk on the property bid. Watch only."),
 dict(tk="600111",nm="China Rare Earth (CNRE)",ex="SSE",sym="600111.SHG",cur="CNY",tier=3,th="Rare earth",
   conv=1,st="Avoid",entry=53.27,stop=44,t=None,cagr=0.10,ed="2026-05-14",cs="2026-07-11",
   note="🚨 REMOVED v8.0, confirmed — ¥44 stop breached; now ¥37.45 (1-mo −25.6%). Rare-earth momentum broke. Stay out."),
 dict(tk="3750",nm="CATL (HK)",ex="HKEX",sym="3750.HK",cur="HKD",tier=3,th="EV battery / storage",
   conv=2,st="Avoid",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-07-11",
   note="🚨 AVOID — 1-mo −14.7%; small +3.3% bounce but lithium-price + AI-storage-capex caution persists. Storage cycle intact long-term; near-term FLOW negative. Do not initiate."),
 dict(tk="SPALI",nm="Supalai",ex="SET",sym="SPALI.BK",cur="THB",tier=3,th="Property",
   conv=1,st="Avoid",entry=None,stop=None,t=None,cagr=0,ed=None,cs="2026-06-08",
   note="AVOID (yield trap) — 35% EPS decline in 2025. Dovish CPI a mild tailwind but thesis unchanged."),
 dict(tk="BS6",nm="Yangzijiang Shipbuilding",ex="SGX",sym="BS6.SI",cur="SGD",tier=1,th="Shipbuilding / order backlog",
   conv=1,st="Avoid",entry=4.31,stop=3.90,t=None,cagr=0.10,ed="2026-05-15",cs="2026-06-20",approx=3.53,
   note="🚨 REMOVED — stop breached (~S$3.53 < S$3.90), weak order momentum. Exit. SGX price approx."),
]
def build(c):
    sym=c["sym"]; ser=S.get(sym)
    h={"ticker":c["tk"],"name":c["nm"],"exchange":c["ex"],"currency":c["cur"],"tier":c["tier"],"theme":c["th"],
       "conviction":c["conv"],"status":c["st"],"note":c["note"],"source":"eodhd" if sym in S else "yahoo","symbol":sym,
       "entry":c["entry"],"stop":c["stop"],"entry_date":c["ed"],"entry_date_fmt":fmt(c["ed"]),
       "condition_since":c["cs"],"condition_since_fmt":fmt(c["cs"]),
       "days_on_condition":(ASOF-dt.date(*map(int,c["cs"].split("-")))).days if c.get("cs") else 0}
    if ser:
        last=ser[-1]; e=ema(ser,50)
        h.update(last=r2(last),spark=ser,error=None,spark_from=SPARK_FROM,spark_to=SPARK_TO,spark_tf="3M",
                 chg_1d=round((last/ser[-2]-1)*100,2),chg_1m=round((last/ser[-5]-1)*100,2),chg_3m=round((last/ser[0]-1)*100,2),
                 ema50=r2(e),trend_up=last>=e,hi_52w=r2(max(ser)),lo_52w=r2(min(ser)),
                 range_pos=round((last-min(ser))/(max(ser)-min(ser))*100,0) if max(ser)>min(ser) else 50)
    else:
        last=c.get("approx")
        h.update(last=r2(last),spark=[],error=None,spark_from=None,spark_to=None,spark_tf=None,chg_1d=None,chg_1m=None,
                 chg_3m=None,ema50=None,trend_up=None,hi_52w=None,lo_52w=None,range_pos=None)
    entry,stop=c["entry"],c["stop"]; t=c["t"] or []
    t1=t[0] if len(t)>0 else None; t6=t[1] if len(t)>1 else None; t12=t[2] if len(t)>2 else None
    h["pct_vs_entry"]=round((last/entry-1)*100,1) if (entry and last) else None
    h["dist_to_stop"]=round((last/stop-1)*100,1) if (stop and last) else None
    h["suggest_entry"]=r2(max(stop*1.02,last*0.93)) if (stop and last and c["st"] not in ("Avoid","Reduce")) else None
    above=[x for x in (t1,t6,t12) if x and last and x>last]
    if above: h["suggest_exit"]=r2(min(above)); h["targets_met"]=False
    elif t6 or t12 or t1: h["suggest_exit"]=r2(max([x for x in (t1,t6,t12) if x])); h["targets_met"]=True
    else: h["suggest_exit"]=None; h["targets_met"]=None
    h["reward_risk"]=round((t12-last)/(last-stop),2) if (t12 and stop and last and last>stop) else None
    t3=interp3(t1,t6); g=c["cagr"] or 0
    h["upside"]={"3mo":round((t3/last-1)*100,1) if (t3 and last) else None,"6mo":round((t6/last-1)*100,1) if (t6 and last) else None,
                 "12mo":round((t12/last-1)*100,1) if (t12 and last) else None,"3yr":round((t12*(1+g)**2/last-1)*100,1) if (t12 and last) else None,
                 "5yr":round((t12*(1+g)**4/last-1)*100,1) if (t12 and last) else None}
    return h
holds=[build(c) for c in CFG]
scored=sorted([h for h in holds if h.get("chg_3m") is not None],key=lambda h:h["chg_3m"]); n=len(scored)
for i,h in enumerate(scored): h["rs"]=round(i/max(n-1,1)*99+1)
for h in holds: h.setdefault("rs",None)
awaiting=sum(1 for h in holds if not h["spark"])
data={"meta":{"title":"STOCK Monitor — Daily","generated":GEN,"asof":"2026-07-17","version":"v9.0","awaiting_sync":awaiting,
              "count":len(holds),"note":"Prices: EODHD main-board closes to Fri Jul 17 (TH/HK/China-A/US). SGX web-approx (labelled). NOT financial advice."},
      "holdings":holds}
json.dump(data,open("data.json","w"),ensure_ascii=False,indent=2)
open("data.js","w").write("window.DASHBOARD_DATA = "+json.dumps(data,ensure_ascii=False)+";\n")
wl={"meta":{"title":"STOCK Monitor — Daily","owner":"ToR","schema_version":2,"source_version":"v9.0 (2026-07-18)",
            "note":"Absolute price targets. Upside computed live vs latest close. NOT financial advice."},
    "holdings":[{"ticker":c["tk"],"name":c["nm"],"exchange":c["ex"],"source":"eodhd" if c["sym"] in S else "yahoo","symbol":c["sym"],
                 "currency":c["cur"],"tier":c["tier"],"theme":c["th"],"conviction":c["conv"],"status":c["st"],"entry":c["entry"],
                 "stop":c["stop"],"target_1mo":(c["t"][0] if c["t"] else None),"target_6mo":(c["t"][1] if c["t"] else None),
                 "target_12mo":(c["t"][2] if c["t"] else None),"cagr_long":c["cagr"],"entry_date":c["ed"],"condition_since":c["cs"],"note":c["note"]} for c in CFG]}
json.dump(wl,open("watchlist.json","w"),ensure_ascii=False,indent=2)
print("v9.0 sync done",GEN,"| holdings",len(holds),"| awaiting",awaiting)
print("status:",{s:sum(1 for h in holds if h["status"]==s) for s in ["Hold","Trim","Reduce","Watch","Avoid"]})
