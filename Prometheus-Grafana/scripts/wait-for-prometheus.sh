#!/usr/bin/env bash
set -euo pipefail
echo "[wait-for-prometheus] Waiting for Prometheus ..."
until docker compose exec -T prometheus wget -qO- http://localhost:9090/-/ready >/dev/null 2>&1; do
  sleep 2
  echo -n "."
done
echo
echo "[wait-for-prometheus] Prometheus is ready."
