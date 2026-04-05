#!/usr/bin/env python3
import ccxt
import os

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

print("🔍 TESTING GEMINI TICKER DATA")
print("="*70)

symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'DOT/USD']

for symbol in symbols:
    try:
        ticker = exchange.fetch_ticker(symbol)
        print(f"\n{symbol}:")
        print(f"  Last: ${ticker['last']:.2f}")
        print(f"  Open: ${ticker['open'] if ticker['open'] else 'N/A'}")
        print(f"  Change: {ticker['percentage'] if ticker['percentage'] else 'N/A'}%")
        print(f"  High: ${ticker['high'] if ticker['high'] else 'N/A'}")
        print(f"  Low: ${ticker['low'] if ticker['low'] else 'N/A'}")
        
        # Check if percentage is None
        if ticker['percentage'] is None:
            print(f"  ⚠️  PERCENTAGE IS NONE - This could be the bug!")
            if ticker['open'] and ticker['open'] > 0:
                calculated = ((ticker['last'] - ticker['open']) / ticker['open']) * 100
                print(f"  📊 Calculated change: {calculated:.2f}%")
                
                # Check if this would trigger a trade
                if calculated <= -1.0:
                    print(f"  🟢 WOULD TRIGGER BUY (dropped {abs(calculated):.1f}%)")
                else:
                    print(f"  🔴 Would NOT trigger buy (change {calculated:.1f}%)")
        else:
            if ticker['percentage'] <= -1.0:
                print(f"  🟢 WOULD TRIGGER BUY (dropped {abs(ticker['percentage']):.1f}%)")
            else:
                print(f"  🔴 Would NOT trigger buy (change {ticker['percentage']:.1f}%)")
                
    except Exception as e:
        print(f"❌ Error with {symbol}: {e}")