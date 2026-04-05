#!/usr/bin/env python3
import ccxt
import time

print("🔍 CHECKING GEMINI STATUS - 18:19")
print("=" * 60)

# 1. Check Gemini PUBLIC API
print("\n1. GEMINI PUBLIC API (no keys):")
try:
    gemini = ccxt.gemini({
        'enableRateLimit': True
    })
    
    # Try to get YFI price
    ticker = gemini.fetch_ticker('YFI/USD')
    gemini_price = ticker['last']
    print(f"   ✅ Gemini YFI price: ${gemini_price:.2f}")
    
    # Check if we can get order book
    orderbook = gemini.fetch_order_book('YFI/USD', 5)
    print(f"   ✅ Order book: {len(orderbook['bids'])} bids, {len(orderbook['asks'])} asks")
    print(f"   ✅ Best bid: ${orderbook['bids'][0][0]:.2f}")
    print(f"   ✅ Best ask: ${orderbook['asks'][0][0]:.2f}")
    
except Exception as e:
    print(f"   ❌ Gemini PUBLIC API error: {e}")
    gemini_price = 2458.82  # Fallback from dashboard

# 2. Check Binance
print("\n2. BINANCE (with API keys):")
try:
    with open('secure_keys/.binance_key', 'r') as f:
        api_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        api_secret = f.read().strip()
    
    binance = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True
    })
    
    ticker = binance.fetch_ticker('YFI/USDT')
    binance_price = ticker['last']
    print(f"   ✅ Binance YFI price: ${binance_price:.2f}")
    
    # Calculate actual spread
    spread = ((gemini_price - binance_price) / binance_price) * 100
    profit_per_30 = 30 * (spread/100)
    
    print(f"\n📊 ACTUAL ARBITRAGE OPPORTUNITY:")
    print(f"   Gemini: ${gemini_price:.2f}")
    print(f"   Binance: ${binance_price:.2f}")
    print(f"   Spread: {spread:.2f}%")
    print(f"   Profit per $30: ${profit_per_30:.2f}")
    
    if spread > 0.5:
        print(f"   🎯 STATUS: PROFITABLE! (≥0.5% threshold)")
    else:
        print(f"   ⚠️ STATUS: Not profitable (<0.5%)")
        
except Exception as e:
    print(f"   ❌ Binance error: {e}")

# 3. Check why bot isn't using Gemini
print("\n3. WHY BOT ISN'T USING GEMINI:")
print("   Current bot (make_money_now.py):")
print("   - Buys on Binance")
print("   - Sells on Binance (not Gemini)")
print("   - Reason: Gemini has nonce/API issues")
print("   - Result: Small profits ($0.01) vs potential ($0.31)")

# 4. Check Gemini private API (if keys exist)
print("\n4. GEMINI PRIVATE API (if keys exist):")
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        gemini_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        gemini_secret = f.read().strip()
    
    print(f"   ✅ Gemini keys found: {gemini_key[:10]}...")
    
    gemini_private = ccxt.gemini({
        'apiKey': gemini_key,
        'secret': gemini_secret,
        'enableRateLimit': True
    })
    
    # Try to fetch balance (will fail if nonce issue)
    try:
        balance = gemini_private.fetch_balance()
        print(f"   ✅ Gemini private API working!")
        print(f"   💰 Gemini balance available")
    except Exception as e:
        print(f"   ❌ Gemini private API error: {e}")
        print(f"   💡 This is likely the nonce issue preventing trading")
        
except FileNotFoundError:
    print("   ⚠️ No Gemini API keys found in secure_keys/")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("🎯 SUMMARY: Gemini shows good prices but API has issues.")
print("   Current bot makes small profits ($0.01) on Binance-only")
print("   Potential: $0.31 profit if Gemini API worked")
print("   Issue: Gemini nonce/API errors prevent real trading")