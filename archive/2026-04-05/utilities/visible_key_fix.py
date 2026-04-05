#!/usr/bin/env python3
"""
Fix API keys with VISIBLE input so you can verify
"""

import os
import sys
from datetime import datetime

def show_current_keys():
    """Show current key status"""
    print("\n" + "="*60)
    print("🔍 CURRENT KEY STATUS")
    print("="*60)
    
    files = {
        "Gemini Key": "secure_keys/.gemini_key",
        "Gemini Secret": "secure_keys/.gemini_secret",
        "Binance Key": "secure_keys/.binance_key", 
        "Binance Secret": "secure_keys/.binance_secret"
    }
    
    for name, path in files.items():
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read().strip()
                if content:
                    if "Secret" in name:
                        # Show full secret for verification
                        print(f"📄 {name}:")
                        print(f"   '{content}'")
                        print(f"   Length: {len(content)} characters")
                    else:
                        print(f"✅ {name}: {content[:15]}...")
                else:
                    print(f"❌ {name}: EMPTY FILE")
        else:
            print(f"❌ {name}: FILE NOT FOUND")
    
    print("="*60)

def fix_gemini_secret():
    """Fix Gemini secret (visible input)"""
    print("\n" + "="*60)
    print("🔧 FIX GEMINI SECRET (Visible Input)")
    print("="*60)
    
    print("\n📝 CURRENT GEMINI SECRET FILE:")
    if os.path.exists("secure_keys/.gemini_secret"):
        with open("secure_keys/.gemini_secret", 'r') as f:
            current = f.read().strip()
            print(f"   Content: '{current}'")
            print(f"   Length: {len(current)} chars")
    else:
        print("   File doesn't exist")
    
    print("\n✏️ ENTER CORRECT GEMINI SECRET (Visible):")
    print("Copy EXACTLY from Gemini website → API Settings")
    print("Should be ~40 characters like: 2pXgR9kL8zqY7wV5tS3uM6nB4cD1fG8hJ2")
    print()
    
    new_secret = input("Gemini Secret: ").strip()
    
    print(f"\n📋 YOU ENTERED: '{new_secret}'")
    print(f"   Length: {len(new_secret)} characters")
    
    confirm = input("\n✅ Is this correct? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        with open("secure_keys/.gemini_secret", 'w') as f:
            f.write(new_secret)
        os.chmod("secure_keys/.gemini_secret", 0o600)
        print("✅ Gemini secret updated!")
    else:
        print("❌ Cancelled. Secret not changed.")
    
    return confirm == 'yes'

def verify_binance_secret():
    """Verify Binance secret is correct"""
    print("\n" + "="*60)
    print("🔍 VERIFY BINANCE SECRET")
    print("="*60)
    
    if not os.path.exists("secure_keys/.binance_secret"):
        print("❌ Binance secret file not found")
        return False
    
    with open("secure_keys/.binance_secret", 'r') as f:
        current_secret = f.read().strip()
    
    print(f"\n📄 CURRENT BINANCE SECRET:")
    print(f"   '{current_secret}'")
    print(f"   Length: {len(current_secret)} characters")
    
    print("\n🔑 BINANCE SECRET SHOULD BE:")
    print("   • 64+ characters long")
    print("   • No spaces at start/end")
    print("   • Copied EXACTLY from Binance website")
    
    print("\n🤔 COMMON ISSUES:")
    print("   1. Missing first/last character")
    print("   2. Hidden spaces before/after")
    print("   3. Wrong character (0 vs O, 1 vs l)")
    
    print("\n✏️ RE-ENTER IF NEEDED (or press Enter to keep current):")
    new_secret = input("Binance Secret: ").strip()
    
    if new_secret:  # User entered something new
        print(f"\n📋 NEW SECRET: '{new_secret}'")
        print(f"   Length: {len(new_secret)} characters")
        
        confirm = input("\n✅ Update Binance secret? (yes/no): ").strip().lower()
        if confirm == 'yes':
            with open("secure_keys/.binance_secret", 'w') as f:
                f.write(new_secret)
            os.chmod("secure_keys/.binance_secret", 0o600)
            print("✅ Binance secret updated!")
            return True
        else:
            print("❌ Kept current secret")
            return False
    else:
        print("✅ Keeping current Binance secret")
        return True

def test_connections():
    """Test connections after fixes"""
    print("\n" + "="*60)
    print("🔌 TESTING CONNECTIONS")
    print("="*60)
    
    import ccxt
    
    # Test Gemini
    print("\n📈 Testing Gemini...")
    try:
        with open("secure_keys/.gemini_key", 'r') as f:
            g_key = f.read().strip()
        with open("secure_keys/.gemini_secret", 'r') as f:
            g_secret = f.read().strip()
        
        if not g_key or not g_secret:
            print("❌ Missing Gemini key or secret")
        else:
            exchange = ccxt.gemini({
                'apiKey': g_key,
                'secret': g_secret,
                'enableRateLimit': True
            })
            balance = exchange.fetch_balance()
            usd = balance['total'].get('USD', 0)
            print(f"✅ Gemini CONNECTED!")
            print(f"   Balance: ${usd:.2f}")
            print(f"   Key: {g_key[:10]}...")
            print(f"   Secret length: {len(g_secret)} chars ✓")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
    
    # Test Binance
    print("\n📉 Testing Binance...")
    try:
        with open("secure_keys/.binance_key", 'r') as f:
            b_key = f.read().strip()
        with open("secure_keys/.binance_secret", 'r') as f:
            b_secret = f.read().strip()
        
        if not b_key or not b_secret:
            print("❌ Missing Binance key or secret")
        else:
            exchange = ccxt.binance({
                'apiKey': b_key,
                'secret': b_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            balance = exchange.fetch_balance()
            usdt = balance['total'].get('USDT', 0)
            print(f"✅ Binance CONNECTED!")
            print(f"   Balance: ${usdt:.2f}")
            print(f"   Key: {b_key[:10]}...")
            print(f"   Secret length: {len(b_secret)} chars ✓")
    except Exception as e:
        print(f"❌ Binance error: {e}")
        print("   Common fix: Re-copy EXACT secret from Binance website")
    
    print("="*60)

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🔑 VISIBLE API KEY FIX")
    print("="*60)
    print("All input visible so you can verify correctness")
    print("="*60)
    
    try:
        # Show current status
        show_current_keys()
        
        # Fix Gemini secret (it's empty)
        print("\n⚠️ ISSUE DETECTED: Gemini secret is EMPTY")
        fix_gemini_secret()
        
        # Verify Binance secret
        print("\n⚠️ Binance had signature error - verifying secret...")
        verify_binance_secret()
        
        # Test connections
        test_connections()
        
        print("\n" + "="*60)
        print("🎯 KEY FIX COMPLETE!")
        print("="*60)
        
        print("\n🚀 NEXT:")
        print("1. Fund accounts:")
        print("   • Gemini: $200")
        print("   • Binance: $50")
        
        print("\n2. Activate REAL trading:")
        print("   ./activate_real_system_now.sh")
        
        print("\n3. Check Telegram:")
        print("   Message @MMCashEarner_bot: /status")
        
        print("\n💰 READY FOR REAL $250 TRADING!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()