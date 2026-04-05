#!/usr/bin/env python3
import ccxt
import time

exchanges = {
    'kucoin': ccxt.kucoin({'enableRateLimit': True}),
    'mexc': ccxt.mexc({'enableRateLimit': True}),
    'gateio': ccxt.gateio({'enableRateLimit': True}),
}

pairs = ['ADA/USDT', 'XRP/USDT', 'DOGE/USDT', 'SHIB/USDT']

print('🔍 ALTCOIN SPREAD CHECK (Should be 1-5% for real profit)')
print('='*60)

for pair in pairs:
    print(f'\n📊 {pair}:')
    
    prices = {}
    for name, exchange in exchanges.items():
        try:
            ticker = exchange.fetch_ticker(pair)
            prices[name] = {'bid': ticker['bid'], 'ask': ticker['ask']}
            print(f'   {name:8} Bid: ${ticker["bid"]:8.4f} Ask: ${ticker["ask"]:8.4f}')
        except Exception as e:
            print(f'   {name:8} Error: {str(e)[:40]}')
    
    if len(prices) >= 2:
        # Calculate spread
        bids = [p['bid'] for p in prices.values() if p['bid']]
        asks = [p['ask'] for p in prices.values() if p['ask']]
        
        if bids and asks:
            max_bid = max(bids)
            min_ask = min(asks)
            
            if min_ask > 0:
                spread = max_bid - min_ask
                spread_percent = (spread / min_ask) * 100
                
                print(f'   📈 Max bid: ${max_bid:.4f}')
                print(f'   📉 Min ask: ${min_ask:.4f}')
                print(f'   💰 Spread: {spread_percent:.2f}% (${spread:.4f})')
                
                if spread_percent >= 1.0:
                    print(f'   ✅ GOOD: ≥1% spread (target met)')
                    profit_100 = spread * (100 / min_ask)
                    print(f'   💵 Profit on $100: ${profit_100:.2f}')
                else:
                    print(f'   ❌ LOW: {spread_percent:.2f}% (below 1% target)')
    
    time.sleep(1)