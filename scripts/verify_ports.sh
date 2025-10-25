#!/usr/bin/env bash
set -euo pipefail
ports=(4444 7860 9100 6006 4317)
for p in "${ports[@]}"; do
  if lsof -i TCP:$p -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $p is in use"; exit 1
  fi
done
echo "All required ports are free."
