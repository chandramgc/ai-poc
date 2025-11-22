# Deployment Guide

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose (optional)
- Hugging Face token
- Sufficient disk space (5-10GB for model)

#### Steps

1. **Clone and Configure**
```bash
cd /path/to/ai-poc
cp .env.example .env
# Edit .env with your tokens
```

2. **Build Image**
```bash
docker build -t llm-fastapi-service:latest .
```

3. **Run Container**
```bash
docker run -d \
  --name llm-service \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/config.yml:/app/config.yml:ro \
  --restart unless-stopped \
  --memory="4g" \
  --cpus="2" \
  llm-fastapi-service:latest
```

4. **Verify**
```bash
curl http://localhost:8000/health
docker logs llm-service
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  llm-service:
    build: .
    image: llm-fastapi-service:latest
    container_name: llm-service
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./config.yml:/app/config.yml:ro
      - model-cache:/app/.cache
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  model-cache:
```

Run:
```bash
docker-compose up -d
docker-compose logs -f
```

---

### Option 2: Direct Python Deployment

#### Prerequisites
- Python 3.11+
- Poetry 1.7+
- systemd (for service management)

#### Steps

1. **Setup Application**
```bash
cd /path/to/ai-poc
poetry install --only main
cp .env.example .env
# Edit .env
```

2. **Test Run**
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. **Create Systemd Service**

Create `/etc/systemd/system/llm-service.service`:

```ini
[Unit]
Description=LLM FastAPI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ai-poc
Environment="PATH=/path/to/ai-poc/.venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/path/to/ai-poc/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Enable and Start**
```bash
sudo systemctl daemon-reload
sudo systemctl enable llm-service
sudo systemctl start llm-service
sudo systemctl status llm-service
```

5. **View Logs**
```bash
sudo journalctl -u llm-service -f
```

---

### Option 3: Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster
- kubectl configured
- Container registry access

#### Deployment YAML

Create `k8s-deployment.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: llm-service-secrets
type: Opaque
stringData:
  HUGGINGFACE_TOKEN: "your-token-here"
  SECURITY__API_KEY: "your-api-key-here"

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-service-config
data:
  config.yml: |
    app:
      name: "LLM FastAPI Service"
      host: "0.0.0.0"
      port: 8000
    model:
      name: "google/gemma-2-2b-it"
      device: "cpu"
      max_tokens: 512
    rate_limit:
      requests_per_minute: 10

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-service
  template:
    metadata:
      labels:
        app: llm-service
    spec:
      containers:
      - name: llm-service
        image: your-registry/llm-fastapi-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: HUGGINGFACE_TOKEN
          valueFrom:
            secretKeyRef:
              name: llm-service-secrets
              key: HUGGINGFACE_TOKEN
        - name: SECURITY__API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-service-secrets
              key: SECURITY__API_KEY
        volumeMounts:
        - name: config
          mountPath: /app/config.yml
          subPath: config.yml
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: llm-service-config

---
apiVersion: v1
kind: Service
metadata:
  name: llm-service
spec:
  selector:
    app: llm-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
kubectl get pods -w
kubectl logs -f deployment/llm-service
```

---

## Reverse Proxy Setup

### Nginx Configuration

```nginx
upstream llm_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Timeouts for long-running requests
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;

    location / {
        proxy_pass http://llm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streaming support
        proxy_buffering off;
        proxy_cache off;
    }

    # Rate limiting (additional layer)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
    limit_req zone=api_limit burst=5 nodelay;
}
```

---

## Monitoring Setup

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'llm-service'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard

Import dashboard with queries:

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Latency (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Tokens generated
rate(tokens_generated_total[5m])
```

---

## Environment-Specific Configurations

### Development
```bash
APP__LOG_LEVEL=DEBUG
CACHE__ENABLED=true
RATE_LIMIT__REQUESTS_PER_MINUTE=100
MODEL__DEVICE=cpu
```

### Staging
```bash
APP__LOG_LEVEL=INFO
CACHE__ENABLED=true
RATE_LIMIT__REQUESTS_PER_MINUTE=50
MODEL__DEVICE=cpu
```

### Production
```bash
APP__LOG_LEVEL=WARNING
CACHE__ENABLED=true
CACHE__SIZE=500
RATE_LIMIT__REQUESTS_PER_MINUTE=10
MODEL__DEVICE=cuda  # if GPU available
SECURITY__ENABLE_PII_FILTER=true
```

---

## Scaling Recommendations

### Vertical Scaling
- CPU: 2-4 cores minimum
- RAM: 4-8GB for small models, 16GB+ for larger
- GPU: Optional but recommended for production

### Horizontal Scaling
- Load balancer (nginx/HAProxy)
- Multiple service replicas
- Shared cache (Redis) - requires code modification
- Rate limiting across instances

### Model Optimization
- Use quantized models (int8/int4)
- Enable model caching
- Consider model distillation
- Use optimized inference engines (ONNX, TensorRT)

---

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Rotate API keys regularly
- [ ] Set strong `SECURITY__API_KEY`
- [ ] Enable rate limiting
- [ ] Use firewall rules
- [ ] Keep dependencies updated
- [ ] Enable PII filtering if handling sensitive data
- [ ] Use secrets management (Vault, AWS Secrets Manager)
- [ ] Monitor for unusual traffic patterns
- [ ] Set up intrusion detection
- [ ] Regular security audits

---

## Backup and Recovery

### Model Cache
```bash
# Backup model cache
tar -czf model-cache-backup.tar.gz ~/.cache/huggingface

# Restore
tar -xzf model-cache-backup.tar.gz -C ~/
```

### Configuration
```bash
# Backup
cp .env .env.backup
cp config.yml config.yml.backup

# Restore
cp .env.backup .env
cp config.yml.backup config.yml
```

---

## Troubleshooting Production Issues

### High Memory Usage
- Check model size: `MODEL__NAME`
- Reduce cache size: `CACHE__SIZE`
- Limit max tokens: `MODEL__MAX_TOKENS`
- Use smaller model

### Slow Responses
- Check device: prefer `MODEL__DEVICE=cuda`
- Enable caching: `CACHE__ENABLED=true`
- Reduce `MODEL__MAX_TOKENS`
- Scale horizontally

### Rate Limit Errors
- Increase: `RATE_LIMIT__REQUESTS_PER_MINUTE`
- Increase burst: `RATE_LIMIT__BURST_SIZE`
- Scale horizontally

---

## Support and Maintenance

### Health Checks
Monitor `/health` endpoint (should return 200)

### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/llm-service
```

### Updates
```bash
# Pull latest code
git pull origin main

# Update dependencies
poetry update

# Rebuild Docker
docker build -t llm-fastapi-service:latest .

# Rolling update
docker-compose up -d --force-recreate
```

---

**Deploy with confidence! 🚀**
