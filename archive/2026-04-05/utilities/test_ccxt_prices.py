#!/usr/bin/env python3
"""
Test CCXT price fetching to find the bug
"""

import ccxt
import time

def test_gemini_prices():
    print("🔍 TESTING GEMINI PRICE FETCHING")
    print("="*60)
    
    # Initialize exchange
    exchange = ccxt.gemini({
        'apiKey': '',
        'secret': '',
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    
    # Test symbols
    test_symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        
        try:
            # Method 1: Fetch ticker
            ticker = exchange.fetch_ticker(symbol)
            print(f"  Ticker last price: ${ticker['last']}")
            print(f"  Ticker info: {ticker}")
            
            # Method 2: Fetch OHLCV
            ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=1)
            if ohlcv:
                # OHLCV format: [timestamp, open, high, low, close, volume]
                print(f"  OHLCV close price: ${ohlcv[0][4]}")
                print(f"  OHLCV full: {ohlcv[0]}")
            
            # Method 3: Check if price needs conversion
            print(f"  Market info: {exchange.market(symbol)}")
            
            # Check precision
            market = exchange.market(symbol)
            print(f"  Precision: price={market['precision']['price']}, amount={market['precision']['amount']}")
            
            time.sleep(1)  # Rate limit
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*60)
    print("🔍 CHECKING FOR UNIT CONVERSION BUGS")
    
    # Common bugs:
    print("\n1. Price might be returned as string:")
    print("   ticker['last'] might be '65000.00' not 65000.0")
    
    print("\n2. Price might be in wrong units:")
    print("   Some APIs return price in SATOSHIS (1e8) for BTC")
    print("   $65,000 BTC = 65,000,000,000 satoshis (wrong!)")
    
    print("\n3. Precision might be wrong:")
    print("   Market might have precision=8 (8 decimal places)")
    print("   But price might be shown with 2 decimal places")
    
    print("\n4. CCXT might need price conversion:")
    print("   Some exchanges need manual price conversion")

def test_bug_reproduction():
    """Try to reproduce the bug"""
    print("\n" + "="*60)
    print("🔍 REPRODUCING THE BUG")
    
    # The bug: amount = position_value / current_price
    # Where position_value = $39.32
    # Wrong amounts were: BTC=34.5, SOL=49.3
    
    # Calculate what current_price would give those amounts
    position_value = 39.32
    
    wrong_btc_amount = 34.5049640925584
    wrong_sol_amount = 49.292805846512
    
    btc_price_calc = position_value / wrong_btc_amount
    sol_price_calc = position_value / wrong_sol_amount
    
    print(f"\nTo get wrong BTC amount {wrong_btc_amount}:")
    print(f"  current_price would be: ${btc_price_calc}")
    print(f"  Real BTC price: ~$65,000")
    print(f"  Ratio: {65000 / btc_price_calc:.0f}×")
    
    print(f"\nTo get wrong SOL amount {wrong_sol_amount}:")
    print(f"  current_price would be: ${sol_price_calc}")
    print(f"  Real SOL price: ~$150")
    print(f"  Ratio: {150 / sol_price_calc:.0f}×")
    
    print("\n" + "="*60)
    print("🎯 SUSPECTED BUG:")
    print(f"The price is being divided by {65000 / btc_price_calc:.0f}× for BTC")
    print(f"and by {150 / sol_price_calc:.0f}× for SOL")
    print("\nThis looks like a SATOSHI conversion bug!")
    print("1 BTC = 100,000,000 satoshis")
    print(f"57,000× is close to 100,000× (satoshi conversion)")
    print(f"188× might be another unit conversion")

if __name__ == "__main__":
    # test_gemini_prices()  # Might fail without API keys
    test_bug_reproduction()
    
    print("\n" + "="*60)
    print("🚨 RECOMMENDED FIX:")
    print("1. Check the calculate_24h_change() function")
    print("2. Add debug logging to see what price CCXT returns")
    print("3. Check if price needs conversion from satoshis")
    print("4. Add: current_price = float(current_price) to ensure it's a number")
    print("5. Add: if current_price < 10: current_price *= 10000  # Fix satoshi bug")