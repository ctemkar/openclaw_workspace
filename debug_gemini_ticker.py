#!/usr/bin/env python3
import ccxt
import os
import json

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

print("🔍 DEBUG GEMINI TICKER - What data is available?")
print("="*70)

symbol = 'BTC/USD'
ticker = exchange.fetch_ticker(symbol)

print(f"\n📊 Full ticker data for {symbol}:")
print(json.dumps(ticker, indent=2))

print(f"\n🔍 Available keys:")
for key in ticker.keys():
    print(f"  {key}: {ticker[key]}")

print(f"\n🎯 Checking alternative methods...")

# Try OHLCV data (candles)
print(f"\n📈 Trying OHLCV (1-hour candles, last 24):")
try:
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=24)
    if ohlcv:
        print(f"  Got {len(ohlcv)} candles")
        # First candle (24h ago)
        open_24h = ohlcv[0][1]  # Open price
        # Last candle (now)
        close_now = ohlcv[-1][4]  # Close price
        
        if open_24h > 0:
            change_24h = ((close_now - open_24h) / open_24h) * 100
            print(f"  24h ago: ${open_24h:.2f}")
            print(f"  Now: ${close_now:.2f}")
            print(f"  24h change: {change_24h:.2f}%")
            
            if change_24h <= -1.0:
                print(f"  🟢 WOULD TRIGGER BUY (dropped {abs(change_24h):.1f}%)")
            else:
                print(f"  🔴 Would NOT trigger buy (change {change_24h:.1f}%)")
except Exception as e:
    print(f"  ❌ OHLCV error: {e}")

# Try different timeframes
print(f"\n⏰ Trying different timeframes...")
timeframes = ['5m', '15m', '1h', '4h', '1d']
for tf in timeframes:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=2)
        if len(ohlcv) >= 2:
            prev_close = ohlcv[0][4]
            current = ohlcv[1][4]
            if prev_close > 0:
                change = ((current - prev_close) / prev_close) * 100
                print(f"  {tf}: {change:.2f}% change")
    except:
        pass