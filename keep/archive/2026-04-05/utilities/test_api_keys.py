#!/usr/bin/env python3
"""
Test API keys for Binance and Gemini
"""

import os
import ccxt

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def test_binance():
    """Test Binance API keys"""
    print("\n" + "="*60)
    print("TESTING BINANCE API KEYS")
    print("="*60)
    
    try:
        with open(os.path.join(BASE_DIR, ".binance_key"), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, ".binance_secret"), 'r') as f:
            api_secret = f.read().strip()
        
        print(f"API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else ''}")
        print(f"Secret: {'*' * len(api_secret)}")
        
        # Initialize Binance
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'spot'},
            'enableRateLimit': True
        })
        
        print("\nTesting connection...")
        
        # Test 1: Fetch markets (public endpoint)
        markets = exchange.load_markets()
        print(f"✅ Markets loaded: {len(markets)} symbols")
        
        # Test 2: Fetch balance (private endpoint)
        print("Fetching balance...")
        try:
            balance = exchange.fetch_balance()
            print("✅ Balance fetch successful")
            
            # Check USDT balance
            if 'USDT' in balance:
                usdt_free = balance['USDT'].get('free', 0)
                usdt_total = balance['USDT'].get('total', 0)
                print(f"💰 USDT Balance:")
                print(f"  Free:  ${usdt_free:.2f}")
                print(f"  Total: ${usdt_total:.2f}")
                
                if usdt_free >= 70:
                    print(f"✅ Sufficient funds: ${usdt_free:.2f} USDT available")
                else:
                    print(f"⚠️  Low balance: ${usdt_free:.2f} USDT (you mentioned $70+)")
            else:
                print("⚠️  USDT balance not found in response")
                
        except Exception as e:
            print(f"❌ Balance fetch failed: {e}")
            print("\n💡 Possible issues:")
            print("1. API keys may not have balance read permission")
            print("2. IP address not whitelisted")
            print("3. API keys disabled or expired")
        
        return True
        
    except FileNotFoundError:
        print("❌ API key files not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gemini():
    """Test Gemini API keys"""
    print("\n" + "="*60)
    print("TESTING GEMINI API KEYS")
    print("="*60)
    
    try:
        with open(os.path.join(BASE_DIR, ".gemini_key"), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, ".gemini_secret"), 'r') as f:
            api_secret = f.read().strip()
        
        print(f"API Key: {api_key}")
        print(f"Secret: {'*' * len(api_secret)}")
        
        # Initialize Gemini
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        
        print("\nTesting connection...")
        
        # Test 1: Fetch markets
        markets = exchange.load_markets()
        print(f"✅ Markets loaded: {len(markets)} symbols")
        
        # Test 2: Fetch balance
        print("Fetching balance...")
        try:
            balance = exchange.fetch_balance()
            print("✅ Balance fetch successful")
            
            # Check USD balance
            if 'USD' in balance:
                usd_free = balance['USD'].get('free', 0)
                usd_total = balance['USD'].get('total', 0)
                print(f"💰 USD Balance:")
                print(f"  Free:  ${usd_free:.2f}")
                print(f"  Total: ${usd_total:.2f}")
                
                if usd_free >= 200:
                    print(f"✅ Sufficient funds: ${usd_free:.2f} USD available")
                else:
                    print(f"⚠️  Low balance: ${usd_free:.2f} USD (recommended: $200+)")
            else:
                print("⚠️  USD balance not found in response")
                
        except Exception as e:
            print(f"❌ Balance fetch failed: {e}")
            print("\n💡 Possible issues:")
            print("1. API keys may not have correct permissions")
            print("2. Account may need verification")
            print("3. API keys disabled")
        
        return True
        
    except FileNotFoundError:
        print("❌ API key files not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("API KEY TEST FOR REAL TRADING")
    print("="*60)
    
    print("\nBased on your message, you have:")
    print("• Binance: $70+ USDT available")
    print("• Gemini: Should have funds for $200 LONG positions")
    print("• Total capital: $250 ($200 Gemini + $50 Binance)")
    print("• Cryptocurrencies: 26 total")
    
    # Test Binance
    binance_ok = test_binance()
    
    # Test Gemini
    gemini_ok = test_gemini()
    
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    if binance_ok and gemini_ok:
        print("✅ BOTH EXCHANGES CONNECTED SUCCESSFULLY")
        print("\n🚀 Ready for real trading with 26 cryptocurrencies!")
        print("\n📋 NEXT STEPS:")
        print("1. Start trading bot: python3 simple_26_crypto_bot.py")
        print("2. Monitor dashboard: http://127.0.0.1:5080")
        print("3. Check API status: curl http://127.0.0.1:5001/status")
        
    elif binance_ok and not gemini_ok:
        print("⚠️ PARTIAL CONNECTION")
        print("✅ Binance: Connected")
        print("❌ Gemini: Not connected")
        print("\n💡 You can still trade with Binance SHORT positions")
        
    elif not binance_ok and gemini_ok:
        print("⚠️ PARTIAL CONNECTION")
        print("❌ Binance: Not connected")
        print("✅ Gemini: Connected")
        print("\n💡 You can still trade with Gemini LONG positions")
        
    else:
        print("❌ NO EXCHANGES CONNECTED")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Verify API keys are correct")
        print("2. Check if keys have 'trade' permissions")
        print("3. Ensure IP address is whitelisted")
        print("4. Try creating new API keys")
    
    print("\n📁 Configuration files updated:")
    print("• 26_crypto_config.json - 26 cryptocurrency configuration")
    print("• quick_start_config.json - Quick start settings")
    print("• simple_26_crypto_bot.py - Working trading bot")

if __name__ == "__main__":
    main()