#!/usr/bin/env python3
"""
DEBUG Gemini Clearance - Find out why it's not working
"""

import ccxt
import json

print("🔧 DEBUGGING GEMINI CLEARANCE")
print("="*60)

try:
    # Load Gemini keys
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    print("✅ Gemini API keys loaded")
    
    # Initialize Gemini
    exchange = ccxt.gemini({
        'apiKey': GEMINI_KEY,
        'secret': GEMINI_SECRET,
        'enableRateLimit': True,
    })
    
    # Get full balance
    balance = exchange.fetch_balance()
    
    print("\n📊 FULL GEMINI BALANCE:")
    for currency, amount in balance['total'].items():
        if amount > 0.00000001:
            free = balance['free'].get(currency, 0)
            print(f"  {currency}: {amount:.8f} (Free: {free:.8f})")
    
    print("\n🔍 CHECKING TRADING PAIRS...")
    
    # Test each cryptocurrency
    test_cryptos = ['BTC', 'LTC', 'FIL', 'DOGE', 'DOT', 'FET', 'ATOM', 'PEPE', 'XRP', 'BONK']
    
    for crypto in test_cryptos:
        amount = balance['total'].get(crypto, 0)
        if amount > 0:
            print(f"\n{crypto}: {amount:.8f}")
            
            # Try different symbol formats
            symbol_formats = [
                f"{crypto}/USD",
                f"{crypto}USD",
                f"{crypto}/USDT",
                f"{crypto}USDT"
            ]
            
            for symbol in symbol_formats:
                try:
                    print(f"  Testing symbol: {symbol}")
                    
                    # Check if market exists
                    market = exchange.market(symbol)
                    print(f"    ✅ Market exists")
                    print(f"    Limits: min={market['limits']['amount']['min']:.8f}")
                    print(f"    Precision: {market['precision']['amount']}")
                    
                    # Check current price
                    ticker = exchange.fetch_ticker(symbol)
                    print(f"    Price: ${ticker['last']:.8f}")
                    
                    # Check if we have enough to trade
                    min_amount = market['limits']['amount']['min']
                    if amount >= min_amount:
                        print(f"    ✅ Amount sufficient (≥ {min_amount:.8f})")
                        
                        # Try a small test order (if amount is reasonable)
                        if amount <= 1000:  # Don't test with huge amounts
                            print(f"    Would sell {amount:.8f} {crypto}")
                            value = amount * ticker['last']
                            print(f"    Value: ${value:.2f}")
                        else:
                            print(f"    ⚠️  Large amount - manual check needed")
                    
                    else:
                        print(f"    ❌ Amount too small (min: {min_amount:.8f})")
                    
                    break  # Found working symbol
                    
                except Exception as e:
                    print(f"    ❌ {type(e).__name__}: {str(e)[:80]}")
    
    print("\n🔧 CHECKING KNOWN GEMINI PAIRS...")
    known_pairs = exchange.load_markets()
    gemini_usd_pairs = [p for p in known_pairs.keys() if '/USD' in p]
    
    print(f"Found {len(gemini_usd_pairs)} USD pairs on Gemini:")
    for pair in sorted(gemini_usd_pairs)[:20]:  # Show first 20
        print(f"  {pair}")
    
    print("\n💰 CHECKING SPECIFIC HOLDINGS...")
    
    # Check BTC specifically (should work)
    btc_amount = balance['total'].get('BTC', 0)
    if btc_amount > 0:
        print(f"\nBTC: {btc_amount:.8f}")
        try:
            btc_market = exchange.market('BTC/USD')
            btc_min = btc_market['limits']['amount']['min']
            print(f"  Min BTC trade: {btc_min:.8f}")
            print(f"  Our amount: {btc_amount:.8f}")
            
            if btc_amount >= btc_min:
                print(f"  ✅ Can trade BTC")
                
                # Get ticker
                btc_ticker = exchange.fetch_ticker('BTC/USD')
                btc_price = btc_ticker['last']
                btc_value = btc_amount * btc_price
                print(f"  BTC price: ${btc_price:.2f}")
                print(f"  BTC value: ${btc_value:.2f}")
                
                # Try a REAL test (sell 0.0001 BTC if we have enough)
                test_sell_amount = 0.0001
                if btc_amount >= test_sell_amount and test_sell_amount >= btc_min:
                    print(f"\n  🧪 TEST: Would sell {test_sell_amount:.8f} BTC")
                    print(f"     Value: ${test_sell_amount * btc_price:.2f}")
                else:
                    print(f"  ⚠️  Cannot test (need at least {btc_min:.8f} BTC)")
            else:
                print(f"  ❌ BTC amount too small (min: {btc_min:.8f})")
                
        except Exception as e:
            print(f"  ❌ BTC check failed: {e}")
    
    print("\n🎯 DIAGNOSIS:")
    
    # Common issues:
    print("\n1. MINIMUM ORDER SIZE:")
    print("   Gemini has high minimums (e.g., 0.0001 BTC = ~$6.60)")
    print("   Small amounts of altcoins may be below minimum")
    
    print("\n2. SYMBOL FORMAT:")
    print("   Gemini uses 'BTC/USD' not 'BTC/USDT'")
    print("   Some cryptos may not have USD pairs")
    
    print("\n3. MARKET HOURS:")
    print("   Gemini has trading hours (not 24/7 like Binance)")
    
    print("\n4. LIQUIDITY:")
    print("   Low-volume pairs may not execute")
    
    print("\n" + "="*60)
    print("🚀 RECOMMENDED FIX:")
    print("="*60)
    print("\nCreate a script that:")
    print("1. Checks minimum order size for each crypto")
    print("2. Only sells if amount ≥ minimum")
    print("3. Uses correct 'CRYPTO/USD' symbol format")
    print("4. Handles small amounts (aggregate or skip)")
    print("5. Logs what can/cannot be sold")
    
except Exception as e:
    print(f"❌ Debug error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Debug complete")
print("="*60)