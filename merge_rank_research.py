"""Merge live 06-21 research (web-sourced, from _res_*.json) into the ranking tabs:
reorder by current CUS, refresh sector/driver/risk/guide/backlog/cash/bull/base,
fold latest quarter into guide, recompute tp from the new base case. Keep prices
(already current), 8Q earnings bars, spark, cus."""
import json, datetime as dt
GEN = "2026-06-21 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
FILES = [("us_top10.json","US_TOP10","_res_us.json"),
         ("china_top10.json","CHINA_TOP10","_res_cn.json"),
         ("th_top10.json","TH_TOP10","_res_th.json")]
for fn, var, rf in FILES:
    j = json.load(open(fn)); res = json.load(open(rf))
    ex = {n["ticker"]: n for n in j["names"]}
    out = []
    for r in res["names"]:
        n = ex.get(r["ticker"])
        if not n:
            print("  WARN new ticker not in prior roster:", r["ticker"]); continue
        n["name"] = r.get("name", n.get("name"))
        for k in ("sector","driver","risk","backlog","cash","bull","base"):
            if k in r: n[k] = r[k]
        lq = r.get("latest_quarter")
        n["guide"] = (r.get("guide","") + (("  ·  Latest: " + lq) if lq else "")).strip()
        n["latest_quarter"] = lq
        b3 = (r.get("base") or {}).get("3m", 0)
        if n.get("last") is not None:
            n["buy"] = round(n["last"]*0.93, 2)
            n["tp"]  = round(n["last"]*(1+b3/100), 2)
        out.append(n)
    j["names"] = out
    m = j["meta"]
    m["reference_date"] = res["reference_date"]
    m["generated"] = GEN
    m["market_note"] = res["market_note"]
    m["research_asof"] = "2026-06-21 (live web research)"
    if "prices_asof" in m: m["prices_asof"] = m["prices_asof"].replace("2026-06-04","2026-06-21")
    json.dump(j, open(fn,"w"), ensure_ascii=False, indent=2)
    open(fn.replace(".json",".js"),"w").write("window."+var+" = "+json.dumps(j, ensure_ascii=False)+";\n")
    print(fn, "-> reordered", len(out), "names | ref", res["reference_date"], "| order:", [n["ticker"] for n in out])
print("merge done", GEN)
