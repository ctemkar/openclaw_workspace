import json
import datetime

# Current prices from CoinGecko
btc_price = 70996
eth_price = 2177.62

# Parse trades from the dashboard
trades_data = '''{"count":10,"timestamp":"2026-03-19T03:32:01.048856","trades":[{"amount":0.00428856924752764,"model":"LLM_Analysis_ETH_USD","price":2331.78,"side":"buy","status":"filled","time":"10:21:22"},{"amount":0.0001345244667719186,"model":"LLM_Analysis_BTC_USD","price":74335.92,"side":"buy","status":"filled","time":"10:21:21"},{"amount":0.0001345750121117511,"model":"Gemini","price":74308.0,"side":"buy","status":"filled","time":"10:20:26"},{"amount":0.00013457358140268468,"model":"Gemini","price":74308.79,"side":"buy","status":"filled","time":"10:18:29"},{"amount":0.00013453038469636157,"model":"Gemini","price":74332.65,"side":"buy","status":"filled","time":"10:14:36"},{"amount":0.00013455424265000813,"model":"Gemini","price":74319.47,"side":"buy","status":"filled","time":"10:14:33"},{"price":74094.64,"quantity":0.002699,"reason":"Near support level: $73556.12 (current: $74094.64)","side":"BUY","symbol":"BTC/USD","time":"13:39:48"},{"price":2325.28,"quantity":0.086,"reason":"Near support level: $2308.08 (current: $2325.28)","side":"BUY","symbol":"ETH/USD","time":"13:39:49"},{"price":71386.0,"quantity":0.002802,"reason":"Near support level: $70896.70 (current: $71386.00)","side":"BUY","symbol":"BTC/USD","time":"00:33:00"},{"price":2193.6,"quantity":0.0912,"reason":"Near support level: $2167.99 (current: $2193.60)","side":"BUY","symbol":"ETH/USD","time":"00:33:02"}]}'''

trades = json.loads(trades_data)['trades']

# Calculate positions
btc_total = 0
btc_cost = 0
eth_total = 0
eth_cost = 0

for trade in trades:
    if 'symbol' in trade:
        # Old format
        if trade['symbol'] == 'BTC/USD':
            btc_total += trade['quantity']
            btc_cost += trade['quantity'] * trade['price']
        elif trade['symbol'] == 'ETH/USD':
            eth_total += trade['quantity']
            eth_cost += trade['quantity'] * trade['price']
    else:
        # New format
        if 'model' in trade:
            if 'ETH' in trade['model']:
                eth_total += trade['amount']
                eth_cost += trade['amount'] * trade['price']
            elif 'BTC' in trade['model']:
                btc_total += trade['amount']
                btc_cost += trade['amount'] * trade['price']

# Calculate averages
btc_avg = btc_cost / btc_total if btc_total > 0 else 0
eth_avg = eth_cost / eth_total if eth_total > 0 else 0

# Calculate current values
btc_value = btc_total * btc_price
eth_value = eth_total * eth_price

# Calculate P&L
btc_pl = btc_value - btc_cost
eth_pl = eth_value - eth_cost

# Calculate percentages
btc_pl_pct = (btc_pl / btc_cost * 100) if btc_cost > 0 else 0
eth_pl_pct = (eth_pl / eth_cost * 100) if eth_cost > 0 else 0

# Calculate stop-loss and take-profit levels
btc_stop = btc_avg * 0.95
btc_take = btc_avg * 1.10
eth_stop = eth_avg * 0.95
eth_take = eth_avg * 1.10

# Calculate distances to stop-loss and take-profit
btc_to_stop = ((btc_price - btc_stop) / btc_stop * 100) if btc_stop > 0 else 0
btc_to_take = ((btc_take - btc_price) / btc_price * 100) if btc_price > 0 else 0
eth_to_stop = ((eth_price - eth_stop) / eth_stop * 100) if eth_stop > 0 else 0
eth_to_take = ((eth_take - eth_price) / eth_price * 100) if eth_price > 0 else 0

# Total portfolio
total_cost = btc_cost + eth_cost
total_value = btc_value + eth_value
total_pl = total_value - total_cost
total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0

# Capital utilization
capital = 1000
deployed_capital = total_cost
available_capital = capital - deployed_capital
deployed_pct = (deployed_capital / capital * 100)

print('=== POSITION ANALYSIS ===')
print('')
print('BTC/USD POSITION:')
print(f'  Total BTC: {btc_total:.6f}')
print(f'  Average Entry: ${btc_avg:.2f}')
print(f'  Total Cost: ${btc_cost:.2f}')
print(f'  Current Price: ${btc_price}')
print(f'  Current Value: ${btc_value:.2f}')
print(f'  P&L: ${btc_pl:.2f} ({btc_pl_pct:.2f}%)')
print(f'  5% Stop-Loss: ${btc_stop:.2f}')
print(f'  10% Take-Profit: ${btc_take:.2f}')
print(f'  Distance to Stop-Loss: {btc_to_stop:.1f}%')
print(f'  Distance to Take-Profit: {btc_to_take:.1f}%')
print('')
print('ETH/USD POSITION:')
print(f'  Total ETH: {eth_total:.6f}')
print(f'  Average Entry: ${eth_avg:.2f}')
print(f'  Total Cost: ${eth_cost:.2f}')
print(f'  Current Price: ${eth_price}')
print(f'  Current Value: ${eth_value:.2f}')
print(f'  P&L: ${eth_pl:.2f} ({eth_pl_pct:.2f}%)')
print(f'  5% Stop-Loss: ${eth_stop:.2f}')
print(f'  10% Take-Profit: ${eth_take:.2f}')
print(f'  Distance to Stop-Loss: {eth_to_stop:.1f}%')
print(f'  Distance to Take-Profit: {eth_to_take:.1f}%')
print('')
print('=== PORTFOLIO SUMMARY ===')
print(f'Total Capital: ${capital:.2f}')
print(f'Deployed Capital: ${deployed_capital:.2f} ({deployed_pct:.1f}%)')
print(f'Available Capital: ${available_capital:.2f} ({100-deployed_pct:.1f}%)')
print(f'Total Portfolio Value: ${total_value:.2f}')
print(f'Total P&L: ${total_pl:.2f} ({total_pl_pct:.2f}%)')
print('')
print('=== RISK ASSESSMENT ===')
btc_risk = 'CRITICAL' if btc_to_stop < 1 else 'HIGH' if btc_to_stop < 3 else 'MODERATE' if btc_to_stop < 5 else 'LOW'
eth_risk = 'CRITICAL' if eth_to_stop < 1 else 'HIGH' if eth_to_stop < 3 else 'MODERATE' if eth_to_stop < 5 else 'LOW'
overall_risk = 'EXTREME' if min(btc_to_stop, eth_to_stop) < 1 else 'HIGH' if min(btc_to_stop, eth_to_stop) < 2 else 'MODERATE'
print(f'BTC Risk Level: {btc_risk}')
print(f'ETH Risk Level: {eth_risk}')
print(f'Overall Risk: {overall_risk}')