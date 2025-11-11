# Prometheus + Grafana + Alertmanager (ARM64) — macOS M4 Docker Desktop

A ready-to-run **observability stack** for Apple Silicon:
- **Prometheus** (6010) — metrics DB & UI
- **Pushgateway** (6012) — push custom metrics
- **Node Exporter** (6013) — host metrics (demo)
- **Grafana** (6011) — dashboards (pre-provisioned Prometheus + Alertmanager datasources)
- **Alertmanager** (6014) — view + group alerts

## Ports & URLs
- Prometheus → http://localhost:6010
- Grafana → http://localhost:6011  (user: `admin`, pass: `admin`)
- Pushgateway → http://localhost:6012
- Node Exporter → http://localhost:6013/metrics
- Alertmanager → http://localhost:6014

## Start
```bash
cd Prometheus-Grafana
chmod +x scripts/*.sh
docker compose up -d
./scripts/wait-for-prometheus.sh
./scripts/wait-for-grafana.sh
```

## Send Data → See in Grafana

Push demo metrics:

```bash
./scripts/push-sample-metrics.sh
```

Open Grafana dashboard "Sample — Prometheus Pushgateway Demo" and watch:
- `demo_app_requests_total`
- `demo_app_latency_seconds`
- `push_time_seconds`

## Trigger a Demo Alert

We ship an alert rule that fires when `demo_app_requests_total > 5`.

```bash
./scripts/push-alert-metric.sh           # pushes value 6 by default
```

Then check:
- **Alertmanager UI**: http://localhost:6014  (alert `DemoRequestsHigh` should be firing)
- **Grafana** → Alerting → Alert rules/Alertmanager (Alertmanager datasource is pre-provisioned)

Another rule (`NodeExporterDown`) fires if node-exporter is unreachable for 30s. To test, temporarily stop it:

```bash
docker compose stop node-exporter
```

## Query Examples
- `demo_app_requests_total`
- `rate(node_cpu_seconds_total[1m])`
- `up{job="pushgateway"}`
- `ALERTS{alertname="DemoRequestsHigh"}`

## Data Persistence
- Prometheus data: Docker volume `prometheus_data`
- Grafana data: Docker volume `grafana_data`

Reset (data loss):

```bash
docker compose down -v
```

## Troubleshooting
- **Ports busy**: Change values in `.env` (6010–6014).
- **No metrics yet**: Wait a few seconds (scrape/evaluation: 5s/5s) or refresh.
- **Grafana login fails**: Ensure creds match `.env`.
- **Want notifications (Slack/Email/Webhook)**: edit `alertmanager/config.yml` receiver `default`.
- **macOS Note**: Node Exporter runs in limited mode (container metrics only) due to macOS Docker Desktop limitations. For full host metrics monitoring, deploy on Linux.

## Extending
- Add more jobs in `prometheus/prometheus.yml`.
- Add more alerts in `prometheus/rules/alerts.yml`.
- Configure Alertmanager receivers (Slack/email/webhook) in `alertmanager/config.yml`.

---

## Quickstart (copy/paste)
```bash
cd Prometheus-Grafana
chmod +x scripts/*.sh
docker compose up -d
./scripts/wait-for-prometheus.sh
./scripts/wait-for-grafana.sh
./scripts/push-sample-metrics.sh
./scripts/push-alert-metric.sh
open http://localhost:6011
open http://localhost:6014
```

## Acceptance checks
- ✅ 5 containers come up healthy: `prometheus`, `alertmanager`, `pushgateway`, `node-exporter`, `grafana`.
- ✅ Pushing metrics makes them visible in Prometheus and Grafana.
- ✅ Running `./scripts/push-alert-metric.sh` causes `DemoRequestsHigh` to appear in Alertmanager and in Grafana's Alertmanager view.
