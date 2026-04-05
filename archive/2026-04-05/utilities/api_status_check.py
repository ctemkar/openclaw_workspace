#!/usr/bin/env python3
import requests
import json
import datetime

print('=== API & MARKET STATUS CHECK ===')
print(f'Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Check dashboard API
try:
    response = requests.get('http://localhost:57696/api/trading/progress', timeout=10)
    print(f'Dashboard API: ✅ Accessible (status: {response.json().get("status", "unknown")})')
except Exception as e:
    print(f'Dashboard API: ❌ Error: {e}')

print()

# Check if we can get market data
print('=== MARKET DATA AVAILABILITY ===')
# Try to get current BTC price from common sources
sources = [
    ('CoinGecko', 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'),
    ('CoinCap', 'https://api.coincap.io/v2/assets/bitcoin'),
    ('Binance', 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
]

for name, url in sources:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if name == 'CoinGecko':
                price = data['bitcoin']['usd']
            elif name == 'CoinCap':
                price = float(data['data']['priceUsd'])
            elif name == 'Binance':
                price = float(data['price'])
            print(f'{name}: ✅ ${price:,.2f}')
        else:
            print(f'{name}: ❌ HTTP {response.status_code}')
    except Exception as e:
        print(f'{name}: ❌ Error: {type(e).__name__}')

print()

# Check trading config
print('=== TRADING CONFIGURATION ===')
try:
    with open('trading_config.json', 'r') as f:
        config = json.load(f)
    print(f'Capital: ${config["capital"]:.2f}')
    print(f'Trade Size: ${config["trade_size_usd"]:.2f}')
    print(f'Stop Loss: {config["stop_loss_pct"]*100:.1f}%')
    print(f'Take Profit: {config["take_profit_pct"]*100:.1f}%')
except Exception as e:
    print(f'Config Error: {e}')

print()

# Check completed trades
print('=== TRADING HISTORY ===')
try:
    with open('completed_trades.json', 'r') as f:
        trades = json.load(f)
    print(f'Total Trades: {len(trades)}')
    print(f'Last Trade: {trades[0]["time"] if trades else "None"}')
    print(f'Last Action: {trades[0]["side"] if trades else "None"} {trades[0]["amount"] if trades else 0} BTC')
except Exception as e:
    print(f'Trades Error: {e}')

print()

# Recommendations
print('=== RECOMMENDATIONS ===')
print('1. API Issues: "str object has no attribute get" suggests API response parsing error')
print('2. Check: Verify API keys and endpoints for Gemini/other exchanges')
print('3. Debug: Add logging to see raw API responses')
print('4. Fallback: Implement multiple data sources for redundancy')
print('5. Error Handling: Add try-catch around API calls with retry logic')

print()
print('=== CHECK COMPLETE ===')