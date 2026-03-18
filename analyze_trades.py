import json
from datetime import datetime

# Parse the trades data
trades_data = '''{"count":12,"timestamp":"2026-03-18T15:56:49.752741","trades":[{"amount":0.00013515202913877747,"model":"Gemini-Pro","price":73990.75,"side":"buy","status":"filled","time":"15:05:29"},{"amount":0.00013522648610865638,"model":"Gemini-Pro","price":73950.01,"side":"buy","status":"filled","time":"15:05:28"},{"amount":0.00013452624028485123,"model":"Gemini","price":74334.94,"side":"buy","status":"filled","time":"10:21:28"},{"amount":0.10531637037661135,"model":"LLM_Analysis_SOL_USD","price":94.952,"side":"sell","status":"filled","time":"10:21:23"},{"amount":0.00428856924752764,"model":"LLM_Analysis_ETH_USD","price":2331.78,"side":"buy","status":"filled","time":"10:21:22"},{"amount":0.0001345244667719186,"model":"LLM_Analysis_BTC_USD","price":74335.92,"side":"buy","status":"filled","time":"10:21:21"},{"amount":0.0001345750121117511,"model":"Gemini","price":74308.0,"side":"buy","status":"filled","time":"10:20:26"},{"amount":0.00013457358140268468,"model":"Gemini","price":74308.79,"side":"buy","status":"filled","time":"10:18:29"},{"amount":0.00013453038469636157,"model":"Gemini","price":74332.65,"side":"buy","status":"filled","time":"10:14:36"},{"amount":0.00013455424265000813,"model":"Gemini","price":74319.47,"side":"buy","status":"filled","time":"10:14:33"},{"price":74094.64,"quantity":0.002699,"reason":"Near support level: $73556.12 (current: $74094.64)","side":"BUY","symbol":"BTC/USD","time":"13:39:48"},{"price":2325.28,"quantity":0.086,"reason":"Near support level: $2308.08 (current: $2325.28)","side":"BUY","symbol":"ETH/USD","time":"13:39:49"}]}'''

data = json.loads(trades_data)
trades = data['trades']

print(f'Total trades: {len(trades)}')
print()

# Analyze buy trades
buy_trades = [t for t in trades if t.get('side', '').lower() == 'buy']
sell_trades = [t for t in trades if t.get('side', '').lower() == 'sell']

print(f'Buy trades: {len(buy_trades)}')
print(f'Sell trades: {len(sell_trades)}')
print()

# Check for recent trades (last hour)
current_time = datetime.now().strftime('%H:%M:%S')
print(f'Current time: {current_time}')

# Check if any trades might be at risk (assuming current prices)
# For BTC: current ~$74083, for ETH: current ~$2325
btc_buys = [t for t in buy_trades if 'BTC' in str(t.get('symbol', '')) or 'btc' in str(t.get('model', '')).lower()]
eth_buys = [t for t in buy_trades if 'ETH' in str(t.get('symbol', '')) or 'eth' in str(t.get('model', '')).lower()]

print('BTC Buy positions:')
for trade in btc_buys:
    price = trade.get('price', 0)
    stop_loss = price * 0.95  # 5% stop-loss
    take_profit = price * 1.10  # 10% take-profit
    print(f'  Price: ${price:.2f}, Stop-loss: ${stop_loss:.2f}, Take-profit: ${take_profit:.2f}')

print()
print('ETH Buy positions:')
for trade in eth_buys:
    price = trade.get('price', 0)
    stop_loss = price * 0.95  # 5% stop-loss
    take_profit = price * 1.10  # 10% take-profit
    print(f'  Price: ${price:.2f}, Stop-loss: ${stop_loss:.2f}, Take-profit: ${take_profit:.2f}')

# Check for critical conditions
print()
print('=== RISK ANALYSIS ===')
current_btc_price = 74083.87  # From summary
current_eth_price = 2325.41   # From summary

critical_alerts = []

for trade in btc_buys:
    price = trade.get('price', 0)
    stop_loss = price * 0.95
    take_profit = price * 1.10
    
    if current_btc_price <= stop_loss:
        alert = f"⚠️ CRITICAL: BTC position at ${price:.2f} has hit STOP-LOSS at ${stop_loss:.2f} (current: ${current_btc_price:.2f})"
        critical_alerts.append(alert)
        print(alert)
    elif current_btc_price >= take_profit:
        alert = f"✅ TAKE-PROFIT: BTC position at ${price:.2f} has reached TAKE-PROFIT at ${take_profit:.2f} (current: ${current_btc_price:.2f})"
        critical_alerts.append(alert)
        print(alert)
    else:
        drawdown = (price - current_btc_price) / price * 100
        if drawdown > 3:  # More than 3% drawdown
            alert = f"⚠️ WARNING: BTC position at ${price:.2f} has {drawdown:.1f}% drawdown (current: ${current_btc_price:.2f})"
            critical_alerts.append(alert)
            print(alert)

for trade in eth_buys:
    price = trade.get('price', 0)
    stop_loss = price * 0.95
    take_profit = price * 1.10
    
    if current_eth_price <= stop_loss:
        alert = f"⚠️ CRITICAL: ETH position at ${price:.2f} has hit STOP-LOSS at ${stop_loss:.2f} (current: ${current_eth_price:.2f})"
        critical_alerts.append(alert)
        print(alert)
    elif current_eth_price >= take_profit:
        alert = f"✅ TAKE-PROFIT: ETH position at ${price:.2f} has reached TAKE-PROFIT at ${take_profit:.2f} (current: ${current_eth_price:.2f})"
        critical_alerts.append(alert)
        print(alert)
    else:
        drawdown = (price - current_eth_price) / price * 100
        if drawdown > 3:  # More than 3% drawdown
            alert = f"⚠️ WARNING: ETH position at ${price:.2f} has {drawdown:.1f}% drawdown (current: ${current_eth_price:.2f})"
            critical_alerts.append(alert)
            print(alert)

print()
print(f'Total critical alerts: {len(critical_alerts)}')