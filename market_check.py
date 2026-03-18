#!/usr/bin/env python3
import json
import datetime

# Load completed trades
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

# Calculate position
total_btc = sum(trade['amount'] for trade in trades if trade['side'] == 'buy')
total_cost = sum(trade['amount'] * trade['price'] for trade in trades if trade['side'] == 'buy')
avg_price = total_cost / total_btc if total_btc > 0 else 0

print('=== MARKET ANALYSIS ===')
print(f'Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Use last trade price as current market proxy
current_price = trades[0]['price'] if trades else 0
print(f'Current Market Price (proxy): ${current_price:,.2f}')
print(f'Average Entry Price: ${avg_price:,.2f}')
print(f'Price Difference: ${current_price - avg_price:,.2f}')
print(f'Price Change %: {(current_price/avg_price - 1)*100:.4f}%')
print()

# Check different stop-loss levels
print('=== STOP-LOSS ANALYSIS ===')
stop_loss_levels = [0.0003, 0.001, 0.01, 0.02, 0.03]  # 0.03%, 0.1%, 1%, 2%, 3%

for sl_pct in stop_loss_levels:
    sl_price = avg_price * (1 - sl_pct)
    distance_pct = (current_price - sl_price) / avg_price * 100
    status = "✅ ABOVE" if current_price > sl_price else "🚨 BELOW"
    print(f'{sl_pct*100:.3f}% stop-loss (${sl_price:,.2f}): {status} {distance_pct:.4f}%')

print()

# Check take-profit levels
print('=== TAKE-PROFIT ANALYSIS ===')
tp_levels = [0.02, 0.03, 0.05, 0.10]  # 2%, 3%, 5%, 10%

for tp_pct in tp_levels:
    tp_price = avg_price * (1 + tp_pct)
    distance_pct = (tp_price - current_price) / avg_price * 100
    status = "🎯 REACHED" if current_price >= tp_price else "📈 NEEDED"
    print(f'{tp_pct*100:.1f}% take-profit (${tp_price:,.2f}): {status} {distance_pct:.4f}%')

print()

# Volatility analysis
print('=== VOLATILITY ASSESSMENT ===')
# Typical crypto volatility ranges
if abs(current_price - avg_price) / avg_price < 0.001:  # < 0.1%
    print('✅ Low volatility - Position stable')
elif abs(current_price - avg_price) / avg_price < 0.01:  # < 1%
    print('⚠️  Moderate volatility - Normal crypto movement')
elif abs(current_price - avg_price) / avg_price < 0.03:  # < 3%
    print('⚠️  High volatility - Monitor closely')
else:
    print('🚨 Extreme volatility - High risk')

print()

# Recommendations
print('=== RECOMMENDATIONS ===')
price_change = (current_price - avg_price) / avg_price * 100

if price_change < -0.5:
    print('1. Position showing loss - Consider stop-loss adjustment')
elif price_change > 1.5:
    print('1. Position approaching profit - Consider take-profit strategy')
else:
    print('1. Position stable - Continue monitoring')

print('2. For crypto trading, consider 1-2% stop-loss (not 0.03%)')
print('3. Set realistic take-profit targets (2-5% for crypto)')
print('4. Monitor market conditions for volatility changes')

print()
print('=== ANALYSIS COMPLETE ===')