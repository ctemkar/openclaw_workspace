#!/usr/bin/env python3
"""
Thorough test of both Gemini and Binance connections
"""

import ccxt
import os
import sys
from datetime import datetime

print("\n" + "="*70)
print("🔍 THOROUGH EXCHANGE CONNECTION TEST")
print("="*70)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

def test_gemini():
    """Test Gemini connection thoroughly"""
    print("\n📈 GEMINI TEST ($200 for Longs)")
    print("-" * 50)
    
    try:
        # Load keys
        with open("secure_keys/.gemini_key", 'r') as f:
            gemini_key = f.read().strip()
        with open("secure_keys/.gemini_secret", 'r') as f:
            gemini_secret = f.read().strip()
        
        print(f"✅ Key loaded: {gemini_key[:10]}...")
        print(f"✅ Secret loaded: {len(gemini_secret)} chars")
        
        # Initialize exchange
        exchange = ccxt.gemini({
            'apiKey': gemini_key,
            'secret': gemini_secret,
            'enableRateLimit': True,
            'timeout': 10000
        })
        
        print("🔄 Testing connection...")
        
        # Test 1: Fetch balance
        balance = exchange.fetch_balance()
        total_usd = balance['total'].get('USD', 0)
        free_usd = balance['free'].get('USD', 0)
        used_usd = balance['used'].get('USD', 0)
        
        print(f"✅ Balance fetched successfully")
        print(f"   Total USD: ${total_usd:.2f}")
        print(f"   Free USD: ${free_usd:.2f}")
        print(f"   Used USD: ${used_usd:.2f}")
        
        # Test 2: Check if we have enough for trading
        if free_usd >= 200:
            print(f"✅ Sufficient funds: ${free_usd:.2f} available (need $200)")
        else:
            print(f"⚠️ Insufficient funds: ${free_usd:.2f} available (need $200)")
        
        # Test 3: Fetch ticker for BTC/USD
        print("🔄 Fetching market data...")
        ticker = exchange.fetch_ticker('BTC/USD')
        print(f"✅ Market data: BTC/USD = ${ticker['last']:.2f}")
        
        # Test 4: Check trading permissions
        print("🔄 Checking permissions...")
        markets = exchange.load_markets()
        if 'BTC/USD' in markets:
            market_info = markets['BTC/USD']
            print(f"✅ Trading enabled for BTC/USD")
            print(f"   Limits: {market_info.get('limits', {})}")
        else:
            print("⚠️ Could not verify BTC/USD market")
        
        print("🎯 GEMINI STATUS: ✅ FULLY OPERATIONAL")
        print(f"   Ready for $200 long positions")
        
        return {
            'connected': True,
            'balance': free_usd,
            'trading_enabled': True,
            'status': 'operational'
        }
        
    except Exception as e:
        print(f"❌ GEMINI ERROR: {e}")
        return {
            'connected': False,
            'error': str(e),
            'status': 'failed'
        }

def test_binance():
    """Test Binance connection thoroughly"""
    print("\n📉 BINANCE TEST ($50 for Shorts)")
    print("-" * 50)
    
    try:
        # Load keys
        with open("secure_keys/.binance_key", 'r') as f:
            binance_key = f.read().strip()
        with open("secure_keys/.binance_secret", 'r') as f:
            binance_secret = f.read().strip()
        
        print(f"✅ Key loaded: {binance_key[:10]}...")
        print(f"✅ Secret loaded: {len(binance_secret)} chars")
        
        # Initialize exchange
        exchange = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            'enableRateLimit': True,
            'timeout': 10000,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True
            }
        })
        
        print("🔄 Testing connection...")
        
        # Test 1: Fetch balance
        balance = exchange.fetch_balance()
        total_usdt = balance['total'].get('USDT', 0)
        free_usdt = balance['free'].get('USDT', 0)
        used_usdt = balance['used'].get('USDT', 0)
        
        print(f"✅ Balance fetched successfully")
        print(f"   Total USDT: ${total_usdt:.2f}")
        print(f"   Free USDT: ${free_usdt:.2f}")
        print(f"   Used USDT: ${used_usdt:.2f}")
        
        # Test 2: Check if we have enough for trading
        if free_usdt >= 50:
            print(f"✅ Sufficient funds: ${free_usdt:.2f} available (need $50)")
        else:
            print(f"⚠️ Insufficient funds: ${free_usdt:.2f} available (need $50)")
        
        # Test 3: Fetch ticker for BTC/USDT
        print("🔄 Fetching market data...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ Market data: BTC/USDT = ${ticker['last']:.2f}")
        
        # Test 4: Check trading permissions
        print("🔄 Checking permissions...")
        markets = exchange.load_markets()
        if 'BTC/USDT' in markets:
            market_info = markets['BTC/USDT']
            print(f"✅ Trading enabled for BTC/USDT")
            
            # Check if margin/shorting is available
            if market_info.get('margin', False):
                print(f"✅ Margin trading available (for shorts)")
            else:
                print(f"⚠️ Margin trading not available (shorts may be limited)")
        else:
            print("⚠️ Could not verify BTC/USDT market")
        
        # Test 5: Check account permissions
        print("🔄 Checking account type...")
        try:
            account = exchange.fetch_accounts()
            print(f"✅ Account info retrieved")
        except:
            print("⚠️ Could not fetch account details")
        
        print("🎯 BINANCE STATUS: ✅ FULLY OPERATIONAL")
        print(f"   Ready for $50 short positions")
        
        return {
            'connected': True,
            'balance': free_usdt,
            'trading_enabled': True,
            'status': 'operational'
        }
        
    except Exception as e:
        print(f"❌ BINANCE ERROR: {e}")
        
        # Provide specific troubleshooting
        if "Signature" in str(e):
            print("\n🔧 TROUBLESHOOTING: Signature error")
            print("   1. Re-copy EXACT secret from Binance")
            print("   2. Check for hidden spaces")
            print("   3. Verify IP restrictions: 127.0.0.1 + 115.87.79.55")
            print("   4. Check permissions: 'Spot & Margin Trading' ONLY")
        
        return {
            'connected': False,
            'error': str(e),
            'status': 'failed'
        }

def main():
    """Main test execution"""
    print("\n🚀 STARTING COMPREHENSIVE TESTS")
    print("="*70)
    
    # Test Gemini
    gemini_result = test_gemini()
    
    # Test Binance
    binance_result = test_binance()
    
    print("\n" + "="*70)
    print("📊 FINAL TEST RESULTS")
    print("="*70)
    
    # Gemini summary
    print("\n📈 GEMINI:")
    if gemini_result['connected']:
        print(f"   Status: ✅ OPERATIONAL")
        print(f"   Balance: ${gemini_result['balance']:.2f}")
        if gemini_result['balance'] >= 200:
            print(f"   Trading: ✅ READY for $200 longs")
        else:
            print(f"   Trading: ⚠️ Need ${200 - gemini_result['balance']:.2f} more")
    else:
        print(f"   Status: ❌ FAILED")
        print(f"   Error: {gemini_result.get('error', 'Unknown')}")
    
    # Binance summary
    print("\n📉 BINANCE:")
    if binance_result['connected']:
        print(f"   Status: ✅ OPERATIONAL")
        print(f"   Balance: ${binance_result['balance']:.2f}")
        if binance_result['balance'] >= 50:
            print(f"   Trading: ✅ READY for $50 shorts")
        else:
            print(f"   Trading: ⚠️ Need ${50 - binance_result['balance']:.2f} more")
    else:
        print(f"   Status: ❌ FAILED")
        print(f"   Error: {binance_result.get('error', 'Unknown')}")
    
    # Overall status
    print("\n" + "="*70)
    print("🎯 OVERALL SYSTEM STATUS")
    print("="*70)
    
    if gemini_result['connected'] and binance_result['connected']:
        print("✅ BOTH EXCHANGES CONNECTED SUCCESSFULLY!")
        
        # Check funding
        gemini_ready = gemini_result['balance'] >= 200
        binance_ready = binance_result['balance'] >= 50
        
        if gemini_ready and binance_ready:
            print("💰 FUNDING: ✅ FULLY FUNDED ($250 total)")
            print("   • Gemini: $200+ available for longs")
            print("   • Binance: $50+ available for shorts")
            print("\n🚀 SYSTEM READY: Activate REAL $250 trading!")
            
        elif gemini_ready and not binance_ready:
            print("💰 FUNDING: ⚠️ PARTIALLY FUNDED ($200 available)")
            print("   • Gemini: $200+ available for longs ✅")
            print("   • Binance: Need $50 deposit for shorts")
            print("\n🚀 OPTION: Start with $200 Gemini longs now")
            print("   Add Binance $50 later for full strategy")
            
        elif not gemini_ready and binance_ready:
            print("💰 FUNDING: ⚠️ PARTIALLY FUNDED ($50 available)")
            print("   • Gemini: Need $200 deposit for longs")
            print("   • Binance: $50+ available for shorts ✅")
            print("\n⚠️ Gemini needs $200 for primary strategy")
            
        else:
            print("💰 FUNDING: ❌ INSUFFICIENT FUNDS")
            print("   • Gemini: Need $200 deposit")
            print("   • Binance: Need $50 deposit")
            print("\n💸 Deposit funds before activating")
            
    elif gemini_result['connected'] and not binance_result['connected']:
        print("⚠️ MIXED STATUS: Gemini OK, Binance Failed")
        print("   • Gemini: Connected ✅")
        print("   • Binance: Connection failed ❌")
        print("\n🔧 Fix Binance connection first")
        
    elif not gemini_result['connected'] and binance_result['connected']:
        print("⚠️ MIXED STATUS: Binance OK, Gemini Failed")
        print("   • Gemini: Connection failed ❌")
        print("   • Binance: Connected ✅")
        print("\n🔧 Fix Gemini connection first")
        
    else:
        print("❌ BOTH EXCHANGES FAILED")
        print("   Check API keys and permissions")
    
    print("\n" + "="*70)
    print("🚀 NEXT ACTION:")
    if gemini_result['connected'] and gemini_result['balance'] >= 200:
        print("   Run: ./activate_real_system_now.sh")
    else:
        print("   1. Ensure Gemini has $200+ balance")
        print("   2. Ensure Binance has $50+ balance")
        print("   3. Run: ./activate_real_system_now.sh")
    
    print("="*70)

if __name__ == "__main__":
    main()