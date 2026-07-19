"""Refresh ranking-tab prices to Fri Jun 26 closes (US/China/Thai live snapshots).
RESEARCH stays the 2026-06-21 live-regenerated set — only last/spark-tip/chg_3m/buy/tp move."""
import json, datetime as dt
GEN = "2026-06-27 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
PR = {
 ("us_top10.json","US_TOP10"): {"NVDA":192.53,"AAPL":283.78,"TSLA":379.71,"MSFT":372.97,"AMZN":232.69,
   "GOOGL":337.39,"META":550.25,"BRK-B":498.66,"LLY":1208.12,"WMT":115.69},
 ("china_top10.json","CHINA_TOP10"): {"601138.SH":70.22,"300308.SZ":1253.89,"300750.SZ":381.0,"300502.SZ":566.0,
   "688256.SH":1458,"300394.SZ":318.0,"688041.SH":344.9,"688981.SH":148.76,"603986.SH":770.0,"002594.SZ":78.2},
 ("th_top10.json","TH_TOP10"): {"GULF":59.75,"ADVANC":351,"AOT":62.25,"CPALL":45.0,"KTB":36.5,"KBANK":214,
   "BBL":176,"CPN":66.75,"BDMS":18.9,"MINT":24.8},
}
ASOF = "26 Jun 2026"
for (fn,var),prices in PR.items():
    j = json.load(open(fn))
    for n in j["names"]:
        p = prices.get(n["ticker"])
        if p is None: continue
        sp = n.get("spark") or []
        if sp: sp[-1] = p; n["chg_3m"] = round((p/sp[0]-1)*100,2)
        n["last"] = p; n["spark_to"] = ASOF.replace(" 2026","-26").replace("Jun","Jun")
        b3 = (n.get("base") or {}).get("3m",0)
        n["buy"] = round(p*0.93,2); n["tp"] = round(p*(1+b3/100),2)
    j["meta"]["generated"] = GEN
    j["meta"]["prices_asof"] = ASOF + " (research " + j["meta"].get("reference_date","2026-06-21") + ")"
    json.dump(j,open(fn,"w"),ensure_ascii=False,indent=2)
    open(fn.replace(".json",".js"),"w").write("window."+var+" = "+json.dumps(j,ensure_ascii=False)+";\n")
    print(fn,"prices ->",ASOF,"| #1",j["names"][0]["ticker"],j["names"][0]["last"])
print("ranking price refresh done",GEN)
