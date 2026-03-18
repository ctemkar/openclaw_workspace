import json
import datetime
import math

# Current prices from the summary
btc_price = 71043.00
eth_price = 2190.87

# Trades from the API
trades_data = {
    'trades': [
        {'amount': 0.00428856924752764, 'price': 2331.78, 'side': 'buy', 'status': 'filled', 'time': '10:21:22'},
        {'amount': 0.0001345244667719186, 'price': 74335.92, 'side': 'buy', 'status': 'filled', 'time': '10:21:21'},
        {'amount': 0.0001345750121117511, 'price': 74308.0, 'side': 'buy', 'status': 'filled', 'time': '10:20:26'},
        {'amount': 0.00013457358140268468, 'price': 74308.79, 'side': 'buy', 'status': 'filled', 'time': '10:18:29'},
        {'amount': 0.00013453038469636157, 'price': 74332.65, 'side': 'buy', 'status': 'filled', 'time': '10:14:36'},
        {'amount': 0.00013455424265000813, 'price': 74319.47, 'side': 'buy', 'status': 'filled', 'time': '10:14:33'},
        {'price': 74094.64, 'quantity': 0.002699, 'reason': 'Near support level: $73556.12 (current: $74094.64)', 'side': 'BUY', 'symbol': 'BTC/USD', 'time': '13:39:48'},
        {'price': 2325.28, 'quantity': 0.086, 'reason': 'Near support level: $2308.08 (current: $2325.28)', 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '13:39:49'},
        {'price': 71386.0, 'quantity': 0.002802, 'reason': 'Near support level: $70896.70 (current: $71386.00)', 'side': 'BUY', 'symbol': 'BTC/USD', 'time': '00:33:00'},
        {'price': 2193.6, 'quantity': 0.0912, 'reason': 'Near support level: $2167.99 (current: $2193.60)', 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '00:33:02'}
    ]
}

# Calculate P&L for each position
btc_positions = []
eth_positions = []
total_btc_investment = 0
total_eth_investment = 0
total_btc_value = 0
total_eth_value = 0

for i, trade in enumerate(trades_data['trades']):
    if 'symbol' in trade:
        symbol = trade['symbol']
        price = trade['price']
        quantity = trade['quantity']
    else:
        # Determine symbol from price range
        price = trade['price']
        if price > 10000:  # BTC
            symbol = 'BTC/USD'
            quantity = trade['amount']
        else:  # ETH
            symbol = 'ETH/USD'
            quantity = trade['amount']
    
    current_value = quantity * (btc_price if symbol == 'BTC/USD' else eth_price)
    investment = quantity * price
    pnl_percent = ((current_value - investment) / investment) * 100
    
    position = {
        'index': i+1,
        'buy_price': price,
        'quantity': quantity,
        'current_value': current_value,
        'investment': investment,
        'pnl_percent': pnl_percent,
        'symbol': symbol
    }
    
    if symbol == 'BTC/USD':
        btc_positions.append(position)
        total_btc_investment += investment
        total_btc_value += current_value
    else:
        eth_positions.append(position)
        total_eth_investment += investment
        total_eth_value += current_value

# Calculate averages and drawdowns
btc_total_qty = sum(p['quantity'] for p in btc_positions)
eth_total_qty = sum(p['quantity'] for p in eth_positions)

btc_avg_price = total_btc_investment / btc_total_qty if btc_total_qty > 0 else 0
eth_avg_price = total_eth_investment / eth_total_qty if eth_total_qty > 0 else 0

btc_drawdown = ((btc_price - btc_avg_price) / btc_avg_price) * 100 if btc_avg_price > 0 else 0
eth_drawdown = ((eth_price - eth_avg_price) / eth_avg_price) * 100 if eth_avg_price > 0 else 0

# Portfolio weighted drawdown
total_investment = total_btc_investment + total_eth_investment
total_value = total_btc_value + total_eth_value
portfolio_drawdown = ((total_value - total_investment) / total_investment) * 100 if total_investment > 0 else 0

print('BTC Positions:')
for pos in btc_positions:
    print(f'  Position {pos["index"]}: Buy @ ${pos["buy_price"]:.2f} → Current: ${btc_price:.2f} → P&L: {pos["pnl_percent"]:.2f}%')
print()
print('ETH Positions:')
for pos in eth_positions:
    print(f'  Position {pos["index"]}: Buy @ ${pos["buy_price"]:.2f} → Current: ${eth_price:.2f} → P&L: {pos["pnl_percent"]:.2f}%')
print()
print(f'BTC Average Buy Price: ${btc_avg_price:.2f}')
print(f'BTC Current Drawdown: {btc_drawdown:.2f}%')
print(f'ETH Average Buy Price: ${eth_avg_price:.2f}')
print(f'ETH Current Drawdown: {eth_drawdown:.2f}%')
print(f'Portfolio Weighted Drawdown: {portfolio_drawdown:.2f}%')