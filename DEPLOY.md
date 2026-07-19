# Deploy the dashboard to GitHub Pages

The Claude GitHub connector is **read-only**, so the files are uploaded from your browser
(which has full write access to your own repo). Repo is already created:
**https://github.com/torukung/stock-monitor-dashboard**

## Step 1 — Upload the site files (makes it live)

1. In **Finder**, open: `Documents/AI Workshop/Adeptio - Obsidian Vault/STOCK Monitor/web`
2. On the repo page click **Add file → Upload files**.
3. Drag in these **7 files** (this is the whole dashboard the page needs):
   - `index.html`
   - `data.js`
   - `us_top10.js`
   - `china_top10.js`
   - `th_top10.js`
   - `recap.js`
   - `drop_screen.js`
4. Click **Commit changes**.

> Do NOT drag the `.git` folder or `__pycache__`. Just the 7 files above.

## Step 2 — Turn on GitHub Pages

1. Repo → **Settings → Pages**.
2. **Source:** Deploy from a branch. **Branch:** `main`, folder **`/ (root)`** → **Save**.
3. Wait ~1 minute. Your live dashboard:
   **https://torukung.github.io/stock-monitor-dashboard/**

That's it — all six tabs are live with the current data.

## Step 3 — (Optional) daily auto-refresh of the Watchlist tab

The Watchlist prices can refresh themselves daily via GitHub Actions:

1. Upload two more files (same **Add file → Upload files**): `update.py` and `watchlist.json`.
2. Create the workflow: **Add file → Create new file**, name it exactly
   `.github/workflows/update.yml` (typing the slashes makes the folders), paste the
   contents of your local `web/.github/workflows/update.yml`, commit.
3. Add your key: **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `EODHD_API_KEY`  ·  Value: your EODHD API token (from eodhd.com)
4. The Action runs each weekday after the Asia close and commits fresh `data.js`.

## How the other tabs update

The US / China / Thailand / Recap / Drop-screen tabs are regenerated **on your Mac** by
your weekly Cowork scheduled tasks (they rewrite `us_top10.js`, `recap.js`, etc. in this
`web/` folder). To push those updates to the live site, re-upload the changed `*.js`
files (Step 1) — or ask me and I'll prepare them. The daily Action only refreshes the
Watchlist.

*Not financial advice — informational tracker only.*
