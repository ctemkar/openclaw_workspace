#!/usr/bin/env python3
"""
Update dashboard data files with REAL current data from exchanges
"""

import os
import json
import ccxt
from datetime import datetime
import time

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
TRADING_DATA_DIR = os.path.join(BASE_DIR, "trading_data")

print("🔄 UPDATING DASHBOARD DATA WITH REAL VALUES")
print("="*60)

# Read API keys
def read_api_key(filename):
    try:
        with open(os.path.join(BASE_DIR, 'secure_keys', filename), 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

# Initialize exchanges
gemini_key = read_api_key('.gemini_key')
gemini_secret = read_api_key('.gemini_secret')
binance_key = read_api_key('.binance_key')
binance_secret = read_api_key('.binance_secret')

if not all([gemini_key, gemini_secret, binance_key, binance_secret]):
    print("❌ Missing API keys")
    exit(1)

# Initialize Gemini
gemini = ccxt.gemini({
    'apiKey': gemini_key,
    'secret': gemini_secret,
    'enableRateLimit': True,
})

# Initialize Binance Futures
binance = ccxt.binance({
    'apiKey': binance_key,
    'secret': binance_secret,
    'options': {
        'defaultType': 'future',
    },
    'enableRateLimit': True,
})

print("✅ Connected to exchanges")

# Get REAL balances
print("\n💰 FETCHING REAL BALANCES")
print("-" * 40)

try:
    # Gemini balance
    gemini_balance = gemini.fetch_balance()
    gemini_total = float(gemini_balance['total']['USD'])
    gemini_free = float(gemini_balance['free']['USD'])
    
    print(f"Gemini:")
    print(f"  Total USD: ${gemini_total:.2f}")
    print(f"  Free USD: ${gemini_free:.2f}")
    
    # Binance balance
    binance_balance = binance.fetch_balance()
    binance_total = float(binance_balance['total']['USDT'])
    binance_free = float(binance_balance['free']['USDT'])
    
    print(f"Binance:")
    print(f"  Total USDT: ${binance_total:.2f}")
    print(f"  Free USDT: ${binance_free:.2f}")
    
    # Get open positions
    binance_positions = binance.fetch_positions()
    open_positions = [p for p in binance_positions if float(p['contracts']) > 0]
    
    print(f"\n📊 Open Positions: {len(open_positions)}")
    position_count = 0
    total_position_value = 0
    
    for pos in open_positions:
        contracts = float(pos['contracts'])
        entry_price = float(pos['entryPrice'])
        mark_price = float(pos['markPrice'])
        position_value = abs(contracts) * mark_price
        
        print(f"  {pos['symbol']}: {contracts} contracts")
        print(f"    Value: ${position_value:.2f}, P&L: ${pos['unrealizedPnl']}")
        
        position_count += 1
        total_position_value += position_value
    
    # Update capital.json
    capital_data = {
        "gemini_total": gemini_total,
        "binance_total": binance_total,
        "total_capital": gemini_total + binance_total,
        "deployed": total_position_value,
        "available_gemini": gemini_free,
        "available_binance": binance_free,
        "position_count": position_count,
        "avg_position_value": total_position_value / max(position_count, 1),
        "last_updated": datetime.now().isoformat()
    }
    
    # Create trading_data directory if it doesn't exist
    os.makedirs(TRADING_DATA_DIR, exist_ok=True)
    
    # Write capital.json
    capital_file = os.path.join(TRADING_DATA_DIR, "capital.json")
    with open(capital_file, 'w') as f:
        json.dump(capital_data, f, indent=2)
    
    print(f"\n✅ Updated {capital_file}")
    print(f"   Total capital: ${capital_data['total_capital']:.2f}")
    print(f"   Deployed: ${capital_data['deployed']:.2f}")
    print(f"   Positions: {capital_data['position_count']}")
    
    # Update bot_status.json
    bot_status = {
        "status": "running",
        "last_cycle": datetime.now().isoformat(),
        "cycle_interval": 300,
        "position_size_percent": 5,
        "mode": "aggressive",
        "exchanges": {
            "gemini": "operational",
            "binance": "operational"
        },
        "last_updated": datetime.now().isoformat()
    }
    
    status_file = os.path.join(TRADING_DATA_DIR, "bot_status.json")
    with open(status_file, 'w') as f:
        json.dump(bot_status, f, indent=2)
    
    print(f"✅ Updated {status_file}")
    
    # Read trade history and update trades.json
    try:
        history_file = os.path.join(BASE_DIR, "26_crypto_trade_history.json")
        with open(history_file, 'r') as f:
            trade_history = json.load(f)
        
        # Convert to dashboard format
        dashboard_trades = []
        for trade in trade_history[-10:]:  # Last 10 trades
            dashboard_trade = {
                "exchange": trade.get('exchange', 'unknown'),
                "symbol": trade.get('symbol', 'unknown'),
                "side": trade.get('side', 'unknown'),
                "price": trade.get('current_price', 0),
                "amount": trade.get('amount', 0),
                "value": trade.get('position_value', 0),
                "order_id": trade.get('order_id', 'unknown'),
                "timestamp": trade.get('execution_time', datetime.now().isoformat())
            }
            dashboard_trades.append(dashboard_trade)
        
        trades_file = os.path.join(TRADING_DATA_DIR, "trades.json")
        with open(trades_file, 'w') as f:
            json.dump(dashboard_trades, f, indent=2)
        
        print(f"✅ Updated {trades_file} with {len(dashboard_trades)} recent trades")
        
    except FileNotFoundError:
        print(f"⚠️ No trade history file found")
    
    print("\n" + "="*60)
    print("✅ DASHBOARD DATA UPDATED WITH REAL VALUES!")
    print("="*60)
    print(f"\n📊 Current Reality:")
    print(f"   Total Capital: ${capital_data['total_capital']:.2f}")
    print(f"   Gemini: ${gemini_total:.2f} (${gemini_free:.2f} free)")
    print(f"   Binance: ${binance_total:.2f} (${binance_free:.2f} free)")
    print(f"   Open Positions: {position_count}")
    print(f"   Deployed Capital: ${total_position_value:.2f}")
    
except Exception as e:
    print(f"❌ Error updating dashboard data: {e}")
    import traceback
    traceback.print_exc()