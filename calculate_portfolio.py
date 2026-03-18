#!/usr/bin/env python3
import json

btc_price = 74083
trades = [
    {'amount': 0.00013374340845611425, 'price': 74770.04},
    {'amount': 0.00013368983957219252, 'price': 74800.0},
    {'amount': 0.00013381716266667096, 'price': 74728.83},
    {'amount': 0.00013381716266667096, 'price': 74728.83}
]

total_btc = sum(t['amount'] for t in trades)
total_investment = sum(t['amount'] * t['price'] for t in trades)
current_value = total_btc * btc_price
pnl = current_value - total_investment
pnl_percent = (pnl / total_investment) * 100

print(f'Total BTC Holdings: {total_btc:.6f} BTC')
print(f'Total Investment: ${total_investment:.2f}')
print(f'Current Value at ${btc_price:,}: ${current_value:.2f}')
print(f'P&L: ${pnl:.2f} ({pnl_percent:.2f}%)')
print(f'Stop Loss (3%): ${total_investment * 0.97:.2f}')
print(f'Take Profit (2%): ${total_investment * 1.02:.2f}')
print(f'Critical Drawdown (5%): ${total_investment * 0.95:.2f}')

# Check alerts
stop_loss_triggered = current_value < (total_investment * 0.97)
take_profit_triggered = current_value > (total_investment * 1.02)
critical_drawdown = current_value < (total_investment * 0.95)

print(f'\nALERT STATUS:')
print(f'Stop Loss Triggered: {"YES" if stop_loss_triggered else "NO"}')
print(f'Take Profit Triggered: {"YES" if take_profit_triggered else "NO"}')
print(f'Critical Drawdown: {"YES" if critical_drawdown else "NO"}')

if stop_loss_triggered:
    print(f'🚨 STOP LOSS TRIGGERED! Current value ${current_value:.2f} is below stop loss threshold ${total_investment * 0.97:.2f}')
if take_profit_triggered:
    print(f'🎯 TAKE PROFIT TRIGGERED! Current value ${current_value:.2f} is above take profit threshold ${total_investment * 1.02:.2f}')
if critical_drawdown:
    print(f'🔥 CRITICAL DRAWDOWN! Current value ${current_value:.2f} is below critical threshold ${total_investment * 0.95:.2f}')