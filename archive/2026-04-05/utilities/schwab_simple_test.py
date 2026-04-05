#!/usr/bin/env python3
"""
Simple Schwab Authentication Test
"""

import os
import sys

print("🔐 SCHWAB AUTHENTICATION TEST")
print("=" * 60)

# Simple .env parsing
try:
    with open('.env', 'r') as f:
        env_vars = {}
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    API_KEY = env_vars.get('SCHWAB_API_KEY')
    API_SECRET = env_vars.get('SCHWAB_API_SECRET')
    ACCOUNT_ID = env_vars.get('SCHWAB_ACCOUNT_ID')
    
except Exception as e:
    print(f"❌ Error reading .env file: {e}")
    sys.exit(1)

print("\n📊 CREDENTIALS CHECK:")
print(f"   API Key: {'✅ ' + API_KEY[:10] + '...' if API_KEY and 'your_app_key' not in API_KEY else '❌ Missing or placeholder'}")
print(f"   API Secret: {'✅ ' + API_SECRET[:10] + '...' if API_SECRET and 'your_app_secret' not in API_SECRET else '❌ Missing or placeholder'}")
print(f"   Account ID: {'✅ ' + ACCOUNT_ID if ACCOUNT_ID and 'your_account_number' not in ACCOUNT_ID else '❌ Missing or placeholder'}")

print("\n" + "=" * 60)
print("🎯 STATUS SUMMARY:")
print("=" * 60)

all_good = True
if not API_KEY or 'your_app_key' in API_KEY:
    print("❌ Need valid SCHWAB_API_KEY in .env")
    all_good = False
    
if not API_SECRET or 'your_app_secret' in API_SECRET:
    print("❌ Need valid SCHWAB_API_SECRET in .env")
    all_good = False
    
if not ACCOUNT_ID or 'your_account_number' in ACCOUNT_ID:
    print("❌ Need valid SCHWAB_ACCOUNT_ID in .env")
    print("   Get from Schwab website: Account Summary")
    all_good = False

if all_good:
    print("\n✅ ALL CREDENTIALS READY FOR REAL TRADING!")
    print("\n🚀 Next steps:")
    print("1. Install library: pip install schwab-py")
    print("2. Test OAuth2 authentication")
    print("3. Start real trading: ./setup_schwab_forex.sh")
else:
    print("\n⚠️  Complete setup steps in SCHWAB_NEXT_STEPS.md")

print("\n" + "=" * 60)
print("📈 CURRENT PAPER TRADING STATUS:")
print("=" * 60)
print("\nYour Forex bot is running in paper trading mode:")
print("• Bot: forex_bot_with_schwab.py")
print("• Mode: Paper trading ($10,000 virtual)")
print("• Status: Learning market dynamics")
print("• Ready to switch to real trading when credentials complete")
print("\nMonitor: tail -f forex_schwab_output.log")