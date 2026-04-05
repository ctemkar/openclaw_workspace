#!/usr/bin/env python3
"""
Setup API keys for Binance and Gemini real trading
"""

import os
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
SECURE_DIR = os.path.join(BASE_DIR, "secure_keys")

def setup_binance_keys():
    """Setup Binance API keys"""
    print("\n" + "="*60)
    print("SETUP BINANCE API KEYS")
    print("="*60)
    
    print("\n📋 BINANCE API KEY REQUIREMENTS:")
    print("1. Go to Binance.com → API Management")
    print("2. Create new API key with these permissions:")
    print("   • Enable Reading")
    print("   • Enable Spot & Margin Trading")
    print("   • Enable Withdrawals (optional for trading)")
    print("3. Save the API Key and Secret Key")
    print("4. Make sure to enable IP restrictions for security")
    
    print("\n🔑 ENTER YOUR BINANCE API KEYS:")
    print("(Press Enter to skip if you want to enter manually)")
    
    api_key = input("API Key: ").strip()
    if not api_key:
        print("\n⏭️ Skipping Binance setup. You can:")
        print("1. Run this script again with your keys")
        print("2. Manually edit secure_keys/.binance_key and .binance_secret")
        print("3. Use the existing symlinks if keys are already configured")
        return False
    
    api_secret = input("Secret Key: ").strip()
    if not api_secret:
        print("❌ Secret key is required")
        return False
    
    # Save keys
    key_file = os.path.join(SECURE_DIR, ".binance_key")
    secret_file = os.path.join(SECURE_DIR, ".binance_secret")
    
    with open(key_file, 'w') as f:
        f.write(api_key)
    with open(secret_file, 'w') as f:
        f.write(api_secret)
    
    # Update symlinks
    os.system(f"ln -sf {key_file} {os.path.join(BASE_DIR, '.binance_key')}")
    os.system(f"ln -sf {secret_file} {os.path.join(BASE_DIR, '.binance_secret')}")
    
    print(f"\n✅ Binance API keys saved to:")
    print(f"   Key: {key_file}")
    print(f"   Secret: {secret_file}")
    
    # Test the keys
    print("\n🧪 Testing Binance connection...")
    try:
        import ccxt
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'spot'}
        })
        
        # Simple test - fetch balance
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        print(f"✅ Connection successful!")
        print(f"💰 USDT Balance: ${usdt_balance:.2f}")
        
        if usdt_balance >= 70:
            print("✅ Sufficient funds for real trading ($70+ USDT)")
        else:
            print(f"⚠️ Current balance: ${usdt_balance:.2f} USDT")
            print("   You mentioned having $70+ USDT - please verify")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n💡 Possible issues:")
        print("1. API keys may be incorrect")
        print("2. IP address not whitelisted")
        print("3. API permissions insufficient")
        print("4. 2FA may be required")
        return False

def setup_gemini_keys():
    """Setup Gemini API keys"""
    print("\n" + "="*60)
    print("SETUP GEMINI API KEYS")
    print("="*60)
    
    print("\n📋 GEMINI API KEY REQUIREMENTS:")
    print("1. Go to Gemini.com → Settings → API")
    print("2. Create new API key")
    print("3. Set permissions: 'Trader' role recommended")
    print("4. Save the API Key and Secret Key")
    
    print("\n🔑 ENTER YOUR GEMINI API KEYS:")
    print("(Press Enter to skip if you want to enter manually)")
    
    api_key = input("API Key: ").strip()
    if not api_key:
        print("\n⏭️ Skipping Gemini setup. You can:")
        print("1. Run this script again with your keys")
        print("2. Manually edit secure_keys/.gemini_key and .gemini_secret")
        print("3. Use the existing symlinks if keys are already configured")
        return False
    
    api_secret = input("Secret Key: ").strip()
    if not api_secret:
        print("❌ Secret key is required")
        return False
    
    # Save keys
    key_file = os.path.join(SECURE_DIR, ".gemini_key")
    secret_file = os.path.join(SECURE_DIR, ".gemini_secret")
    
    with open(key_file, 'w') as f:
        f.write(api_key)
    with open(secret_file, 'w') as f:
        f.write(api_secret)
    
    # Update symlinks
    os.system(f"ln -sf {key_file} {os.path.join(BASE_DIR, '.gemini_key')}")
    os.system(f"ln -sf {secret_file} {os.path.join(BASE_DIR, '.gemini_secret')}")
    
    print(f"\n✅ Gemini API keys saved to:")
    print(f"   Key: {key_file}")
    print(f"   Secret: {secret_file}")
    
    # Test the keys
    print("\n🧪 Testing Gemini connection...")
    try:
        import ccxt
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': api_secret
        })
        
        # Simple test - fetch balance
        balance = exchange.fetch_balance()
        usd_balance = balance.get('USD', {}).get('free', 0)
        print(f"✅ Connection successful!")
        print(f"💰 USD Balance: ${usd_balance:.2f}")
        
        if usd_balance >= 200:
            print("✅ Sufficient funds for Gemini longs ($200+ USD)")
        else:
            print(f"⚠️ Current balance: ${usd_balance:.2f} USD")
            print("   Recommended: $200+ for conservative trading")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n💡 Possible issues:")
        print("1. API keys may be incorrect")
        print("2. Account may need verification")
        print("3. API permissions insufficient")
        return False

def check_existing_keys():
    """Check if API keys already exist and work"""
    print("\n" + "="*60)
    print("CHECKING EXISTING API KEYS")
    print("="*60)
    
    # Check Binance
    binance_key_file = os.path.join(BASE_DIR, ".binance_key")
    binance_secret_file = os.path.join(BASE_DIR, ".binance_secret")
    
    if os.path.exists(binance_key_file) and os.path.getsize(binance_key_file) > 1:
        print("📦 Binance API key file exists")
        with open(binance_key_file, 'r') as f:
            key_content = f.read().strip()
            print(f"   Key length: {len(key_content)} chars")
    else:
        print("❌ Binance API key file missing or empty")
    
    # Check Gemini
    gemini_key_file = os.path.join(BASE_DIR, ".gemini_key")
    gemini_secret_file = os.path.join(BASE_DIR, ".gemini_secret")
    
    if os.path.exists(gemini_key_file) and os.path.getsize(gemini_key_file) > 1:
        print("📦 Gemini API key file exists")
        with open(gemini_key_file, 'r') as f:
            key_content = f.read().strip()
            print(f"   Key length: {len(key_content)} chars")
    else:
        print("❌ Gemini API key file missing or empty")

def main():
    """Main function"""
    print("API KEY SETUP FOR REAL TRADING")
    print("="*60)
    print("Configure Binance and Gemini API keys for real trading")
    print("="*60)
    
    # Create secure directory if it doesn't exist
    os.makedirs(SECURE_DIR, exist_ok=True)
    
    # Check existing keys first
    check_existing_keys()
    
    print("\n" + "="*60)
    print("SETUP OPTIONS")
    print("="*60)
    print("1. Setup Binance API keys")
    print("2. Setup Gemini API keys")
    print("3. Setup both")
    print("4. Skip setup (use existing keys)")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    binance_setup = False
    gemini_setup = False
    
    if choice == '1':
        binance_setup = setup_binance_keys()
    elif choice == '2':
        gemini_setup = setup_gemini_keys()
    elif choice == '3':
        binance_setup = setup_binance_keys()
        if binance_setup:
            gemini_setup = setup_gemini_keys()
    elif choice == '4':
        print("\n⏭️ Skipping setup. Using existing API keys.")
        return
    elif choice == '5':
        print("\n👋 Exiting setup.")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice")
        return
    
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    
    if binance_setup or gemini_setup:
        print("\n✅ API keys configured successfully!")
        print("\n🚀 NEXT STEPS:")
        print("1. Start the trading bot: python3 conservative_crypto_trading.py")
        print("2. Monitor dashboard: http://127.0.0.1:5080")
        print("3. Check API status: curl http://127.0.0.1:5001/status")
        print("4. View logs: tail -f trading.log")
        
        print("\n⚠️ IMPORTANT SECURITY NOTES:")
        print("• API keys are stored in secure_keys/ directory")
        print("• Never share your API keys")
        print("• Use IP whitelisting on exchange accounts")
        print("• Regularly rotate API keys")
        print("• Monitor account activity")
    else:
        print("\n⚠️ Setup incomplete. Please run this script again.")
        print("\n💡 MANUAL SETUP INSTRUCTIONS:")
        print("1. Create API keys on Binance/Gemini")
        print("2. Save them to secure_keys/.binance_key/.binance_secret")
        print("3. Save them to secure_keys/.gemini_key/.gemini_secret")
        print("4. Ensure files have proper permissions: chmod 600 secure_keys/*")
        print("5. Run the trading system again")

if __name__ == "__main__":
    main()