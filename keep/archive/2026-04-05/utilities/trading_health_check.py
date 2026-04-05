#!/usr/bin/env python3
import json
import datetime

print('=== TRADING HEALTH CHECK ===')
print(f'Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Load config
with open('trading_config.json', 'r') as f:
    config = json.load(f)

print('=== CONFIGURATION ===')
print(f'Capital: ${config["capital"]:.2f}')
print(f'Trade Size: ${config["trade_size_usd"]:.2f}')
print(f'Stop Loss: {config["stop_loss_pct"]*100:.1f}%')
print(f'Take Profit: {config["take_profit_pct"]*100:.1f}%')
print()

# Load completed trades
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

print('=== TRADING PERFORMANCE ===')
print(f'Total Trades: {len(trades)}')
print(f'Buy Trades: {sum(1 for t in trades if t["side"] == "buy")}')
print(f'Sell Trades: {sum(1 for t in trades if t["side"] == "sell")}')

# Calculate metrics
total_invested = sum(t['amount'] * t['price'] for t in trades if t['side'] == 'buy')
total_btc = sum(t['amount'] for t in trades if t['side'] == 'buy')
avg_price = total_invested / total_btc if total_btc > 0 else 0

print(f'Total BTC Position: {total_btc:.8f} BTC')
print(f'Total Invested: ${total_invested:.2f}')
print(f'Average Entry: ${avg_price:.2f}')
print()

# Check against config
config_capital = config['capital']
config_trade_size = config['trade_size_usd']

print('=== CONFIGURATION COMPLIANCE ===')
if total_invested <= config_capital:
    print(f'✅ Capital usage: ${total_invested:.2f} / ${config_capital:.2f}')
else:
    print(f'⚠️  Capital overuse: ${total_invested:.2f} > ${config_capital:.2f}')

# Check individual trade sizes
trade_sizes = [t['amount'] * t['price'] for t in trades]
if trade_sizes:
    avg_trade_size = sum(trade_sizes) / len(trade_sizes)
    print(f'Average trade size: ${avg_trade_size:.2f}')
    if avg_trade_size <= config_trade_size * 1.1:  # 10% tolerance
        print(f'✅ Trade sizes within config range')
    else:
        print(f'⚠️  Trade sizes exceed config (${config_trade_size:.2f})')

print()

# Risk assessment
print('=== RISK ASSESSMENT ===')
capital_usage_pct = (total_invested / config_capital * 100) if config_capital > 0 else 0
print(f'Capital Utilization: {capital_usage_pct:.1f}%')

if capital_usage_pct < 50:
    print('✅ Low capital utilization - Room for more trades')
elif capital_usage_pct < 80:
    print('⚠️  Moderate capital utilization - Monitor closely')
else:
    print('🚨 High capital utilization - Consider reducing position')

print()

# Recommendations
print('=== RECOMMENDATIONS ===')
if capital_usage_pct < 30:
    print('1. Consider increasing trade size to utilize capital more efficiently')
elif capital_usage_pct > 70:
    print('1. Consider reducing position or increasing capital allocation')

print('2. Monitor strategy errors - investigate API response parsing')
print('3. Verify trade execution logic for "insufficient funds" errors')
print('4. Consider implementing error recovery and retry logic')

print()
print('=== HEALTH CHECK COMPLETE ===')