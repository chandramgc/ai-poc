#!/usr/bin/env bash
set -euo pipefail
echo "[wait-for-grafana] Waiting for Grafana ..."
until docker compose exec -T grafana wget -qO- http://localhost:3000/api/health >/dev/null 2>&1; do
  sleep 2
  echo -n "."
done
echo
echo "[wait-for-grafana] Grafana is ready."
