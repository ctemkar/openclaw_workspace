#!/usr/bin/env python3
"""
Simple verification of .env file without python-dotenv
"""

import os

def load_env_manually():
    """Load .env file manually"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("❌ .env file not found!")
        return {}
    
    return env_vars

def main():
    print("🔐 Verifying .env file")
    print("=" * 40)
    
    # Load environment variables
    env_vars = load_env_manually()
    
    if not env_vars:
        print("❌ No environment variables loaded")
        return
    
    # Check critical keys
    critical_keys = [
        'GEMINI_API_KEY',
        'GEMINI_API_SECRET',
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET'
    ]
    
    print(f"📊 Loaded {len(env_vars)} environment variables")
    print("\n🔑 Critical API Keys:")
    
    all_present = True
    for key in critical_keys:
        value = env_vars.get(key)
        if value:
            # Show first/last few chars (don't expose full key)
            display = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
            print(f"✅ {key}: {display} (length: {len(value)})")
        else:
            print(f"❌ {key}: MISSING")
            all_present = False
    
    print("\n📝 Other variables:")
    other_vars = [k for k in env_vars.keys() if k not in critical_keys]
    for key in sorted(other_vars):
        value = env_vars[key]
        print(f"  {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    print("\n" + "=" * 40)
    if all_present:
        print("✅ All critical API keys present in .env")
        print("\n⚠️  NEXT: Update Python files to use os.environ instead of secure_keys/")
    else:
        print("❌ Missing critical API keys!")
        print("\n🚨 EMERGENCY: Add missing keys to .env file")

if __name__ == "__main__":
    main()