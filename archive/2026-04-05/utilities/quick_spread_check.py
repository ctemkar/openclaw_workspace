import ccxt
from datetime import datetime

# Quick check of top spreads
cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'MANA']

print("Quick Spread Check - Sorted by Highest Spread")
print("=" * 60)
print(f"Time: {datetime.now().strftime('%H:%M:%S')}")

binance = ccxt.binance()
gemini = ccxt.gemini()

spreads = []

for crypto in cryptos:
    try:
        symbol = f"{crypto}/USDT"
        b_price = binance.fetch_ticker(symbol)['last']
        
        try:
            g_price = gemini.fetch_ticker(symbol)['last']
            spread = ((g_price - b_price) / b_price) * 100
            profit_100 = (spread / 100) * 100
            
            spreads.append({
                'crypto': crypto,
                'binance': b_price,
                'gemini': g_price,
                'spread': spread,
                'profit': profit_100
            })
        except:
            spreads.append({
                'crypto': crypto,
                'binance': b_price,
                'gemini': 'N/A',
                'spread': 0,
                'profit': 0
            })
    except:
        continue

# Sort by spread (highest first)
spreads.sort(key=lambda x: x['spread'], reverse=True)

print("\nTop Spreads (Highest to Lowest):")
print(f"{'Crypto':<8} {'Binance':<12} {'Gemini':<12} {'Spread %':<10} {'Profit/$100':<12}")
print("-" * 60)

for s in spreads:
    if s['gemini'] != 'N/A' and s['spread'] > 0:
        b_price = f"${s['binance']:,.4f}" if s['binance'] < 100 else f"${s['binance']:,.2f}"
        g_price = f"${s['gemini']:,.4f}" if s['gemini'] < 100 else f"${s['gemini']:,.2f}"
        spread = f"{s['spread']:.2f}%"
        profit = f"${s['profit']:.2f}"
        
        print(f"{s['crypto']:<8} {b_price:<12} {g_price:<12} {spread:<10} {profit:<12}")

# Show MANA specifically
print("\n" + "=" * 60)
print("MANA Specific (from practical profit bot):")

for s in spreads:
    if s['crypto'] == 'MANA' and s['gemini'] != 'N/A':
        print(f"Binance: ${s['binance']:.4f}")
        print(f"Gemini:  ${s['gemini']:.4f}")
        print(f"Spread:  {s['spread']:.2f}%")
        print(f"Profit per $100: ${s['profit']:.2f}")
        break

print("\n" + "=" * 60)
print("Note: This shows REAL spreads sorted from highest to lowest")
print("Arbitrage trading should focus on highest spreads first!")