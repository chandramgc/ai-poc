# 🔐 Supabase + Langfuse Secrets Generator

Complete automated secrets and JWT tokens generator for your Supabase + Langfuse stack.

## 🎯 What It Does

This script automatically generates and updates **ALL** required secrets for your stack:

### Secrets Generated
1. ✅ **JWT_SECRET** - Master secret for Supabase JWT signing
2. ✅ **LANGFUSE_NEXTAUTH_SECRET** - NextAuth secret for Langfuse
3. ✅ **LANGFUSE_SALT** - Salt for Langfuse encryption

### JWT Tokens Generated
4. ✅ **SUPABASE_ANON_KEY** - Public/client-side JWT token
5. ✅ **SUPABASE_SERVICE_ROLE_KEY** - Admin/backend JWT token

### Files Updated Automatically
- ✅ `.env` - All secrets and tokens
- ✅ `kong.yml` - JWT tokens for API gateway

## 🚀 Quick Start

### Generate Everything (Recommended)

```bash
cd supabase-langfuse
./generate-jwt.sh
```

This will:
1. Generate new `JWT_SECRET`
2. Generate new `LANGFUSE_NEXTAUTH_SECRET`
3. Generate new `LANGFUSE_SALT`
4. Generate JWT tokens signed with the new `JWT_SECRET`
5. Update all values in `.env`
6. Update JWT tokens in `kong.yml`
7. Create backups of both files

## 📋 Usage Options

### 1. Generate All Secrets + Tokens (Default)

```bash
./generate-jwt.sh
```

**Generates & Updates:**
- JWT_SECRET
- LANGFUSE_NEXTAUTH_SECRET
- LANGFUSE_SALT
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY

**Files Updated:**
- .env (all 5 values)
- kong.yml (2 JWT tokens)

### 2. Generate Only Secrets (Keep Existing Tokens)

```bash
./generate-jwt.sh --secrets-only
```

**Generates & Updates:**
- JWT_SECRET
- LANGFUSE_NEXTAUTH_SECRET
- LANGFUSE_SALT

**Files Updated:**
- .env (3 secrets only)

**Use Case:** When you want new application secrets but don't need to regenerate JWT tokens.

### 3. Generate Only Tokens (Use Existing JWT_SECRET)

```bash
./generate-jwt.sh --tokens-only
```

**Generates & Updates:**
- SUPABASE_ANON_KEY (using existing JWT_SECRET)
- SUPABASE_SERVICE_ROLE_KEY (using existing JWT_SECRET)

**Files Updated:**
- .env (2 tokens only)
- kong.yml (2 tokens)

**Use Case:** When you need to regenerate JWT tokens but want to keep your existing JWT_SECRET.

### 4. Show Help

```bash
./generate-jwt.sh --help
```

## 📝 Example Output

```bash
$ ./generate-jwt.sh

================================================================================
Supabase + Langfuse Secrets & JWT Generator
================================================================================

📁 Found .env in workspace root: ../.env

🔐 Generating new secrets...
   ✅ Generated JWT_SECRET
   ✅ Generated LANGFUSE_NEXTAUTH_SECRET
   ✅ Generated LANGFUSE_SALT

🔑 Generating JWT tokens...

✅ Secrets Generated Successfully!
================================================================================

🔐 SECRETS:
--------------------------------------------------------------------------------
JWT_SECRET=hPqiHMA45xoMVpzh3TGEpjSVKzOvx/zuTddo8m7EqYM=

LANGFUSE_NEXTAUTH_SECRET=Q0osEpMVdmpGhhFQFMcAdS9GwLKkHj91xyv7lOYoyuQ=

LANGFUSE_SALT=3yJTQkfDfXOpeE5EF5XUPQLT+egd1TT8yQH1ougkyVk=

--------------------------------------------------------------------------------

🔑 JWT TOKENS:
--------------------------------------------------------------------------------
SUPABASE_ANON_KEY:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

SUPABASE_SERVICE_ROLE_KEY:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

--------------------------------------------------------------------------------

================================================================================

📝 Updating ../.env...
   ✅ Backup created: ../.env.backup
   ✅ Updated JWT_SECRET
   ✅ Updated LANGFUSE_NEXTAUTH_SECRET
   ✅ Updated LANGFUSE_SALT
   ✅ Updated SUPABASE_ANON_KEY
   ✅ Updated SUPABASE_SERVICE_ROLE_KEY

✅ .env file updated successfully!

📝 Updating kong.yml...
   ✅ Backup created: kong.yml.backup
   ✅ Updated anon consumer key
   ✅ Updated service_role consumer key

✅ kong.yml updated successfully!

================================================================================
⚠️  IMPORTANT NOTES:
1. Keep these tokens secret - never commit them to version control
2. The SERVICE_ROLE_KEY has full database access - protect it carefully
3. These tokens are valid for 10 years
4. If you updated .env, restart your Docker services:
   docker compose restart
================================================================================

✅ Done!
```

## 🔄 Complete Workflow

### Initial Setup

```bash
# 1. Navigate to directory
cd supabase-langfuse

# 2. Generate all secrets
./generate-jwt.sh

# 3. Start services
docker compose up -d

# 4. Verify services
docker compose ps
```

### Rotating Secrets (Full)

```bash
# 1. Generate new secrets and tokens
./generate-jwt.sh

# 2. Restart services
docker compose restart

# Note: This will invalidate all existing sessions!
```

### Rotating Only JWT Tokens

```bash
# 1. Generate new tokens (keeps existing JWT_SECRET)
./generate-jwt.sh --tokens-only

# 2. Restart services
docker compose restart
```

### Updating Only Application Secrets

```bash
# 1. Generate new app secrets only
./generate-jwt.sh --secrets-only

# 2. Restart services
docker compose restart
```

## 🔐 Security Features

### 1. Automatic Backups

Before updating any file, the script creates backups:

- `.env.backup` - Previous .env state
- `kong.yml.backup` - Previous kong.yml state

### 2. Restore from Backup

If something goes wrong:

```bash
# Restore .env
mv .env.backup .env

# Restore kong.yml
mv kong.yml.backup kong.yml

# Restart services
docker compose restart
```

### 3. Secure Generation

All secrets are generated using OpenSSL's cryptographically secure random number generator:

```bash
openssl rand -base64 32
```

This generates 32 bytes (256 bits) of randomness, base64-encoded.

## 📊 What Gets Updated

### `.env` File

```bash
# Secrets (when running default or --secrets-only)
JWT_SECRET=<new-secret>
LANGFUSE_NEXTAUTH_SECRET=<new-secret>
LANGFUSE_SALT=<new-secret>

# JWT Tokens (when running default or --tokens-only)
SUPABASE_ANON_KEY=<new-token>
SUPABASE_SERVICE_ROLE_KEY=<new-token>
```

### `kong.yml` File

```yaml
consumers:
  - username: anon
    keyauth_credentials:
      - key: <new-anon-token>    # Updated with --tokens-only or default
  - username: service_role
    keyauth_credentials:
      - key: <new-service-role-token>    # Updated with --tokens-only or default
```

## ⚙️ Requirements

- **OpenSSL** - For generating secure random secrets
- **Node.js** - For generating JWT tokens (only needed for token generation)
- **Bash** - Compatible shell (zsh, bash, etc.)

### Check Requirements

```bash
# Check OpenSSL
openssl version

# Check Node.js (only needed for JWT tokens)
node --version
```

## 🎯 Use Cases

### 1. First-Time Setup

```bash
cd supabase-langfuse
cp .env.example .env
./generate-jwt.sh
docker compose up -d
```

### 2. Security Breach - Full Rotation

```bash
./generate-jwt.sh  # Generate everything new
docker compose restart
# Notify users - all sessions invalidated
```

### 3. JWT Secret Compromised

```bash
./generate-jwt.sh  # New JWT_SECRET + tokens
docker compose restart
```

### 4. Need New JWT Tokens Only

```bash
./generate-jwt.sh --tokens-only
docker compose restart
```

### 5. Langfuse Secret Rotation

```bash
./generate-jwt.sh --secrets-only
docker compose restart
```

### 6. Moving to Production

```bash
# Generate production secrets
./generate-jwt.sh

# Copy .env to production server
scp .env production-server:/path/to/supabase-langfuse/

# Or set as environment variables in your deployment
```

## 🛡️ Best Practices

### 1. Regular Rotation

Rotate secrets periodically (e.g., every 90 days):

```bash
# Set up a reminder
./generate-jwt.sh
docker compose restart
```

### 2. Different Secrets Per Environment

```bash
# Development
./generate-jwt.sh
mv .env .env.development

# Staging
./generate-jwt.sh
mv .env .env.staging

# Production
./generate-jwt.sh
mv .env .env.production
```

### 3. Secure Storage

- ✅ Never commit `.env` to version control
- ✅ Use a password manager for backup
- ✅ Store backups securely
- ✅ Use environment variables in production

### 4. Access Control

- ✅ `JWT_SECRET` - Only backend/admin
- ✅ `SUPABASE_SERVICE_ROLE_KEY` - Backend only
- ✅ `SUPABASE_ANON_KEY` - Can be public
- ✅ `LANGFUSE_NEXTAUTH_SECRET` - Backend only
- ✅ `LANGFUSE_SALT` - Backend only

## 🐛 Troubleshooting

### "openssl: command not found"

**Solution:**
```bash
# macOS
brew install openssl

# Ubuntu/Debian
sudo apt-get install openssl
```

### "node: command not found"

**Solution:**
```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or use --secrets-only if you don't need JWT tokens
./generate-jwt.sh --secrets-only
```

### ".env file not found"

**Solution:**
```bash
# Create from example
cp .env.example .env

# Or create blank
touch .env

# Then run the script
./generate-jwt.sh
```

### "Services not picking up new secrets"

**Solution:**
```bash
# Full restart
docker compose down
docker compose up -d

# Check logs
docker compose logs -f
```

### "Existing sessions invalidated"

This is expected when you regenerate `JWT_SECRET` or `LANGFUSE_NEXTAUTH_SECRET`.

**Solution:**
- Users need to log in again
- API clients need new tokens
- Update any hardcoded tokens in your code

## 📚 Related Documentation

- **`README.md`** - Main project documentation
- **`GENERATE-JWT-GUIDE.md`** - Detailed JWT generation methods
- **`SCRIPTS-README.md`** - Original token-only script docs
- **`docker-compose.yml`** - Service configuration
- **`.env.example`** - Example environment variables

## ✅ Verification

After running the script, verify all secrets are updated:

```bash
# Check all secrets in .env
grep -E "^(JWT_SECRET|LANGFUSE|SUPABASE)" .env

# Check kong.yml tokens
grep "key: eyJ" kong.yml

# Verify services are running
docker compose ps

# Test Supabase API
curl -H "apikey: YOUR_ANON_KEY" http://localhost:6001/rest/v1/

# Test Langfuse
curl http://localhost:6000/api/public/health
```

## 🎉 Summary

**One command to generate everything:**

```bash
./generate-jwt.sh
```

**What it does:**
- ✅ Generates 3 secure secrets (256-bit each)
- ✅ Generates 2 JWT tokens (10-year validity)
- ✅ Updates .env automatically
- ✅ Updates kong.yml automatically
- ✅ Creates backups
- ✅ Shows clear output

**No manual editing required!** 🚀
