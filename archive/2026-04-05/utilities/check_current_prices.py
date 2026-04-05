#!/usr/bin/env python3
import ccxt
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_key'), 'r') as f:
    key = f.read().strip()
with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_secret'), 'r') as f:
    secret = f.read().strip()

exchange = ccxt.gemini({
    'apiKey': key,
    'secret': secret,
    'enableRateLimit': True
})

print("🔍 CURRENT GEMINI PRICES & 24H CHANGE")
print("="*70)

cryptos = ['BTC', 'ETH', 'SOL', 'DOT', 'XRP', 'DOGE', 'LTC', 'UNI', 'LINK', 'AVAX', 'ATOM', 'FIL']

for crypto in cryptos:
    symbol = f"{crypto}/USD"
    try:
        # Get OHLCV for 24h change
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=24)
        if ohlcv and len(ohlcv) >= 24:
            open_24h = ohlcv[0][1]
            current = ohlcv[-1][4]
            
            if open_24h > 0:
                change = ((current - open_24h) / open_24h) * 100
                
                # Get current ticker for latest price
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                print(f"{crypto}:")
                print(f"  Current: ${current_price:.2f}")
                print(f"  24h ago: ${open_24h:.2f}")
                print(f"  24h change: {change:.2f}%")
                
                if change <= -1.0:
                    print(f"  🟢 BUY SIGNAL (dropped {abs(change):.1f}%)")
                else:
                    print(f"  🔴 NO BUY (change {change:.1f}%)")
                print()
                
    except Exception as e:
        print(f"{crypto}: Error - {e}")