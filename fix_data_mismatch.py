#!/usr/bin/env python3
"""
FIX DATA MISMATCH
Update trades.json to show actual positions from Gemini API
"""

import json
import os
import ccxt
from datetime import datetime

print("="*70)
print("🔄 FIXING DATA MISMATCH - UPDATING TO REALITY")
print("="*70)

def load_env():
    """Load environment variables"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars
    except:
        return {}

def get_actual_gemini_positions():
    """Get actual positions from Gemini API"""
    env = load_env()
    gemini_key = env.get('GEMINI_API_KEY')
    gemini_secret = env.get('GEMINI_API_SECRET')
    
    if not gemini_key or not gemini_secret:
        print("❌ Gemini API keys not available")
        return {}
    
    try:
        exchange = ccxt.gemini({
            'apiKey': gemini_key,
            'secret': gemini_secret,
            'enableRateLimit': True,
        })
        
        balance = exchange.fetch_balance()
        
        positions = {}
        
        # Get non-zero balances (excluding USD)
        for currency, amount in balance['free'].items():
            if amount > 0.000001 and currency != 'USD':
                # Get current price
                symbol = f"{currency}/USD"
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    
                    positions[currency] = {
                        'amount': amount,
                        'current_price': current_price,
                        'value': amount * current_price
                    }
                except:
                    positions[currency] = {
                        'amount': amount,
                        'current_price': 0,
                        'value': 0
                    }
        
        # Also get USD balance
        positions['USD'] = {
            'amount': balance['free'].get('USD', 0),
            'current_price': 1,
            'value': balance['free'].get('USD', 0)
        }
        
        return positions
        
    except Exception as e:
        print(f"❌ Error getting Gemini positions: {e}")
        return {}

def get_entry_prices_from_history(asset, actual_amount):
    """Get entry prices from backup trades for remaining amount"""
    backup_file = 'trading_data/trades_backup.json'
    
    if not os.path.exists(backup_file):
        return 0, 0  # No entry price available
    
    with open(backup_file, 'r') as f:
        trades = json.load(f)
    
    # Get all BUY trades for this asset on Gemini
    buy_trades = []
    for trade in trades:
        if (trade.get('exchange') == 'gemini' and 
            trade.get('side') == 'buy' and
            asset in trade.get('symbol', '')):
            buy_trades.append(trade)
    
    if not buy_trades:
        return 0, 0
    
    # Sort by timestamp (oldest first)
    buy_trades.sort(key=lambda x: x.get('timestamp', ''))
    
    # Calculate which trades contribute to remaining amount
    remaining = actual_amount
    total_cost = 0
    total_amount_used = 0
    
    for trade in buy_trades:
        trade_amount = trade.get('amount', 0)
        trade_price = trade.get('price', 0)
        
        if remaining <= 0:
            break
        
        if trade_amount <= remaining:
            # Use entire trade
            total_cost += trade_amount * trade_price
            total_amount_used += trade_amount
            remaining -= trade_amount
        else:
            # Use partial trade (FIFO)
            fraction = remaining / trade_amount
            total_cost += remaining * trade_price
            total_amount_used += remaining
            remaining = 0
    
    if total_amount_used > 0:
        avg_entry_price = total_cost / total_amount_used
        return avg_entry_price, total_amount_used
    else:
        return 0, 0

def main():
    # Get actual positions
    print("\n🔍 GETTING ACTUAL POSITIONS FROM GEMINI...")
    actual_positions = get_actual_gemini_positions()
    
    if not actual_positions:
        print("❌ Could not get actual positions")
        return
    
    print("\n💰 ACTUAL GEMINI POSITIONS:")
    for asset, data in actual_positions.items():
        if asset != 'USD' and data['amount'] > 0:
            print(f"  {asset}: {data['amount']:.6f} @ ${data['current_price']:.2f} = ${data['value']:.2f}")
    
    print(f"  USD cash: ${actual_positions.get('USD', {}).get('amount', 0):.2f}")
    
    # Create updated trades
    print("\n🔄 CREATING UPDATED TRADES.JSON...")
    updated_trades = []
    
    for asset, data in actual_positions.items():
        if asset != 'USD' and data['amount'] > 0:
            # Get entry price from history
            entry_price, amount_used = get_entry_prices_from_history(asset, data['amount'])
            
            if entry_price > 0:
                # Calculate P&L
                current_price = data['current_price']
                pnl = (current_price - entry_price) * data['amount']
                pnl_percent = (current_price / entry_price - 1) * 100
                
                trade = {
                    'exchange': 'gemini',
                    'symbol': f"{asset}/USD",
                    'side': 'buy',
                    'price': entry_price,
                    'amount': data['amount'],
                    'current_price': current_price,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'value': entry_price * data['amount'],
                    'timestamp': datetime.now().isoformat(),
                    'type': 'spot',
                    'note': f'Actual position from Gemini API. Entry price calculated from {amount_used:.6f} of historical buys.'
                }
                
                updated_trades.append(trade)
                
                print(f"\n📊 {asset}:")
                print(f"  Amount: {data['amount']:.6f}")
                print(f"  Entry: ${entry_price:.2f}")
                print(f"  Current: ${current_price:.2f}")
                print(f"  P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)")
    
    # Add USD cash as a "trade" for tracking
    usd_amount = actual_positions.get('USD', {}).get('amount', 0)
    if usd_amount > 0:
        updated_trades.append({
            'exchange': 'gemini',
            'symbol': 'USD/CASH',
            'side': 'cash',
            'price': 1,
            'amount': usd_amount,
            'current_price': 1,
            'pnl': 0,
            'pnl_percent': 0,
            'value': usd_amount,
            'timestamp': datetime.now().isoformat(),
            'type': 'cash',
            'note': 'Available cash for trading'
        })
        print(f"\n💰 USD cash: ${usd_amount:.2f}")
    
    # Save updated trades
    output_file = 'trading_data/trades.json'
    with open(output_file, 'w') as f:
        json.dump(updated_trades, f, indent=2)
    
    print(f"\n✅ Updated {output_file} with {len(updated_trades)} positions")
    
    # Calculate total P&L
    total_pnl = sum(t.get('pnl', 0) for t in updated_trades)
    print(f"📈 TOTAL P&L: ${total_pnl:.2f}")
    
    # Create summary
    summary = {
        'fix_timestamp': datetime.now().isoformat(),
        'previous_mismatch': {
            'eth_dashboard': 0.137152,
            'eth_actual': actual_positions.get('ETH', {}).get('amount', 0),
            'sol_dashboard': 0.460077,
            'sol_actual': actual_positions.get('SOL', {}).get('amount', 0)
        },
        'updated_positions': len(updated_trades),
        'total_pnl': total_pnl,
        'note': 'Data mismatch fixed - dashboard now shows actual positions from Gemini API'
    }
    
    summary_file = 'trading_data/data_mismatch_fix.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Fix summary saved to: {summary_file}")
    
    print("\n" + "="*70)
    print("🎯 DATA MISMATCH FIXED!")
    print("="*70)
    print("1. Dashboard now shows ACTUAL positions from Gemini API")
    print("2. P&L calculated based on actual remaining positions")
    print("3. Entry prices calculated using FIFO from historical buys")
    print("4. Cash balance included for completeness")
    print("="*70)
    
    print("\n💡 NEXT STEPS:")
    print("1. Restart dashboards to show updated data")
    print("2. Run LLM loss alerts to verify fix")
    print("3. Monitor with accurate position tracking")
    print("="*70)

if __name__ == "__main__":
    main()