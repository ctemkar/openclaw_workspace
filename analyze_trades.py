#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Current prices from CoinGecko
btc_price = 67564
eth_price = 2063.71

# Load trading history
history_path = '/Users/chetantemkar/.openclaw/workspace/app/trading_history.json'
if os.path.exists(history_path):
    with open(history_path, 'r') as f:
        history = json.load(f)
    
    print('=== STOP-LOSS & TAKE-PROFIT ANALYSIS ===')
    print(f'Current BTC Price: ${btc_price:,.2f}')
    print(f'Current ETH Price: ${eth_price:,.2f}')
    print()
    
    alerts = []
    
    # Check all open trades
    for date, trades in history['daily_trades'].items():
        for trade in trades:
            if trade.get('status') == 'OPEN':
                symbol = trade['symbol']
                entry = float(trade['entry_price'])
                stop_loss = float(trade['stop_loss'])
                take_profit = float(trade['take_profit'])
                current_price = btc_price if 'BTC' in symbol else eth_price
                
                # Calculate P&L percentage
                pnl_pct = ((current_price - entry) / entry) * 100
                
                print(f'{symbol} Trade:')
                print(f'  Entry: ${entry:,.2f}')
                print(f'  Current: ${current_price:,.2f}')
                print(f'  P&L: {pnl_pct:+.2f}%')
                print(f'  Stop-loss: ${stop_loss:,.2f} ({((stop_loss - entry)/entry*100):.1f}%)')
                print(f'  Take-profit: ${take_profit:,.2f} ({((take_profit - entry)/entry*100):.1f}%)')
                
                # Check stop-loss
                if current_price <= stop_loss:
                    alert = f'🚨 STOP-LOSS TRIGGERED for {symbol}: Current ${current_price:,.2f} <= Stop-loss ${stop_loss:,.2f}'
                    alerts.append(alert)
                    print(f'  ⚠️  STOP-LOSS TRIGGERED!')
                
                # Check take-profit
                elif current_price >= take_profit:
                    alert = f'🎯 TAKE-PROFIT TRIGGERED for {symbol}: Current ${current_price:,.2f} >= Take-profit ${take_profit:,.2f}'
                    alerts.append(alert)
                    print(f'  ✅ TAKE-PROFIT TRIGGERED!')
                
                # Check drawdown (if P&L < -3%)
                elif pnl_pct < -3:
                    alert = f'⚠️  SIGNIFICANT DRAWDOWN for {symbol}: P&L {pnl_pct:+.2f}% (below -3%)'
                    alerts.append(alert)
                    print(f'  ⚠️  Significant drawdown ({pnl_pct:+.2f}%)')
                
                else:
                    print(f'  ✅ Within normal range')
                print()
    
    if alerts:
        print('=== CRITICAL ALERTS DETECTED ===')
        for alert in alerts:
            print(alert)
    else:
        print('✅ No critical alerts detected')
else:
    print('Trading history file not found')