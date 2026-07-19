#!/bin/bash
# Double-click this file to refresh the 4 Singapore (Yahoo) names.
# It installs yfinance the first time, then runs update_yahoo.py.
cd "$(dirname "$0")" || exit 1

echo "Installing yfinance (first run only)…"
python3 -m pip install --quiet yfinance 2>/dev/null \
  || python3 -m pip install --quiet --user yfinance 2>/dev/null \
  || python3 -m pip install --quiet --break-system-packages yfinance 2>/dev/null

echo
python3 update_yahoo.py
echo
read -n 1 -s -r -p "Done — press any key to close this window."
echo
