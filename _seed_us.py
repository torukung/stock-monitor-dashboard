"""One-off: build the initial us_top10.js/json for the US Top-10 ranking tab,
from the 2026-06-04 ranking report (CUS, slice ranks, bull probabilities) plus
already-fetched EODHD weekly closes. The weekly scheduled task regenerates this."""
import json, datetime as dt

DATES = ["03-09","03-16","03-23","03-30","04-06","04-13","04-20","04-27","05-04","05-11","05-18","05-26","06-01","06-08"]
def _fmt(mm_dd): return dt.date.fromisoformat("2026-"+mm_dd).strftime("%d-%b-%y")

# ticker: [name, sector, cus, capPromote, A,B,C, bull(1m,3m,13y), base(1m,3m,13y), driver, risk, closes[14]]
CFG = {
 "NVDA": ["NVIDIA","Info Tech",15.0,False,1,1,1,[25,35,40],[12,22,85],"Blackwell shipments + Computex follow-through","AI capex digestion / in-house silicon",
   [180.25,172.7,167.52,177.39,188.63,201.68,208.27,198.45,215.2,225.32,215.33,211.14,205.1,208.64]],
 "AAPL": ["Apple","Info Tech",12.8,False,2,3,5,[15,25,20],[5,10,35],"WWDC AI roadmap (Jun 9)","Overbought at ATH / China share loss",
   [250.12,247.99,248.8,255.92,260.48,270.23,271.06,280.14,293.32,300.23,308.82,312.06,307.34,301.54]],
 "TSLA": ["Tesla","Cons. Disc.",11.6,False,8,2,2,[30,35,30],[18,20,60],"Robotaxi paid ride-hailing launch","NHTSA / safety incident",
   [391.2,367.96,361.83,360.59,348.95,400.62,376.3,390.82,428.35,422.24,426.01,435.79,391,408.95]],
 "MSFT": ["Microsoft","Info Tech",11.4,False,4,4,6,[15,25,25],[4,10,45],"Build conference + Copilot ARR; Azure reaccel","AI capex digestion",
   [395.55,381.87,356.77,373.46,370.87,422.79,424.62,414.44,415.12,421.92,418.57,450.24,416.67,411.74]],
 "AMZN": ["Amazon","Cons. Disc.",10.1,False,5,5,8,[20,32,35],[8,18,70],"AWS reacceleration + Prime Day reads","Retail margin / FTC antitrust",
   [207.67,205.37,199.34,209.77,238.38,250.56,263.99,268.26,272.68,264.14,266.32,270.64,246.03,245.22]],
 "GOOGL":["Alphabet","Comm. Services",10.0,False,3,7,9,[22,30,30],[10,16,60],"Post-raise overhang abating; Gemini scaling","DOJ remedy / search disintermediation",
   [302.28,301,274.34,295.77,317.24,341.68,344.4,385.69,400.8,396.78,382.97,380.34,368.53,363.31]],
 "META": ["Meta Platforms","Comm. Services",9.3,False,7,6,7,[18,26,25],[6,14,45],"Llama 5 / Superintelligence Labs hires","Capex / Reality Labs burn",
   [613.71,593.66,525.72,574.46,629.86,688.55,675.03,608.75,609.63,614.23,610.26,632.51,593,585.39]],
 "LLY":  ["Eli Lilly","Health Care",2.4,True,10,None,None,[22,30,35],[8,15,65],"Orforglipron oral GLP-1 readout","Phase-3 miss / GLP-1 competition",
   [985.08,906.7,878.24,935.58,939.47,927.03,883.96,963.33,948.45,1004.92,1065,1105,1131.42,1149.15]],
 "BRK-B":["Berkshire Hathaway","Financials",2.8,True,9,None,None,[8,12,8],[2,5,12],"Abel deal flow; $397B cash deployment","Succession execution risk",
   [490.03,480.94,468.49,477.35,479.9,474.58,469.32,473.01,475.94,482.7,486.38,474.48,488.13,487]],
 "WMT":  ["Walmart","Cons. Staples",2.0,True,11,None,None,[10,14,12],[3,6,15],"E-comm margin + ad Connect flywheel","Tariff margin hit / Amazon grocery",
   [126.52,119.02,122.89,125.79,126.77,127.5,129.92,131.6,130.43,131.45,120.27,115.75,118.88,119.83]],
}

names=[]
for tk,c in CFG.items():
    closes=c[11]; last=closes[-1]; chg3=(last/closes[0]-1)*100
    names.append({
        "ticker":tk,"name":c[0],"sector":c[1],"cus":c[2],"cap_promote":c[3],
        "sliceA":c[4],"sliceB":c[5],"sliceC":c[6],
        "bull":{"1m":c[7][0],"3m":c[7][1],"13y":c[7][2]},
        "base":{"1m":c[8][0],"3m":c[8][1],"13y":c[8][2]},
        "driver":c[9],"risk":c[10],"currency":"USD",
        "last":round(last,2),"chg_3m":round(chg3,1),
        "spark":closes,"spark_from":_fmt(DATES[0]),"spark_to":_fmt(DATES[-1]),"spark_tf":"3M",
    })
names.sort(key=lambda n:-n["cus"])
payload={"meta":{
    "title":"US Stock Top-10 Weight Ranking",
    "generated":dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "reference_date":"2026-06-04",
    "universe":"US-listed (NYSE + NASDAQ), ex-ETF/ADR/SPAC, > $5",
    "methodology":"Composite Universe Score = 0.40 market-cap rank + 0.30 dollar-volume rank + 0.30 attention rank. Final 10 honors a GICS cap of 3 per sector (LLY/BRK-B/WMT promoted). Bull % = probability of >15% (1m) / >25% (3m) / >100% (1-3yr).",
    "sector_cap":"max 3 per GICS sector",
 },"names":names}
open("us_top10.json","w").write(json.dumps(payload,indent=2))
open("us_top10.js","w").write("window.US_TOP10 = "+json.dumps(payload)+";\n")
print("Wrote us_top10.js / .json —",len(names),"names; order:",", ".join(n["ticker"] for n in names))
