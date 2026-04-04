#!/usr/bin/env python3
"""
Update Binance API credentials with the new working key/secret
"""

import os
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
SECRETS_DIR = os.path.join(BASE_DIR, "secure_keys")

def update_credentials():
    """Update the API key and secret files"""
    
    # Based on your test output:
    # API Key: dT0OIm9a... (first 8 chars)
    # Secret: EqD0zlJQ... (first 8 chars)
    
    # The FULL secret you provided earlier:
    full_secret = "EqD0zlJQq2D4lMFDpMdUJcVB8F6NuSufYdPdHOydGSW6zZHs9D5uUB85eYuPWIyo"
    
    print("🔧 UPDATING BINANCE API CREDENTIALS")
    print("=" * 50)
    
    # Check current files
    key_file = os.path.join(SECRETS_DIR, ".binance_key")
    secret_file = os.path.join(SECRETS_DIR, ".binance_secret")
    
    print(f"📁 Key file: {key_file}")
    print(f"📁 Secret file: {secret_file}")
    
    # IMPORTANT: I need the FULL API key from you
    # The test showed "dT0OIm9a..." but that's just the first 8 chars
    # Please provide the FULL API key
    
    print("\n❓ I NEED THE FULL API KEY:")
    print("   The test showed: 'dT0OIm9a...' (first 8 chars)")
    print("   But I need the COMPLETE API key string")
    print("\n📝 Please provide the FULL API key (not just first 8 chars)")
    print("   It should look something like: dT0OIm9aXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    
    # For now, I'll update just the secret (since we have the full secret)
    print(f"\n✅ Updating SECRET with provided value (64 chars)")
    
    try:
        with open(secret_file, 'w') as f:
            f.write(full_secret)
        print(f"   Secret updated: {full_secret[:10]}...{full_secret[-10:]}")
        
        # Check if key file exists
        if os.path.exists(key_file):
            current_key = open(key_file).read().strip()
            print(f"   Current key: {current_key[:10]}...{current_key[-10:]}")
            print(f"   ⚠️ Key may need updating if it's not 'dT0OIm9a...'")
        else:
            print(f"   ❌ Key file doesn't exist!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Provide FULL API key (not truncated)")
    print("2. Run: python3 diagnose_binance_api.py")
    print("3. Restart trading bots if needed")
    print("4. Check IP whitelisting on Binance dashboard")
    
    print("\n📊 CURRENT STATUS:")
    print("   ✅ Secret updated: EqD0zlJQ...PWIyo")
    print("   ⚠️ Key may be outdated: need full 'dT0OIm9a...' key")
    print("   💰 MANA balance: 118.661 (needs >119)")
    print("   💵 USDT balance: 1.7375")

if __name__ == "__main__":
    update_credentials()