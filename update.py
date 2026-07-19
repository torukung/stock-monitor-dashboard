#!/usr/bin/env python3
"""
STOCK Monitor — daily updater.

Reads watchlist.json, pulls ~1y of daily history for each holding
(EODHD for covered markets, Yahoo Finance via yfinance for Singapore/SGX),
computes the analysis angles, and writes data.js + data.json next to this file.

Run:  EODHD_API_KEY=xxxxxxxx python3 update.py
Deps: pip install yfinance   (only needed for the Singapore/SGX names)
"""

import os, sys, json, time, datetime as dt, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
EODHD_KEY = os.environ.get("EODHD_API_KEY", "demo")
LOOKBACK_DAYS = 400          # ~1y, enough for 52w range + 200d trend
MASK = 999999.9999           # EODHD "no data" sentinel to skip
TODAY = dt.date.today()


def _fmtdate(iso):
    """ISO yyyy-mm-dd -> '15-May-26'."""
    if not iso:
        return None
    try:
        return dt.date.fromisoformat(iso).strftime("%d-%b-%y")
    except Exception:
        return None


def _days_since(iso):
    if not iso:
        return None
    try:
        return (TODAY - dt.date.fromisoformat(iso)).days
    except Exception:
        return None


# ---------------------------------------------------------------- helpers
def _dec(price):
    """Sensible decimal places for display by magnitude."""
    if price is None:
        return None
    a = abs(price)
    if a >= 1000:
        return round(price, 0)
    if a >= 100:
        return round(price, 1)
    return round(price, 2)


def pct(new, old):
    if not old or new is None or old is None:
        return None
    return (new / old - 1.0) * 100.0


def ema(values, span):
    if not values:
        return None
    k = 2.0 / (span + 1.0)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e


def ret_over(series, days):
    """series = [(date_iso, close), ...] ascending. Return % change from the
    bar closest on-or-before (last_date - days) to the last bar."""
    if len(series) < 2:
        return None
    last_d = dt.date.fromisoformat(series[-1][0])
    cutoff = last_d - dt.timedelta(days=days)
    ref = None
    for d_iso, c in series:
        if dt.date.fromisoformat(d_iso) <= cutoff:
            ref = c
        else:
            break
    if ref is None:
        ref = series[0][1]
    return pct(series[-1][1], ref)


def interp_3mo(t1, t6):
    """Geometric interpolation for a 3-month target between 1mo and 6mo."""
    if t1 is None or t6 is None or t1 <= 0 or t6 <= 0:
        return None
    return t1 * (t6 / t1) ** ((3 - 1) / (6 - 1))


# ---------------------------------------------------------------- fetchers
def fetch_eodhd(symbol):
    frm = (dt.date.today() - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()
    url = ("https://eodhd.com/api/eod/%s?api_token=%s&fmt=json&period=d&from=%s"
           % (symbol, EODHD_KEY, frm))
    with urllib.request.urlopen(url, timeout=30) as r:
        rows = json.loads(r.read().decode())
    out = []
    for d in rows:
        c = d.get("close", d.get("adjusted_close"))   # actual close, matches entry/target levels
        if c is None or c == MASK:
            continue
        out.append((d["date"], float(c)))
    return out


def fetch_yahoo(symbol):
    import yfinance as yf  # lazy: only needed for the Singapore (SGX) names
    h = yf.Ticker(symbol).history(period="1y", auto_adjust=False)
    return [(idx.date().isoformat(), float(row["Close"]))
            for idx, row in h.iterrows() if row["Close"] == row["Close"]]


def fetch(cfg):
    src = cfg.get("source")
    sym = cfg.get("symbol")
    try:
        series = fetch_eodhd(sym) if src == "eodhd" else fetch_yahoo(sym)
        return series, None
    except Exception as e:                       # noqa: BLE001
        return [], "%s: %s" % (type(e).__name__, e)


# ---------------------------------------------------------------- analytics
def compute(cfg, series):
    """Return the full metric dict for one holding given ascending series."""
    closes = [c for _, c in series]
    last = closes[-1] if closes else None
    out = {
        "ticker": cfg["ticker"], "name": cfg["name"], "exchange": cfg["exchange"],
        "currency": cfg["currency"], "tier": cfg["tier"], "theme": cfg["theme"],
        "conviction": cfg["conviction"], "status": cfg["status"], "note": cfg.get("note", ""),
        "source": cfg["source"], "symbol": cfg["symbol"],
        "entry": cfg.get("entry"), "stop": cfg.get("stop"),
        "entry_date": cfg.get("entry_date"), "entry_date_fmt": _fmtdate(cfg.get("entry_date")),
        "condition_since": cfg.get("condition_since"),
        "condition_since_fmt": _fmtdate(cfg.get("condition_since")),
        "days_on_condition": _days_since(cfg.get("condition_since")),
        "last": _dec(last),
        "spark": [round(c, 4) for c in closes[-65:]],   # ~3mo of daily / all weekly
        "error": None,
    }
    # sparkline timeframe tag + date range
    sdates = [d for d, _ in series][-65:]
    if sdates:
        out["spark_from"] = _fmtdate(sdates[0])
        out["spark_to"] = _fmtdate(sdates[-1])
        span = (dt.date.fromisoformat(sdates[-1]) - dt.date.fromisoformat(sdates[0])).days
        out["spark_tf"] = ("1Y" if span > 300 else "6M" if span > 150
                           else "3M" if span > 60 else "1M" if span > 20 else "%dD" % span)
    if not closes:
        return out

    # momentum / returns
    out["chg_1d"] = round(pct(closes[-1], closes[-2]), 2) if len(closes) > 1 else None
    out["chg_1w"] = round(ret_over(series, 7), 2) if ret_over(series, 7) is not None else None
    out["chg_1m"] = round(ret_over(series, 30), 2) if ret_over(series, 30) is not None else None
    out["chg_3m"] = round(ret_over(series, 91), 2) if ret_over(series, 91) is not None else None

    # trend vs 50-bar EMA + position in 52w range
    out["ema50"] = _dec(ema(closes[-50:], 50)) if len(closes) >= 5 else None
    out["trend_up"] = (out["ema50"] is not None and last >= out["ema50"])
    hi = max(closes); lo = min(closes)
    out["hi_52w"] = _dec(hi); out["lo_52w"] = _dec(lo)
    out["range_pos"] = round((last - lo) / (hi - lo) * 100, 0) if hi > lo else None

    # P&L vs entry, distance to stop
    out["pct_vs_entry"] = round(pct(last, cfg["entry"]), 1) if cfg.get("entry") else None
    out["dist_to_stop"] = round(pct(last, cfg["stop"]), 1) if cfg.get("stop") else None

    # suggested buy-on-dip / take-profit / reward:risk
    stop = cfg.get("stop"); t12 = cfg.get("target_12mo")
    if stop:
        out["suggest_entry"] = _dec(max(stop * 1.02, last * 0.93))
    else:
        out["suggest_entry"] = None
    targets = [t for t in (cfg.get("target_1mo"), cfg.get("target_6mo"), t12) if t]
    above = [t for t in targets if t > last]
    if above:
        out["suggest_exit"] = _dec(min(above)); out["targets_met"] = False
    elif targets:
        out["suggest_exit"] = _dec(max(targets)); out["targets_met"] = True
    else:
        out["suggest_exit"] = None; out["targets_met"] = None
    if stop and t12 and last > stop:
        out["reward_risk"] = round((t12 - last) / (last - stop), 2)
    else:
        out["reward_risk"] = None

    # upside ladder: 3mo / 6mo / 12mo / 3yr / 5yr
    t1, t6 = cfg.get("target_1mo"), cfg.get("target_6mo")
    t3 = interp_3mo(t1, t6)
    g = cfg.get("cagr_long") or 0.0
    up = {}
    up["3mo"] = round(pct(t3, last), 1) if t3 else None
    up["6mo"] = round(pct(t6, last), 1) if t6 else None
    up["12mo"] = round(pct(t12, last), 1) if t12 else None
    up["3yr"] = round(pct(t12 * (1 + g) ** 2, last), 1) if t12 else None
    up["5yr"] = round(pct(t12 * (1 + g) ** 4, last), 1) if t12 else None
    out["upside"] = up
    return out


def add_rs_rank(rows):
    """0-100 relative-strength rank across the watchlist on 3-month return."""
    scored = [r for r in rows if r.get("chg_3m") is not None]
    scored.sort(key=lambda r: r["chg_3m"])
    n = len(scored)
    for i, r in enumerate(scored):
        r["rs"] = round((i + (n > 1 and 0 or 0)) / max(n - 1, 1) * 99 + 1) if n > 1 else 50
    for r in rows:
        r.setdefault("rs", None)
    return rows


# ---------------------------------------------------------------- main
def build(seed_series=None):
    wl = json.load(open(os.path.join(HERE, "watchlist.json")))
    rows, errors = [], []
    for cfg in wl["holdings"]:
        if seed_series is not None:                      # offline seed mode
            series = seed_series.get(cfg["symbol"], [])
            err = None if series else "no seed series"
        else:
            series, err = fetch(cfg)
            time.sleep(0.15)
        row = compute(cfg, series)
        if err and not series:
            row["error"] = err
            errors.append("%s (%s)" % (cfg["ticker"], err))
        rows.append(row)

    add_rs_rank(rows)
    payload = {
        "meta": {
            "title": wl["meta"]["title"],
            "generated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "note": wl["meta"]["note"],
            "errors": errors,
        },
        "holdings": rows,
    }
    with open(os.path.join(HERE, "data.json"), "w") as f:
        json.dump(payload, f, indent=2)
    with open(os.path.join(HERE, "data.js"), "w") as f:
        f.write("window.DASHBOARD_DATA = " + json.dumps(payload) + ";\n")
    print("Wrote data.js / data.json — %d holdings, %d errors" % (len(rows), len(errors)))
    if errors:
        print("  errors:", "; ".join(errors))
    return payload


if __name__ == "__main__":
    build()
