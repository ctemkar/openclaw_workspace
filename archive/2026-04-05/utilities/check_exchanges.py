#!/usr/bin/env python3
"""
Check exchange APIs and fix crypto arbitration
"""
import requests
import json

print("🔍 CHECKING EXCHANGE APIS & FIXING CRYPTO ARBITRATION")
print("=" * 60)

# Check Binance
print("\n1. 📊 BINANCE API:")
try:
    resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        btc_price = float(data['price'])
        print(f"   ✅ Accessible - BTC: ${btc_price:.2f}")
        
        # Check MANA specifically
        resp2 = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT', timeout=10)
        if resp2.status_code == 200:
            mana_data = resp2.json()
            mana_price = float(mana_data['price'])
            print(f"   ✅ MANA: ${mana_price:.4f}")
        else:
            print(f"   ⚠️  MANA error: {resp2.status_code}")
            
    else:
        print(f"   ❌ Error: {resp.status_code}")
        print(f"   Response: {resp.text[:100]}")
        
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    print("   ⚠️  Possible Thailand geographic restriction")

# Check Gemini
print("\n2. 💎 GEMINI API:")
try:
    resp = requests.get('https://api.gemini.com/v1/pubticker/btcusd', timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        btc_price = float(data['last'])
        print(f"   ✅ Accessible - BTC: ${btc_price:.2f}")
        
        # Check MANA
        resp2 = requests.get('https://api.gemini.com/v1/pubticker/manausd', timeout=10)
        if resp2.status_code == 200:
            mana_data = resp2.json()
            mana_price = float(mana_data['last'])
            print(f"   ✅ MANA: ${mana_price:.4f}")
        else:
            print(f"   ⚠️  MANA error: {resp2.status_code}")
            
    else:
        print(f"   ❌ Error: {resp.status_code}")
        print(f"   Response: {resp.text[:100]}")
        
except Exception as e:
    print(f"   ❌ Connection failed: {e}")

# Check arbitration spread
print("\n3. 📈 ARBITRATION OPPORTUNITY:")
try:
    # Get MANA prices
    binance_resp = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=MANAUSDT', timeout=10)
    gemini_resp = requests.get('https://api.gemini.com/v1/pubticker/manausd', timeout=10)
    
    if binance_resp.status_code == 200 and gemini_resp.status_code == 200:
        b_price = float(binance_resp.json()['price'])
        g_price = float(gemini_resp.json()['last'])
        spread = ((g_price - b_price) / b_price) * 100
        
        print(f"   Binance:  ${b_price:.4f}")
        print(f"   Gemini:   ${g_price:.4f}")
        print(f"   Spread:   {spread:.2f}%")
        
        if spread > 0.5:
            profit_per_mana = g_price - b_price
            print(f"   ✅ PROFITABLE: ${profit_per_mana:.4f} per MANA")
            print(f"   For 1000 MANA: ${profit_per_mana * 1000:.2f} profit")
        else:
            print(f"   ⚠️  Not profitable enough (need >0.5%)")
    else:
        print(f"   ❌ Can't compare prices")
        
except Exception as e:
    print(f"   ❌ Error calculating spread: {e}")

# Check running bots
print("\n4. 🤖 RUNNING BOTS:")
import subprocess
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
bots = ['practical_profit', '26_crypto', 'real_26', 'arbitration']
for bot in bots:
    if bot in result.stdout:
        print(f"   ✅ {bot} bot: RUNNING")
    else:
        print(f"   ❌ {bot} bot: NOT RUNNING")

print("\n5. 🚨 PRACTICAL PROFIT BOT ERROR:")
print("   Error: 'Filter failure: NOTIONAL'")
print("   Meaning: Order size too small for Binance")
print("   Solution: Increase trade size or use different exchange")

print("\n6. 🎯 IMMEDIATE FIXES NEEDED:")
print("   1. Restart 26-crypto bot (main arbitrage)")
print("   2. Fix Binance 'NOTIONAL' error (increase trade size)")
print("   3. Check if Thailand IP blocked from Binance")
print("   4. Consider VPN or alternative exchange")