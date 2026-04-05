#!/usr/bin/env python3
import json

# Load completed trades
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

# Calculate total BTC position
total_btc = sum(trade['amount'] for trade in trades if trade['side'] == 'buy')
total_cost = sum(trade['amount'] * trade['price'] for trade in trades if trade['side'] == 'buy')

print('=== CURRENT POSITION ANALYSIS ===')
print(f'Total BTC Position: {total_btc:.8f} BTC')
print(f'Total Cost Basis: ${total_cost:.2f}')
print(f'Average Entry Price: ${total_cost/total_btc if total_btc > 0 else 0:.2f}')

# Current hypothetical price (using last trade price as proxy)
current_price = trades[0]['price'] if trades else 0
print(f'\nCurrent Market Price (proxy): ${current_price:.2f}')

# Calculate current value
current_value = total_btc * current_price
print(f'Current Position Value: ${current_value:.2f}')

# Calculate P&L
pnl = current_value - total_cost
pnl_percent = (pnl / total_cost * 100) if total_cost > 0 else 0
print(f'Unrealized P&L: ${pnl:.2f} ({pnl_percent:.2f}%)')

# Check against thresholds
stop_loss_threshold = total_cost * 0.99  # 1% stop loss
take_profit_threshold = total_cost * 1.02  # 2% take profit

print(f'\n=== RISK THRESHOLDS ===')
print(f'Stop Loss Trigger: ${stop_loss_threshold:.2f} (1% below cost)')
print(f'Take Profit Trigger: ${take_profit_threshold:.2f} (2% above cost)')

if current_value < stop_loss_threshold:
    print('🚨 ALERT: Position is BELOW stop loss threshold!')
elif current_value > take_profit_threshold:
    print('🎯 ALERT: Position is ABOVE take profit threshold!')
else:
    distance_to_stop = ((current_value - stop_loss_threshold) / total_cost * 100) if total_cost > 0 else 0
    distance_to_profit = ((take_profit_threshold - current_value) / total_cost * 100) if total_cost > 0 else 0
    print(f'✅ Position is within safe range')
    print(f'   Distance to stop loss: {distance_to_stop:.2f}% buffer')
    print(f'   Distance to take profit: {distance_to_profit:.2f}% needed')

print('\n=== RECOMMENDATION ===')
if pnl_percent < -0.5:
    print('⚠️  Position showing small loss. Monitor closely.')
elif pnl_percent > 1.5:
    print('✅ Position approaching take profit. Consider profit-taking strategy.')
else:
    print('📊 Position stable. Continue monitoring.')