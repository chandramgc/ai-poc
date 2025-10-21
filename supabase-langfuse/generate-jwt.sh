#!/bin/bash
#
# Supabase + Langfuse Secrets Generator
#
# This script generates all required secrets and JWT tokens for Supabase and Langfuse.
# It automatically updates .env and kong.yml files.
#
# Usage: ./generate-jwt.sh [options]
#   Options:
#     --secrets-only    Only generate/update secrets (JWT_SECRET, LANGFUSE_NEXTAUTH_SECRET, LANGFUSE_SALT)
#     --tokens-only     Only generate/update JWT tokens (uses existing JWT_SECRET)
#     --help           Show this help message
#

set -e

# Parse command line arguments
GENERATE_SECRETS=true
GENERATE_TOKENS=true

for arg in "$@"; do
    case $arg in
        --secrets-only)
            GENERATE_TOKENS=false
            ;;
        --tokens-only)
            GENERATE_SECRETS=false
            ;;
        --help)
            echo "Usage: ./generate-jwt.sh [options]"
            echo ""
            echo "Options:"
            echo "  --secrets-only    Only generate/update secrets (JWT_SECRET, LANGFUSE_NEXTAUTH_SECRET, LANGFUSE_SALT)"
            echo "  --tokens-only     Only generate/update JWT tokens (uses existing JWT_SECRET)"
            echo "  --help           Show this help message"
            echo ""
            echo "Default: Generates both secrets and tokens"
            exit 0
            ;;
    esac
done

echo "================================================================================"
echo "Supabase + Langfuse Secrets & JWT Generator"
echo "================================================================================"
echo ""

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo "❌ Error: openssl is not installed"
    echo "Please install openssl"
    exit 1
fi

# Check if node is installed
if ! command -v node &> /dev/null && [ "$GENERATE_TOKENS" = true ]; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Try to find .env file
ENV_FILE=""
WORKSPACE_ENV="../.env"
LOCAL_ENV=".env"

if [ -f "$LOCAL_ENV" ]; then
    ENV_FILE="$LOCAL_ENV"
    echo "📁 Found .env in current directory: $LOCAL_ENV"
elif [ -f "$WORKSPACE_ENV" ]; then
    ENV_FILE="$WORKSPACE_ENV"
    echo "📁 Found .env in workspace root: $WORKSPACE_ENV"
else
    echo "⚠️  No .env file found. Will only display secrets/tokens."
fi

# Generate or read secrets
JWT_SECRET=""
LANGFUSE_NEXTAUTH_SECRET=""
LANGFUSE_SALT=""

if [ "$GENERATE_SECRETS" = true ]; then
    echo ""
    echo "🔐 Generating new secrets..."
    
    # Generate new secrets
    JWT_SECRET=$(openssl rand -base64 32)
    LANGFUSE_NEXTAUTH_SECRET=$(openssl rand -base64 32)
    LANGFUSE_SALT=$(openssl rand -base64 32)
    
    echo "   ✅ Generated JWT_SECRET"
    echo "   ✅ Generated LANGFUSE_NEXTAUTH_SECRET"
    echo "   ✅ Generated LANGFUSE_SALT"
else
    # Read existing secrets from .env
    if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
        JWT_SECRET=$(grep "^JWT_SECRET=" "$ENV_FILE" | cut -d'=' -f2- | tr -d ' "' || true)
        LANGFUSE_NEXTAUTH_SECRET=$(grep "^LANGFUSE_NEXTAUTH_SECRET=" "$ENV_FILE" | cut -d'=' -f2- | tr -d ' "' || true)
        LANGFUSE_SALT=$(grep "^LANGFUSE_SALT=" "$ENV_FILE" | cut -d'=' -f2- | tr -d ' "' || true)
        
        if [ -z "$JWT_SECRET" ]; then
            echo "⚠️  JWT_SECRET not found in .env, generating new one..."
            JWT_SECRET=$(openssl rand -base64 32)
        else
            echo "✅ Using existing JWT_SECRET from .env"
        fi
        
        if [ -z "$LANGFUSE_NEXTAUTH_SECRET" ]; then
            echo "⚠️  LANGFUSE_NEXTAUTH_SECRET not found in .env, generating new one..."
            LANGFUSE_NEXTAUTH_SECRET=$(openssl rand -base64 32)
        fi
        
        if [ -z "$LANGFUSE_SALT" ]; then
            echo "⚠️  LANGFUSE_SALT not found in .env, generating new one..."
            LANGFUSE_SALT=$(openssl rand -base64 32)
        fi
    else
        echo "❌ Error: No .env file found and --tokens-only specified"
        exit 1
    fi
fi

if [ "$GENERATE_TOKENS" = true ]; then
    echo ""
    echo "🔑 Generating JWT tokens..."
fi
echo ""

# Generate tokens using Node.js (only if requested)
if [ "$GENERATE_TOKENS" = true ]; then
    RESULT=$(node - <<EOF
const crypto = require('crypto');

// Simple JWT implementation
function base64UrlEncode(str) {
    return Buffer.from(str)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

function generateJWT(secret, role) {
    const now = Math.floor(Date.now() / 1000);
    const expiry = now + (10 * 365 * 24 * 60 * 60); // 10 years
    
    const header = {
        alg: 'HS256',
        typ: 'JWT'
    };
    
    const payload = {
        role: role,
        iss: 'supabase',
        iat: now,
        exp: expiry
    };
    
    const encodedHeader = base64UrlEncode(JSON.stringify(header));
    const encodedPayload = base64UrlEncode(JSON.stringify(payload));
    const signatureInput = encodedHeader + '.' + encodedPayload;
    
    const signature = crypto
        .createHmac('sha256', secret)
        .update(signatureInput)
        .digest('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
    
    return signatureInput + '.' + signature;
}

const secret = '${JWT_SECRET}';
const anonKey = generateJWT(secret, 'anon');
const serviceRoleKey = generateJWT(secret, 'service_role');

// Output in a format that bash can parse
console.log('ANON_KEY=' + anonKey);
console.log('SERVICE_ROLE_KEY=' + serviceRoleKey);
EOF
)

    # Parse the output
    ANON_KEY=$(echo "$RESULT" | grep "^ANON_KEY=" | cut -d'=' -f2)
    SERVICE_ROLE_KEY=$(echo "$RESULT" | grep "^SERVICE_ROLE_KEY=" | cut -d'=' -f2)
fi

# Display results
echo "✅ Secrets Generated Successfully!"
echo "================================================================================"
echo ""

if [ "$GENERATE_SECRETS" = true ]; then
    echo "� SECRETS:"
    echo "--------------------------------------------------------------------------------"
    echo "JWT_SECRET=$JWT_SECRET"
    echo ""
    echo "LANGFUSE_NEXTAUTH_SECRET=$LANGFUSE_NEXTAUTH_SECRET"
    echo ""
    echo "LANGFUSE_SALT=$LANGFUSE_SALT"
    echo ""
    echo "--------------------------------------------------------------------------------"
    echo ""
fi

if [ "$GENERATE_TOKENS" = true ]; then
    echo "🔑 JWT TOKENS:"
    echo "--------------------------------------------------------------------------------"
    echo "SUPABASE_ANON_KEY:"
    echo "$ANON_KEY"
    echo ""
    echo "SUPABASE_SERVICE_ROLE_KEY:"
    echo "$SERVICE_ROLE_KEY"
    echo ""
    echo "--------------------------------------------------------------------------------"
    echo ""
fi

echo "================================================================================"
echo ""

# Update .env file if it exists
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    echo "📝 Updating $ENV_FILE..."
    
    # Create a backup
    cp "$ENV_FILE" "${ENV_FILE}.backup"
    echo "   ✅ Backup created: ${ENV_FILE}.backup"
    
    # Update secrets if generated
    if [ "$GENERATE_SECRETS" = true ]; then
        # Update or add JWT_SECRET
        if grep -q "^JWT_SECRET=" "$ENV_FILE"; then
            sed -i.tmp "s|^JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" "$ENV_FILE"
            rm "${ENV_FILE}.tmp"
            echo "   ✅ Updated JWT_SECRET"
        else
            echo "JWT_SECRET=$JWT_SECRET" >> "$ENV_FILE"
            echo "   ✅ Added JWT_SECRET"
        fi
        
        # Update or add LANGFUSE_NEXTAUTH_SECRET
        if grep -q "^LANGFUSE_NEXTAUTH_SECRET=" "$ENV_FILE"; then
            sed -i.tmp "s|^LANGFUSE_NEXTAUTH_SECRET=.*|LANGFUSE_NEXTAUTH_SECRET=$LANGFUSE_NEXTAUTH_SECRET|" "$ENV_FILE"
            rm "${ENV_FILE}.tmp"
            echo "   ✅ Updated LANGFUSE_NEXTAUTH_SECRET"
        else
            echo "LANGFUSE_NEXTAUTH_SECRET=$LANGFUSE_NEXTAUTH_SECRET" >> "$ENV_FILE"
            echo "   ✅ Added LANGFUSE_NEXTAUTH_SECRET"
        fi
        
        # Update or add LANGFUSE_SALT
        if grep -q "^LANGFUSE_SALT=" "$ENV_FILE"; then
            sed -i.tmp "s|^LANGFUSE_SALT=.*|LANGFUSE_SALT=$LANGFUSE_SALT|" "$ENV_FILE"
            rm "${ENV_FILE}.tmp"
            echo "   ✅ Updated LANGFUSE_SALT"
        else
            echo "LANGFUSE_SALT=$LANGFUSE_SALT" >> "$ENV_FILE"
            echo "   ✅ Added LANGFUSE_SALT"
        fi
    fi
    
    # Update JWT tokens if generated
    if [ "$GENERATE_TOKENS" = true ]; then
        # Update or add SUPABASE_ANON_KEY
        if grep -q "^SUPABASE_ANON_KEY=" "$ENV_FILE"; then
            sed -i.tmp "s|^SUPABASE_ANON_KEY=.*|SUPABASE_ANON_KEY=$ANON_KEY|" "$ENV_FILE"
            rm "${ENV_FILE}.tmp"
            echo "   ✅ Updated SUPABASE_ANON_KEY"
        else
            echo "SUPABASE_ANON_KEY=$ANON_KEY" >> "$ENV_FILE"
            echo "   ✅ Added SUPABASE_ANON_KEY"
        fi
        
        # Update or add SUPABASE_SERVICE_ROLE_KEY
        if grep -q "^SUPABASE_SERVICE_ROLE_KEY=" "$ENV_FILE"; then
            sed -i.tmp "s|^SUPABASE_SERVICE_ROLE_KEY=.*|SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY|" "$ENV_FILE"
            rm "${ENV_FILE}.tmp"
            echo "   ✅ Updated SUPABASE_SERVICE_ROLE_KEY"
        else
            echo "SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY" >> "$ENV_FILE"
            echo "   ✅ Added SUPABASE_SERVICE_ROLE_KEY"
        fi
    fi
    
    echo ""
    echo "✅ .env file updated successfully!"
    echo ""
else
    echo "⚠️  No .env file found - skipping automatic update"
    echo ""
    if [ "$GENERATE_SECRETS" = true ]; then
        echo "📝 Manually add these secrets to your .env file:"
        echo ""
        echo "JWT_SECRET=$JWT_SECRET"
        echo "LANGFUSE_NEXTAUTH_SECRET=$LANGFUSE_NEXTAUTH_SECRET"
        echo "LANGFUSE_SALT=$LANGFUSE_SALT"
    fi
    if [ "$GENERATE_TOKENS" = true ]; then
        echo "SUPABASE_ANON_KEY=$ANON_KEY"
        echo "SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY"
    fi
    echo ""
fi

# Check for kong.yml and update it automatically
KONG_FILE="kong.yml"
if [ -f "$KONG_FILE" ]; then
    echo "� Updating $KONG_FILE..."
    
    cp "$KONG_FILE" "${KONG_FILE}.backup"
    echo "   ✅ Backup created: ${KONG_FILE}.backup"
    
    # Update using awk to handle multi-line YAML structure
    awk -v anon="$ANON_KEY" -v service="$SERVICE_ROLE_KEY" '
    /username: anon/ { in_anon=1 }
    /username: service_role/ { in_anon=0; in_service=1 }
    /username:/ && !/username: (anon|service_role)/ { in_anon=0; in_service=0 }
    /- key:/ {
        if (in_anon) {
            print "      - key: " anon
            next
        } else if (in_service) {
            print "      - key: " service
            next
        }
    }
    { print }
    ' "$KONG_FILE" > "${KONG_FILE}.new"
    
    mv "${KONG_FILE}.new" "$KONG_FILE"
    echo "   ✅ Updated anon consumer key"
    echo "   ✅ Updated service_role consumer key"
    echo ""
    echo "✅ kong.yml updated successfully!"
    echo ""
else
    echo "⚠️  kong.yml not found in current directory - skipping Kong update"
    echo "   If you need to update Kong, run this script from the supabase-langfuse directory"
    echo ""
fi

echo "================================================================================"
echo "⚠️  IMPORTANT NOTES:"
echo "1. Keep these tokens secret - never commit them to version control"
echo "2. The SERVICE_ROLE_KEY has full database access - protect it carefully"
echo "3. These tokens are valid for 10 years"
echo "4. If you updated .env, restart your Docker services:"
echo "   docker compose restart"
echo "================================================================================"
echo ""
echo "✅ Done!"
echo ""
