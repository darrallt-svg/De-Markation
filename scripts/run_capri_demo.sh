#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt
cp 'Criteria Grouping Models/CAPRI.json' config/criteria.json

echo "Starting De-Markation demo on http://127.0.0.1:5000"
DEMO_MODE=true python app.py
