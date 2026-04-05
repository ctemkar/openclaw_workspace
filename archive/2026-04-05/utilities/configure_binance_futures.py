#!/usr/bin/env python3
"""
Configure Binance Futures for trading
"""

import os
import ccxt
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_futures():
    """Configure Binance Futures for trading"""
    print("=" * 70)
    print("⚙️  CONFIGURING BINANCE FUTURES")
    print("=" * 70)
    
    # Load API keys
    try:
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.binance_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
    except Exception as e:
        print(f"❌ API key error: {e}")
        return False
    
    # Initialize exchange
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'future'},
            'enableRateLimit': True
        })
        
        print("✅ Binance Futures connected")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Step 1: Check current position mode
    print("\n1. 🔍 Checking current position mode...")
    try:
        # Try to get position mode
        response = exchange.fapiPrivateGetPositionSideDual()
        print(f"   Current position mode: {response}")
        
        # Set to ONE_WAY mode (simpler for beginners)
        print("\n2. ⚙️  Setting position mode to ONE_WAY...")
        params = {'dualSidePosition': 'false'}  # false = ONE_WAY, true = HEDGE
        response = exchange.fapiPrivatePostPositionSideDual(params)
        print(f"   Position mode set: {response}")
        
    except Exception as e:
        print(f"   ❌ Position mode error: {e}")
    
    # Step 2: Check margin mode for a symbol
    print("\n3. 🔍 Checking margin mode for DOT/USDT...")
    try:
        # Check current margin mode
        params = {'symbol': 'DOTUSDT'}
        response = exchange.fapiPrivateGetMarginType(params)
        print(f"   Current margin mode: {response}")
        
        # Set to ISOLATED (recommended for beginners)
        print("\n4. ⚙️  Setting margin mode to ISOLATED...")
        params = {
            'symbol': 'DOTUSDT',
            'marginType': 'ISOLATED'
        }
        response = exchange.fapiPrivatePostMarginType(params)
        print(f"   Margin mode set: {response}")
        
    except Exception as e:
        print(f"   ❌ Margin mode error: {e}")
    
    # Step 3: Set leverage
    print("\n5. ⚙️  Setting leverage for DOT/USDT...")
    try:
        params = {
            'symbol': 'DOTUSDT',
            'leverage': 2
        }
        response = exchange.fapiPrivatePostLeverage(params)
        print(f"   Leverage set to 2x: {response}")
    except Exception as e:
        print(f"   ❌ Leverage error: {e}")
    
    # Step 4: Test a small market buy (to verify)
    print("\n6. 🧪 Testing with tiny market buy...")
    try:
        # Get current price
        ticker = exchange.fetch_ticker('DOT/USDT')
        price = ticker['last']
        print(f"   DOT/USDT price: ${price:.4f}")
        
        # Calculate tiny amount ($1 worth)
        amount = 1 / price
        print(f"   Would buy {amount:.4f} DOT ($1 worth)")
        
        # UNCOMMENT FOR REAL TEST
        # order = exchange.create_order(
        #     symbol='DOT/USDT',
        #     type='market',
        #     side='buy',
        #     amount=amount
        # )
        # print(f"   Test order placed: {order['id']}")
        
        print("   ⚠️  Test order NOT placed (commented for safety)")
        
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Step 5: Check account status
    print("\n7. 📊 Checking account status...")
    try:
        balance = exchange.fetch_balance()
        free_usdt = balance.get('USDT', {}).get('free', 0)
        total_usdt = balance.get('USDT', {}).get('total', 0)
        
        print(f"   Free USDT: ${free_usdt:.2f}")
        print(f"   Total USDT: ${total_usdt:.2f}")
        print(f"   Positions: {len(balance.get('info', {}).get('positions', []))}")
        
        # Check if we have any open positions
        positions = exchange.fetch_positions()
        open_positions = [p for p in positions if float(p['contracts']) > 0]
        
        print(f"   Open positions: {len(open_positions)}")
        for pos in open_positions:
            print(f"     {pos['symbol']}: {pos['side']} {pos['contracts']} contracts")
        
    except Exception as e:
        print(f"   ❌ Account status error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ CONFIGURATION COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. The trading bot should now work")
    print("2. It will use ONE_WAY position mode")
    print("3. ISOLATED margin mode")
    print("4. 2x leverage")
    print("\n⚠️  If errors persist, check:")
    print("   • Binance Futures trading permissions")
    print("   • API key permissions (enable Futures)")
    print("   • Account verification level")
    
    return True

if __name__ == "__main__":
    configure_futures()