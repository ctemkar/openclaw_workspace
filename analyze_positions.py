import json
import math
from datetime import datetime

# Current prices
btc_price = 70463
eth_price = 2185.71

# Parse trades from the system
trades_data = '''{"count":10,"timestamp":"2026-03-19T17:20:10.337866","trades":[{"amount":0.00428856924752764,"model":"LLM_Analysis_ETH_USD","price":2331.78,"side":"buy","status":"filled","time":"10:21:22"},{"amount":0.0001345244667719186,"model":"LLM_Analysis_BTC_USD","price":74335.92,"side":"buy","status":"filled","time":"10:21:21"},{"amount":0.0001345750121117511,"model":"Gemini","price":74308.0,"side":"buy","status":"filled","time":"10:20:26"},{"amount":0.00013457358140268468,"model":"Gemini","price":74308.79,"side":"buy","status":"filled","time":"10:18:29"},{"amount":0.00013453038469636157,"model":"Gemini","price":74332.65,"side":"buy","status":"filled","time":"10:14:36"},{"amount":0.00013455424265000813,"model":"Gemini","price":74319.47,"side":"buy","status":"filled","time":"10:14:33"},{"price":74094.64,"quantity":0.002699,"reason":"Near support level: $73556.12 (current: $74094.64)","side":"BUY","symbol":"BTC/USD","time":"13:39:48"},{"price":2325.28,"quantity":0.086,"reason":"Near support level: $2308.08 (current: $2325.28)","side":"BUY","symbol":"ETH/USD","time":"13:39:49"},{"price":71386.0,"quantity":0.002802,"reason":"Near support level: $70896.70 (current: $71386.00)","side":"BUY","symbol":"BTC/USD","time":"00:33:00"},{"price":2193.6,"quantity":0.0912,"reason":"Near support level: $2167.99 (current: $2193.60)","side":"BUY","symbol":"ETH/USD","time":"00:33:02"}]}'''

data = json.loads(trades_data)
trades = data['trades']

# Filter for most recent buy trades (assuming they're open positions)
btc_trades = []
eth_trades = []

for trade in trades:
    if 'symbol' in trade:
        if trade['symbol'] == 'BTC/USD' and trade['side'].upper() == 'BUY':
            btc_trades.append(trade)
        elif trade['symbol'] == 'ETH/USD' and trade['side'].upper() == 'BUY':
            eth_trades.append(trade)
    elif 'side' in trade and trade['side'] == 'buy':
        # New format trades
        if 'model' in trade and 'BTC' in trade['model']:
            btc_trades.append(trade)
        elif 'model' in trade and 'ETH' in trade['model']:
            eth_trades.append(trade)

print('BTC Trades:', len(btc_trades))
print('ETH Trades:', len(eth_trades))

# Calculate weighted average prices and total quantities
def calculate_position(trades, current_price, symbol):
    if not trades:
        return None
    
    total_quantity = 0
    total_cost = 0
    
    for trade in trades:
        if 'quantity' in trade:
            qty = trade['quantity']
            price = trade['price']
        elif 'amount' in trade:
            qty = trade['amount']
            price = trade['price']
        else:
            continue
            
        total_quantity += qty
        total_cost += qty * price
    
    if total_quantity == 0:
        return None
    
    avg_price = total_cost / total_quantity
    current_value = total_quantity * current_price
    pnl_percent = ((current_price - avg_price) / avg_price) * 100
    pnl_dollar = current_value - total_cost
    
    return {
        'symbol': symbol,
        'quantity': total_quantity,
        'avg_price': avg_price,
        'current_price': current_price,
        'pnl_percent': pnl_percent,
        'pnl_dollar': pnl_dollar,
        'current_value': current_value,
        'cost_basis': total_cost
    }

btc_pos = calculate_position(btc_trades, btc_price, 'BTC/USD')
eth_pos = calculate_position(eth_trades, eth_price, 'ETH/USD')

print('\n=== POSITION ANALYSIS ===')
if btc_pos:
    print(f"BTC Position:")
    print(f"  Quantity: {btc_pos['quantity']:.6f} BTC")
    print(f"  Avg Price: ${btc_pos['avg_price']:.2f}")
    print(f"  Current: ${btc_pos['current_price']:.2f}")
    print(f"  P&L: {btc_pos['pnl_percent']:.2f}% (${btc_pos['pnl_dollar']:.2f})")
    status = 'STOP-LOSS' if btc_pos['pnl_percent'] <= -5 else 'APPROACHING STOP-LOSS' if btc_pos['pnl_percent'] <= -4 else 'OK'
    print(f"  Status: {status}")

if eth_pos:
    print(f"\nETH Position:")
    print(f"  Quantity: {eth_pos['quantity']:.6f} ETH")
    print(f"  Avg Price: ${eth_pos['avg_price']:.2f}")
    print(f"  Current: ${eth_pos['current_price']:.2f}")
    print(f"  P&L: {eth_pos['pnl_percent']:.2f}% (${eth_pos['pnl_dollar']:.2f})")
    status = 'STOP-LOSS' if eth_pos['pnl_percent'] <= -5 else 'APPROACHING STOP-LOSS' if eth_pos['pnl_percent'] <= -4 else 'OK'
    print(f"  Status: {status}")

# Check for critical alerts
print('\n=== RISK ASSESSMENT ===')
critical_alerts = []
if btc_pos and btc_pos['pnl_percent'] <= -5:
    critical_alerts.append(f"BTC position at {btc_pos['pnl_percent']:.2f}% loss exceeds 5% stop-loss threshold")
elif btc_pos and btc_pos['pnl_percent'] <= -4:
    print(f"⚠️ BTC position approaching stop-loss: {btc_pos['pnl_percent']:.2f}% loss")

if eth_pos and eth_pos['pnl_percent'] <= -5:
    critical_alerts.append(f"ETH position at {eth_pos['pnl_percent']:.2f}% loss exceeds 5% stop-loss threshold")
elif eth_pos and eth_pos['pnl_percent'] <= -4:
    print(f"⚠️ ETH position approaching stop-loss: {eth_pos['pnl_percent']:.2f}% loss")

if critical_alerts:
    print('\n🚨 CRITICAL ALERTS:')
    for alert in critical_alerts:
        print(f"  • {alert}")
else:
    print('No critical alerts at this time.')