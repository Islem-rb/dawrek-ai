#!/usr/bin/env bash
# One-command start: creates a venv on first run, installs deps, starts Dawrek.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi
[ -f .env ] || cp .env.example .env
exec .venv/bin/python -m backend.main
