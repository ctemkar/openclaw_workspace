import json
from datetime import datetime

# Current market prices from CoinGecko
current_prices = {
    'BTC': 74594,
    'ETH': 2333.43,
    'SOL': 95.37
}

# Based on logs, there were 4 BTC trades at these prices
trade_prices = [74770.04, 74800.0, 74700.83, 74700.83]
current_btc_price = current_prices['BTC']

# Calculate losses
losses = []
for price in trade_prices:
    loss = (current_btc_price - price) / price * 100
    losses.append(loss)

total_investment = sum(trade_prices)
current_value = len(trade_prices) * current_btc_price
total_loss = current_value - total_investment
total_loss_pct = total_loss / total_investment * 100

print('Current Time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print(f'Market Prices: BTC=${current_btc_price:,}, ETH=${current_prices["ETH"]:,.2f}, SOL=${current_prices["SOL"]:.2f}')
print()
print('Active Trades Analysis:')
print('Number of active trades: 4 (all BTC)')
for i, (price, loss) in enumerate(zip(trade_prices, losses), 1):
    print(f'  Trade {i}: Buy ${price:,.2f}, Current ${current_btc_price:,} = {loss:.2f}% loss')
print()
print('Portfolio Summary:')
print(f'  Total Investment: ${total_investment:,.2f}')
print(f'  Current Value: ${current_value:,.2f}')
print(f'  Total Loss: ${total_loss:,.2f} ({total_loss_pct:.2f}%)')
print()
print('Risk Assessment:')
print('  Stop Loss Threshold: 1% (from config)')
print(f'  Current Loss Level: {abs(total_loss_pct):.2f}%')

stop_loss_triggered = 'YES' if any(loss < -1 for loss in losses) else 'NO'
print('  Stop Loss Triggered:', stop_loss_triggered)

take_profit_triggered = 'YES' if any(loss > 2 for loss in losses) else 'NO'
print('  Take Profit Triggered:', take_profit_triggered)
print()
print('System Status:')
print('  Trading Bot: Running (PID 2917)')
print('  Strategy Errors: Continuous "str object has no attribute get" errors')
print('  Dashboard: Not responding on port 5001')
print('  Last Trade Activity: 04:45:54 (buy order)')