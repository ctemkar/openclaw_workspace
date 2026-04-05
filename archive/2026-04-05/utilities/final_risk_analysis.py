import json
import requests
from datetime import datetime
import re

# Get current trades
response = requests.get('http://localhost:5001/trades')
trades_data = response.json()

# Get summary for current prices
summary_response = requests.get('http://localhost:5001/summary')
summary_text = summary_response.text

# Extract current prices from summary
btc_price_match = re.search(r'BTC/USD.*?Price: \$([\d\.]+)', summary_text, re.DOTALL)
eth_price_match = re.search(r'ETH/USD.*?Price: \$([\d\.]+)', summary_text, re.DOTALL)

current_prices = {}
if btc_price_match:
    current_prices['BTC/USD'] = float(btc_price_match.group(1))
else:
    current_prices['BTC/USD'] = 71231.00

if eth_price_match:
    current_prices['ETH/USD'] = float(eth_price_match.group(1))
else:
    current_prices['ETH/USD'] = 2203.23

print('=== POSITION RISK ANALYSIS ===')
print('Timestamp:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('Current Prices:')
print('  BTC/USD: $' + str(current_prices['BTC/USD']))
print('  ETH/USD: $' + str(current_prices['ETH/USD']))
print()

# Analyze positions for stop-loss conditions
stop_loss_threshold = 0.05  # 5%
take_profit_threshold = 0.10  # 10%

critical_alerts = []
take_profit_alerts = []

for trade in trades_data.get('trades', []):
    symbol = trade.get('symbol', '')
    price = trade.get('price')
    side = trade.get('side', '').lower()
    
    if not price or not symbol:
        continue
    
    if side not in ['buy', 'b']:
        continue
    
    # Determine which current price to use
    current_price = None
    symbol_name = None
    
    if 'BTC' in symbol or 'BTC' in str(trade.get('model', '')):
        current_price = current_prices['BTC/USD']
        symbol_name = 'BTC/USD'
    elif 'ETH' in symbol or 'ETH' in str(trade.get('model', '')):
        current_price = current_prices['ETH/USD']
        symbol_name = 'ETH/USD'
    else:
        continue
    
    # Calculate P&L percentage
    if current_price and price:
        pnl_pct = (current_price - price) / price * 100
        
        print('Position:', symbol_name)
        print('  Entry Price: $' + str(price))
        print('  Current Price: $' + str(current_price))
        print('  P&L: ' + str(round(pnl_pct, 1)) + '%')
        
        # Check stop-loss
        if pnl_pct <= -stop_loss_threshold * 100:
            alert_msg = f'STOP-LOSS TRIGGERED: {symbol_name} position at {pnl_pct:.1f}% loss'
            print('  ⚠️ ' + alert_msg)
            critical_alerts.append({
                'symbol': symbol_name,
                'entry_price': price,
                'current_price': current_price,
                'pnl_pct': pnl_pct,
                'alert': alert_msg
            })
        elif pnl_pct >= take_profit_threshold * 100:  # Take-profit
            alert_msg = f'TAKE-PROFIT TARGET REACHED: {symbol_name} position at {pnl_pct:.1f}% gain'
            print('  ✅ ' + alert_msg)
            take_profit_alerts.append({
                'symbol': symbol_name,
                'entry_price': price,
                'current_price': current_price,
                'pnl_pct': pnl_pct,
                'alert': alert_msg
            })
        else:
            print('  ✅ Within normal range')
        print()

print('=== SUMMARY ===')
if critical_alerts:
    print(f'⚠️ CRITICAL ALERTS DETECTED: {len(critical_alerts)}')
    for alert in critical_alerts:
        print('  - ' + alert['alert'])
        print(f'    Entry: ${alert["entry_price"]:.2f}, Current: ${alert["current_price"]:.2f}')
else:
    print('✅ No critical stop-loss conditions detected')

if take_profit_alerts:
    print(f'✅ TAKE-PROFIT ALERTS: {len(take_profit_alerts)}')
    for alert in take_profit_alerts:
        print('  - ' + alert['alert'])
        print(f'    Entry: ${alert["entry_price"]:.2f}, Current: ${alert["current_price"]:.2f}')

# Update critical alerts log if needed
if critical_alerts:
    alert_entry = f"""
--- Critical Alert Update ---
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] STOP-LOSS CONDITIONS DETECTED
"""
    for alert in critical_alerts:
        alert_entry += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {alert['alert']}\n"
        alert_entry += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] DETAILS: Entry ${alert['entry_price']:.2f}, Current ${alert['current_price']:.2f}, Loss: {alert['pnl_pct']:.1f}%\n"
        alert_entry += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ACTION REQUIRED: Review position for potential closure\n"
    
    alert_entry += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total positions at risk: {len(critical_alerts)}\n"
    alert_entry += f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Next check: 5 minutes\n"
    
    with open('./critical_alerts.log', 'a') as f:
        f.write(alert_entry)
    
    print('\n⚠️ Critical alerts logged to critical_alerts.log')
else:
    print('\n✅ No critical alerts to log')