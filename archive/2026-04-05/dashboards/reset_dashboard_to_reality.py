#!/usr/bin/env python3
"""
RESET DASHBOARD TO REALITY
Clear fictional trades and start fresh with actual positions
"""

import json
import os
from datetime import datetime

print("="*70)
print("🔄 RESETTING DASHBOARD TO SHOW REALITY")
print("="*70)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")

# Backup old trades
backup_file = os.path.join(BASE_DIR, "trading_data", "trades_backup.json")

try:
    # Read current trades
    with open(trades_file, 'r') as f:
        old_trades = json.load(f)
    
    print(f"📊 Current dashboard has {len(old_trades)} trades")
    
    # Backup
    with open(backup_file, 'w') as f:
        json.dump(old_trades, f, indent=2)
    
    print(f"📁 Backup saved to: {backup_file}")
    
    # Create new trades based on reality
    print("\n🔍 Creating new trades based on ACTUAL reality:")
    
    # Based on our checks, here's the REAL situation:
    # Gemini: $563 USD cash, tiny ETH/SOL
    # Binance: $70.15 total, $72.62 free (after closing positions)
    # No open positions on either exchange
    
    new_trades = []
    
    # Add a "system reset" trade to mark the reset
    reset_trade = {
        'exchange': 'system',
        'symbol': 'RESET',
        'side': 'reset',
        'price': 0,
        'amount': 0,
        'current_price': 0,
        'pnl': 0,
        'pnl_percent': 0,
        'timestamp': datetime.now().isoformat(),
        'note': 'Dashboard reset to reality. Old trades backed up.'
    }
    new_trades.append(reset_trade)
    
    # Add current reality
    reality_trade = {
        'exchange': 'reality',
        'symbol': 'STATUS',
        'side': 'info',
        'price': 0,
        'amount': 0,
        'current_price': 0,
        'pnl': 0,
        'pnl_percent': 0,
        'timestamp': datetime.now().isoformat(),
        'note': 'ACTUAL: Gemini $563 cash, Binance $70 balance, no open positions'
    }
    new_trades.append(reality_trade)
    
    # Write new trades
    with open(trades_file, 'w') as f:
        json.dump(new_trades, f, indent=2)
    
    print(f"✅ Dashboard reset to {len(new_trades)} trades (reality)")
    print("   Old fictional trades backed up")
    
    # Create a summary file
    summary = {
        'reset_timestamp': datetime.now().isoformat(),
        'old_trade_count': len(old_trades),
        'new_trade_count': len(new_trades),
        'reality': {
            'gemini_cash_usd': 563.08,
            'gemini_eth': 0.00235,
            'gemini_sol': 0.059865,
            'binance_total_usdt': 70.15,
            'binance_free_usdt': 72.62,
            'open_positions': 0
        },
        'backup_file': backup_file
    }
    
    summary_file = os.path.join(BASE_DIR, "trading_data", "reality_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📋 Reality summary saved to: {summary_file}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("📊 NEW REALITY:")
print("1. Gemini: $563.08 USD cash + tiny ETH/SOL")
print("2. Binance: $70.15 total, $72.62 free USDT")
print("3. NO open positions on either exchange")
print("4. Dashboard shows reality, not fiction")
print("="*70)

print("\n💡 NEXT STEPS:")
print("1. Restart dashboards to show new reality")
print("2. Start fresh with accurate trading")
print("3. Monitor with real-time dashboard (port 5014)")
print("4. Keep Gemini-only strategy running")
print("="*70)