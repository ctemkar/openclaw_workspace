#!/usr/bin/env python3
"""
CHECK WHAT SYMBOLS GEMINI ACTUALLY HAS
"""

import ccxt

print("🔍 CHECKING GEMINI AVAILABLE SYMBOLS")
print("="*60)

gemini = ccxt.gemini({'enableRateLimit': True})

try:
    symbols = gemini.fetch_markets()
    print(f"✅ Gemini has {len(symbols)} symbols:")
    
    # Group by quote currency
    symbols_by_quote = {}
    for symbol in symbols:
        quote = symbol['quote']
        if quote not in symbols_by_quote:
            symbols_by_quote[quote] = []
        symbols_by_quote[quote].append(symbol['base'])
    
    for quote, bases in symbols_by_quote.items():
        print(f"\n📊 {quote} pairs ({len(bases)}):")
        # Sort alphabetically
        bases.sort()
        for i in range(0, len(bases), 5):
            print(f"   {', '.join(bases[i:i+5])}")
    
    # Check for specific cryptos
    print("\n🔍 LOOKING FOR SPECIFIC CRYPTOS:")
    cryptos_to_find = ['XTZ', 'YFI', 'FIL', 'DOT', 'MANA', 'ATOM', 'COMP', 'UNI', 'AVAX', 'AAVE', 'BTC', 'ETH', 'SOL']
    
    found = []
    not_found = []
    
    for crypto in cryptos_to_find:
        found_symbol = None
        for symbol in symbols:
            if symbol['base'] == crypto:
                found_symbol = f"{crypto}/{symbol['quote']}"
                break
        
        if found_symbol:
            found.append(found_symbol)
        else:
            not_found.append(crypto)
    
    print(f"✅ Found: {', '.join(found)}")
    print(f"❌ Not found: {', '.join(not_found)}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎯 CONCLUSION:")
print("If Gemini doesn't have XTZ, YFI, etc., we CAN'T arbitrage them!")
print("We can only arbitrage cryptos available on BOTH exchanges.")
print("="*60)