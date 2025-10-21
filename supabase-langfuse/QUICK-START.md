# Quick Start Guide - Supabase + Langfuse Stack

## 🚀 Your Stack is Running!

All services have been successfully deployed on your Apple Silicon Mac.

## 🌐 Access Your Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Langfuse** | http://localhost:6005 | LLM observability & monitoring |
| **Supabase API** | http://localhost:6001 | Kong API Gateway |
| **Supabase Studio** | http://localhost:6002 | Database admin UI |
| **PostgreSQL** | localhost:6003 | Direct database access |
| **Mailpit** | http://localhost:6004 | Email testing interface |

## ⚡ Quick Commands

### Check Status
```bash
cd /Users/girish/MyDrive/Workspace/ai-poc/supabase-langfuse
docker compose ps
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f langfuse
```

### Restart Stack
```bash
docker compose restart
```

### Stop Stack
```bash
docker compose down
```

### Start Stack
```bash
docker compose up -d
```

## 🔑 View Your Credentials

```bash
cd /Users/girish/MyDrive/Workspace/ai-poc/supabase-langfuse
cat .env | grep -E "^(SUPABASE_ANON_KEY|SUPABASE_SERVICE_ROLE_KEY|POSTGRES_PASSWORD)="
```

## 📝 First Steps

### 1. Access Langfuse
1. Open http://localhost:6005
2. Create your first account
3. Start tracking your LLM applications

### 2. Access Supabase Studio
1. Open http://localhost:6002
2. Explore your PostgreSQL databases
3. Create tables and manage data

### 3. Test Email Sending
1. Open http://localhost:6004
2. Trigger any email from your services
3. View captured emails in Mailpit UI

### 4. Connect to PostgreSQL
```bash
psql postgresql://postgres:your-super-secret-and-long-postgres-password@localhost:6003/postgres
```

## 🎯 What's Configured

✅ **Langfuse v2** - No ClickHouse required  
✅ **Mailpit** - ARM64 compatible email testing  
✅ **Kong Gateway** - All Supabase APIs unified  
✅ **Auto-generated Secrets** - Secure JWT tokens  
✅ **Shared Database** - PostgreSQL 15 for all services  

## 📖 Documentation

- **Detailed Deployment Info:** `DEPLOYMENT-SUMMARY.md`
- **Full Documentation:** `README.md`
- **JWT Generation:** `SECRETS-GENERATOR-README.md`

## 🆘 Troubleshooting

### Services not starting?
```bash
docker compose down
docker compose up -d
docker compose logs -f
```

### Port conflicts?
```bash
lsof -i :6005  # Langfuse
lsof -i :6001  # Kong
lsof -i :6002  # Studio
lsof -i :6003  # PostgreSQL
lsof -i :6004  # Mailpit
```

### Need to regenerate secrets?
```bash
./generate-jwt.sh
docker compose restart
```

---

**Ready to start!** 🎉

All services should be fully operational within 60 seconds of starting.
