#!/usr/bin/env python3
"""
STOCK Monitor — Yahoo-only refresh (run this on your Mac).

The 4 Singapore (SGX) names use Yahoo Finance via yfinance,
because EODHD doesn't cover that exchange. Yahoo is NOT reachable from the
Cowork sandbox, so this little script lets you refresh just those names locally,
where Yahoo works fine.

What it does:
  • fetches ~1y daily history for ONLY the source=="yahoo" holdings
  • merges them into the existing data.js / data.json
  • leaves the 15 EODHD rows exactly as they are (no EODHD API key needed)
  • recomputes the relative-strength rank across the full watchlist

Run from the web/ folder:
    pip install yfinance
    python3 update_yahoo.py
"""

import os, sys, json, time, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import update  # reuse the exact same fetch + analytics as the daily updater

try:
    import yfinance  # noqa: F401
except ImportError:
    sys.exit("yfinance is not installed. Run:  pip install yfinance")


def main():
    wl = json.load(open(os.path.join(HERE, "watchlist.json")))
    data_path = os.path.join(HERE, "data.json")

    if os.path.exists(data_path):
        payload = json.load(open(data_path))
    else:
        payload = {"meta": dict(wl["meta"]), "holdings": []}

    # index existing rows by ticker so we replace yahoo rows in place
    by_ticker = {r["ticker"]: r for r in payload.get("holdings", [])}

    yahoo_cfgs = [h for h in wl["holdings"] if h.get("source") == "yahoo"]
    print("Refreshing %d Yahoo names from Yahoo Finance ...\n" % len(yahoo_cfgs))

    errors = []
    for cfg in yahoo_cfgs:
        series, err = update.fetch(cfg)          # source=="yahoo" -> fetch_yahoo
        row = update.compute(cfg, series)
        if not series:                           # empty counts as failure too
            msg = err or "no data returned from Yahoo (check the symbol)"
            row["error"] = msg
            errors.append("%s (%s)" % (cfg["ticker"], msg))
            print("  %-5s %-8s FAILED: %s" % (cfg["ticker"], cfg["symbol"], msg))
        else:
            row["error"] = None
            print("  %-5s %-8s %d bars, last %s  (1m %s%%, 3m %s%%)"
                  % (cfg["ticker"], cfg["symbol"], len(series),
                     row.get("last"), row.get("chg_1m"), row.get("chg_3m")))
        by_ticker[cfg["ticker"]] = row
        time.sleep(0.3)

    # rebuild holdings in watchlist order, preserving every non-yahoo row as-is
    order = [h["ticker"] for h in wl["holdings"]]
    rows = [by_ticker[t] for t in order if t in by_ticker]
    rows += [r for t, r in by_ticker.items() if t not in order]

    for r in rows:                                # recompute RS cleanly
        r.pop("rs", None)
    update.add_rs_rank(rows)

    payload["holdings"] = rows
    meta = payload.setdefault("meta", {})
    meta["title"] = wl["meta"]["title"]
    meta["note"] = wl["meta"]["note"]
    meta["generated"] = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    meta["errors"] = ["%s (%s)" % (r["ticker"], r["error"])
                      for r in rows if r.get("error")]

    with open(data_path, "w") as f:
        json.dump(payload, f, indent=2)
    with open(os.path.join(HERE, "data.js"), "w") as f:
        f.write("window.DASHBOARD_DATA = " + json.dumps(payload) + ";\n")

    ok = len(yahoo_cfgs) - len(errors)
    print("\nRefreshed %d/%d Yahoo names; %d still erroring. Wrote data.js / data.json."
          % (ok, len(yahoo_cfgs), len(errors)))
    if errors:
        print("  errors:", "; ".join(errors))


if __name__ == "__main__":
    main()
