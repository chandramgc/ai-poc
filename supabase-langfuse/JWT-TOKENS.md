# 🎯 Quick Reference: Your Supabase JWT Tokens

## ✅ Your Configuration (Already Updated!)

### JWT Secret
```
JiA3qyur0XC/X+rVy20dETq4VR1YBZG3K0v3YH/8/dg=
```

### ANON Key (Public/Client Access)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzYxMDY3NDk0LCJleHAiOjIwNzY0Mjc0OTR9.nKDNI05SOCP0BWSQo-zFC-tbCXfvAQu6-7GVza7hwVY
```

### Service Role Key (Admin/Backend Access)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3NjEwNjc0OTQsImV4cCI6MjA3NjQyNzQ5NH0.9S30PItGY2BIF9kLIvm6NZVu_waXw0wpxHpICPiQTAk
```

### Token Details
- **Issued At:** October 21, 2025
- **Expires:** November 5, 2035 (10 years from now)
- **Algorithm:** HS256
- **Issuer:** supabase

---

## 📝 Files Updated

✅ `/Users/girish/MyDrive/Workspace/ai-poc/.env`
✅ `/Users/girish/MyDrive/Workspace/ai-poc/supabase-langfuse/kong.yml`

---

## 🚀 Next Steps

1. **Start your stack:**
   ```bash
   cd supabase-langfuse
   docker compose up -d
   ```

2. **Check services are healthy:**
   ```bash
   docker compose ps
   ```

3. **Access your services:**
   - Langfuse: http://localhost:6000
   - Supabase API: http://localhost:6001
   - Supabase Studio: http://localhost:6002
   - PostgreSQL: localhost:6003

---

## 🔑 Using Your Keys

### In Client Applications (JavaScript/TypeScript)

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'http://localhost:6001'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzYxMDY3NDk0LCJleHAiOjIwNzY0Mjc0OTR9.nKDNI05SOCP0BWSQo-zFC-tbCXfvAQu6-7GVza7hwVY'

const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### In Backend/Admin Operations

```javascript
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3NjEwNjc0OTQsImV4cCI6MjA3NjQyNzQ5NH0.9S30PItGY2BIF9kLIvm6NZVu_waXw0wpxHpICPiQTAk'

const supabase = createClient(supabaseUrl, supabaseServiceKey)
```

### Python Example

```python
from supabase import create_client, Client

url = "http://localhost:6001"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzYxMDY3NDk0LCJleHAiOjIwNzY0Mjc0OTR9.nKDNI05SOCP0BWSQo-zFC-tbCXfvAQu6-7GVza7hwVY"

supabase: Client = create_client(url, key)
```

### cURL Example

```bash
# Using ANON key
curl 'http://localhost:6001/rest/v1/your-table' \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzYxMDY3NDk0LCJleHAiOjIwNzY0Mjc0OTR9.nKDNI05SOCP0BWSQo-zFC-tbCXfvAQu6-7GVza7hwVY" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzYxMDY3NDk0LCJleHAiOjIwNzY0Mjc0OTR9.nKDNI05SOCP0BWSQo-zFC-tbCXfvAQu6-7GVza7hwVY"
```

---

## 🔒 Security Reminders

- ✅ **ANON key** is safe to use in client-side code
- ⚠️  **SERVICE_ROLE key** should NEVER be exposed to clients
- 🔐 Keep your `.env` file secure and never commit to git
- 🔄 Consider rotating keys periodically for production use

---

## 🔄 Need to Regenerate?

If you ever need new tokens (e.g., JWT_SECRET changed):

```bash
cd supabase-langfuse
./generate-jwt.sh
```

Or see `GENERATE-JWT-GUIDE.md` for other methods.

---

## ✅ Verification

Verify your tokens at https://jwt.io/:

1. Paste your token in "Encoded" field
2. Paste your JWT_SECRET in "Verify Signature" field  
3. Should show "Signature Verified" ✅

---

**Generated on:** October 21, 2025
**Valid until:** November 5, 2035
