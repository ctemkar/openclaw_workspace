#!/usr/bin/env python3
"""
SAFE TEST - Check conditions before real trading
"""

import os
import json
import ccxt
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_test():
    """Run safe tests before real trading"""
    print("=" * 70)
    print("🔒 SAFE TRADING TEST - PRE-FLIGHT CHECK")
    print("=" * 70)
    
    # Test 1: Check API keys
    print("\n1. 🔑 Testing API keys...")
    try:
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.binance_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        print(f"   ✅ API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"   ✅ Secret: {'*' * len(api_secret)} ({len(api_secret)} chars)")
    except Exception as e:
        print(f"   ❌ API key error: {e}")
        return False
    
    # Test 2: Check connection
    print("\n2. 🔗 Testing Binance Futures connection...")
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'future'},
            'enableRateLimit': True
        })
        
        markets = exchange.load_markets()
        print(f"   ✅ Connected: {len(markets)} markets")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test 3: Check balance
    print("\n3. 💰 Checking balance...")
    try:
        balance = exchange.fetch_balance()
        free_usdt = balance.get('USDT', {}).get('free', 0)
        total_usdt = balance.get('USDT', {}).get('total', 0)
        
        print(f"   ✅ Free USDT: ${free_usdt:.2f}")
        print(f"   ✅ Total USDT: ${total_usdt:.2f}")
        
        if total_usdt < 10:
            print(f"   ⚠️  Low balance: ${total_usdt:.2f} (need $10+)")
            return False
    except Exception as e:
        print(f"   ❌ Balance check failed: {e}")
        return False
    
    # Test 4: Check current market conditions
    print("\n4. 📊 Checking current market conditions...")
    try:
        # Check a few major pairs
        test_pairs = ['BTC/USDT', 'ETH/USDT', 'DOT/USDT', 'COMP/USDT']
        
        for pair in test_pairs:
            try:
                ticker = exchange.fetch_ticker(pair)
                price = ticker['last']
                change = ticker.get('percentage', 0)
                
                status = "📉 SHORT opportunity" if change < -1.0 else "➡️  Neutral"
                print(f"   {pair:12} ${price:8.2f} {change:6.2f}% {status}")
            except:
                print(f"   {pair:12} Error fetching data")
    except Exception as e:
        print(f"   ❌ Market check failed: {e}")
    
    # Test 5: Check if we can place a SMALL test order
    print("\n5. 🧪 Testing order placement (SIMULATED)...")
    try:
        # Try to get order book for BTC
        orderbook = exchange.fetch_order_book('BTC/USDT', limit=5)
        print(f"   ✅ Order book accessible")
        print(f"   Best bid: ${orderbook['bids'][0][0]:.2f}")
        print(f"   Best ask: ${orderbook['asks'][0][0]:.2f}")
    except Exception as e:
        print(f"   ❌ Order book failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 RECOMMENDED SAFE START:")
    print("=" * 70)
    
    print("\nOPTION 1: PAPER TRADING (Recommended)")
    print("   • Continue with simulation mode")
    print("   • Build confidence with fake trades")
    print("   • No real money risk")
    
    print("\nOPTION 2: MICRO TRADING")
    print("   • Trade with $5-10 only")
    print("   • Test with tiny positions")
    print("   • Minimal risk")
    
    print("\nOPTION 3: FULL TRADING")
    print("   • Use full $77.68")
    print("   • Higher risk/reward")
    print("   • NOT recommended for first trades")
    
    print("\n💡 MY RECOMMENDATION:")
    print("   Start with OPTION 1 or 2")
    print("   Test for 1-2 days")
    print("   Then scale up")
    
    print(f"\n⏰ Test completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    
    return True

def get_user_choice():
    """Get user choice for trading mode"""
    print("\n" + "=" * 70)
    print("SELECT TRADING MODE:")
    print("=" * 70)
    print("1. PAPER TRADING - Simulation only (safe)")
    print("2. MICRO TRADING - $5-10 real trades (low risk)")
    print("3. FULL TRADING - $77.68 real trades (higher risk)")
    print("4. CANCEL - Don't trade now")
    print("=" * 70)
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        return 'paper'
    elif choice == '2':
        return 'micro'
    elif choice == '3':
        return 'full'
    else:
        return 'cancel'

if __name__ == "__main__":
    if safe_test():
        choice = get_user_choice()
        
        if choice == 'paper':
            print("\n✅ Continuing with PAPER TRADING (simulation)")
            print("   The bot will create trade plans but not execute")
            
        elif choice == 'micro':
            print("\n⚠️  Starting MICRO TRADING ($5-10 positions)")
            print("   Will execute REAL trades with tiny amounts")
            print("   Minimal risk testing")
            
            # Create micro trading config
            config = {
                'mode': 'micro',
                'max_trade_size': 10.00,
                'leverage': 1,
                'daily_trades': 1,
                'enabled': True,
                'started': datetime.now().isoformat()
            }
            
            config_file = os.path.join(BASE_DIR, "micro_trading_config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Config saved: {config_file}")
            
        elif choice == 'full':
            print("\n🚨 STARTING FULL TRADING ($77.68)")
            print("   REAL MONEY AT RISK")
            print("   Confirm you understand the risks")
            
            confirm = input("\nType 'YES' to confirm full trading: ").strip()
            if confirm == 'YES':
                print("✅ Full trading enabled")
            else:
                print("❌ Cancelled - staying in paper mode")
                choice = 'paper'
        
        else:
            print("\n❌ Trading cancelled")
        
        print(f"\nSelected mode: {choice.upper()}")
        
    else:
        print("\n❌ Pre-flight checks failed")
        print("   Fix issues before trading")