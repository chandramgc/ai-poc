# Redis on Docker (Apple Silicon)

This setup provides a production-ready Redis instance running in Docker on macOS (Apple Silicon), with persistence and password protection.

## Prerequisites

- Docker Desktop for macOS
- Apple Silicon Mac (M1/M2/M3/M4)

## Getting Started

The configuration is ready to use. The setup includes:
- Password protection (configurable via .env)
- Data persistence using named volumes
- Health checking
- Configurable logging levels
- Multi-arch support (no Rosetta required)

## Running Redis

1. Start Redis:
```bash
docker compose down && docker compose --env-file .env up -d
```

2. Check the logs:
```bash
docker compose logs -f redis
```

3. Test the connection from inside the container:
```bash
docker exec -it redis redis-cli -a "$REDIS_PASSWORD" ping
# Should return: PONG
```

4. (Optional) Test from your Mac if you have redis-cli installed:
```bash
# Install redis-cli if needed:
# brew install redis

redis-cli -a "$REDIS_PASSWORD" -p "$REDIS_PORT" ping
```

## Stopping and Cleaning Up

Stop the container:
```bash
docker compose down
```

List volumes:
```bash
docker volume ls
```

Remove the data volume (warning: data loss!):
```bash
docker volume rm redis_data
```

## Troubleshooting

### Port 6379 Already in Use
Check what's using the port:
```bash
lsof -i :6379
```
Then either:
- Stop the conflicting process, or
- Change REDIS_PORT in .env

### Reset Password/Data
1. Stop containers: `docker compose down`
2. Remove volume: `docker volume rm redis_data`
3. Start fresh: `docker compose up -d`

### No redis-cli on Host
Use the container's CLI:
```bash
docker exec -it redis redis-cli -a "$REDIS_PASSWORD"
```

## Connection String

For applications connecting to this Redis instance:
```
redis://:changeme123@localhost:6379/0
```

# Test Redis connection
redis-cli -a "changeme123" ping  # Should return PONG

# Set a value
redis-cli -a "changeme123" set test "hello"

# Get the value
redis-cli -a "changeme123" get test

Remember to change the password in .env for production use!