#!/usr/bin/env python3
"""
Test the current Binance API credentials
"""

import ccxt
import os
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
SECRETS_DIR = os.path.join(BASE_DIR, "secure_keys")

def test_credentials():
    """Test if current credentials work"""
    
    # Read current credentials
    key_file = os.path.join(SECRETS_DIR, ".binance_key")
    secret_file = os.path.join(SECRETS_DIR, ".binance_secret")
    
    try:
        with open(key_file, 'r') as f:
            api_key = f.read().strip()
        
        with open(secret_file, 'r') as f:
            api_secret = f.read().strip()
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False
    
    print(f"🔍 Testing credentials:")
    print(f"   Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''} (length: {len(api_key)})")
    print(f"   Secret: {api_secret[:10]}...{api_secret[-10:] if len(api_secret) > 20 else ''} (length: {len(api_secret)})")
    
    # Initialize exchange
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    try:
        # Test public data
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Public data works: BTC = ${ticker['last']:.2f}")
        
        # Test private data
        print("📊 Testing balance fetch...")
        balance = exchange.fetch_balance()
        print(f"✅ Balance fetch successful!")
        
        # Show some balances
        print(f"💰 Account summary:")
        print(f"   Total assets: {len(balance['total'])}")
        
        # Show non-zero balances
        for asset, amount in balance['total'].items():
            if amount > 0.0001:  # Show significant balances
                free = balance['free'].get(asset, 0)
                used = balance['used'].get(asset, 0)
                print(f"   {asset}: {amount:.6f} (free: {free:.6f}, used: {used:.6f})")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        
        # Check specific error
        if "Signature" in str(e):
            print("⚠️ Signature error - key and secret don't match")
            print("⚠️ Need to update BOTH key and secret")
        elif "Invalid API-key" in str(e):
            print("⚠️ Invalid API key - key may be wrong or IP not whitelisted")
        elif "permissions" in str(e):
            print("⚠️ Permission error - check API key permissions on Binance")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TESTING CURRENT BINANCE CREDENTIALS")
    print("=" * 60)
    
    success = test_credentials()
    
    print("=" * 60)
    if success:
        print("🎉 CREDENTIALS ARE WORKING!")
    else:
        print("❌ CREDENTIALS NEED FIXING")
        print("\n📝 ACTION REQUIRED:")
        print("1. Get FULL API key from Binance dashboard")
        print("2. Update secure_keys/.binance_key with complete key")
        print("3. Ensure secret is correct (64 chars)")
        print("4. Check IP whitelisting on Binance")
    
    print("=" * 60)