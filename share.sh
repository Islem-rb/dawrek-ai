#!/usr/bin/env bash
# Public HTTPS link to this laptop for a live demo: free, no account (Cloudflare Quick Tunnel).
# Phones join over 4G and the microphone works (HTTPS). The link changes on every start;
# the QR code on /screen follows it automatically. Stop with Ctrl+C.
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v cloudflared >/dev/null; then
  echo "cloudflared is not installed. On Ubuntu/Debian:"
  echo "  curl -L -o /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
  echo "  sudo dpkg -i /tmp/cloudflared.deb"
  exit 1
fi
export PORT=${PORT:-8000}
./run.sh &
APP=$!
trap 'kill $APP 2>/dev/null' EXIT
until curl -s "localhost:$PORT/api/info" >/dev/null; do sleep 1; done
echo -e "\n  Look for the https://….trycloudflare.com link below, then open /screen on it.\n"
cloudflared tunnel --no-autoupdate --url "http://localhost:$PORT"
