# Docker Deployment Guide

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed (comes with Docker Desktop)

## Quick Start

### 1. Build and Start the Application

```bash
# Build and start the containers
docker-compose up -d

# View logs
docker-compose logs -f app

# Check container status
docker-compose ps
```

### 2. Access the Application

- **API Base URL**: http://localhost:1001
- **API Documentation**: http://localhost:1001/docs
- **Health Check**: http://localhost:1001/healthz

### 3. Test the API

**REST API:**
```bash
curl -H "X-API-Key: dev" "http://localhost:1001/relationship?name=Saanvi"
```

**WebSocket (using websocat or wscat):**
```bash
websocat ws://localhost:1001/relationship/stream
# Then send: {"name": "Saanvi", "trace": true}
```

## Docker Commands

### Start Services
```bash
# Start in background
docker-compose up -d

# Start with build (after code changes)
docker-compose up -d --build

# Start with logs
docker-compose up
```

### Stop Services
```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers, volumes, and images
docker-compose down -v --rmi all
```

### View Logs
```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Logs for specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100
```

### Container Management
```bash
# List running containers
docker-compose ps

# Execute command in container
docker-compose exec app bash

# Restart container
docker-compose restart app

# View resource usage
docker stats
```

## Configuration

### Environment Variables

Edit `docker-compose.yml` to change configuration:

```yaml
environment:
  - LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
  - ALLOW_FUZZY=true        # Enable fuzzy matching
  - API_KEY=dev             # API authentication key
  - CORS_ORIGINS=http://localhost:3000,http://localhost:1001
  - EXCEL_PATH=data/relationships.csv
  - ALIASES_PATH=data/aliases.csv
```

### Port Configuration

Change the exposed port by editing `docker-compose.yml`:

```yaml
ports:
  - "9000:1001"  # Map port 9000 on host to 1001 in container
```

Or use environment variable:
```bash
PORT=9000 docker-compose up -d
```

## Data Management

### Update Data Files

The `data` directory is mounted as a read-only volume. To update data:

1. Update files in `./data/` directory
2. Reload data via API:
   ```bash
   curl -X POST -H "X-API-Key: dev" http://localhost:8000/reload
   ```

Or restart the container:
```bash
docker-compose restart app
```

## Troubleshooting

### Container Won't Start

1. Check logs:
   ```bash
   docker-compose logs app
   ```

2. Verify port availability:
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

3. Rebuild container:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Health Check Failing

```bash
# Check health status
docker-compose ps

# Check health endpoint
curl http://localhost:8000/healthz

# View detailed logs
docker-compose logs --tail=50 app
```

### Permission Issues

If you encounter permission errors with data files:

```bash
# Fix permissions (macOS/Linux)
chmod -R 755 data/
```

### Container Uses Too Much Memory

1. Check resource usage:
   ```bash
   docker stats
   ```

2. Limit resources in `docker-compose.yml`:
   ```yaml
   services:
     app:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
           reservations:
             memory: 256M
   ```

## Production Deployment

### Security Recommendations

1. **Change API Key**: Update `API_KEY` environment variable
2. **Use HTTPS**: Put behind a reverse proxy (nginx, Traefik)
3. **Limit CORS**: Specify exact origins in `CORS_ORIGINS`
4. **Read-only filesystem**: Already configured for data volume
5. **Non-root user**: Already configured in Dockerfile

### Monitoring

Add health checks and monitoring:

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Scaling

To run multiple instances:

```bash
docker-compose up -d --scale app=3
```

Note: You'll need a load balancer for proper distribution.

## Additional Commands

### Clean Up Docker System

```bash
# Remove unused containers, networks, images
docker system prune

# Remove everything including volumes
docker system prune -a --volumes
```

### View Container Details

```bash
# Inspect container
docker inspect relationship-finder-api

# View container processes
docker-compose top
```

### Export/Import Images

```bash
# Save image to file
docker save -o relationship-finder.tar relationship-finder-api

# Load image from file
docker load -i relationship-finder.tar
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f app`
2. Verify configuration in `docker-compose.yml`
3. Review Dockerfile for build issues
