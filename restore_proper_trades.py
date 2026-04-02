#!/usr/bin/env python3
"""
RESTORE PROPER TRADES WITH ENTRY PRICES AND REAL P&L
Use backup trades to restore actual entry prices and calculate real P&L
"""

import json
import os
import ccxt
from datetime import datetime

print("="*70)
print("🔄 RESTORING PROPER TRADES WITH REAL ENTRY PRICES & P&L")
print("="*70)

# Load backup trades
backup_file = 'trading_data/trades_backup.json'
with open(backup_file, 'r') as f:
    backup_trades = json.load(f)

print(f"📁 Loaded {len(backup_trades)} trades from backup")

# Load API keys for current prices
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
        return {}

env = load_env()
gemini_key = env.get('GEMINI_API_KEY')
gemini_secret = env.get('GEMINI_API_SECRET')
binance_key = env.get('BINANCE_API_KEY')
binance_secret = env.get('BINANCE_API_SECRET')

# Initialize exchanges for current prices
exchanges = {}

if gemini_key and gemini_secret:
    exchanges['gemini'] = ccxt.gemini({
        'apiKey': gemini_key,
        'secret': gemini_secret,
        'enableRateLimit': True,
    })

if binance_key and binance_secret:
    exchanges['binance'] = ccxt.binance({
        'apiKey': binance_key,
        'secret': binance_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'},
    })

print(f"✅ Connected to {len(exchanges)} exchanges for current prices")

# Process trades: update current_price and calculate real P&L
print("\n🔍 Updating trades with current prices and real P&L...")

updated_trades = []
successful_updates = 0
failed_updates = 0

for trade in backup_trades:
    try:
        exchange_name = trade.get('exchange', '')
        symbol = trade.get('symbol', '')
        
        # Skip if no exchange or symbol
        if not exchange_name or not symbol:
            updated_trades.append(trade)
            continue
        
        # Get current price
        current_price = None
        
        if exchange_name in exchanges:
            try:
                ticker = exchanges[exchange_name].fetch_ticker(symbol)
                current_price = ticker['last']
            except:
                # Try alternative symbol format
                if 'USDT' in symbol and exchange_name == 'binance':
                    # Binance futures symbol
                    alt_symbol = symbol.replace('/USDT', ':USDT')
                    try:
                        ticker = exchanges[exchange_name].fetch_ticker(alt_symbol)
                        current_price = ticker['last']
                    except:
                        pass
        
        # Update trade
        updated_trade = trade.copy()
        
        if current_price is not None:
            updated_trade['current_price'] = current_price
            
            # Calculate real P&L
            entry_price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            
            if entry_price > 0 and amount > 0:
                if trade.get('side') == 'buy':  # LONG
                    pnl = (current_price - entry_price) * amount
                    pnl_percent = (current_price / entry_price - 1) * 100
                else:  # SHORT (for Binance)
                    pnl = (entry_price - current_price) * amount
                    pnl_percent = (entry_price / current_price - 1) * 100
                
                updated_trade['pnl'] = pnl
                updated_trade['pnl_percent'] = pnl_percent
                updated_trade['value'] = entry_price * amount
                
                successful_updates += 1
            else:
                failed_updates += 1
        else:
            failed_updates += 1
        
        updated_trades.append(updated_trade)
        
    except Exception as e:
        print(f"❌ Error updating trade: {e}")
        updated_trades.append(trade)
        failed_updates += 1

# Save updated trades
output_file = 'trading_data/trades_with_real_pnl.json'
with open(output_file, 'w') as f:
    json.dump(updated_trades, f, indent=2)

print(f"\n✅ Updated {successful_updates} trades with real P&L")
print(f"⚠️  Failed to update {failed_updates} trades")
print(f"📄 Saved to: {output_file}")

# Also update the main trades.json with a subset (only open positions)
print("\n🔍 Filtering for actual open positions...")

# Based on our reality check, we only have 2 Gemini positions
gemini_positions = []
total_eth = 0
total_sol = 0

for trade in updated_trades:
    if trade.get('exchange') == 'gemini' and trade.get('side') == 'buy':
        symbol = trade.get('symbol', '')
        if 'ETH' in symbol:
            total_eth += trade.get('amount', 0)
            gemini_positions.append(trade)
        elif 'SOL' in symbol:
            total_sol += trade.get('amount', 0)
            gemini_positions.append(trade)

print(f"📊 Found {len(gemini_positions)} Gemini positions:")
print(f"  ETH: {total_eth:.6f} total")
print(f"  SOL: {total_sol:.6f} total")

# Calculate aggregated positions
aggregated_trades = []

# Aggregate ETH positions
if total_eth > 0:
    eth_trades = [t for t in gemini_positions if 'ETH' in t.get('symbol', '')]
    if eth_trades:
        # Calculate weighted average entry price
        total_value = sum(t.get('price', 0) * t.get('amount', 0) for t in eth_trades)
        avg_entry_price = total_value / total_eth
        
        # Get current price
        current_price = eth_trades[0].get('current_price', 0)
        pnl = (current_price - avg_entry_price) * total_eth
        pnl_percent = (current_price / avg_entry_price - 1) * 100
        
        aggregated_trades.append({
            'exchange': 'gemini',
            'symbol': 'ETH/USD',
            'side': 'buy',
            'price': avg_entry_price,
            'amount': total_eth,
            'current_price': current_price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'value': avg_entry_price * total_eth,
            'timestamp': datetime.now().isoformat(),
            'type': 'spot',
            'note': f'Aggregated from {len(eth_trades)} trades'
        })

# Aggregate SOL positions
if total_sol > 0:
    sol_trades = [t for t in gemini_positions if 'SOL' in t.get('symbol', '')]
    if sol_trades:
        # Calculate weighted average entry price
        total_value = sum(t.get('price', 0) * t.get('amount', 0) for t in sol_trades)
        avg_entry_price = total_value / total_sol
        
        # Get current price
        current_price = sol_trades[0].get('current_price', 0)
        pnl = (current_price - avg_entry_price) * total_sol
        pnl_percent = (current_price / avg_entry_price - 1) * 100
        
        aggregated_trades.append({
            'exchange': 'gemini',
            'symbol': 'SOL/USD',
            'side': 'buy',
            'price': avg_entry_price,
            'amount': total_sol,
            'current_price': current_price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'value': avg_entry_price * total_sol,
            'timestamp': datetime.now().isoformat(),
            'type': 'spot',
            'note': f'Aggregated from {len(sol_trades)} trades'
        })

# Update main trades.json
with open('trading_data/trades.json', 'w') as f:
    json.dump(aggregated_trades, f, indent=2)

print(f"\n✅ Updated main trades.json with {len(aggregated_trades)} aggregated positions")

# Show P&L summary
print("\n" + "="*70)
print("📊 REAL P&L SUMMARY (BASED ON ACTUAL ENTRY PRICES)")
print("="*70)

total_pnl = 0
for trade in aggregated_trades:
    symbol = trade['symbol']
    entry = trade['price']
    current = trade['current_price']
    pnl = trade['pnl']
    pnl_pct = trade['pnl_percent']
    
    print(f"\n{symbol}:")
    print(f"  Entry: ${entry:.2f}")
    print(f"  Current: ${current:.2f}")
    print(f"  P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
    
    total_pnl += pnl

print(f"\n📈 TOTAL P&L: ${total_pnl:.2f}")
print("="*70)

print("\n💡 NEXT STEPS:")
print("1. Restart dashboards to show real P&L")
print("2. Monitor with accurate profit/loss tracking")
print("3. Trading bot uses real entry prices for decisions")
print("="*70)