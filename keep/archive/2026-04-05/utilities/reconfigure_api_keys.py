#!/usr/bin/env python3
"""
Reconfigure API keys for both exchanges
"""

import os
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
SECURE_DIR = os.path.join(BASE_DIR, "secure_keys")

def reconfigure_binance():
    """Reconfigure Binance API keys"""
    print("\n" + "="*60)
    print("RECONFIGURE BINANCE API KEYS")
    print("="*60)
    
    print("\n📋 BINANCE SETUP INSTRUCTIONS:")
    print("1. Go to Binance.com → API Management")
    print("2. DELETE the old API key (SdiE3ZgEYz...U6D9)")
    print("3. Create NEW API key with permissions:")
    print("   • Enable Reading")
    print("   • Enable Spot & Margin Trading")
    print("4. Copy the NEW API Key and Secret Key")
    print("5. Enter them below")
    
    print("\n🔑 ENTER NEW BINANCE API KEY:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API key required")
        return False
    
    print("\n🔑 ENTER NEW BINANCE SECRET KEY:")
    api_secret = input("Secret Key: ").strip()
    
    if not api_secret:
        print("❌ Secret key required")
        return False
    
    # Save keys
    key_file = os.path.join(SECURE_DIR, ".binance_key")
    secret_file = os.path.join(SECURE_DIR, ".binance_secret")
    
    os.makedirs(SECURE_DIR, exist_ok=True)
    
    with open(key_file, 'w') as f:
        f.write(api_key)
    with open(secret_file, 'w') as f:
        f.write(api_secret)
    
    # Update symlinks
    os.system(f"ln -sf {key_file} {os.path.join(BASE_DIR, '.binance_key')}")
    os.system(f"ln -sf {secret_file} {os.path.join(BASE_DIR, '.binance_secret')}")
    
    print(f"\n✅ Binance keys saved")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
    print(f"   Secret: {'*' * len(api_secret)} ({len(api_secret)} chars)")
    
    return True

def reconfigure_gemini():
    """Reconfigure Gemini API keys"""
    print("\n" + "="*60)
    print("RECONFIGURE GEMINI API KEYS")
    print("="*60)
    
    print("\n📋 GEMINI SETUP INSTRUCTIONS:")
    print("1. Go to Gemini.com → Settings → API")
    print("2. DELETE the old API key (account-OWhm4Tn1VHlfjmdKL5Cw)")
    print("3. Create NEW API key with 'Trader' role")
    print("4. Copy the NEW API Key and Secret Key")
    print("5. Enter them below")
    
    print("\n🔑 ENTER NEW GEMINI API KEY:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API key required")
        return False
    
    print("\n🔑 ENTER NEW GEMINI SECRET KEY:")
    api_secret = input("Secret Key: ").strip()
    
    if not api_secret:
        print("❌ Secret key required")
        return False
    
    # Save keys
    key_file = os.path.join(SECURE_DIR, ".gemini_key")
    secret_file = os.path.join(SECURE_DIR, ".gemini_secret")
    
    os.makedirs(SECURE_DIR, exist_ok=True)
    
    with open(key_file, 'w') as f:
        f.write(api_key)
    with open(secret_file, 'w') as f:
        f.write(api_secret)
    
    # Update symlinks
    os.system(f"ln -sf {key_file} {os.path.join(BASE_DIR, '.gemini_key')}")
    os.system(f"ln -sf {secret_file} {os.path.join(BASE_DIR, '.gemini_secret')}")
    
    print(f"\n✅ Gemini keys saved")
    print(f"   API Key: {api_key}")
    print(f"   Secret: {'*' * len(api_secret)} ({len(api_secret)} chars)")
    
    return True

def test_connections():
    """Test both connections"""
    print("\n" + "="*60)
    print("TESTING CONNECTIONS")
    print("="*60)
    
    import ccxt
    
    # Test Binance
    print("\n🔍 Testing Binance...")
    try:
        with open(os.path.join(BASE_DIR, ".binance_key"), 'r') as f:
            binance_key = f.read().strip()
        with open(os.path.join(BASE_DIR, ".binance_secret"), 'r') as f:
            binance_secret = f.read().strip()
        
        binance = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            'options': {'defaultType': 'spot'}
        })
        
        markets = binance.load_markets()
        print(f"✅ Binance: Connected ({len(markets)} markets)")
        
        # Check balance
        balance = binance.fetch_balance()
        if 'USDT' in balance:
            usdt = balance['USDT'].get('free', 0)
            print(f"   USDT Balance: ${usdt:.2f}")
    except Exception as e:
        print(f"❌ Binance: {e}")
    
    # Test Gemini
    print("\n🔍 Testing Gemini...")
    try:
        with open(os.path.join(BASE_DIR, ".gemini_key"), 'r') as f:
            gemini_key = f.read().strip()
        with open(os.path.join(BASE_DIR, ".gemini_secret"), 'r') as f:
            gemini_secret = f.read().strip()
        
        gemini = ccxt.gemini({
            'apiKey': gemini_key,
            'secret': gemini_secret
        })
        
        markets = gemini.load_markets()
        print(f"✅ Gemini: Connected ({len(markets)} markets)")
        
        # Check balance
        balance = gemini.fetch_balance()
        if 'USD' in balance:
            usd = balance['USD'].get('free', 0)
            print(f"   USD Balance: ${usd:.2f}")
    except Exception as e:
        print(f"❌ Gemini: {e}")

def main():
    """Main function"""
    print("RECONFIGURE API KEYS FOR 26-CRYPTO TRADING")
    print("="*60)
    print("Current API keys are invalid/empty")
    print("You need to create NEW API keys on both exchanges")
    print("="*60)
    
    print("\n⚠️  CURRENT ISSUES:")
    print("1. Binance: API key invalid")
    print("2. Gemini: Secret key empty")
    print("3. Trading cannot start without valid keys")
    
    print("\n🔄 RECONFIGURATION OPTIONS:")
    print("1. Reconfigure Binance only")
    print("2. Reconfigure Gemini only")
    print("3. Reconfigure both")
    print("4. Test current connections")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        if reconfigure_binance():
            test_connections()
    elif choice == '2':
        if reconfigure_gemini():
            test_connections()
    elif choice == '3':
        if reconfigure_binance():
            if reconfigure_gemini():
                test_connections()
    elif choice == '4':
        test_connections()
    elif choice == '5':
        print("\n👋 Exiting")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice")

if __name__ == "__main__":
    main()