"""Refresh ranking-tab prices to current EODHD closes (US/China = Thu Jun 18,
TH = Fri Jun 19). RESEARCH (rosters, drivers, earnings) stays the 2026-06-04
report — only last/spark-tip/chg_3m/buy/tp move. Flag vintage in meta."""
import json, datetime as dt
GEN = "2026-06-20 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
PR = {
 ("us_top10.json","US_TOP10","18-Jun-26"): {"NVDA":210.69,"AAPL":298.01,"TSLA":400.49,"MSFT":379.4,
   "AMZN":244.39,"GOOGL":368.03,"META":577.22,"BRK-B":489.46,"LLY":1098.57,"WMT":117.18},
 ("china_top10.json","CHINA_TOP10","18-Jun-26"): {"601138.SH":78.08,"300308.SZ":1367.88,"300750.SZ":391.55,
   "300502.SZ":581.48,"688256.SH":1507.46,"300394.SZ":336.6,"688041.SH":328.0,"688981.SH":140.7,
   "603986.SH":629.0,"002594.SZ":88.13},
 ("th_top10.json","TH_TOP10","19-Jun-26"): {"GULF":63.75,"ADVANC":357,"AOT":59.75,"CPALL":46.25,"KTB":36.25,
   "KBANK":207,"BBL":175,"CPN":65,"BDMS":18.3,"MINT":24.6},
}
for (fn, var, asof), prices in PR.items():
    j = json.load(open(fn))
    for n in j["names"]:
        p = prices.get(n["ticker"])
        if p is None: continue
        sp = n.get("spark") or []
        if sp: sp[-1] = p
        n["last"] = p
        n["spark_to"] = asof
        if sp: n["chg_3m"] = round((p/sp[0]-1)*100, 2)
        b3 = (n.get("base") or {}).get("3m", 0)
        n["buy"] = round(p*0.93, 2)
        n["tp"] = round(p*(1+b3/100), 2)
    j["meta"]["generated"] = GEN
    j["meta"]["prices_asof"] = asof.replace("-Jun-26", " Jun 2026") + " (research " + j["meta"].get("reference_date","2026-06-04") + ")"
    json.dump(j, open(fn,"w"), ensure_ascii=False, indent=2)
    open(fn.replace(".json",".js"),"w").write("window."+var+" = "+json.dumps(j, ensure_ascii=False)+";\n")
    print(fn, "->", var, "| prices", asof, "| names", len(j["names"]))
print("ranking refresh done", GEN)
