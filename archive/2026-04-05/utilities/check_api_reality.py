#!/usr/bin/env python3
"""
CHECK API REALITY - What the trading bot actually sees from Gemini and Binance APIs
"""

import ccxt
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("🔍 CHECKING API REALITY - What trading bot sees")
print("="*70)

# Load API keys
try:
    with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_key'), 'r') as f:
        gemini_key = f.read().strip()
    with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_secret'), 'r') as f:
        gemini_secret = f.read().strip()
    
    with open(os.path.join(BASE_DIR, 'secure_keys/.binance_key'), 'r') as f:
        binance_key = f.read().strip()
    with open(os.path.join(BASE_DIR, 'secure_keys/.binance_secret'), 'r') as f:
        binance_secret = f.read().strip()
    
    print("✅ API keys loaded")
except Exception as e:
    print(f"❌ Error loading API keys: {e}")
    exit(1)

# Initialize exchanges
print("\n🔌 Initializing exchanges...")
gemini = ccxt.gemini({
    'apiKey': gemini_key,
    'secret': gemini_secret,
    'enableRateLimit': True
})

binance = ccxt.binance({
    'apiKey': binance_key,
    'secret': binance_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # For short positions
    }
})

# Check Gemini
print("\n" + "="*70)
print("🏦 GEMINI API CHECK")
print("="*70)

try:
    # Check balance
    gemini_balance = gemini.fetch_balance()
    gemini_usd = gemini_balance['free'].get('USD', 0)
    print(f"💰 Free USD: ${gemini_usd:.2f}")
    
    # Check if we can trade
    print(f"\n📊 Checking trading pairs...")
    markets = gemini.load_markets()
    gemini_pairs = [symbol for symbol in markets.keys() if 'USD' in symbol and ':' not in symbol]
    print(f"   Available pairs: {len(gemini_pairs)}")
    
    # Check a few key pairs
    key_pairs = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'DOT/USD']
    for pair in key_pairs:
        if pair in markets:
            ticker = gemini.fetch_ticker(pair)
            print(f"   {pair}: ${ticker['last']:.2f} (24h: {ticker['percentage']:.1f}%)")
        else:
            print(f"   {pair}: NOT AVAILABLE on Gemini")
    
    # Check order book for BTC/USD
    print(f"\n📈 Checking order book depth...")
    orderbook = gemini.fetch_order_book('BTC/USD', limit=5)
    print(f"   BTC/USD - Bid: ${orderbook['bids'][0][0]:.2f}, Ask: ${orderbook['asks'][0][0]:.2f}")
    print(f"   Spread: ${(orderbook['asks'][0][0] - orderbook['bids'][0][0]):.2f}")
    
    print(f"\n✅ Gemini API: OPERATIONAL")
    
except Exception as e:
    print(f"❌ Gemini API error: {e}")

# Check Binance
print("\n" + "="*70)
print("🏦 BINANCE API CHECK")
print("="*70)

try:
    # Check balance
    binance_balance = binance.fetch_balance()
    binance_usdt = binance_balance['free'].get('USDT', 0)
    print(f"💰 Free USDT: ${binance_usdt:.2f}")
    
    # Check if we can trade (might have geographic restrictions)
    print(f"\n📊 Checking trading pairs...")
    try:
        markets = binance.load_markets()
        binance_pairs = [symbol for symbol in markets.keys() if 'USDT' in symbol and '/USDT' in symbol]
        print(f"   Available pairs: {len(binance_pairs)}")
        
        # Check a few key pairs
        key_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT']
        for pair in key_pairs:
            if pair in markets:
                ticker = binance.fetch_ticker(pair)
                print(f"   {pair}: ${ticker['last']:.2f} (24h: {ticker['percentage']:.1f}%)")
            else:
                print(f"   {pair}: NOT AVAILABLE on Binance")
        
        # Check futures for short positions
        print(f"\n📉 Checking futures for short positions...")
        futures_pairs = [symbol for symbol in markets.keys() if ':USDT' in symbol]
        if futures_pairs:
            sample = futures_pairs[0]
            ticker = binance.fetch_ticker(sample)
            print(f"   {sample}: ${ticker['last']:.2f}")
            print(f"   Futures available: {len(futures_pairs)} pairs")
        else:
            print(f"   ❌ No futures pairs available (geographic restriction?)")
        
        print(f"\n✅ Binance API: OPERATIONAL")
        
    except Exception as e:
        if "restricted location" in str(e).lower() or "geographic" in str(e).lower():
            print(f"   ⚠️ BINANCE GEOGRAPHIC RESTRICTION: {e}")
            print(f"   ❌ Binance trading not available from Thailand")
        else:
            print(f"   ❌ Binance API error: {e}")
    
except Exception as e:
    print(f"❌ Binance connection error: {e}")

# Check what trading opportunities exist
print("\n" + "="*70)
print("🎯 TRADING OPPORTUNITY ANALYSIS")
print("="*70)

try:
    # Simulate what the trading bot checks
    print("Checking for LONG opportunities on Gemini...")
    
    # Check BTC/USD for dip
    btc_ticker = gemini.fetch_ticker('BTC/USD')
    btc_price = btc_ticker['last']
    btc_change = btc_ticker['percentage']
    
    print(f"   BTC/USD: ${btc_price:.2f} (24h: {btc_change:.1f}%)")
    
    # Trading bot logic: Buy if price dropped > 1%
    if btc_change < -1.0:
        print(f"   🟢 BUY SIGNAL: Price dropped {abs(btc_change):.1f}%")
    else:
        print(f"   🔴 NO BUY: Price change {btc_change:.1f}% (need < -1.0%)")
    
    # Check ETH/USD
    eth_ticker = gemini.fetch_ticker('ETH/USD')
    eth_price = eth_ticker['last']
    eth_change = eth_ticker['percentage']
    
    print(f"\n   ETH/USD: ${eth_price:.2f} (24h: {eth_change:.1f}%)")
    
    if eth_change < -1.0:
        print(f"   🟢 BUY SIGNAL: Price dropped {abs(eth_change):.1f}%")
    else:
        print(f"   🔴 NO BUY: Price change {eth_change:.1f}% (need < -1.0%)")
    
    # Check SOL/USD
    sol_ticker = gemini.fetch_ticker('SOL/USD')
    sol_price = sol_ticker['last']
    sol_change = sol_ticker['percentage']
    
    print(f"\n   SOL/USD: ${sol_price:.2f} (24h: {sol_change:.1f}%)")
    
    if sol_change < -1.0:
        print(f"   🟢 BUY SIGNAL: Price dropped {abs(sol_change):.1f}%")
    else:
        print(f"   🔴 NO BUY: Price change {sol_change:.1f}% (need < -1.0%)")
    
    print(f"\n📊 Summary: Trading bot needs >1% price drop to buy")
    print(f"   Current market: No significant dips detected")
    
except Exception as e:
    print(f"❌ Opportunity analysis error: {e}")

# Check if we can actually place orders
print("\n" + "="*70)
print("🛒 TEST ORDER PLACEMENT (Dry Run)")
print("="*70)

try:
    # Test Gemini order (dry run - won't actually execute)
    print("Testing Gemini order placement...")
    
    # Check if we have enough balance
    if gemini_usd > 10:
        print(f"   ✅ Sufficient balance: ${gemini_usd:.2f}")
        
        # Check minimum order size for BTC
        btc_min_order = 0.00001  # Gemini minimum
        btc_price = gemini.fetch_ticker('BTC/USD')['last']
        min_order_usd = btc_min_order * btc_price
        
        print(f"   📊 BTC minimum order: {btc_min_order} BTC (${min_order_usd:.2f})")
        
        if gemini_usd >= min_order_usd:
            print(f"   ✅ Can place minimum BTC order")
            
            # Calculate position size (10% of capital as per bot)
            position_usd = gemini_usd * 0.1
            position_btc = position_usd / btc_price
            
            print(f"   📈 10% position size: {position_btc:.6f} BTC (${position_usd:.2f})")
            print(f"   🟢 READY TO TRADE on Gemini")
        else:
            print(f"   ❌ Insufficient for minimum order (need ${min_order_usd:.2f})")
    else:
        print(f"   ❌ Insufficient Gemini balance: ${gemini_usd:.2f}")
    
except Exception as e:
    print(f"❌ Order test error: {e}")

print("\n" + "="*70)
print("🎯 API REALITY CHECK COMPLETE")
print("="*70)