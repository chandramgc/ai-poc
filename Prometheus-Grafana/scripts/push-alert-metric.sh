#!/usr/bin/env bash
set -euo pipefail

PG_PORT="${PUSHGATEWAY_PORT:-6012}"
JOB="${1:-demo-job}"
INSTANCE="${2:-local}"

# This sets the counter above the alert threshold (>5) to trigger DemoRequestsHigh
VALUE="${3:-6}"

echo "[push-alert] Setting demo_app_requests_total=${VALUE} to trigger alert ..."
cat <<EOF | curl -s --data-binary @- "http://localhost:${PG_PORT}/metrics/job/${JOB}/instance/${INSTANCE}"
# TYPE demo_app_requests_total counter
demo_app_requests_total ${VALUE}
EOF
echo "[push-alert] Metric pushed. Alert should fire shortly (evaluation every ${PROMETHEUS_EVALUATION_INTERVAL:-5s})."
