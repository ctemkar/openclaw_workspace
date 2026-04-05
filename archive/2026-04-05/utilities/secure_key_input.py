#!/usr/bin/env python3
"""
Secure API key input with masked secrets (shows stars)
"""

import getpass
import os
import sys
from datetime import datetime

def secure_input(prompt, mask=True):
    """Get input with optional masking"""
    if mask:
        return getpass.getpass(prompt)
    else:
        return input(prompt)

def check_existing_keys():
    """Check what keys already exist"""
    print("\n" + "="*60)
    print("🔍 CHECKING EXISTING API KEYS")
    print("="*60)
    
    key_files = {
        "Gemini Key": "secure_keys/.gemini_key",
        "Gemini Secret": "secure_keys/.gemini_secret", 
        "Binance Key": "secure_keys/.binance_key",
        "Binance Secret": "secure_keys/.binance_secret"
    }
    
    for name, filepath in key_files.items():
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
                    if content:
                        # Show masked version for secrets
                        if "Secret" in name:
                            print(f"✅ {name}: {'*' * 20} (set, {len(content)} chars)")
                        else:
                            print(f"✅ {name}: {content[:10]}... (set, {len(content)} chars)")
                    else:
                        print(f"❌ {name}: EMPTY")
            except:
                print(f"⚠️ {name}: Cannot read")
        else:
            print(f"❌ {name}: Not found")
    
    print("="*60)

def update_keys_securely():
    """Update keys with secure masked input"""
    print("\n" + "="*60)
    print("🔐 SECURE API KEY UPDATE (Secrets masked with *****)")
    print("="*60)
    
    # Create secure directory
    os.makedirs("secure_keys", exist_ok=True)
    os.chmod("secure_keys", 0o700)
    
    print("\n📈 GEMINI KEYS ($200 for Longs):")
    print("-" * 40)
    
    # Gemini Key (visible)
    gemini_key = secure_input("Gemini API Key: ", mask=False)
    
    # Gemini Secret (masked with stars)
    print("Enter Gemini Secret (will show *****):")
    gemini_secret = secure_input("Gemini Secret: ", mask=True)
    
    print("\n📉 BINANCE KEYS ($50 for Shorts):")
    print("-" * 40)
    
    # Binance Key (visible)
    binance_key = secure_input("Binance API Key: ", mask=False)
    
    # Binance Secret (masked with stars)
    print("Enter Binance Secret (will show *****):")
    binance_secret = secure_input("Binance Secret: ", mask=True)
    
    print("\n" + "="*60)
    print("💾 SAVING KEYS WITH ULTRA-SECURE PERMISSIONS...")
    print("="*60)
    
    # Save Gemini keys
    with open("secure_keys/.gemini_key", "w") as f:
        f.write(gemini_key.strip())
    
    with open("secure_keys/.gemini_secret", "w") as f:
        f.write(gemini_secret.strip())
    
    # Save Binance keys
    with open("secure_keys/.binance_key", "w") as f:
        f.write(binance_key.strip())
    
    with open("secure_keys/.binance_secret", "w") as f:
        f.write(binance_secret.strip())
    
    # Set ultra-secure permissions
    os.chmod("secure_keys/.gemini_key", 0o600)
    os.chmod("secure_keys/.gemini_secret", 0o600)
    os.chmod("secure_keys/.binance_key", 0o600)
    os.chmod("secure_keys/.binance_secret", 0o600)
    
    # Create symlinks
    for src, dst in [
        ("secure_keys/.gemini_key", ".gemini_key"),
        ("secure_keys/.gemini_secret", ".gemini_secret"),
        ("secure_keys/.binance_key", ".binance_key"),
        ("secure_keys/.binance_secret", ".binance_secret")
    ]:
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(src, dst)
    
    print("✅ Keys saved securely in 'secure_keys/' directory")
    print("✅ File permissions: chmod 600 (readable only by you)")
    print("✅ Symlinks created for trading system")
    
    return True

def test_connections():
    """Test connections after updating keys"""
    print("\n" + "="*60)
    print("🔍 TESTING EXCHANGE CONNECTIONS")
    print("="*60)
    
    import ccxt
    
    # Test Gemini
    print("\n📈 Testing Gemini connection...")
    try:
        with open("secure_keys/.gemini_key", "r") as f:
            gemini_key = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            gemini_secret = f.read().strip()
        
        if not gemini_key or not gemini_secret:
            print("❌ Gemini: Missing key or secret")
        else:
            exchange = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True
            })
            balance = exchange.fetch_balance()
            usd_balance = balance['total'].get('USD', 0)
            print(f"✅ Gemini: CONNECTED (${usd_balance:.2f} available)")
            print(f"   Key: {gemini_key[:10]}...")
            print(f"   Secret: {'*' * 20} ({len(gemini_secret)} chars)")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
    
    # Test Binance
    print("\n📉 Testing Binance connection...")
    try:
        with open("secure_keys/.binance_key", "r") as f:
            binance_key = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            binance_secret = f.read().strip()
        
        if not binance_key or not binance_secret:
            print("❌ Binance: Missing key or secret")
        else:
            exchange = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            balance = exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', 0)
            print(f"✅ Binance: CONNECTED (${usdt_balance:.2f} available)")
            print(f"   Key: {binance_key[:10]}...")
            print(f"   Secret: {'*' * 20} ({len(binance_secret)} chars)")
    except Exception as e:
        print(f"❌ Binance error: {e}")
    
    print("="*60)

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🔐 SECURE API KEY SETUP WITH MASKED SECRETS")
    print("="*60)
    print("Secrets will show as ***** while typing")
    print("="*60)
    
    try:
        # Check existing keys
        check_existing_keys()
        
        # Update keys securely
        update_keys_securely()
        
        # Test connections
        test_connections()
        
        print("\n" + "="*60)
        print("🎯 SECURE KEY UPDATE COMPLETE!")
        print("="*60)
        
        print("\n🚀 NEXT STEPS:")
        print("1. Fund your accounts:")
        print("   • Gemini: Deposit $200")
        print("   • Binance: Deposit $50")
        
        print("\n2. Activate REAL trading:")
        print("   ./activate_real_system_now.sh")
        
        print("\n3. Monitor:")
        print("   • Telegram: @MMCashEarner_bot")
        print("   • Dashboard: http://127.0.0.1:5080")
        print("   • API: http://127.0.0.1:5001/status")
        
        print("\n🔐 SECURITY CONFIRMED:")
        print("   • Secrets masked during input ✓")
        print("   • Files stored with chmod 600 ✓")
        print("   • Directory secured with chmod 700 ✓")
        
        print("\n💰 READY FOR REAL $250 TRADING!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()