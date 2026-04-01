import requests
import json
import time
from datetime import datetime

def get_gemini_price():
    try:
        url = 'https://api.gemini.com/v1/pubticker/solusd'
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['last'])
    except:
        return None

def get_binance_price():
    try:
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT'
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return None

gemini_price = get_gemini_price()
binance_price = get_binance_price()

print('Current Time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
if gemini_price:
    print('SOL/USD (Gemini): ${:.3f}'.format(gemini_price))
else:
    print('SOL/USD (Gemini): N/A')
    
if binance_price:
    print('SOL/USDT (Binance): ${:.3f}'.format(binance_price))
else:
    print('SOL/USDT (Binance): N/A')

# Calculate P&L for positions
positions = [
    {'amount': 0.646635, 'entry': 82.22},
    {'amount': 0.645206, 'entry': 82.40},
    {'amount': 0.645731, 'entry': 82.33},
    {'amount': 0.645034, 'entry': 82.42},
    {'amount': 0.644956, 'entry': 82.43}
]

if gemini_price:
    total_value = 0
    total_entry = 0
    for pos in positions:
        pos_value = pos['amount'] * gemini_price
        entry_value = pos['amount'] * pos['entry']
        total_value += pos_value
        total_entry += entry_value
    
    pnl = total_value - total_entry
    pnl_percent = (pnl / total_entry) * 100
    
    print('\n=== SOL POSITIONS P&L ===')
    print('Total Position Value: ${:.2f}'.format(total_value))
    print('Total Entry Value: ${:.2f}'.format(total_entry))
    print('Unrealized P&L: ${:.2f} ({:.2f}%)'.format(pnl, pnl_percent))
    
    # Check stop-loss and take-profit
    avg_entry = total_entry / sum(pos['amount'] for pos in positions)
    stop_loss = avg_entry * 0.97  # 3% stop-loss
    take_profit = avg_entry * 1.05  # 5% take-profit
    
    print('\n=== TRIGGER LEVELS ===')
    print('Average Entry Price: ${:.2f}'.format(avg_entry))
    print('Stop-Loss Trigger: < ${:.2f} (3% loss)'.format(stop_loss))
    print('Take-Profit Trigger: > ${:.2f} (5% gain)'.format(take_profit))
    
    if gemini_price < stop_loss:
        print('🔴 STOP-LOSS TRIGGERED! Current price ${:.3f} < ${:.2f}'.format(gemini_price, stop_loss))
    elif gemini_price > take_profit:
        print('🟢 TAKE-PROFIT TRIGGERED! Current price ${:.3f} > ${:.2f}'.format(gemini_price, take_profit))
    else:
        print('🟡 NO TRIGGERS - Price within range: ${:.2f} < ${:.3f} < ${:.2f}'.format(stop_loss, gemini_price, take_profit))
else:
    print('\n⚠️  Cannot calculate P&L - Gemini price unavailable')