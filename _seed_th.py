"""Seed th_top10.js for the Thailand Top-10 tab — same schema as US/China
(+buy +tp +8Q earnings +backlog +cash). From the 2026-06-04 Thai ranking report
+ fetched EODHD .BK weekly prices. Earnings/backlog/cash are illustrative seed
values anchored to the report; the weekly task replaces them with web figures."""
import json, datetime as dt

LBL=["Q2'25","Q3'25","Q4'25","Q1'26","Q2'26","Q3'26","Q4'26","Q1'27"]
NOTE=("Buy = ~7% below last; take-profit = last x (1 + 3-month base case). "
      "Earnings (8Q revenue), backlog and cash are illustrative seed values anchored to the latest ranking report — "
      "the weekly task replaces them with web-researched figures.")
def _dec(p):
    a=abs(p); return round(p,0) if a>=1000 else round(p,1) if a>=100 else round(p,2)
def gen_earn(latest,qoq,beats,miss=()):
    r=latest; arr=[]
    for _ in range(8): arr.append(round(r,1) if r<100 else round(r)); r=r/(1+qoq/100.0)
    arr=arr[::-1]; out=[]
    for i,v in enumerate(arr):
        res="beat" if i>=8-beats else "inline"
        if i in miss: res="miss"
        out.append({"label":LBL[i],"rev":v,"res":res})
    return out

CLOSES={
 "AOT":[49,48.75,52.25,53,54,54.75,54.5,51.25,51.25,53,52.75,55.25,58,57.25],
 "CPALL":[46.5,45.5,44,45.5,47.75,47.5,44.75,43.5,43.75,46.25,46.5,47.25,45.75,45.25],
 "ADVANC":[363,380,367,365,363,353,349,340,350,365,355,353,361,358],
 "MINT":[22.1,21.5,21.5,21.8,22.5,22.5,21.6,20.7,21.2,21.7,21.9,22.5,22.9,22.2],
 "GULF":[56.25,56.75,58.25,59.25,59.5,57.75,56,57.5,60,59.75,60.75,62,67,64.5],
 "BBL":[167.5,166,167.5,165.5,166,164.5,158.5,162.5,163,165,168.5,173,174.5,170],
 "CPN":[64.25,63.25,61.25,62.25,63.5,64.75,62.25,62,64.75,64.75,66.5,64.5,64.75,64.25],
 "KTB":[34.25,34.5,35,35.25,33,31.25,32.25,33,32.75,34.25,34.75,34.75,35.25,35],
 "KBANK":[189,189.5,191,190.5,192,189,190,194,195,196.5,197,201,201,200],
 "BDMS":[18.8,18.9,18.4,19,18.6,18.7,18.5,18.3,18.4,18.3,18.1,18.2,18.4,18.2],
}
# ticker:[name,sector,cus,A,B,C,bull(1m,3m,13y),base(1m,3m,13y),driver,risk,earn(late฿bn,qoq,beats,miss),backlog,cash,guide]
TH={
 "AOT":["Airports of Thailand","Transport",11.0,5,7,3,[45,55,75],[10,20,100],"Inbound tourist arrival momentum","China tourist safety perception",[17.3,5,6,()],"Concession through 2027","strong","Suvarnabhumi satellite terminal"],
 "CPALL":["CP All / 7-Eleven","Cons. Staples",10.3,9,3,4,[45,50,75],[9,17,90],"Buyback + 7-Eleven SSSG beat","CP-group governance discount",[230,4,6,()],"n/a","฿7.5B buyback","Aug Q2 + CPAXT real-estate"],
 "ADVANC":["Advanced Info Service","Telecom",11.6,2,5,7,[40,50,75],[8,15,80],"Q2 print + dividend; data-centre","NBTC tariff cap",[56,3,6,()],"n/a","strong FCF","AI / data-centre ARPU"],
 "MINT":["Minor International","Hospitality",2.4,None,15,9,[40,50,75],[8,22,100],"European summer hotel RevPAR","ME conflict; high net debt",[40,4,4,(3,)],"forward bookings up","levered","Anantara asset-light pivot"],
 "GULF":["Gulf Development","Utilities / Holdings",12.0,4,6,2,[40,50,70],[7,17,80],"Data-centre Phase-1 commissioning","SET 10% single-stock cap",[32,5,6,()],"PPA + data-centre pipeline","n/a","Hyperscale DC buildout"],
 "BBL":["Bangkok Bank","Banks",5.1,10,13,10,[30,40,70],[5,13,75],"P/B re-rate; ASEAN lending","NIM compression at 1% rate",[34,2,4,()],"n/a","n/a","ASEAN earnings contribution"],
 "CPN":["Central Pattana","Real Estate",4.7,11,11,12,[30,40,70],[5,15,72],"Macquarie Outperform; mall footfall","E-commerce share gain",[12,3,5,()],"leasing pipeline H2","n/a","Mall-portfolio yield mgmt"],
 "KTB":["Krung Thai Bank","Banks",9.0,7,8,6,[35,40,65],[4,11,57],"Pao Tang fee income","Momentum reversal (GS Neutral)",[28,2,4,(2,)],"n/a","n/a","Digital payment fee income"],
 "KBANK":["Kasikornbank","Banks",5.7,13,2,15,[30,35,70],[5,12,70],"K Plus monetisation; wealth fees","SME asset quality if GDP<2.5%",[40,2,4,()],"n/a","n/a","Digital banking moat"],
 "BDMS":["Bangkok Dusit Medical","Healthcare",3.4,15,14,8,[25,35,70],[4,13,75],"Int'l-patient mix recovery","Medical-tourism volatility (ME)",[26,3,4,(4,)],"n/a","strong","Aging-Thailand demographic"],
}
def chg3(c): return round((c[-1]/c[0]-1)*100,1)
names=[]
for tk,c in TH.items():
    cl=CLOSES[tk]; es=c[10]; b3=c[7][1]; last=cl[-1]
    n={"ticker":tk,"name":c[0],"sector":c[1],"cus":c[2],"cap_promote":False,
       "sliceA":c[3] or None,"sliceB":c[4] or None,"sliceC":c[5] or None,
       "bull":{"1m":c[6][0],"3m":c[6][1],"13y":c[6][2]},"base":{"1m":c[7][0],"3m":c[7][1],"13y":c[7][2]},
       "driver":c[8],"risk":c[9],"currency":"THB","rev_unit":"฿bn",
       "last":_dec(last),"chg_3m":chg3(cl),"spark":cl,"spark_from":"09-Mar-26","spark_to":"08-Jun-26","spark_tf":"3M",
       "buy":_dec(last*0.93),"tp":_dec(last*(1+b3/100.0)),
       "earnings":gen_earn(es[0],es[1],es[2],es[3]),"backlog":c[11],"cash":c[12],"guide":c[13]}
    names.append(n)
names.sort(key=lambda n:-n["cus"])
payload={"meta":{"title":"Thailand SET Top-10 Weight Ranking","generated":dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "reference_date":"2026-06-04","universe":"SET + mai; ex warrants/DR/REIT; ex Cash-Balance/Trading-Alert names",
    "methodology":"CUS = 0.40 market-cap rank + 0.30 THB-turnover rank + 0.30 attention rank. FX 32.5 THB/USD. Bull % = P(>10% 1m / >20% 3m / >75% 1-3yr), local THB. Max 3 per SET sector.",
    "sector_cap":"max 3 per SET sector","note":NOTE},"names":names}
open("th_top10.json","w").write(json.dumps(payload,indent=2,ensure_ascii=False))
open("th_top10.js","w").write("window.TH_TOP10 = "+json.dumps(payload,ensure_ascii=False)+";\n")
print("Thailand:",len(names),"names | order:",", ".join(n["ticker"] for n in names))
