#!/usr/bin/env python3
"""
Fix Binance API secret key issue
"""

import os
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
SECRET_FILE = os.path.join(BASE_DIR, "secure_keys", ".binance_secret")

def check_current_secret():
    """Check current secret file"""
    print("🔍 Checking current Binance secret file...")
    
    if os.path.exists(SECRET_FILE):
        size = os.path.getsize(SECRET_FILE)
        with open(SECRET_FILE, 'rb') as f:
            content = f.read()
        
        print(f"  File size: {size} bytes")
        print(f"  Content (hex): {content.hex()}")
        
        if size <= 1:
            print("  ❌ File is empty or has only newline")
            return False
        elif size < 20:
            print(f"  ⚠️  File is very small ({size} bytes), likely invalid")
            return False
        else:
            print(f"  ✅ File has {size} bytes, might be valid")
            # Show first and last few chars (masked)
            secret = content.decode('utf-8', errors='ignore').strip()
            if len(secret) > 8:
                masked = secret[:4] + "..." + secret[-4:]
                print(f"  Secret: {masked}")
            return True
    else:
        print("  ❌ File does not exist")
        return False

def add_binance_secret():
    """Add Binance API secret"""
    print("\n" + "="*60)
    print("ADD BINANCE API SECRET KEY")
    print("="*60)
    
    print("\n📋 INSTRUCTIONS:")
    print("1. Go to Binance.com → API Management")
    print("2. Find your API key (starts with 'SdiE3ZgEYz...')")
    print("3. Click 'Show' next to the Secret Key")
    print("4. Copy the entire Secret Key")
    
    print("\n🔑 ENTER YOUR BINANCE SECRET KEY:")
    print("(The input will not be shown for security)")
    
    try:
        import getpass
        secret = getpass.getpass("Secret Key: ").strip()
        
        if not secret:
            print("\n❌ No secret key entered")
            return False
        
        if len(secret) < 20:
            print(f"\n⚠️  Warning: Secret key is very short ({len(secret)} chars)")
            print("   Binance secret keys are typically 64 characters")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                return False
        
        # Save the secret
        os.makedirs(os.path.dirname(SECRET_FILE), exist_ok=True)
        with open(SECRET_FILE, 'w') as f:
            f.write(secret)
        
        print(f"\n✅ Secret key saved to: {SECRET_FILE}")
        print(f"   Length: {len(secret)} characters")
        
        # Set secure permissions
        os.chmod(SECRET_FILE, 0o600)
        print("   Permissions set to 600 (owner read/write only)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_binance_connection():
    """Test Binance connection with new secret"""
    print("\n" + "="*60)
    print("TESTING BINANCE CONNECTION")
    print("="*60)
    
    try:
        import ccxt
        
        # Read keys
        with open(os.path.join(BASE_DIR, ".binance_key"), 'r') as f:
            api_key = f.read().strip()
        with open(SECRET_FILE, 'r') as f:
            api_secret = f.read().strip()
        
        print(f"API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
        print(f"Secret: {'*' * len(api_secret)}")
        
        # Initialize exchange
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'spot'},
            'enableRateLimit': True
        })
        
        print("\nTesting connection...")
        
        # Test public endpoint
        markets = exchange.load_markets()
        print(f"✅ Markets loaded: {len(markets)} symbols")
        
        # Test private endpoint (balance)
        print("Fetching balance...")
        try:
            balance = exchange.fetch_balance()
            print("✅ Balance fetch successful!")
            
            # Check USDT balance
            if 'USDT' in balance:
                usdt_free = balance['USDT'].get('free', 0)
                usdt_total = balance['USDT'].get('total', 0)
                print(f"\n💰 USDT BALANCE:")
                print(f"   Free:  ${usdt_free:.2f}")
                print(f"   Total: ${usdt_total:.2f}")
                
                if usdt_free >= 50:
                    print(f"✅ Sufficient funds for trading: ${usdt_free:.2f}")
                else:
                    print(f"⚠️  Low balance: ${usdt_free:.2f} (need $50+)")
            else:
                print("⚠️  USDT balance not found")
                
            return True
            
        except Exception as e:
            print(f"❌ Balance fetch failed: {e}")
            print("\n💡 Possible issues:")
            print("1. API key disabled or expired")
            print("2. IP address not whitelisted")
            print("3. Insufficient permissions")
            return False
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("FIX BINANCE API SECRET FOR 26-CRYPTO TRADING")
    print("="*60)
    
    # Check current
    has_secret = check_current_secret()
    
    if has_secret:
        print("\n⚠️  Secret file exists but might be invalid")
        choice = input("\nDo you want to: (1) Test current secret, (2) Enter new secret, (3) Cancel? [1/2/3]: ").strip()
        
        if choice == '1':
            test_binance_connection()
            return
        elif choice == '2':
            if add_binance_secret():
                test_binance_connection()
            return
        else:
            print("Cancelled")
            return
    else:
        # No valid secret, add one
        if add_binance_secret():
            test_binance_connection()

if __name__ == "__main__":
    main()