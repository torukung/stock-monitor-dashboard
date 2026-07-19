# STOCK Monitor — daily dashboard

A self-updating web page for your research watchlist. Each name shows a 3-month
price chart, your entry, a suggested buy-on-dip level, take-profit and stop,
reward:risk, momentum/RS, trend, and an upside ladder for **3mo / 6mo / 12mo / 3yr / 5yr**.

## Files

| File | What it is |
|------|------------|
| `index.html` | The dashboard. Open it in any browser. |
| `watchlist.json` | Your holdings + entry/stop/targets. **This is the file you edit.** |
| `update.py` | Fetches prices, computes the analysis, writes `data.js` + `data.json`. |
| `data.js` / `data.json` | Generated output the page reads. Don't edit by hand. |
| `.github/workflows/update.yml` | Runs `update.py` automatically every weekday. |
| `_seed.py` | One-off that built the first `data.js` from sample prices (optional, ignore). |

## See it now

Double-click `index.html` — it opens with real data already baked in for the
15 EODHD-covered names. The 4 Singapore names show "awaiting sync" until
you run the updater once (next section).

## Run the updater yourself (local)

1. Get your EODHD API key: eodhd.com → dashboard → **API token**.
2. Install Python deps (one time):
   ```
   pip install yfinance
   ```
3. Run it (from inside this `web/` folder):
   ```
   EODHD_API_KEY=your_key_here python3 update.py
   ```
   This refreshes `data.js`, including the Singapore names via Yahoo.
   Reload `index.html` to see the update.

## Make it auto-update daily + put it online (free)

Hosting on GitHub Pages runs the daily refresh and serves the page for free.

1. Create a new GitHub repo and upload the **contents of this `web/` folder** to it
   (so `index.html` sits at the repo root).
2. Repo **Settings → Secrets and variables → Actions → New repository secret**:
   - Name: `EODHD_API_KEY`  ·  Value: your EODHD key.
3. Repo **Settings → Pages**: set Source = `Deploy from a branch`, branch = `main`, folder = `/ (root)`.
4. The workflow in `.github/workflows/update.yml` runs every weekday at 13:00 UTC
   (20:00 Bangkok, after Asia closes), refreshes the data, and commits it. The page
   updates itself. You can also trigger it anytime from the repo's **Actions** tab.

Your page lives at `https://<your-username>.github.io/<repo-name>/`.
Keep the repo **private** if you don't want it public — Pages still works on private
repos for personal use, or add Cloudflare Access in front of it.

## Editing the watchlist

Open `watchlist.json` and edit a holding. Key fields:

- `source`: `eodhd` (Thailand/HK/China/US) or `yahoo` (Singapore).
- `symbol`: EODHD form (`AMATA.BK`, `9988.HK`, `688256.SHG`) or Yahoo form (`BS6.SI`, `S63.SI`).
- `entry`, `stop`, `target_1mo`, `target_6mo`, `target_12mo`: absolute prices (not %).
- `cagr_long`: annual growth used to extend the 12mo target into the 3yr/5yr upside.
- Set targets to `null` for a watch-only name (no upside ladder shown).

Then re-run `update.py`. No need to touch `index.html`.

## How the numbers are built

- **Upside** = target ÷ latest close − 1. The 3-mo target is interpolated between
  your 1-mo and 6-mo targets; 3yr/5yr = 12-mo target grown at `cagr_long`.
- **Suggested buy** = a dip level, `max(stop×1.02, last×0.93)` — never below your stop.
- **Take-profit** = nearest target above price (flips to "trail" once all targets are met).
- **Reward:risk** = (12-mo target − price) ÷ (price − stop).
- **RS** = 1–100 rank of each name's 3-month return across the watchlist.
- **Trend** = last close vs 50-day EMA.

## Data routing (why two sources)

EODHD ($20 plan) covers Thailand, Hong Kong, China A-shares, Taiwan, Korea and US,
but **not** Singapore (SGX) — those come free from Yahoo Finance via `yfinance`.
SK Hynix on EODHD returns masked prices, so route it to Yahoo too if you add it.
India (NSE) is **excluded** from the watchlist (no reliable feed). Full detail in `../04_DATA_SOURCES.md`.

## US, China & Thailand Top 10 tabs (identical scheme)

Three weighted-ranking tabs, side by side, on **one shared layout** so the data points line up. Each ranks 10 names by composite **weight** (CUS = market-cap 40 + turnover/volume 30 + mentions/attention 30), with **suggested buy** and **take-profit** price columns, a 3-mo mini chart, and **bull-probability** columns for 1m / 3m / 1-3yr. Sortable by weight or any horizon.

**Click any row to expand** an earnings panel: an **8-quarter revenue chart** (bars coloured beat / miss / in-line), plus **backlog**, **cash**, **guidance**, and the driver / risk. Buy = ~7% below last; take-profit = last × (1 + 3-month base case) — the level before momentum tends to stall.

- US reads `us_top10.js` — `weekly-us-stock-top-10-weight-ranking`.
- China reads `china_top10.js` — `weekly---china-market-top-10-weighted-ranking`.
- Thailand reads `th_top10.js` — `weekly-th-stock-top-10-weight-ranking`.

All three tasks also write their full markdown reports to `../Reports/Rankings/`. Earnings, backlog and cash come from **web research** (EODHD fundamentals and FMP statements aren't on the current plans), so they're best-effort and the weekly tasks keep them fresh.

## Weekly recap tab (3rd tab)

A weekly market recap: news/top-of-mind + a bull outlook (1M / 6M / 3yr) on top, then stocks grouped by country (TH / HK / China A / US / SG), sector trends by region across 1M / 6M / 3yr, and **moving-in / moving-out** lists. A name moves in only when its watchlist signal *and* 1-month momentum both turn up; it moves out when both roll over. Moving-out entries keep the date they first dropped (`out since …`) and are auto-removed once the name moves back in.

It reads `recap.js`, regenerated every **Saturday ~12:05 Bangkok** by the existing `stock-thchinaus-weekly-scraping` task (the same one that versions `02_WATCHLIST.md` and writes the Apple-style HTML report). That task now also reads the previous `recap.js` to carry the moving-out dates forward.

## Drop screen tab (4th tab)

The weekly steep-decliner screen: news recap on top, a **Suggested — nearly matched** section for names that passed most of the three hard filters (IPO age < 5y, two straight growth years, strong/growing backlog), then decliners grouped by country (Thailand / US). Each assessed name shows an **8-quarter revenue chart** with bars coloured by **beat / miss / in-line**, plus **backlog**, **cash** and **guidance**, and a moving-in / moving-out list (same dated persistence as the recap tab).

It reads `drop_screen.js`, regenerated weekly by the existing `weekly-stock-drop-screen` task (the same one that writes the Drop Screen markdown report). Earnings/backlog/cash come from web research — EODHD fundamentals and FMP statements are not on the current plans, so figures are best-effort and a name is excluded rather than guessed when a hard filter can't be verified.

*Not financial advice — an informational tracker only.*
