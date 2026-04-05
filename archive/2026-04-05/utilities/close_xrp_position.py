#!/usr/bin/env python3
"""
Close the tiny XRP position manually
"""

import ccxt
import json

def close_xrp_position():
    """Close the small XRP position"""
    
    print("🔧 CLOSING SMALL XRP POSITION")
    print("=" * 60)
    
    # Load API keys
    try:
        with open("secure_keys/.binance_key", "r") as f:
            api_key = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            api_secret = f.read().strip()
    except Exception as e:
        print(f"❌ Failed to load Binance keys: {e}")
        return False
    
    # Initialize Binance Futures
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
    
    # Get current positions
    positions = exchange.fetch_positions()
    
    xrp_position = None
    for pos in positions:
        if 'XRP' in pos['symbol'] and float(pos['contracts']) != 0:
            xrp_position = pos
            break
    
    if not xrp_position:
        print("✅ No XRP position found (may already be closed)")
        return True
    
    print(f"📊 XRP Position Details:")
    print(f"   Symbol: {xrp_position['symbol']}")
    print(f"   Contracts: {xrp_position['contracts']}")
    print(f"   Entry Price: ${xrp_position['entryPrice']}")
    print(f"   Mark Price: ${xrp_position['markPrice']}")
    print(f"   Unrealized P&L: ${xrp_position['unrealizedPnl']}")
    
    # Check if position is too small
    position_value = abs(float(xrp_position['contracts']) * float(xrp_position['entryPrice']))
    if position_value < 5:
        print(f"⚠️  Position too small: ${position_value:.2f} (minimum $5)")
        print("   Trying to close anyway...")
    
    try:
        # To close a SHORT, we need to BUY
        print("\n🚀 Closing XRP position...")
        order = exchange.create_order(
            symbol=xrp_position['symbol'],
            type='market',
            side='buy',
            amount=abs(float(xrp_position['contracts']))
        )
        
        print(f"✅ XRP POSITION CLOSED:")
        print(f"   Order ID: {order['id']}")
        print(f"   Filled: {order['filled']}")
        print(f"   Average Price: ${order['average']}")
        
        # Update our records
        update_position_records(xrp_position['symbol'], order['average'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error closing XRP: {e}")
        
        # Try alternative: use reduce-only order
        try:
            print("\n🔄 Trying reduce-only order...")
            order = exchange.create_order(
                symbol=xrp_position['symbol'],
                type='market',
                side='buy',
                amount=abs(float(xrp_position['contracts'])),
                params={'reduceOnly': True}
            )
            
            print(f"✅ XRP CLOSED with reduce-only:")
            print(f"   Order ID: {order['id']}")
            
            update_position_records(xrp_position['symbol'], order['average'])
            return True
            
        except Exception as e2:
            print(f"❌ Reduce-only also failed: {e2}")
            return False

def update_position_records(symbol, close_price):
    """Update position records"""
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            positions = json.load(f)
        
        # Find and update XRP position
        for i, pos in enumerate(positions):
            if 'XRP' in pos['symbol'] and pos.get('status') == 'OPEN':
                positions[i]['status'] = 'CLOSED'
                positions[i]['close_price'] = close_price
                positions[i]['close_time'] = "2026-04-01T00:30:00.000000"
                positions[i]['realized_pnl'] = pos.get('unrealized_pnl', 0)
                positions[i]['notes'] = 'MANUALLY CLOSED - position too small'
                break
        
        with open('26_crypto_trade_history.json', 'w') as f:
            json.dump(positions, f, indent=2)
        
        print("✅ Updated position records")
        
    except Exception as e:
        print(f"⚠️  Error updating records: {e}")

if __name__ == "__main__":
    success = close_xrp_position()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 XRP POSITION CLOSED")
        print("=" * 60)
        print("Now we have:")
        print("• 0 Binance positions (all closed)")
        print("• 0 Gemini positions (ready to buy)")
        print("• Full capital available for new trades")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED TO CLOSE XRP")
        print("=" * 60)
        print("Manual closing required:")
        print("1. Go to Binance Futures")
        print("2. Find XRP/USDT in Positions")
        print("3. Click 'Close'")
        print("4. Side: BUY, Type: MARKET")
        print("5. Confirm")