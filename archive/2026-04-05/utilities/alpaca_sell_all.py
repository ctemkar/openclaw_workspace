#!/usr/bin/env python3
"""
SELL ALL HOLDINGS IN ALPACA ACCOUNT
Converts entire portfolio to CASH for maximum investment capital
"""
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import time

print("🚨 SELLING ALL ALPACA HOLDINGS - REAL MONEY ACTION")
print("=" * 70)

# Load environment variables
load_dotenv()

# Get Alpaca keys
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

if not api_key or not api_secret:
    print("❌ ERROR: Alpaca API keys not found in .env file")
    exit(1)

print(f"✅ API Key: {api_key[:10]}...")
print(f"✅ API Secret: {api_secret[:10]}...")

# Connect to Alpaca (LIVE trading)
try:
    api = tradeapi.REST(
        api_key,
        api_secret,
        'https://api.alpaca.markets',  # LIVE trading
        api_version='v2'
    )
    
    # Get current account status
    account = api.get_account()
    print(f"\n📊 CURRENT ACCOUNT STATUS:")
    print(f"   Account ID: {account.id}")
    print(f"   Status: {account.status}")
    print(f"   Cash: ${account.cash}")
    print(f"   Buying Power: ${account.buying_power}")
    print(f"   Portfolio Value: ${account.portfolio_value}")
    
    # Get current positions
    positions = api.list_positions()
    
    if not positions:
        print(f"\n✅ NO HOLDINGS FOUND - Already 100% cash")
        print(f"   Available cash: ${account.cash}")
        print(f"   Ready for investment!")
        exit(0)
    
    print(f"\n📦 CURRENT HOLDINGS ({len(positions)} positions):")
    total_position_value = 0
    
    for position in positions:
        value = float(position.market_value)
        total_position_value += value
        print(f"   {position.symbol}: {position.qty} shares × ${position.current_price} = ${value:.2f}")
    
    print(f"\n💰 TOTAL HOLDINGS VALUE: ${total_position_value:.2f}")
    print(f"💰 CURRENT CASH: ${account.cash}")
    print(f"💰 TOTAL AFTER SELL: ${float(account.cash) + total_position_value:.2f}")
    
    # CONFIRMATION REQUIRED
    print(f"\n🚨 🚨 🚨 CRITICAL ACTION REQUIRED 🚨 🚨 🚨")
    print(f"You are about to SELL ${total_position_value:.2f} worth of holdings!")
    print(f"This will convert everything to CASH for investment.")
    print(f"\nType 'SELL ALL' to confirm (REAL MONEY ACTION):")
    
    confirmation = input("Confirmation: ").strip()
    
    if confirmation != "SELL ALL":
        print(f"\n❌ CANCELLED: No confirmation received")
        exit(0)
    
    print(f"\n✅ CONFIRMED: Selling all holdings...")
    
    # Sell all positions
    sold_positions = []
    failed_positions = []
    
    for position in positions:
        try:
            symbol = position.symbol
            qty = position.qty
            
            print(f"\n   Selling {symbol}: {qty} shares...")
            
            # Submit sell order (market order for immediate execution)
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            
            print(f"   ✅ Order submitted: {order.id}")
            sold_positions.append((symbol, qty, float(position.market_value)))
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Failed to sell {symbol}: {e}")
            failed_positions.append((symbol, qty, e))
    
    # Wait for orders to fill
    print(f"\n⏳ Waiting for orders to fill (10 seconds)...")
    time.sleep(10)
    
    # Get updated account status
    account = api.get_account()
    positions = api.list_positions()
    
    print(f"\n🎯 FINAL ACCOUNT STATUS:")
    print(f"   Cash: ${account.cash}")
    print(f"   Buying Power: ${account.buying_power}")
    print(f"   Remaining Positions: {len(positions)}")
    
    if positions:
        print(f"\n⚠️  WARNING: Some positions not sold:")
        for position in positions:
            print(f"   {position.symbol}: {position.qty} shares (${position.market_value})")
    
    print(f"\n✅ COMPLETED:")
    print(f"   Sold {len(sold_positions)} positions")
    print(f"   Failed: {len(failed_positions)} positions")
    print(f"   Available cash: ${account.cash}")
    print(f"   Ready for 100% investment deployment!")
    
except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {e}")
    print(f"   Failed to execute sell orders")
    print(f"   Check API keys and account status")