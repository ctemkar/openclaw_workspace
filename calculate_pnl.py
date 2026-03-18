#!/usr/bin/env python3
import json
import datetime

# Current prices from summary
btc_price = 71333.47
eth_price = 2202.61

# Trades data from /trades endpoint
trades = [
    {'symbol': 'BTC/USD', 'price': 74094.64, 'quantity': 0.002699, 'side': 'BUY'},
    {'symbol': 'BTC/USD', 'price': 71386.0, 'quantity': 0.002802, 'side': 'BUY'},
    {'symbol': 'ETH/USD', 'price': 2325.28, 'quantity': 0.086, 'side': 'BUY'},
    {'symbol': 'ETH/USD', 'price': 2193.6, 'quantity': 0.0912, 'side': 'BUY'}
]

# Calculate P&L
total_investment = 0
current_value = 0
alerts = []

for i, trade in enumerate(trades, 1):
    investment = trade['price'] * trade['quantity']
    total_investment += investment
    
    if trade['symbol'] == 'BTC/USD':
        current_val = btc_price * trade['quantity']
    else:
        current_val = eth_price * trade['quantity']
    
    current_value += current_val
    
    pnl_percent = ((current_val - investment) / investment) * 100
    pnl_amount = current_val - investment
    
    print(f'Trade {i} ({trade["symbol"]}):')
    print(f'  Entry: ${trade["price"]:.2f}, Qty: {trade["quantity"]}')
    print(f'  Current: ${current_val:.2f}, P&L: {pnl_percent:.2f}% (${pnl_amount:.2f})')
    
    # Check for stop-loss (5%)
    if pnl_percent <= -5:
        alerts.append({
            'type': 'STOP-LOSS_TRIGGERED',
            'asset': trade['symbol'],
            'trade_num': i,
            'loss_percent': pnl_percent,
            'loss_amount': pnl_amount,
            'entry_price': trade['price'],
            'current_price': btc_price if trade['symbol'] == 'BTC/USD' else eth_price
        })
    
    # Check for take-profit (10%)
    if pnl_percent >= 10:
        alerts.append({
            'type': 'TAKE-PROFIT_TRIGGERED',
            'asset': trade['symbol'],
            'trade_num': i,
            'gain_percent': pnl_percent,
            'gain_amount': pnl_amount,
            'entry_price': trade['price'],
            'current_price': btc_price if trade['symbol'] == 'BTC/USD' else eth_price
        })

print(f'\nPortfolio Summary:')
print(f'Total Investment: ${total_investment:.2f}')
print(f'Current Value: ${current_value:.2f}')
portfolio_pnl_percent = ((current_value - total_investment) / total_investment) * 100
portfolio_pnl_amount = current_value - total_investment
print(f'Total P&L: {portfolio_pnl_percent:.2f}% (${portfolio_pnl_amount:.2f})')

# Check portfolio drawdown
if portfolio_pnl_percent <= -5:
    alerts.append({
        'type': 'CRITICAL_DRAWDOWN',
        'portfolio_loss_percent': portfolio_pnl_percent,
        'portfolio_loss_amount': portfolio_pnl_amount,
        'threshold': -5
    })

print(f'\nAlerts: {len(alerts)}')
for alert in alerts:
    print(f'  {alert["type"]}: {alert.get("asset", "Portfolio")}')

# Return alerts for logging
print('\n=== ALERTS JSON ===')
print(json.dumps(alerts, indent=2))