#!/usr/bin/env python3
"""
Check what cryptos are actually available on Gemini
"""

import ccxt

def check_gemini_markets():
    print("🔍 CHECKING REAL GEMINI MARKETS")
    print("================================")
    
    try:
        # Initialize Gemini (public only)
        exchange = ccxt.gemini({
            'enableRateLimit': True,
        })
        
        # Load markets
        print("Loading Gemini markets...")
        markets = exchange.load_markets()
        
        # Get all USD pairs
        usd_pairs = [symbol for symbol in markets.keys() if symbol.endswith('/USD')]
        
        print(f"\n📊 Found {len(usd_pairs)} USD trading pairs on Gemini:")
        print("=" * 50)
        
        # Group by base currency
        cryptos = {}
        for pair in sorted(usd_pairs):
            base = pair.split('/')[0]
            if base not in cryptos:
                cryptos[base] = []
            cryptos[base].append(pair)
        
        # List all available cryptos
        available = list(cryptos.keys())
        print(f"Available cryptos ({len(available)}): {', '.join(sorted(available))}")
        
        # Check which from the bot's list are available
        bot_cryptos = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 
                      'OXT', 'MANA', 'MATIC', 'MKR', 'OMG', 'COMP', 'ENJ', 'SNX']
        
        print(f"\n🔍 Checking bot's 16 cryptos against real Gemini availability:")
        print("=" * 60)
        
        available_count = 0
        for crypto in bot_cryptos:
            is_available = crypto in available
            status = "✅ AVAILABLE" if is_available else "❌ NOT AVAILABLE"
            print(f"{crypto:6} | {status}")
            if is_available:
                available_count += 1
        
        print(f"\n📊 RESULT: Only {available_count}/16 cryptos are actually available on Gemini!")
        print(f"   Missing: {[c for c in bot_cryptos if c not in available]}")
        
        if available_count < 8:
            print("\n🚨 CRITICAL ISSUE: Bot is checking for mostly non-existent cryptos!")
            print("   This explains why no Gemini trades are happening!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_gemini_markets()
