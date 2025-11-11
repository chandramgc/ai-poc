#!/usr/bin/env bash
set -euo pipefail

PG_PORT="${PUSHGATEWAY_PORT:-6012}"
JOB="${1:-demo-job}"
INSTANCE="${2:-local}"

echo "[push-sample] Pushing demo metrics to Pushgateway on port ${PG_PORT} ..."
cat <<EOF | curl -s --data-binary @- "http://localhost:${PG_PORT}/metrics/job/${JOB}/instance/${INSTANCE}"
# TYPE demo_app_requests_total counter
demo_app_requests_total 1
# TYPE demo_app_latency_seconds gauge
demo_app_latency_seconds 0.123
EOF

echo "[push-sample] Done. Check Grafana (http://localhost:${GRAFANA_PORT:-6011}) dashboard 'Sample — Prometheus Pushgateway Demo'."
