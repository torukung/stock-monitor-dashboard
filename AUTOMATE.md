# Automate the live dashboard (Netlify)

Live site: **https://tor-stock-monitor.netlify.app/** (Netlify project `tor-stock-monitor`)

Your weekly Cowork tasks already rewrite the data files (`us_top10.js`, `recap.js`,
`drop_screen.js`, etc.) **into this `web/` folder**. The only missing piece is pushing
that folder to Netlify. `publish.command` does exactly that, and a small macOS
scheduled job runs it for you. (This lives on your Mac because neither the GitHub nor
the Netlify connector can publish files from Claude's side.)

## One-time setup (≈3 minutes)

1. **Install the Netlify CLI and log in** — open Terminal and run:
   ```
   npm install -g netlify-cli
   netlify login
   ```
   (A browser opens; click Authorize. This stores your Netlify credentials locally so
   the script can deploy without any token in a file.)

2. **(Optional) daily Watchlist price refresh.** The 5 research tabs refresh from your
   weekly tasks already. To also refresh the *Watchlist* tab's prices automatically,
   give the script your EODHD key and install one Python package:
   ```
   echo "YOUR_EODHD_TOKEN" > ".eodhd_key"
   pip3 install yfinance        # for the 4 Singapore names
   ```
   (Skip this if you only care about the ranking/recap/drop tabs. `.eodhd_key` is never
   uploaded — the script only deploys the 7 site files.)

3. **Test it** — double-click **`publish.command`** (in this `web/` folder). A Terminal
   window runs it and ends with `done — https://tor-stock-monitor.netlify.app/`. Reload
   the site to confirm.

## Schedule it (hands-off)

Run the publish automatically every day at 1:00 PM (after the weekend ranking tasks):
```
cp "com.adeptio.stockmonitor.publish.plist" ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.adeptio.stockmonitor.publish.plist
```
To change the time, edit `Hour`/`Minute` in the plist, then `launchctl unload` + `load`
again. Logs go to `/tmp/stockmonitor-publish.log`.

## What's automated vs not

| Piece | How it refreshes | Automated? |
|-------|------------------|------------|
| Watchlist prices | `update.py` in `publish.command` (needs `.eodhd_key`) | ✅ daily |
| US / China / Thailand / Recap / Drop tabs | your weekly Cowork tasks write the `.js` here | ✅ weekly |
| Publishing all of it to the live site | `publish.command` via the launchd job | ✅ on schedule |

So end-to-end: tasks update the files → the daily job redeploys → the live site stays
current, with no manual dragging.

> The research tabs' figures (bull %, earnings, backlog, cash) are still produced by the
> weekly Cowork tasks (they need Claude + web research) — no server can generate those.
> The job just publishes whatever those tasks have written.

*Not financial advice — informational tracker only.*
