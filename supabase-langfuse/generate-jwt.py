#!/usr/bin/env python3
"""
Supabase JWT Token Generator

This script generates properly signed JWT tokens for Supabase using your JWT_SECRET.
It creates both ANON and SERVICE_ROLE keys and automatically updates .env files.

Usage:
    python3 generate-jwt.py

Requirements:
    pip install pyjwt
"""

import jwt
import datetime
import sys
import os
import re
import shutil


def find_env_file():
    """Find .env file in current directory or parent directory."""
    local_env = ".env"
    workspace_env = "../.env"
    
    if os.path.exists(local_env):
        print(f"📁 Found .env in current directory: {local_env}")
        return local_env
    elif os.path.exists(workspace_env):
        print(f"📁 Found .env in workspace root: {workspace_env}")
        return workspace_env
    else:
        print("⚠️  No .env file found. Will only display tokens.")
        return None


def read_jwt_secret_from_env(env_file):
    """Read JWT_SECRET from .env file."""
    if not env_file or not os.path.exists(env_file):
        return None
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('JWT_SECRET='):
                    secret = line.split('=', 1)[1].strip().strip('"').strip("'")
                    return secret
    except Exception as e:
        print(f"⚠️  Error reading .env file: {e}")
    
    return None


def generate_supabase_jwt(secret: str, role: str, expiry_years: int = 10) -> str:
    """
    Generate a Supabase JWT token.
    
    Args:
        secret: Your JWT_SECRET from .env file
        role: Either 'anon' or 'service_role'
        expiry_years: Token expiry in years (default: 10 years)
    
    Returns:
        Signed JWT token as string
    """
    # Calculate expiry timestamp (10 years from now by default)
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=365 * expiry_years)
    exp_timestamp = int(expiry.timestamp())
    
    # JWT payload
    payload = {
        "role": role,
        "iss": "supabase",
        "iat": int(datetime.datetime.utcnow().timestamp()),
        "exp": exp_timestamp
    }
    
    # Generate token
    token = jwt.encode(payload, secret, algorithm="HS256")
    
    return token


def update_env_file(env_file, anon_key, service_role_key):
    """Update .env file with new JWT tokens."""
    if not env_file or not os.path.exists(env_file):
        return False
    
    try:
        # Create backup
        backup_file = f"{env_file}.backup"
        shutil.copy2(env_file, backup_file)
        print(f"   ✅ Backup created: {backup_file}")
        
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update or add SUPABASE_ANON_KEY
        anon_pattern = r'^SUPABASE_ANON_KEY=.*$'
        if re.search(anon_pattern, content, re.MULTILINE):
            content = re.sub(anon_pattern, f'SUPABASE_ANON_KEY={anon_key}', content, flags=re.MULTILINE)
            print("   ✅ Updated SUPABASE_ANON_KEY")
        else:
            content += f"\nSUPABASE_ANON_KEY={anon_key}\n"
            print("   ✅ Added SUPABASE_ANON_KEY")
        
        # Update or add SUPABASE_SERVICE_ROLE_KEY
        service_pattern = r'^SUPABASE_SERVICE_ROLE_KEY=.*$'
        if re.search(service_pattern, content, re.MULTILINE):
            content = re.sub(service_pattern, f'SUPABASE_SERVICE_ROLE_KEY={service_role_key}', content, flags=re.MULTILINE)
            print("   ✅ Updated SUPABASE_SERVICE_ROLE_KEY")
        else:
            content += f"SUPABASE_SERVICE_ROLE_KEY={service_role_key}\n"
            print("   ✅ Added SUPABASE_SERVICE_ROLE_KEY")
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def update_kong_file(kong_file, anon_key, service_role_key):
    """Update kong.yml with new JWT tokens."""
    if not os.path.exists(kong_file):
        return False
    
    try:
        # Create backup
        backup_file = f"{kong_file}.backup"
        shutil.copy2(kong_file, backup_file)
        print(f"   ✅ Backup created: {backup_file}")
        
        # Read and update content
        with open(kong_file, 'r') as f:
            lines = f.readlines()
        
        updated_lines = []
        in_anon = False
        in_service = False
        
        for line in lines:
            if 'username: anon' in line:
                in_anon = True
                in_service = False
            elif 'username: service_role' in line:
                in_anon = False
                in_service = True
            elif 'username:' in line and 'username: anon' not in line and 'username: service_role' not in line:
                in_anon = False
                in_service = False
            
            if '- key:' in line or 'key:' in line.strip().startswith('- key:'):
                if in_anon:
                    line = f"      - key: {anon_key}\n"
                elif in_service:
                    line = f"      - key: {service_role_key}\n"
            
            updated_lines.append(line)
        
        # Write updated content
        with open(kong_file, 'w') as f:
            f.writelines(updated_lines)
        
        return True
    except Exception as e:
        print(f"❌ Error updating kong.yml: {e}")
        return False


def main():
    print("=" * 80)
    print("Supabase JWT Token Generator")
    print("=" * 80)
    print()
    
    # Find .env file
    env_file = find_env_file()
    
    # Try to get JWT_SECRET from .env
    secret = None
    if env_file:
        secret = read_jwt_secret_from_env(env_file)
        if secret:
            print("✅ Using JWT_SECRET from .env file")
    
    # If not found in .env, ask user
    if not secret:
        print()
        print("Enter your JWT_SECRET:")
        print("(Generate one with: openssl rand -base64 32)")
        print()
        secret = input("JWT_SECRET: ").strip()
        
        if not secret:
            print("❌ Error: JWT_SECRET cannot be empty!")
            sys.exit(1)
    
    print()
    print("Generating tokens...")
    print()
    
    try:
        # Generate ANON key
        anon_key = generate_supabase_jwt(secret, "anon")
        
        # Generate SERVICE_ROLE key
        service_role_key = generate_supabase_jwt(secret, "service_role")
        
        # Display results
        print("✅ JWT Tokens Generated Successfully!")
        print("=" * 80)
        print()
        print("📋 SUPABASE_ANON_KEY:")
        print("-" * 80)
        print(anon_key)
        print()
        print("📋 SUPABASE_SERVICE_ROLE_KEY:")
        print("-" * 80)
        print(service_role_key)
        print()
        print("=" * 80)
        print()
        
        # Update .env file
        if env_file:
            print(f"📝 Updating {env_file}...")
            if update_env_file(env_file, anon_key, service_role_key):
                print()
                print("✅ .env file updated successfully!")
                print()
            else:
                print()
                print("❌ Failed to update .env file")
                print()
        else:
            print("⚠️  No .env file found - skipping automatic update")
            print()
            print("📝 Manually add these to your .env file:")
            print()
            print(f"SUPABASE_ANON_KEY={anon_key}")
            print(f"SUPABASE_SERVICE_ROLE_KEY={service_role_key}")
            print()
        
        # Check for kong.yml
        kong_file = "kong.yml"
        if os.path.exists(kong_file):
            print(f"� Updating {kong_file}...")
            if update_kong_file(kong_file, anon_key, service_role_key):
                print("   ✅ kong.yml updated successfully!")
                print()
        else:
            print("⚠️  kong.yml not found in current directory - skipping Kong update")
            print("   If you need to update Kong, run this script from the supabase-langfuse directory")
            print()
        
        print("=" * 80)
        print("⚠️  IMPORTANT NOTES:")
        print("1. Keep these tokens secret - never commit them to version control")
        print("2. The SERVICE_ROLE_KEY has full database access - protect it carefully")
        print("3. These tokens are valid for 10 years")
        print("4. If you updated .env, restart your Docker services:")
        print("   docker compose restart")
        print("=" * 80)
        print()
        print("✅ Done!")
        print()
        
    except Exception as e:
        print(f"❌ Error generating tokens: {e}")
        print()
        print("💡 Make sure PyJWT is installed:")
        print("   pip install pyjwt")
        sys.exit(1)


if __name__ == "__main__":
    main()
