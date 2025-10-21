# Generating Supabase JWT Tokens

This guide explains how to generate properly signed JWT tokens for your Supabase instance.

## 🎯 Why You Need This

Supabase uses JWT (JSON Web Tokens) for authentication. You need two types of tokens:

1. **ANON Key** (`SUPABASE_ANON_KEY`) - Used by clients for public access
2. **Service Role Key** (`SUPABASE_SERVICE_ROLE_KEY`) - Used for admin/backend access with full permissions

Both must be signed with your `JWT_SECRET`.

## 📋 Prerequisites

You need your `JWT_SECRET` from your `.env` file. If you haven't generated one yet:

```bash
openssl rand -base64 32
```

Example output: `JiA3qyur0XC/X+rVy20dETq4VR1YBZG3K0v3YH/8/dg=`

---

## Method 1: Using the Provided Shell Script (Easiest) ⭐

### Step 1: Make the script executable
```bash
cd supabase-langfuse
chmod +x generate-jwt.sh
```

### Step 2: Run the script
```bash
./generate-jwt.sh
```

### Step 3: Follow the prompts
The script will ask for your JWT_SECRET and generate both tokens.

### Step 4: Copy the output to your .env file
Update these lines in your `.env`:
```bash
SUPABASE_ANON_KEY=<generated-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<generated-service-role-key>
```

### Step 5: Update kong.yml
Also update the keys in `kong.yml` at the bottom:
```yaml
consumers:
  - username: anon
    keyauth_credentials:
      - key: <your-generated-anon-key>
  - username: service_role
    keyauth_credentials:
      - key: <your-generated-service-role-key>
```

---

## Method 2: Using Python Script

### Step 1: Install PyJWT
```bash
pip install pyjwt
```

### Step 2: Run the Python script
```bash
cd supabase-langfuse
python3 generate-jwt.py
```

### Step 3: Follow the same steps as Method 1 (Steps 3-5)

---

## Method 3: Using JWT.io (Manual)

### Step 1: Go to jwt.io
Visit https://jwt.io/

### Step 2: Configure the header (left side)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Step 3: Configure the payload for ANON key
```json
{
  "role": "anon",
  "iss": "supabase",
  "iat": 1729468800,
  "exp": 2045088000
}
```

**Note:** 
- `iat` = Current timestamp (use: `date +%s`)
- `exp` = Expiry timestamp (10 years from now)

### Step 4: Add your secret
In the "Verify Signature" section at the bottom, paste your `JWT_SECRET`

### Step 5: Copy the token
The encoded JWT on the left side is your `SUPABASE_ANON_KEY`

### Step 6: Repeat for SERVICE_ROLE key
Change the payload to:
```json
{
  "role": "service_role",
  "iss": "supabase",
  "iat": 1729468800,
  "exp": 2045088000
}
```

Copy this token as your `SUPABASE_SERVICE_ROLE_KEY`

---

## Method 4: Using Node.js REPL (Quick & Dirty)

```bash
node
```

Then paste this code:

```javascript
const crypto = require('crypto');

function base64UrlEncode(str) {
    return Buffer.from(str).toString('base64')
        .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

function generateJWT(secret, role) {
    const now = Math.floor(Date.now() / 1000);
    const expiry = now + (10 * 365 * 24 * 60 * 60);
    
    const header = { alg: 'HS256', typ: 'JWT' };
    const payload = { role, iss: 'supabase', iat: now, exp: expiry };
    
    const encodedHeader = base64UrlEncode(JSON.stringify(header));
    const encodedPayload = base64UrlEncode(JSON.stringify(payload));
    const signatureInput = encodedHeader + '.' + encodedPayload;
    
    const signature = crypto.createHmac('sha256', secret)
        .update(signatureInput).digest('base64')
        .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    
    return signatureInput + '.' + signature;
}

// Replace with your JWT_SECRET
const secret = 'YOUR_JWT_SECRET_HERE';

console.log('ANON:', generateJWT(secret, 'anon'));
console.log('SERVICE_ROLE:', generateJWT(secret, 'service_role'));
```

---

## 🔍 Verifying Your Tokens

After generating, you can verify your tokens at https://jwt.io/

1. Paste your token in the "Encoded" field
2. Paste your `JWT_SECRET` in the "Verify Signature" field
3. Check that:
   - Algorithm is HS256
   - Role is correct (anon or service_role)
   - Issuer is "supabase"
   - Token shows "Signature Verified" ✅

---

## 📝 Complete .env Example

```bash
# JWT Settings
JWT_SECRET=JiA3qyur0XC/X+rVy20dETq4VR1YBZG3K0v3YH/8/dg=

# Generated tokens (these are examples - generate your own!)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzI5NDY4ODAwLCJleHAiOjIwNDUwODgwMDB9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaXNzIjoic3VwYWJhc2UiLCJpYXQiOjE3Mjk0Njg4MDAsImV4cCI6MjA0NTA4ODAwMH0.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ⚠️ Security Best Practices

1. **Never commit tokens** - Add `.env` to `.gitignore`
2. **Regenerate for production** - Use different tokens for dev/staging/prod
3. **Rotate regularly** - Consider regenerating tokens periodically
4. **Protect SERVICE_ROLE** - This key has full database access
5. **Use environment variables** - Never hardcode in source code

---

## 🆘 Troubleshooting

**Problem: Token validation fails**
- Ensure JWT_SECRET matches between token generation and .env file
- Check that algorithm is HS256
- Verify payload structure is correct

**Problem: "Invalid JWT" errors in logs**
- Make sure tokens in .env and kong.yml match
- Restart services after updating tokens: `docker compose restart`

**Problem: Scripts don't work**
- Check Node.js is installed: `node --version`
- For Python: Check PyJWT is installed: `pip list | grep PyJWT`
- Make shell script executable: `chmod +x generate-jwt.sh`

---

## 🎯 Quick Start (Recommended Path)

```bash
# 1. Generate JWT secret
openssl rand -base64 32

# 2. Add to .env
# JWT_SECRET=<output-from-step-1>

# 3. Generate tokens
cd supabase-langfuse
chmod +x generate-jwt.sh
./generate-jwt.sh

# 4. Copy the output to .env and kong.yml

# 5. Restart services
docker compose restart
```

That's it! 🎉
