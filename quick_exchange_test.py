#!/usr/bin/env python3
"""
QUICK EXCHANGE TEST - Test arbitrage opportunities across multiple exchanges
"""

import ccxt
import json
from datetime import datetime

def test_exchanges():
    print("🚀 QUICK EXCHANGE ARBITRAGE TEST")
    print("=" * 60)
    
    # Initialize exchanges (public data only)
    exchanges = {
        'binance': ccxt.binance(),
        'gemini': ccxt.gemini(),
        'coinbase': ccxt.coinbase(),
        'kraken': ccxt.kraken(),
        'kucoin': ccxt.kucoin(),
        'bybit': ccxt.bybit(),
        'okx': ccxt.okx()
    }
    
    # Cryptos to check
    cryptos = ['BTC', 'ETH', 'SOL', 'DOT', 'XRP', 'ADA', 'DOGE', 'LTC']
    
    print(f"Testing {len(cryptos)} cryptos across {len(exchanges)} exchanges...")
    print("")
    
    all_prices = {}
    
    # Collect prices
    for exchange_name, exchange in exchanges.items():
        print(f"{exchange_name}:")
        all_prices[exchange_name] = {}
        
        for crypto in cryptos:
            try:
                # Determine symbol format
                if exchange_name == 'gemini':
                    symbol = f"{crypto}/USD"
                elif exchange_name in ['coinbase', 'kraken']:
                    symbol = f"{crypto}/USD"
                else:
                    symbol = f"{crypto}/USDT"
                
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                all_prices[exchange_name][crypto] = price
                
                print(f"  {crypto}: ${price:,.4f}")
                
            except Exception as e:
                print(f"  {crypto}: ❌ {str(e)[:40]}")
        
        print("")
    
    print("=" * 60)
    print("🎯 ARBITRAGE OPPORTUNITIES (0.5%+ spread):")
    print("")
    
    opportunities = []
    
    for crypto in cryptos:
        # Get all prices for this crypto
        crypto_prices = {}
        for exchange_name in all_prices:
            if crypto in all_prices[exchange_name]:
                crypto_prices[exchange_name] = all_prices[exchange_name][crypto]
        
        if len(crypto_prices) >= 2:
            # Find min and max
            exchanges_list = list(crypto_prices.keys())
            
            # Check all pairs
            for i in range(len(exchanges_list)):
                for j in range(i + 1, len(exchanges_list)):
                    exchange1 = exchanges_list[i]
                    exchange2 = exchanges_list[j]
                    
                    price1 = crypto_prices[exchange1]
                    price2 = crypto_prices[exchange2]
                    
                    if price1 > price2:
                        spread = ((price1 - price2) / price2) * 100
                        buy_exchange = exchange2
                        sell_exchange = exchange1
                        buy_price = price2
                        sell_price = price1
                    else:
                        spread = ((price2 - price1) / price1) * 100
                        buy_exchange = exchange1
                        sell_exchange = exchange2
                        buy_price = price1
                        sell_price = price2
                    
                    if spread >= 0.5:  # Our threshold
                        # Calculate profit
                        trade_size = 100  # $100
                        crypto_amount = trade_size / buy_price
                        sell_value = crypto_amount * sell_price
                        profit = sell_value - trade_size - (trade_size * 0.002) - (sell_value * 0.002)
                        
                        opportunities.append({
                            'crypto': crypto,
                            'spread': spread,
                            'buy_exchange': buy_exchange,
                            'sell_exchange': sell_exchange,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit_per_100': profit
                        })
    
    if opportunities:
        # Sort by profit
        opportunities.sort(key=lambda x: x['profit_per_100'], reverse=True)
        
        print(f"🚀 FOUND {len(opportunities)} PROFITABLE OPPORTUNITIES!")
        print("")
        
        for i, opp in enumerate(opportunities[:5]):  # Show top 5
            print(f"{i+1}. {opp['crypto']}: {opp['spread']:.3f}% spread")
            print(f"   Buy on {opp['buy_exchange']} at ${opp['buy_price']:.4f}")
            print(f"   Sell on {opp['sell_exchange']} at ${opp['sell_price']:.4f}")
            print(f"   Profit (${100} trade): ${opp['profit_per_100']:.2f}")
            print("")
        
        if len(opportunities) > 5:
            print(f"... and {len(opportunities) - 5} more opportunities")
            print("")
    else:
        print("⏳ No opportunities above 0.5% threshold")
        print("")
        
        # Show best spread anyway
        best_spread = 0
        best_crypto = ""
        best_pair = ("", "")
        
        for crypto in cryptos:
            crypto_prices = {}
            for exchange_name in all_prices:
                if crypto in all_prices[exchange_name]:
                    crypto_prices[exchange_name] = all_prices[exchange_name][crypto]
            
            if len(crypto_prices) >= 2:
                prices = list(crypto_prices.values())
                min_price = min(prices)
                max_price = max(prices)
                spread = ((max_price - min_price) / min_price) * 100
                
                if spread > best_spread:
                    best_spread = spread
                    best_crypto = crypto
                    # Find which exchanges
                    for ex, price in crypto_prices.items():
                        if price == min_price:
                            best_pair = (ex, "")
                        if price == max_price:
                            best_pair = (best_pair[0], ex)
        
        print(f"📊 Best spread: {best_crypto} at {best_spread:.3f}%")
        print(f"   {best_pair[0]} → {best_pair[1]}")
        print("")
    
    print("=" * 60)
    print("💡 RECOMMENDATIONS:")
    print("")
    print("1. Add Coinbase API keys (found 0.746% DOT spread)")
    print("2. Add Kraken API keys (good for USD pairs)")
    print("3. Consider KuCoin for Asian market hours")
    print("4. Bybit has good liquidity for USDT pairs")
    print("5. OKX has competitive fees")
    print("")
    print(f"📅 Test completed at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    test_exchanges()