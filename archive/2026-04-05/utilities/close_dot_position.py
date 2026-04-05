#!/usr/bin/env python3
"""
URGENT: Close DOT/USDT short position on Binance Futures
"""

import ccxt
import json
import os
from datetime import datetime
import time

def load_binance_keys():
    """Load Binance API keys"""
    try:
        with open("secure_keys/.binance_key", "r") as f:
            api_key = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            api_secret = f.read().strip()
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Failed to load Binance keys: {e}")
        return None, None

def get_dot_position_details():
    """Get DOT position details from our records"""
    try:
        with open('26_crypto_trade_history.json', 'r') as f:
            positions = json.load(f)
        
        for pos in positions:
            if 'DOT' in pos['symbol']:
                return pos
    except Exception as e:
        print(f"❌ Error reading position data: {e}")
    
    return None

def close_dot_position():
    """Close the DOT/USDT short position"""
    print("🚨 CLOSING DOT/USDT SHORT POSITION")
    print("=" * 60)
    
    # Load API keys
    api_key, api_secret = load_binance_keys()
    if not api_key or not api_secret:
        print("❌ Binance API keys not found")
        return False
    
    # Get position details
    dot_position = get_dot_position_details()
    if not dot_position:
        print("❌ DOT position not found in records")
        return False
    
    print(f"📊 POSITION DETAILS:")
    print(f"   Symbol: {dot_position['symbol']}")
    print(f"   Entry Price: ${dot_position.get('entry_price', 0):.4f}")
    print(f"   Current Price: ${dot_position.get('current_price', 0):.4f}")
    print(f"   Position Size: ${abs(dot_position.get('position_size', 0)):.2f}")
    print(f"   Current P&L: ${dot_position.get('unrealized_pnl', 0):.4f} ({dot_position.get('pnl_percent', 0):.2f}%)")
    
    # Initialize Binance Futures
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        print("✅ Binance Futures exchange initialized")
    except Exception as e:
        print(f"❌ Failed to initialize exchange: {e}")
        return False
    
    # Get current position from Binance
    try:
        print("\n🔍 Checking current positions on Binance...")
        positions = exchange.fetch_positions()
        
        dot_binance_position = None
        for pos in positions:
            if ('DOT' in pos['symbol'] or 'DOT/USDT' in pos['symbol']) and float(pos['contracts']) != 0:
                dot_binance_position = pos
                break
        
        if not dot_binance_position:
            print("❌ No open DOT position found on Binance")
            print("   Available positions:")
            for pos in positions:
                if float(pos['contracts']) != 0:
                    print(f"   - {pos['symbol']}: {pos['contracts']} contracts")
            return False
        
        print(f"✅ Found DOT position on Binance:")
        print(f"   Contracts: {dot_binance_position['contracts']}")
        print(f"   Entry Price: ${dot_binance_position['entryPrice']}")
        print(f"   Mark Price: ${dot_binance_position['markPrice']}")
        print(f"   Unrealized P&L: ${dot_binance_position['unrealizedPnl']}")
        
    except Exception as e:
        print(f"❌ Error fetching positions: {e}")
        return False
    
    # Confirm closing
    print("\n⚠️  CONFIRM CLOSING POSITION:")
    print(f"   Symbol: DOT/USDT")
    print(f"   Side: BUY (to close short)")
    print(f"   Amount: {dot_binance_position['contracts']} contracts")
    print(f"   Will lock in loss: ${dot_binance_position['unrealizedPnl']}")
    print(f"   Will free up: ~${abs(float(dot_binance_position['contracts']) * float(dot_binance_position['entryPrice'])):.2f}")
    
    # Ask for confirmation (in real scenario)
    print("\n🔴 TYPE 'YES' TO CONFIRM CLOSING: ", end="")
    confirmation = input()
    
    if confirmation != 'YES':
        print("❌ Cancelled by user")
        return False
    
    # Close position
    try:
        print("\n🚀 CLOSING POSITION...")
        
        # To close a short, we need to BUY
        order = exchange.create_order(
            symbol=dot_binance_position['symbol'],
            type='market',
            side='buy',
            amount=abs(float(dot_binance_position['contracts']))
        )
        
        print(f"✅ ORDER EXECUTED:")
        print(f"   Order ID: {order['id']}")
        print(f"   Filled: {order['filled']}")
        print(f"   Average Price: ${order['average']}")
        
        # Wait a moment and verify position is closed
        time.sleep(2)
        
        positions = exchange.fetch_positions()
        dot_after = None
        for pos in positions:
            if ('DOT' in pos['symbol'] or 'DOT/USDT' in pos['symbol']) and float(pos['contracts']) != 0:
                dot_after = pos
                break
        
        if dot_after:
            print(f"⚠️  Position still open: {dot_after['contracts']} contracts")
            return False
        else:
            print("✅ POSITION SUCCESSFULLY CLOSED")
            
            # Update our records
            update_position_records(dot_position, order['average'])
            
            # Check available balance
            balance = exchange.fetch_balance()
            free_usdt = balance['USDT']['free']
            print(f"\n💰 NEW AVAILABLE BALANCE:")
            print(f"   Free USDT: ${free_usdt:.2f}")
            print(f"   Enough for {int(free_usdt / 13.43)} new trades ($13.43 each)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error closing position: {e}")
        return False

def update_position_records(position, close_price):
    """Update our records after closing position"""
    try:
        # Update 26_crypto_trade_history.json
        with open('26_crypto_trade_history.json', 'r') as f:
            positions = json.load(f)
        
        # Find and update DOT position
        for i, pos in enumerate(positions):
            if 'DOT' in pos['symbol']:
                positions[i]['status'] = 'CLOSED'
                positions[i]['close_price'] = close_price
                positions[i]['close_time'] = datetime.now().isoformat()
                positions[i]['realized_pnl'] = position.get('unrealized_pnl', 0)
                positions[i]['notes'] = 'CLOSED to free capital for trading'
                break
        
        with open('26_crypto_trade_history.json', 'w') as f:
            json.dump(positions, f, indent=2)
        
        print("✅ Updated position records")
        
        # Update system status
        update_system_status()
        
    except Exception as e:
        print(f"⚠️  Error updating records: {e}")

def update_system_status():
    """Update system_status.json with new available balance"""
    try:
        with open('system_status.json', 'r') as f:
            status = json.load(f)
        
        # Estimate new available balance (current + freed capital)
        current_free = status['capital'].get('free_usd', 0.15)
        dot_position_value = 30.70  # From earlier calculation
        
        status['capital']['free_usd'] = current_free + dot_position_value
        status['timestamp'] = datetime.now().isoformat()
        
        # Update positions count
        status['positions']['open'] = 4  # After closing DOT
        status['positions']['closed'] = 3  # +1 closed
        
        with open('system_status.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        print("✅ Updated system status")
        
    except Exception as e:
        print(f"⚠️  Error updating system status: {e}")

def main():
    print("=" * 60)
    print("🚀 DOT POSITION CLOSING SCRIPT")
    print("=" * 60)
    
    success = close_dot_position()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 POSITION CLOSED SUCCESSFULLY!")
        print("=" * 60)
        print("Next steps:")
        print("1. ✅ ~$30.85 now available for trading")
        print("2. 🔄 Restart 26-crypto bot or wait for next cycle")
        print("3. 📈 Bot will use new parameters (3% threshold, 1x leverage)")
        print("4. 💰 Can open 2 positions at $13.43 each")
        print("\nThe bot is READY TO TRADE!")
    else:
        print("\n" + "=" * 60)
        print("❌ FAILED TO CLOSE POSITION")
        print("=" * 60)
        print("Manual closing required:")
        print("1. Go to Binance Futures")
        print("2. Find DOT/USDT in Positions")
        print("3. Click 'Close' or 'Trade'")
        print("4. Side: BUY, Type: MARKET")
        print("5. Confirm")

if __name__ == "__main__":
    main()