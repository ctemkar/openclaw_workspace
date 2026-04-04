#!/usr/bin/env python3
"""
Check Alpaca forex trading capabilities
"""
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 CHECKING ALPACA FOREX CAPABILITIES")
print("="*70)

# Get API keys from .env
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')
base_url = 'https://api.alpaca.markets'  # LIVE trading

if not api_key or not api_secret:
    print("❌ Alpaca API keys not found in .env")
    exit()

try:
    # Connect to Alpaca
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    
    print(f"✅ Connected to Alpaca LIVE account")
    
    # Get account info
    account = api.get_account()
    print(f"📊 Account Status: {account.status}")
    print(f"💰 Cash: ${account.cash}")
    print(f"💵 Buying Power: ${account.buying_power}")
    print(f"📈 Portfolio Value: ${account.portfolio_value}")
    
    # Check forex capabilities
    print("\n🌍 FOREX TRADING CHECK:")
    
    # Try to get forex assets
    try:
        # Common forex pairs
        forex_pairs = ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        
        print("   Testing forex pair availability...")
        for pair in forex_pairs:
            try:
                # Try to get the asset
                asset = api.get_asset(pair)
                print(f"   ✅ {pair}: Available ({asset.exchange})")
            except Exception as e:
                print(f"   ❌ {pair}: Not available or error")
                
    except Exception as e:
        print(f"   ⚠️  Forex check error: {e}")
    
    # Check if we can trade forex
    print("\n🎯 FOREX TRADING PERMISSIONS:")
    try:
        # Check account trading permissions
        print(f"   Account ID: {account.id}")
        print(f"   Pattern Day Trader: {account.pattern_day_trader}")
        print(f"   Trading Blocked: {account.trading_blocked}")
        print(f"   Transfers Blocked: {account.transfers_blocked}")
        print(f"   Account Blocked: {account.account_blocked}")
        
        # Check for forex-specific permissions
        print(f"\n   ⚠️  Note: Alpaca forex may require specific permissions")
        print(f"   💡 Check Alpaca dashboard for forex trading enablement")
        
    except Exception as e:
        print(f"   ❌ Permission check error: {e}")
    
    # Get current positions
    print("\n📦 CURRENT POSITIONS:")
    try:
        positions = api.list_positions()
        if positions:
            for pos in positions:
                print(f"   {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price} (${pos.market_value})")
        else:
            print("   No positions currently held")
    except Exception as e:
        print(f"   ❌ Positions error: {e}")
    
    print("\n" + "="*70)
    print("🎯 CONCLUSION:")
    print("1. If forex pairs show as 'Available' → Can trade forex immediately")
    print("2. If not available → May need to enable forex in Alpaca dashboard")
    print("3. Account has $355.18 capital ready for forex trading")
    print("\n🚀 NEXT: Build REAL forex bot using Alpaca (not simulated!)")
    
except Exception as e:
    print(f"\n❌ ALPACA CONNECTION ERROR: {e}")
    print("   Check API keys and internet connection")