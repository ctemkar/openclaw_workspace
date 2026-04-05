#!/usr/bin/env python3
import json
import requests

# Current prices
btc_price = 66341
eth_price = 2025.21

# Fetch trades
trades_response = requests.get('http://localhost:5001/trades')
trades = trades_response.json()['trades']

print('TRADE ANALYSIS - Stop Loss Check')
print('=' * 50)
print(f'Current Prices: BTC=${btc_price}, ETH=${eth_price}')
print()

critical_alerts = []

for i, trade in enumerate(trades, 1):
    symbol = trade['symbol']
    entry = trade['price']
    quantity = trade['quantity']
    side = trade['side']
    
    if 'BTC' in symbol:
        current = btc_price
    else:
        current = eth_price
    
    pnl_pct = ((current - entry) / entry) * 100
    stop_loss_pct = -5  # 5% stop-loss
    
    if pnl_pct <= stop_loss_pct:
        status = '🚨 STOP-LOSS TRIGGERED'
        critical_alerts.append(f'{symbol} position at ${entry:.2f} is at {pnl_pct:.2f}% loss (stop-loss: {stop_loss_pct}%)')
    else:
        status = '✅ OK'
    
    print(f'Trade {i}: {symbol} {side}')
    print(f'  Entry: ${entry:.2f}')
    print(f'  Current: ${current:.2f}')
    print(f'  P&L: {pnl_pct:+.2f}%')
    print(f'  Stop Loss: {stop_loss_pct}%')
    print(f'  Status: {status}')
    print()

# Log critical alerts if any
if critical_alerts:
    print('=' * 50)
    print('CRITICAL ALERTS DETECTED:')
    for alert in critical_alerts:
        print(f'  ⚠️  {alert}')
    
    # Log to critical alerts file
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
        f.write(f'\n=== STOP-LOSS ALERTS ===\n')
        f.write(f'Timestamp: {timestamp}\n\n')
        for alert in critical_alerts:
            f.write(f'ALERT: {alert}\n')
        f.write(f'\nRECOMMENDED ACTIONS:\n')
        f.write('1. Verify stop-loss execution on exchange\n')
        f.write('2. Close positions manually if stop-loss not executed\n')
        f.write('3. Review trading strategy and risk parameters\n')
        f.write('4. Consider reducing position sizes\n')
        f.write('5. Monitor market conditions closely\n')
        f.write('=' * 50 + '\n')