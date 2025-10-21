# Supabase + Langfuse Docker Stack

A production-ready Docker Compose setup for running [Supabase](https://supabase.com) and [Langfuse](https://langfuse.com) locally on Docker Desktop.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- At least 4GB of RAM allocated to Docker
- Ports 6000, 6001, 6002, and 6003 available on localhost

### Setup

1. **Clone or download this directory**

2. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and update the following critical values:**
   - `POSTGRES_PASSWORD` - Set a strong password for PostgreSQL
   - `JWT_SECRET` - Generate with: `openssl rand -base64 32`
   - `LANGFUSE_NEXTAUTH_SECRET` - Generate with: `openssl rand -base64 32`
   - `LANGFUSE_SALT` - Generate with: `openssl rand -base64 32`
   - `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` - Use the demo keys or generate proper JWTs

   > **Important:** Never commit your `.env` file with real secrets to version control!

4. **Start the stack:**
   ```bash
   docker compose up -d
   ```

5. **Wait for all services to be healthy (typically 30-60 seconds):**
   ```bash
   docker compose ps
   ```

6. **Initialize Langfuse database:**
   
   On first run, Langfuse needs to initialize its database. Check logs:
   ```bash
   docker compose logs -f langfuse
   ```
   
   Wait for the message indicating migrations are complete.

## 🌐 Access URLs

Once all services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Langfuse** | http://localhost:6005 | Langfuse UI for LLM observability |
| **Supabase API Gateway** | http://localhost:6001 | Kong API Gateway for all Supabase services |
| **Supabase Studio** | http://localhost:6002 | Supabase Admin Dashboard |
| **PostgreSQL** | localhost:6003 | PostgreSQL database (direct access) |
| **Mailpit** | http://localhost:6004 | Email testing UI - ARM64 compatible |

### Supabase API Endpoints

All Supabase services are accessible through the Kong gateway at `http://localhost:6001`:

- Auth: `http://localhost:6001/auth/v1/`
- REST API: `http://localhost:6001/rest/v1/`
- Realtime: `http://localhost:6001/realtime/v1/`
- Storage: `http://localhost:6001/storage/v1/`
- Postgres Meta: `http://localhost:6001/pg/`

## 📋 Services Overview

This stack includes:

### Supabase Services
- **supabase-db** - PostgreSQL 15 database (shared by Supabase and Langfuse)
- **supabase-kong** - Kong API Gateway (port 6001)
- **supabase-studio** - Admin UI (port 6002)
- **supabase-auth** - GoTrue authentication service
- **supabase-rest** - PostgREST API
- **supabase-realtime** - Realtime subscriptions
- **supabase-storage** - Object storage
- **supabase-imgproxy** - Image transformations
- **supabase-meta** - PostgreSQL metadata API

### Langfuse Service
- **langfuse** - LLM observability platform (port 6005)

### Development Tools
- **mailpit** - SMTP testing server (Web UI: port 6004, SMTP: port 1025) - ARM64 compatible

## 🔧 Troubleshooting

### Check service status
```bash
docker compose ps
```

All services should show as `healthy` or `running`.

### View logs for specific services

**Langfuse:**
```bash
docker compose logs -f langfuse
```

**Supabase Kong (API Gateway):**
```bash
docker compose logs -f supabase-kong
```

**Supabase Studio:**
```bash
docker compose logs -f supabase-studio
```

**Supabase Auth:**
```bash
docker compose logs -f supabase-auth
```

**PostgreSQL:**
```bash
docker compose logs -f supabase-db
```

**All services:**
```bash
docker compose logs -f
```

### Common Issues

#### Port conflicts
If ports 6000, 6001, 6002, or 6003 are already in use:
1. Stop the conflicting service, or
2. Edit `docker-compose.yml` to change the external port mappings

#### Services not starting
1. Check if Docker Desktop has enough memory allocated (minimum 4GB recommended)
2. Ensure all required environment variables are set in `.env`
3. Check individual service logs for specific errors

#### Database connection errors
1. Ensure PostgreSQL is healthy: `docker compose ps supabase-db`
2. Verify `POSTGRES_PASSWORD` is consistent in `.env`
3. For Langfuse, ensure the `LANGFUSE_DB` database exists (it's created automatically on first run)

#### Langfuse not accessible
1. Check if migrations completed: `docker compose logs langfuse | grep migration`
2. Restart Langfuse: `docker compose restart langfuse`
3. Verify database connectivity

#### Cannot access Supabase Studio
1. Verify Kong is healthy: `docker compose ps supabase-kong`
2. Check Studio logs: `docker compose logs supabase-studio`
3. Ensure `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` are set correctly

### Reset everything
To completely reset the stack and all data:
```bash
docker compose down -v
rm .env
cp .env.example .env
# Edit .env with new secrets
docker compose up -d
```

## 🛠️ Management Commands

### Start services
```bash
docker compose up -d
```

### Stop services
```bash
docker compose stop
```

### Restart services
```bash
docker compose restart
```

### Stop and remove everything (keeps volumes)
```bash
docker compose down
```

### Stop and remove everything including data
```bash
docker compose down -v
```

### Rebuild and restart a specific service
```bash
docker compose up -d --force-recreate --build supabase-studio
```

### Update all images to latest versions
```bash
docker compose pull
docker compose up -d
```

## 📊 Database Access

### Connect to PostgreSQL directly

**Using external client (recommended):**
- Host: `localhost`
- Port: `6003`
- User: Value of `POSTGRES_USER` in `.env` (default: `postgres`)
- Password: Value of `POSTGRES_PASSWORD` in `.env`
- Database: `postgres` (Supabase) or `langfuse` (Langfuse)

**Connection string format:**
```
postgresql://postgres:your-password@localhost:6003/postgres
```

**Using Docker exec:**
```bash
docker compose exec supabase-db psql -U postgres
```

**Using psql from host machine:**
```bash
psql -h localhost -p 6003 -U postgres -d postgres
```

## 🔐 Security Notes

1. **Change default secrets** - All secrets in `.env.example` are placeholders
2. **Never commit `.env`** - Add `.env` to `.gitignore`
3. **Use strong passwords** - Especially for production deployments
4. **Generate proper JWT keys** - The example keys are for demo purposes only
5. **SMTP configuration** - Required for email-based authentication
6. **Network isolation** - All services communicate on isolated `stack_net` network

## 🎯 Port Configuration

This stack uses **custom external port mappings** to avoid conflicts:

| Service | Internal Port | External Port | Note |
|---------|---------------|---------------|------|
| Langfuse | 3000 | **6005** | Custom mapping |
| Kong (API Gateway) | 8000 | **6001** | Custom mapping |
| Supabase Studio | 3000 | **6002** | Custom mapping |
| PostgreSQL | 5432 | **6003** | Custom mapping |
| Mailpit | 8025 | **6005** | Custom mapping |
| All other services | Default | Not exposed | Internal only |

All internal service communication uses default ports for compatibility with official Supabase configurations.

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Langfuse Documentation](https://langfuse.com/docs)
- [Kong Gateway Documentation](https://docs.konghq.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Support

For issues specific to:
- **Supabase**: Check [Supabase GitHub Issues](https://github.com/supabase/supabase/issues)
- **Langfuse**: Check [Langfuse GitHub Issues](https://github.com/langfuse/langfuse/issues)
- **This setup**: Review troubleshooting section above or check Docker logs

## 📝 License

This Docker Compose configuration is provided as-is. Individual services (Supabase, Langfuse, Kong, etc.) are subject to their respective licenses.
