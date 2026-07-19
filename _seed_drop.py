"""One-off: build the initial drop_screen.js/json for the 4th tab (Drop Screen),
from the 2026-06-07 Drop Screen report + a web pull of Planet Labs earnings.
The weekly scheduled task (weekly-stock-drop-screen) regenerates this each Saturday."""
import json, datetime as dt

payload = {
 "meta": {
   "title": "Weekly Drop Screen",
   "generated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
   "week": "1–5 June 2026",
   "source": "scheduled-task weekly-stock-drop-screen",
   "filters": ["IPO age < 5 yrs", "2 straight yrs YoY growth", "Strong / growing backlog"],
   "in_out_rule": "Moving in = newly reaches the shortlist / closest-fit this week. Moving out = was a candidate, now screened out. Moving-out keeps its original since-date and is removed once the name qualifies again.",
   "framing": "Informational research from public web + FMP free tier — not financial advice. Free data is best-effort; names excluded rather than guessed when a hard filter is unverifiable.",
 },
 "recap": {
   "headline": "Nasdaq's worst week in over a year — 0 names passed all 3 filters; closest fit is Planet Labs (PL).",
   "bullets": [
     "Stronger-than-expected May jobs report pushed out rate-cut bets — S&P −2.6%, Nasdaq −4.7%, SOX index worst day in 6+ years.",
     "Steepest US decliners were micro-cap / speculative; two younger names — Planet Labs and Valens — cratered Friday.",
     "Thailand's SET consolidated below 1,600 (1,582.60, −0.76% Fri); only sub-THB1 penny shells hit floor limits — none investable.",
   ],
   "verdict": "None passed all three hard filters. Closest fit: PL — passes growth + backlog, fails only the IPO-age technicality (SPAC vs de-SPAC date).",
 },
 # ---- suggested / nearly matched (closest fit) ----
 "suggested": [
   {"ticker":"PL","name":"Planet Labs PBC","country":"US","sector":"Space / geospatial data",
    "last":32.22,"currency":"USD","drop_pct":-26.0,"period":"Fri 5 Jun",
    "status":"Closest fit","passes":["2-yr YoY growth","Backlog $900M (+79%)"],"fails":["IPO age (SPAC-date technicality)"],
    "why_drop":"Fell ~26% Friday despite an earnings beat — filed a $1.5B ATM offering, trimmed margin guidance, after a parabolic May space-stock rally. Dilution / positioning, not demand.",
    "bull":"Record $900M backlog (+79%) gives rare visibility for a 40%+ grower; defense/geospatial demand is a multi-year tailwind; a move back toward May highs alone is >50%.",
    "bear":"~25× forward sales even after the drop; the $1.5B ATM signals scaled dilution; margins guided down; beta ~2.0; backlog converts over years, so near-term revenue can still disappoint.",
    "rev_unit":"$M",
    "earnings":[{"label":"Q2'25","rev":61,"res":"inline"},{"label":"Q3'25","rev":61,"res":"inline"},{"label":"Q4'25","rev":62,"res":"inline"},
                {"label":"Q1'26","rev":66,"res":"beat"},{"label":"Q2'26","rev":73,"res":"beat"},{"label":"Q3'26","rev":81,"res":"beat"},
                {"label":"Q4'26","rev":87,"res":"beat"},{"label":"Q1'27","rev":94,"res":"beat"}],
    "backlog":"$900M (+79% YoY)","cash":"$731M","guide":"Q2 $102–107M · FY27 $425–441M"},
 ],
 # ---- decliners by country ----
 "countries": [
   {"code":"TH","name":"Thailand","verdict":"No qualifying decliners — nothing investable fell 15%+; board was sub-THB1 penny / floor-limit shells (excluded by size).",
    "decliners":[
      {"ticker":"HPT","name":"Home Pottery","last":0.11,"currency":"THB","drop_pct":-66.7,"period":"daily","verdict":"Excluded — penny / floor-limit"},
      {"ticker":"AKS","name":"AKS Corporation","last":0.01,"currency":"THB","drop_pct":-66.7,"period":"daily","verdict":"Excluded — penny / floor-limit"},
      {"ticker":"ECF","name":"East Coast Furnitech","last":0.02,"currency":"THB","drop_pct":-66.7,"period":"daily","verdict":"Excluded — penny / floor-limit"},
      {"ticker":"MVISION","name":"M Vision","last":0.06,"currency":"THB","drop_pct":-50.0,"period":"daily","verdict":"Excluded — penny / floor-limit"},
      {"ticker":"DELTA","name":"Delta Electronics (TH)","last":349.0,"currency":"THB","drop_pct":-2.0,"period":"Fri","verdict":"Real name but only −2% — far from 15% screen"}]},
   {"code":"US","name":"United States","verdict":"Four names reached the filters; one micro-cap wall failed on size. PL is the closest fit.",
    "decliners":[
      {"ticker":"PL","name":"Planet Labs PBC","last":32.22,"currency":"USD","drop_pct":-26.0,"period":"Fri 5 Jun","verdict":"Closest fit — see Suggested above","tag":"closest"},
      {"ticker":"VLN","name":"Valens Semiconductor","last":2.11,"currency":"USD","drop_pct":-34.7,"period":"Fri 5 Jun","verdict":"Passes IPO age (4.7y); FAILS 2-yr growth — FY24 revenue −31%","tag":"fail",
       "rev_unit":"$M","earnings":[{"label":"FY23","rev":84,"res":"inline"},{"label":"FY24","rev":58,"res":"miss"},{"label":"FY25e","rev":68,"res":"inline"}],
       "backlog":"not assessed (growth fail)","cash":"n/a","note":"Annual figures — quarterly not on free tier."},
      {"ticker":"VRRM","name":"Verra Mobility","last":4.31,"currency":"USD","drop_pct":-69.0,"period":"weekly","verdict":"FAILS IPO age — listed 2017 (~9y); not assessed further","tag":"fail"},
      {"ticker":"ZUMZ","name":"Zumiez","last":17.39,"currency":"USD","drop_pct":-25.9,"period":"Fri","verdict":"FAILS IPO age — listed 2005","tag":"fail"},
      {"ticker":"GMM","name":"Global Mofy AI","last":None,"currency":"USD","drop_pct":-89.0,"period":"weekly","verdict":"Excluded — micro-cap (~$8M)","tag":"size"},
      {"ticker":"SNBR","name":"Sleep Number","last":None,"currency":"USD","drop_pct":-50.0,"period":"weekly","verdict":"Excluded — ~$11M cap & listed 1998","tag":"size"}]},
 ],
 # ---- moving in / out (first screen — no prior file, so out = names screened out this week) ----
 "moving_in": [
   {"ticker":"PL","country":"US","sector":"Space / geospatial","since":"2026-06-07","why":"Reached closest-fit — passes growth + backlog, fails only IPO-age technicality"},
 ],
 "moving_out": [
   {"ticker":"VLN","country":"US","sector":"Semis","since":"2026-06-07","why":"Screened out — FY24 revenue −31% breaks the 2-yr growth filter"},
   {"ticker":"VRRM","country":"US","sector":"Transport tech","since":"2026-06-07","why":"Screened out — IPO 2017, fails the <5-yr age filter"},
 ],
}
open("drop_screen.json","w").write(json.dumps(payload,indent=2))
open("drop_screen.js","w").write("window.DROP_SCREEN = "+json.dumps(payload)+";\n")
print("Wrote drop_screen.js/json — suggested", len(payload["suggested"]),
      "| countries", {c["code"]:len(c["decliners"]) for c in payload["countries"]},
      "| in", len(payload["moving_in"]), "| out", len(payload["moving_out"]))
