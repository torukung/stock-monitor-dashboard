"""Light refresh of recap.js to this week: country-group prices (from the
refreshed data.json / us_top10.json) + this-week macro headline grounded in the
06-14 drop-screen task output. The full catalyst / moving-in-out re-evaluation is
the stock-thchinaus-weekly-scraping task's job (it has not run this week)."""
import json, datetime as dt

GEN = "2026-06-15 " + dt.datetime.utcnow().strftime("%H:%M") + " UTC"
wl = {h["ticker"]: h for h in json.load(open("data.json"))["holdings"]}
us = {n["ticker"]: n for n in json.load(open("us_top10.json"))["names"]}

def us_1m(n):
    s = n.get("spark") or []
    return round((n["last"]/s[-5]-1)*100, 1) if len(s) >= 5 and n.get("last") else None

R = json.load(open("recap.json"))
R["meta"]["generated"] = GEN
R["meta"]["asof"] = "2026-06-13"
R["recap"]["headline"] = "US–Iran draft MOU sparks a regional relief rally; AI-semis firm into the Jun 16-17 FOMC."
R["recap"]["bullets"] = [
    "Draft 14-point US–Iran MOU (lift oil sanctions, reopen Hormuz, unfreeze assets) drove a Fri Jun 12 relief rally — Nikkei +2.8%, Kospi +4.6%, HK +1.9%; SET recovered toward 1,600 (~1,593).",
    "AI-semi / data-center leadership intact (Innolight, Cambricon, AMATA, GULF, STECON); oil names (PTTEP, CNOOC) softening as the Iran risk premium unwinds.",
    "Fed FOMC Jun 16-17 is the week's swing factor; US space names whipsawed by SpaceX's blockbuster Nasdaq IPO on Jun 12.",
]
R["outlook"]["bull_1m"] = 52
R["outlook"]["note"] = ("Relief rally on US–Iran de-escalation lifts near-term odds; FOMC Jun 16-17 is the swing. "
                         "Structural AI/data-center plus the energy-premium unwind favor selective names over 6-36 months.")

for c in R["countries"]:
    for s in c["stocks"]:
        tk = s["ticker"]
        src = wl.get(tk) or us.get(tk)
        if not src:
            continue
        s["last"] = src.get("last")
        cm = src.get("chg_1m") if tk in wl else us_1m(src)
        s["chg_1m"] = cm
        s["trend"] = "up" if (cm or 0) > 1 else "down" if (cm or 0) < -1 else "flat"

for m in R.get("moving_in", []) + R.get("moving_out", []):
    src = wl.get(m["ticker"])
    if src:
        m["mom_1m"] = src.get("chg_1m")

open("recap.json", "w").write(json.dumps(R, ensure_ascii=False, indent=2))
open("recap.js", "w").write("window.RECAP = " + json.dumps(R, ensure_ascii=False) + ";\n")
print("recap refreshed", GEN, "| asof", R["meta"]["asof"])
