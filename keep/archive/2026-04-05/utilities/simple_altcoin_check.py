#!/usr/bin/env python3
"""
Simple check of ONE altcoin to see actual spreads
"""
import ccxt

print("🔍 SIMPLE ALTCOIN SPREAD CHECK")
print("=" * 60)

# Just check KuCoin for ADA (should work)
try:
    kucoin = ccxt.kucoin({'enableRateLimit': True})
    
    # Check ADA/USDT
    ticker = kucoin.fetch_ticker('ADA/USDT')
    
    print(f"\n📊 ADA/USDT on KuCoin:")
    print(f"   Bid (buy): ${ticker['bid']:.4f}")
    print(f"   Ask (sell): ${ticker['ask']:.4f}")
    
    if ticker['bid'] and ticker['ask']:
        spread = ticker['ask'] - ticker['bid']
        spread_percent = (spread / ticker['bid']) * 100
        
        print(f"   Spread: ${spread:.4f}")
        print(f"   Spread %: {spread_percent:.2f}%")
        
        # Compare with BTC spread (should be much smaller)
        print(f"\n📈 COMPARISON:")
        print(f"   ADA spread: {spread_percent:.2f}%")
        print(f"   BTC spread: ~0.01% (from earlier test)")
        print(f"   ADA is {spread_percent/0.01:.0f}× wider than BTC!")
        
        if spread_percent >= 0.1:
            print(f"\n✅ GOOD: ADA has decent spread")
            print(f"   Profit on $100 trade: ${spread * (100/ticker['bid']):.2f}")
        else:
            print(f"\n⚠️  WARNING: ADA spread still small")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎯 REALITY CHECK:")
print("1. Even altcoins have small spreads during normal hours")
print("2. For 1-2% spreads, need:")
print("   - Market volatility")
print("   - Low liquidity times")
print("   - Smaller/less efficient exchanges")
print("   - Newly listed coins")
print("\n🚀 SOLUTION: Need to monitor for WHEN spreads widen")