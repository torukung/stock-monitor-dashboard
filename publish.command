#!/bin/bash
# STOCK Monitor — refresh the Watchlist + publish the whole dashboard to Netlify.
# Double-click to run manually, or let the launchd job run it on a schedule.
# One-time setup (see AUTOMATE.md):  npm install -g netlify-cli  &&  netlify login
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.npm-global/bin:$PATH"
cd "$(dirname "$0")" || exit 1
SITE="1d358a37-cb53-46cc-8c41-010313d235d5"   # tor-stock-monitor.netlify.app
echo "== STOCK Monitor publish — $(date) =="

# 1) Optional: refresh Watchlist prices. Put your EODHD token in a file named
#    .eodhd_key (one line) next to this script. The other 5 tabs are refreshed
#    by your weekly Cowork tasks, which already write their .js into this folder.
if [ -f .eodhd_key ] && command -v python3 >/dev/null 2>&1; then
  export EODHD_API_KEY="$(tr -d '[:space:]' < .eodhd_key)"
  echo "-- refreshing Watchlist (update.py)…"
  python3 update.py || echo "   update.py failed — keeping existing data.js"
fi

# 2) Stage ONLY the site files (keeps seed scripts, .eodhd_key and .git private).
rm -rf .deploy && mkdir -p .deploy
cp index.html data.js us_top10.js china_top10.js th_top10.js recap.js drop_screen.js .deploy/ 2>/dev/null

# 3) Publish to Netlify.
if ! command -v netlify >/dev/null 2>&1; then
  echo "!! netlify CLI not found."
  echo "   One-time:  npm install -g netlify-cli   then   netlify login"
  exit 1
fi
netlify deploy --prod --dir .deploy --site "$SITE"
echo "== done — https://tor-stock-monitor.netlify.app/ =="
