#!/usr/bin/env python3
"""
CLOSE BINANCE LONG POSITIONS
Close the 6 LONG positions we accidentally opened
"""

import ccxt
import os
import json
from datetime import datetime

print("="*70)
print("🛑 CLOSING BINANCE LONG POSITIONS (ACCIDENTALLY OPENED)")
print("="*70)

# Load API keys from .env
def load_env():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return {}

env = load_env()
binance_key = env.get('BINANCE_API_KEY')
binance_secret = env.get('BINANCE_API_SECRET')

if not binance_key or not binance_secret:
    print("❌ Binance API keys not found in .env")
    exit(1)

# Initialize Binance Futures
exchange = ccxt.binance({
    'apiKey': binance_key,
    'secret': binance_secret,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})

print("✅ Binance Futures exchange connected")

# Fetch current positions
try:
    print("\n🔍 Fetching current positions...")
    positions = exchange.fetch_positions()
    
    # Filter for open positions (contracts > 0)
    open_positions = [p for p in positions if abs(p['contracts']) > 0]
    
    if not open_positions:
        print("✅ No open positions found on Binance")
        exit(0)
    
    print(f"Found {len(open_positions)} open positions:")
    
    for pos in open_positions:
        symbol = pos['symbol']
        side = pos['side']
        contracts = pos['contracts']
        entry_price = pos['entryPrice']
        unrealized_pnl = pos['unrealizedPnl']
        
        print(f"\n  Symbol: {symbol}")
        print(f"  Side: {side.upper()}")
        print(f"  Contracts: {contracts}")
        print(f"  Entry: ${entry_price:.2f}")
        print(f"  Unrealized P&L: ${unrealized_pnl:.2f}")
    
    print("\n" + "="*70)
    print("⚠️  These are LONG positions (not SHORT!)")
    print("   We accidentally opened them when trying to close SHORTS")
    print("   Need to close them to stop losses")
    print("="*70)
    
    # Close all positions
    print("\n🛑 Closing all LONG positions...")
    closed = []
    failed = []
    
    for pos in open_positions:
        symbol = pos['symbol']
        contracts = abs(pos['contracts'])
        current_side = pos['side']
        
        # To close a LONG position, we need to SELL
        close_side = 'sell' if current_side == 'long' else 'buy'
        
        try:
            print(f"\n📊 Closing {symbol} {current_side.upper()}...")
            print(f"  Contracts: {contracts}")
            print(f"  Action: {close_side.upper()} to close")
            
            # Place market order to close
            order = exchange.create_order(
                symbol=symbol,
                type='market',
                side=close_side,
                amount=contracts
            )
            
            closed.append({
                'symbol': symbol,
                'original_side': current_side,
                'close_side': close_side,
                'contracts': contracts,
                'order_id': order['id'],
                'status': 'CLOSED'
            })
            
            print(f"✅ Closed: {order['id']}")
            
        except Exception as e:
            failed.append({
                'symbol': symbol,
                'error': str(e),
                'status': 'FAILED'
            })
            print(f"❌ Failed to close {symbol}: {e}")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'closed': closed,
        'failed': failed,
        'total_closed': len(closed),
        'total_failed': len(failed)
    }
    
    results_file = "trading_data/binance_closures.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    if closed:
        print(f"\n✅ Successfully closed {len(closed)} positions")
        print("💰 Risk reduced, positions closed")
    
    if failed:
        print(f"\n⚠️  Failed to close {len(failed)} positions")
        print("   May need to close manually in Binance UI")
    
    # Check new balance
    print("\n🔍 Checking new balance...")
    try:
        balance = exchange.fetch_balance()
        print(f"  Total balance: ${balance['total']['USDT']:.2f} USDT")
        print(f"  Free balance: ${balance['free']['USDT']:.2f} USDT")
    except Exception as e:
        print(f"  Balance check failed: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("💡 WHAT HAPPENED:")
print("1. We tried to 'close SHORT' by BUYING")
print("2. But there were no SHORT positions to close")
print("3. So BUY orders opened NEW LONG positions")
print("4. Now we're closing those accidental LONGs")
print("="*70)