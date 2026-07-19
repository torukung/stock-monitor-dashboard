# Sensor automation — how it runs (set up 2026-07-19)

Two layers, deliberately different technologies:

## Layer 1 — tape scan (deterministic, GitHub Actions)
`.github/workflows/sensor_scan.yml` runs `sensor/sensor_scan.py` every weekday
at **19:30 ICT** (12:30 UTC), commits `sensor/sensor_report.json`, and — once you
add an `NTFY_TOPIC` repo secret — pushes 🔥/⚑ alerts to your phone via ntfy.sh.

- Uses the existing `EODHD_API_KEY` repo secret (same as update.yml). Nothing else to configure.
- To enable phone push: install the **ntfy** app, subscribe to a long random topic
  (e.g. `tor-sensor-x7k2m9`), add it as repo secret `NTFY_TOPIC`.
- Universe: `sensor/sensor_universe.json` — extend freely (any `TICKER.BK`).
- Tier-B flags: `sensor/sensor_watch.json` — dated entries, auto-expire.
- **Canonical copy lives here in `web/sensor/`** (inside the git repo, so Actions
  can run it). The `STOCK Monitor/sensor/` folder at vault level is the original
  delivery copy — safe to ignore or clean up.

## Layer 2 — information tier (agent, Claude scheduled task)
A daily scheduled task ("SET mover sensor — daily brief", weekdays 19:45 ICT)
where Claude re-runs the tape math via the EODHD connector, then does what a
script can't: sweeps RYT9 / Kaohoon / Thunhoon / SET filings for fresh Tier-B
events (earnings, broker targets, Form-59 insider trades, corp actions,
Cash Balance) on anything scoring ≥2.5, updates `sensor_watch.json` when the
desktop app is open, and sends a short verdict. Pause/delete it any time from
the scheduled-tasks list in the Claude app.

## Why not a VM (Oracle / Google free tier) — for now
A once-daily 2-minute script doesn't justify server maintenance. Revisit when
you want **intraday** scanning:

- **Oracle Cloud Always Free** is the strongest free option: 2× ARM VMs (up to
  4 OCPU / 24 GB total), always-free forever. Plan: one VM, a systemd timer
  every 15 min during SET hours (10:00–16:30 ICT) calling EODHD's live/delayed
  quote API for the universe, computing intraday RVOL + ignition tells,
  pushing via the same ntfy topic. Caveats: ARM capacity in popular regions
  requires retrying signup; keep the boot volume default; set a billing alert
  even on free tier.
- **Google Cloud** alternative: Cloud Scheduler → Cloud Run job (free quotas
  cover this easily); less "always-on" babysitting than a VM but more YAML.
- **Cloudflare Workers** (your ToR_Stocks stack): great for serving the alert
  feed/dashboard JSON at the edge; awkward as the Python scanner host.

## Failure modes to know
- EODHD occasionally publishes Thai EOD late → the 19:30 run would score on
  yesterday's bar; the report's `date` field shows which bar was used.
- GitHub Actions cron can drift 5–15 min under load — normal.
- Thresholds were calibrated in a hot regime (turnover +88% YoY, Jun–Jul 2026);
  in a quiet tape expect fewer/no alerts, and consider ALERT ≥3.5 only after
  observing a few weeks of output. Not investment advice.
