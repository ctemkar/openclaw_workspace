#!/usr/bin/env python3
"""
Check what holdings are in Alpaca account
"""
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

print("🔍 CHECKING ALPACA HOLDINGS")
print("=" * 60)

# Load environment variables
load_dotenv()

# Get Alpaca keys
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

if not api_key or not api_secret:
    print("❌ ERROR: Alpaca API keys not found in .env file")
    exit(1)

try:
    # Connect to Alpaca
    api = tradeapi.REST(
        api_key,
        api_secret,
        'https://api.alpaca.markets',
        api_version='v2'
    )
    
    # Get account info
    account = api.get_account()
    print(f"\n📊 ACCOUNT SUMMARY:")
    print(f"   Account ID: {account.id}")
    print(f"   Status: {account.status}")
    print(f"   Cash: ${account.cash}")
    print(f"   Buying Power: ${account.buying_power}")
    print(f"   Portfolio Value: ${account.portfolio_value}")
    
    # Calculate non-cash holdings
    cash_value = float(account.cash)
    portfolio_value = float(account.portfolio_value)
    holdings_value = portfolio_value - cash_value
    
    print(f"\n💰 HOLDINGS BREAKDOWN:")
    print(f"   Cash: ${cash_value:.2f}")
    print(f"   Holdings: ${holdings_value:.2f}")
    print(f"   Total: ${portfolio_value:.2f}")
    
    # Get detailed positions
    positions = api.list_positions()
    
    if not positions:
        print(f"\n✅ NO HOLDINGS - 100% cash already")
        print(f"   ${cash_value:.2f} available for investment")
    else:
        print(f"\n📦 DETAILED HOLDINGS ({len(positions)} positions):")
        
        # Sort by value (highest first)
        positions_sorted = sorted(positions, key=lambda x: float(x.market_value), reverse=True)
        
        for i, position in enumerate(positions_sorted, 1):
            symbol = position.symbol
            qty = position.qty
            price = float(position.current_price)
            value = float(position.market_value)
            pct_portfolio = (value / portfolio_value) * 100
            
            print(f"\n   {i}. {symbol}:")
            print(f"      Shares: {qty}")
            print(f"      Price: ${price:.2f}")
            print(f"      Value: ${value:.2f}")
            print(f"      % of Portfolio: {pct_portfolio:.1f}%")
            
            # Get asset details if available
            try:
                asset = api.get_asset(symbol)
                print(f"      Type: {asset.__dict__.get('class', 'Unknown')}")
                print(f"      Exchange: {asset.exchange}")
            except:
                pass
    
    print(f"\n🎯 RECOMMENDATION:")
    if holdings_value > 0:
        print(f"   Sell ${holdings_value:.2f} in holdings to get ${portfolio_value:.2f} total cash")
        print(f"   This would increase investable capital by {holdings_value/cash_value*100:.0f}%")
    else:
        print(f"   Already 100% cash - ${cash_value:.2f} ready for investment")
    
    print(f"\n⚠️  RISK WARNING:")
    print(f"   Selling holdings may trigger capital gains taxes")
    print(f"   Market conditions affect sale prices")
    print(f"   Consider keeping diversified holdings vs 100% cash")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")