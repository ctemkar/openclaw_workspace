#!/usr/bin/env python3
"""
INVESTIGATE POSITION MISMATCH
Why trades.json shows different amounts than actual exchange
"""

import json
import os
from datetime import datetime

print("="*70)
print("🔍 INVESTIGATING POSITION MISMATCH")
print("="*70)

# Load current trades
with open('trading_data/trades.json', 'r') as f:
    current_trades = json.load(f)

print(f"📊 Current trades.json shows {len(current_trades)} positions:")

expected_eth = 0
expected_sol = 0

for trade in current_trades:
    symbol = trade['symbol']
    amount = trade['amount']
    
    if 'ETH' in symbol:
        expected_eth = amount
        print(f"  ETH: {amount:.6f} (expected)")
    elif 'SOL' in symbol:
        expected_sol = amount
        print(f"  SOL: {amount:.6f} (expected)")

# Load backup trades to see what happened
backup_file = 'trading_data/trades_backup.json'
with open(backup_file, 'r') as f:
    backup_trades = json.load(f)

print(f"\n📁 Backup has {len(backup_trades)} historical trades")

# Analyze Gemini trades
gemini_trades = [t for t in backup_trades if t.get('exchange') == 'gemini']
gemini_buys = [t for t in gemini_trades if t.get('side') == 'buy']
gemini_sells = [t for t in gemini_trades if t.get('side') == 'sell']

print(f"\n🔵 Gemini historical trades:")
print(f"  Total: {len(gemini_trades)}")
print(f"  BUY: {len(gemini_buys)}")
print(f"  SELL: {len(gemini_sells)}")

# Calculate what SHOULD be left
total_eth_bought = sum(t.get('amount', 0) for t in gemini_buys if 'ETH' in t.get('symbol', ''))
total_eth_sold = sum(t.get('amount', 0) for t in gemini_sells if 'ETH' in t.get('symbol', ''))
eth_remaining = total_eth_bought - total_eth_sold

total_sol_bought = sum(t.get('amount', 0) for t in gemini_buys if 'SOL' in t.get('symbol', ''))
total_sol_sold = sum(t.get('amount', 0) for t in gemini_sells if 'SOL' in t.get('symbol', ''))
sol_remaining = total_sol_bought - total_sol_sold

print(f"\n📈 CALCULATED REMAINING POSITIONS:")
print(f"  ETH: Bought {total_eth_bought:.6f}, Sold {total_eth_sold:.6f}, Remaining: {eth_remaining:.6f}")
print(f"  SOL: Bought {total_sol_bought:.6f}, Sold {total_sol_sold:.6f}, Remaining: {sol_remaining:.6f}")

# Check trades_with_real_pnl.json (created earlier)
real_pnl_file = 'trading_data/trades_with_real_pnl.json'
if os.path.exists(real_pnl_file):
    with open(real_pnl_file, 'r') as f:
        real_pnl_trades = json.load(f)
    
    gemini_real = [t for t in real_pnl_trades if t.get('exchange') == 'gemini']
    print(f"\n📋 trades_with_real_pnl.json has {len(gemini_real)} Gemini trades")
    
    # Check if any are SELL
    gemini_sells_real = [t for t in gemini_real if t.get('side') == 'sell']
    if gemini_sells_real:
        print(f"  Includes {len(gemini_sells_real)} SELL trades")
        for sell in gemini_sells_real[:3]:
            print(f"    • {sell.get('symbol')}: {sell.get('amount', 0):.6f}")

print("\n" + "="*70)
print("🤔 ANALYSIS:")
print("="*70)

print(f"1. Expected (trades.json): ETH {expected_eth:.6f}, SOL {expected_sol:.6f}")
print(f"2. Calculated remaining: ETH {eth_remaining:.6f}, SOL {sol_remaining:.6f}")
print(f"3. Actual (API): ETH 0.002350, SOL 0.059865")

print("\n🚨 THE PROBLEM:")
print("When we reset the dashboard, we aggregated ALL historical BUY trades")
print("But we didn't account for SELL trades that already happened!")
print("So trades.json shows FULL positions, but most were already sold.")

print("\n💡 SOLUTION:")
print("1. Update trades.json to show ACTUAL remaining positions")
print("2. Or show NET position (bought - sold) instead of gross")
print("3. Track open vs closed positions separately")

print("\n" + "="*70)
print("📝 RECOMMENDATION:")
print("Update trades.json to show:")
print(f"  ETH: {eth_remaining:.6f} (not {expected_eth:.6f})")
print(f"  SOL: {sol_remaining:.6f} (not {expected_sol:.6f})")
print("="*70)