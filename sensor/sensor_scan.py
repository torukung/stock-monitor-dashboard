#!/usr/bin/env python3
"""
STOCK Monitor — mover sensor (prototype v1.0, 2026-07-19).

Detects the pre-breakout fingerprint found in the Jun-Jul 2026 SET mover study
(SALEE TPIPL TPIPP STPI EPG LTS S PLAT MGC CAZ — see
Reports/SET_Mover_Forensics_2026-07.html):

  Tier A (tape, automated from EODHD daily OHLCV):
    A1  volume LEAK  — a day with vol >= 3x avg20 while |close chg| < 3.5%  (+2.0)
        volume BURST — vol >= 3x with a larger price reaction               (+1.0)
    A2  crescendo    — 5d avg vol >= 1.3x avg20 AND above the 10d ratio     (+1.5)
    A3  squeeze      — ATR14% <= its 25th percentile of trailing 6 months   (+1.0)
    A4  drift        — 20d return >= +15% AND within 15% of 52w high        (+1.5)
    A5  OBV slope    — 20d OBV rising +0.5 / falling -1.0
  Tier B (information, from sensor_watch.json — you maintain the flags):
    B1 earnings_accel +2.0 · B2 broker_note +1.5 · B3 insider_buy +1.5
    B3 insider_sell  -2.0 · B4 corp_action +1.0  · B5 theme +1.0

  ALERT     : score >= 4.0 with at least one Tier-A component
  FLAG '⚑'  : Tier A >= 3.0 with zero Tier B  -> private-channel suspect
  ENTRY tell: close chg >= +4% on >= 2x avg20 volume (reported as 'IGNITION')

Run:  EODHD_API_KEY=xxxxxxxx python3 sensor_scan.py
Universe: sensor_universe.json (list of {"ticker": "SALEE", "symbol": "SALEE.BK"}).
Output: sensor_report.json + console table. Stdlib only, same style as web/update.py.
"""

import os, sys, json, time, math, datetime as dt, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EODHD_KEY = os.environ.get("EODHD_API_KEY", "demo")
LOOKBACK_DAYS = 420
MASK = 999999.9999

ALERT_SCORE = 4.0
FLAG_TAPE_ONLY = 3.0
WATCH_DAYS = {"earnings_accel": 20, "broker_note": 10, "insider_buy": 10,
              "insider_sell": 15, "corp_action": 20, "theme": 45}
WATCH_PTS = {"earnings_accel": 2.0, "broker_note": 1.5, "insider_buy": 1.5,
             "insider_sell": -2.0, "corp_action": 1.0, "theme": 1.0}


def fetch_eodhd(symbol):
    frm = (dt.date.today() - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    url = ("https://eodhd.com/api/eod/%s?api_token=%s&fmt=json&period=d&from=%s"
           % (symbol, EODHD_KEY, frm))
    with urllib.request.urlopen(url, timeout=30) as r:
        rows = json.loads(r.read().decode())
    out = []
    for d in rows:
        c = d.get("close")
        if c is None or c == MASK:
            continue
        out.append({"date": d["date"], "o": float(d.get("open") or c),
                    "h": float(d.get("high") or c), "l": float(d.get("low") or c),
                    "c": float(c), "v": float(d.get("volume") or 0)})
    return out


def sma(vals, n, i):
    w = vals[max(0, i - n):i]          # trailing, excludes bar i
    return sum(w) / len(w) if w else None


def atr_pct(rows, i, n=14):
    if i < n + 1:
        return None
    trs = []
    for j in range(i - n + 1, i + 1):
        hi, lo, pc = rows[j]["h"], rows[j]["l"], rows[j - 1]["c"]
        trs.append(max(hi - lo, abs(hi - pc), abs(lo - pc)))
    c = rows[i]["c"]
    return (sum(trs) / n) / c * 100 if c else None


def analyze(rows):
    """Compute Tier-A components on the LAST bar of rows."""
    n = len(rows)
    if n < 60:
        return None
    closes = [r["c"] for r in rows]; vols = [r["v"] for r in rows]
    i = n - 1
    out = {"components": {}, "tape_score": 0.0, "notes": []}

    def add(name, pts, note):
        out["components"][name] = round(pts, 2)
        out["tape_score"] += pts
        out["notes"].append(note)

    # A1 leak / burst in the last 20 trading days
    best_leak, best_burst = None, None
    for j in range(max(21, i - 19), i + 1):
        a20 = sma(vols, 20, j)
        if not a20:
            continue
        ratio = vols[j] / a20 if a20 else 0
        chg = abs(closes[j] / closes[j - 1] - 1) * 100 if closes[j - 1] else 0
        if ratio >= 3.0:
            if chg < 3.5:
                if not best_leak or ratio > best_leak[1]:
                    best_leak = (rows[j]["date"], ratio)
            elif not best_burst or ratio > best_burst[1]:
                best_burst = (rows[j]["date"], ratio)
    if best_leak:
        add("A1_leak", 2.0, "leak %.1fx on %s (price pinned)" % (best_leak[1], best_leak[0]))
    elif best_burst:
        add("A1_burst", 1.0, "burst %.1fx on %s" % (best_burst[1], best_burst[0]))

    # A2 crescendo
    a20 = sma(vols, 20, i + 1)
    d5 = sma(vols, 5, i + 1); d10 = sma(vols, 10, i + 1)
    if a20 and d5 and d10 and d5 / a20 >= 1.3 and d5 / a20 > d10 / a20:
        add("A2_crescendo", 1.5, "5d vol %.2fx avg20, rising" % (d5 / a20))

    # A3 squeeze: ATR14%% vs trailing 6-month (~126 td) distribution
    cur_atr = atr_pct(rows, i)
    if cur_atr:
        hist = [a for a in (atr_pct(rows, j) for j in range(max(20, i - 126), i)) if a]
        if len(hist) > 40:
            q25 = sorted(hist)[int(len(hist) * 0.25)]
            if cur_atr <= q25:
                add("A3_squeeze", 1.0, "ATR %.1f%% <= 25th pct (%.1f%%)" % (cur_atr, q25))

    # A4 drift near highs
    if i >= 20:
        drift = (closes[i] / closes[i - 20] - 1) * 100
        hi52 = max(closes[max(0, i - 252):i + 1])
        dist_hi = (closes[i] / hi52 - 1) * 100
        if drift >= 15 and dist_hi >= -15:
            add("A4_drift", 1.5, "20d drift +%.0f%%, %.0f%% off high" % (drift, dist_hi))

    # A5 OBV slope over 20d
    obv, obvs = 0.0, []
    for j in range(1, n):
        obv += vols[j] if closes[j] > closes[j - 1] else (-vols[j] if closes[j] < closes[j - 1] else 0)
        obvs.append(obv)
    if len(obvs) > 21:
        delta = obvs[-1] - obvs[-21]
        scale = (sum(vols[-21:]) or 1)
        if delta / scale > 0.08:
            add("A5_obv_up", 0.5, "OBV rising")
        elif delta / scale < -0.08:
            add("A5_obv_down", -1.0, "OBV falling (veto-weight)")

    # ignition tell (today)
    if closes[i - 1] and a20:
        chg = (closes[i] / closes[i - 1] - 1) * 100
        if chg >= 4.0 and vols[i] >= 2 * a20:
            out["ignition"] = "+%.1f%% on %.1fx vol TODAY" % (chg, vols[i] / a20)
    return out


def load_watch():
    p = os.path.join(HERE, "sensor_watch.json")
    if not os.path.exists(p):
        return {}
    return json.load(open(p)).get("flags", {})


def watch_score(ticker, flags, today):
    score, notes = 0.0, []
    for f in flags.get(ticker, []):
        kind = f.get("type")
        if kind not in WATCH_PTS:
            continue
        try:
            age = (today - dt.date.fromisoformat(f["date"])).days
        except Exception:
            continue
        if age <= WATCH_DAYS[kind] * 1.6:            # calendar-day allowance for trading days
            score += WATCH_PTS[kind]
            notes.append("%s %s (%s)" % (kind, f.get("note", ""), f["date"]))
    return score, notes


def main():
    uni = json.load(open(os.path.join(HERE, "sensor_universe.json")))["universe"]
    flags = load_watch()
    today = dt.date.today()
    results, errors = [], []
    for cfg in uni:
        try:
            rows = fetch_eodhd(cfg["symbol"])
            time.sleep(0.15)
            a = analyze(rows)
            if not a:
                errors.append("%s: not enough history" % cfg["ticker"])
                continue
            b, bnotes = watch_score(cfg["ticker"], flags, today)
            total = round(a["tape_score"] + b, 2)
            alert = total >= ALERT_SCORE and a["tape_score"] > 0
            flag = a["tape_score"] >= FLAG_TAPE_ONLY and b == 0
            results.append({
                "ticker": cfg["ticker"], "symbol": cfg["symbol"],
                "last": rows[-1]["c"], "date": rows[-1]["date"],
                "score": total, "tape": round(a["tape_score"], 2), "info": round(b, 2),
                "alert": alert, "private_channel_flag": flag,
                "ignition": a.get("ignition"),
                "components": a["components"], "notes": a["notes"] + bnotes,
            })
        except Exception as e:                                   # noqa: BLE001
            errors.append("%s: %s: %s" % (cfg["ticker"], type(e).__name__, e))
    results.sort(key=lambda r: -r["score"])
    payload = {"meta": {"generated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                        "alert_threshold": ALERT_SCORE, "errors": errors},
               "results": results}
    with open(os.path.join(HERE, "sensor_report.json"), "w") as f:
        json.dump(payload, f, indent=2)

    print("%-7s %8s %6s %6s %6s  %s" % ("TICKER", "LAST", "SCORE", "TAPE", "INFO", "SIGNALS"))
    for r in results:
        mark = "🔥" if r["alert"] else ("⚑ " if r["private_channel_flag"] else "  ")
        ign = "  IGNITION! " + r["ignition"] if r.get("ignition") else ""
        print("%s %-5s %8.2f %6.2f %6.2f %6.2f  %s%s"
              % (mark, r["ticker"], r["last"], r["score"], r["tape"], r["info"],
                 "; ".join(r["notes"][:3]), ign))
    if errors:
        print("errors:", "; ".join(errors))


if __name__ == "__main__":
    main()
