"""Re-seed BOTH ranking tabs on one unified schema so US and China present the
same data points: + suggested buy, + take-profit, + 8Q revenue (beat/miss),
+ backlog, + cash, + guidance. US augments existing us_top10.json; China is
built from the 2026-06-04 China ranking report + fetched EODHD weekly prices.
Earnings/backlog/cash here are illustrative seed values anchored to the report;
the weekly tasks replace them with web-researched figures."""
import json, datetime as dt

LBL = ["Q2'25","Q3'25","Q4'25","Q1'26","Q2'26","Q3'26","Q4'26","Q1'27"]
NOTE = ("Buy = ~7% below last; take-profit = last x (1 + 3-month base case), i.e. the level before momentum tends to stall. "
        "Earnings (8Q revenue), backlog and cash are illustrative seed values anchored to the latest ranking report — "
        "the weekly task replaces them with web-researched per-quarter figures.")

def _dec(p):
    if p is None: return None
    a=abs(p)
    return round(p,0) if a>=1000 else round(p,1) if a>=100 else round(p,2)

def gen_earn(latest, qoq, beats, miss_idx=()):
    r=latest; arr=[]
    for _ in range(8):
        arr.append(round(r,1) if r<100 else round(r)); r=r/(1+qoq/100.0)
    arr=arr[::-1]
    out=[]
    for i,v in enumerate(arr):
        res="beat" if i>=8-beats else "inline"
        if i in miss_idx: res="miss"
        out.append({"label":LBL[i],"rev":v,"res":res})
    return out

def add_levels(n):
    last=n["last"]; b3=n["base"]["3m"]
    n["buy"]=_dec(last*0.93)
    n["tp"]=_dec(last*(1+b3/100.0))

# ---------------- US: augment existing us_top10.json ----------------
US_X = {  # ticker: [latest_rev($B), qoq%, beats, miss_idx, backlog, cash, guide]
 "NVDA": [46,6,8,(),"Data-center demand (RPO n/a)","$45B","Rubin ramp 2H26"],
 "AAPL": [111,4,6,(),"—","$50B","iPhone 17 cycle"],
 "MSFT": [76,5,7,(),"Commercial RPO ~$315B","$80B","Azure +31% cc"],
 "GOOGL":[96,5,7,(),"Cloud backlog ~$90B","$95B","Gemini scaling"],
 "AMZN": [155,4,6,(),"AWS backlog ~$190B","$80B","AWS reaccel"],
 "META": [56,6,6,(),"—","$45B","AI ad ramp"],
 "TSLA": [25,3,3,(4,),"—","$37B","Robotaxi pre-rev"],
 "LLY":  [19.8,9,8,(),"—","$5B","GLP-1 +55% YoY"],
 "BRK-B":[93,2,0,(),"—","$397B","Net equity seller"],
 "WMT":  [170,2,4,(),"—","$9B","e-comm +24%"],
}
us = json.load(open("us_top10.json"))
us["meta"]["note"]=NOTE
for n in us["names"]:
    x=US_X[n["ticker"]]
    n["rev_unit"]="$B"
    n["earnings"]=gen_earn(x[0],x[1],x[2],x[3])
    n["backlog"]=x[4]; n["cash"]=x[5]; n["guide"]=x[6]
    add_levels(n)
us["meta"]["generated"]=dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
open("us_top10.json","w").write(json.dumps(us,indent=2))
open("us_top10.js","w").write("window.US_TOP10 = "+json.dumps(us)+";\n")

# ---------------- China: build fresh ----------------
CN_CLOSES = {
 "601138.SH":[52.49,50.3,49.53,52.18,56.52,60.97,65.01,62.88,63.28,67.62,67.16,73.4,74.06,70.48],
 "300308.SZ":[542.02,612,598,606.52,734.65,851,886.99,857.5,886,1049.87,1037.98,1161.16,1179.99,1154.99],
 "300502.SZ":[394.03,477.05,447.41,455.3,522.5,589,537.27,525.79,551.67,610.05,606.77,706.45,748,725],
 "300394.SZ":[325,312,317.6,333.86,358.9,379.28,323.87,307.5,326.3,399.99,372.5,455.2,457,425.11],
 "688256.SH":[1096.1,1025,1024,1025.7,1210.7,1334,1352.5,1699.96,1182.53,1209,1286,1310,1299.2,1250.36],
 "688041.SH":[235.74,216.42,220.95,213.77,231.82,260,285,296.25,323.28,303.01,312.4,293.9,274.06,259.7],
 "603986.SH":[278.33,290.2,258.66,249.1,265.09,288.96,297.7,312.99,334.1,375.34,468.74,467.01,488,474.01],
 "688981.SH":[107.06,102.18,97.5,91.78,101.01,105.23,110.96,118.73,120.31,119.02,131.33,139.91,127.4,121.92],
 "300750.SZ":[397,413,416.18,386.46,416,444.2,444.9,436,437,423.6,411.16,424,403,393.02],
 "002594.SZ":[99.67,103.03,105.3,99.01,101.67,103.78,99.46,102.98,100.02,96.3,93.75,96.18,93.01,91.19],
}
# ticker:[name, sector, cus, A,B,C, bull(1m,3m,13y), base(1m,3m,13y), driver, risk, earn(latest¥bn,qoq,beats,miss), backlog, cash, guide]
CN = {
 "601138.SH":["Foxconn Industrial Internet","AI server / OEM",9.6,10,5,3,[38,42,32],[13,22,90],"Rubin / GB300 server ramp","US tariff scrutiny on AI servers",[230,9,6,()],"AI server orders rising","n/a","AI servers ~75% of rev by 2027"],
 "300308.SZ":["Zhongji Innolight","Optical / 1.6T",9.1,15,1,2,[45,48,30],[15,27,80],"1.6T ramp + fresh ATH","Customer concentration (Nvidia)",[19.5,22,6,()],"1.6T order book growing","n/a","Q2 1.6T mix lift"],
 "300750.SZ":["CATL","EV battery",8.5,6,8,9,[22,28,18],[7,14,40],"ESS contracts + JV deliveries","IRA / US-route exclusion",[105,4,4,(3,)],"ESS + EV order book","strong","Sodium-ion + ESS pillar"],
 "300502.SZ":["Eoptolink","Optical",7.8,0,2,4,[38,40,32],[14,22,85],"New hyperscaler (AWS) win","Share loss vs Innolight",[7,25,6,()],"800G/1.6T backlog","n/a","1.6T capacity ramp"],
 "688256.SH":["Cambricon","AI chips",7.5,0,6,1,[32,35,30],[12,20,75],"Domestic CSP accelerator orders","US Entity List Footnote-4",[6,28,6,()],"Domestic CSP orders","first +op cash CN¥8.34bn","H1 print + new SoC"],
 "300394.SZ":["Suzhou TFC Optical","Optical / CPO",6.6,0,4,6,[35,38,32],[12,21,85],"CPO design wins (sole-source ELS)","Nvidia ecosystem reliance",[1.5,14,6,()],"CPO attach rising","n/a","Thailand Phase-2 ramp"],
 "688041.SH":["Hygon Information","CPU / DCU",6.0,0,7,5,[30,34,30],[10,19,70],"SOE/telco procurement wins","x86 IP / BIS risk",[4,16,5,()],"SOE procurement pipeline","n/a","Sugon merger synergies"],
 "688981.SH":["SMIC","Foundry",4.8,0,9,7,[28,32,28],[10,17,62],"Q2 guide +14–16% QoQ","Entity List / equipment licensing",[17,4,5,(2,)],"Capacity sold ahead","no dividend","Q2 +14–16% QoQ"],
 "603986.SH":["GigaDevice","Memory",3.9,0,3,0,[30,34,32],[10,18,75],"DRAM upcycle + LPDDR4 qual","Memory cycle peak",[3.4,12,6,()],"DDR4 ramp complete","n/a","LPDDR4 mass prod Q4-26"],
 "002594.SZ":["BYD","EV / auto",3.9,0,11,8,[18,22,22],[6,12,45],"May/Jun delivery prints","Domestic price war (NI −55% YoY)",[170,3,2,(2,5)],"order book solid","strong","Overseas expansion"],
}
def chg3(c): return round((c[-1]/c[0]-1)*100,1)
cn_names=[]
for tk,c in CN.items():
    cl=CN_CLOSES[tk]
    espec=c[10]; bk=c[11]; cash=c[12]; guide=c[13]
    n={"ticker":tk,"name":c[0],"sector":c[1],"cus":c[2],"cap_promote":False,
       "sliceA":c[3] or None,"sliceB":c[4] or None,"sliceC":c[5] or None,
       "bull":{"1m":c[6][0],"3m":c[6][1],"13y":c[6][2]},
       "base":{"1m":c[7][0],"3m":c[7][1],"13y":c[7][2]},
       "driver":c[8],"risk":c[9],"currency":"CNY","rev_unit":"¥bn",
       "last":_dec(cl[-1]),"chg_3m":chg3(cl),"spark":cl,
       "spark_from":"09-Mar-26","spark_to":"08-Jun-26","spark_tf":"3M",
       "earnings":gen_earn(espec[0],espec[1],espec[2],espec[3]),
       "backlog":bk,"cash":cash,"guide":guide}
    add_levels(n)
    cn_names.append(n)
cn_names.sort(key=lambda n:-n["cus"])
cn={"meta":{"title":"China A-share Top-10 Weight Ranking","generated":dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "reference_date":"2026-06-04","universe":"SSE + SZSE A-shares, ex-ST; HK via mentions only; ADRs excluded",
    "methodology":"CUS = 0.40 market-cap rank + 0.30 turnover rank + 0.30 mention rank. FX USD/CNY 6.77. Bull % = P(>15% 1m / >25% 3m / >100% 1-3yr) in local currency.",
    "sector_cap":"none (no GICS cap applied)","note":NOTE},"names":cn_names}
open("china_top10.json","w").write(json.dumps(cn,indent=2))
open("china_top10.js","w").write("window.CHINA_TOP10 = "+json.dumps(cn)+";\n")
print("US augmented:",len(us["names"]),"names | China:",len(cn_names),"names")
print("China order:",", ".join(n["ticker"] for n in cn_names))
