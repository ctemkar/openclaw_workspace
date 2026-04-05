#!/usr/bin/env python3
"""
Check what crypto pairs Alpaca supports for trading
"""
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 CHECKING ALPACA CRYPTO PAIRS AVAILABLE")
print("="*70)

api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')
base_url = 'https://api.alpaca.markets'

try:
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    
    print("✅ Connected to Alpaca LIVE account")
    
    # Get account
    account = api.get_account()
    print(f"💰 Cash available: ${account.cash}")
    print(f"💵 Buying power: ${account.buying_power}")
    
    # Common crypto symbols to check
    crypto_symbols = [
        'BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'DOGE/USD',
        'MATIC/USD', 'DOT/USD', 'AVAX/USD', 'LINK/USD', 'UNI/USD',
        'AAVE/USD', 'SNX/USD', 'MKR/USD', 'COMP/USD', 'YFI/USD'
    ]
    
    print("\n🔎 CHECKING CRYPTO PAIR AVAILABILITY:")
    available_pairs = []
    
    for symbol in crypto_symbols:
        try:
            asset = api.get_asset(symbol)
            if asset.tradable and asset.status == 'active':
                print(f"   ✅ {symbol}: TRADABLE ({asset.exchange})")
                available_pairs.append(symbol)
            else:
                print(f"   ⚠️  {symbol}: Not tradable (status: {asset.status})")
        except Exception as e:
            print(f"   ❌ {symbol}: Not available")
    
    print(f"\n📊 SUMMARY: {len(available_pairs)} crypto pairs available")
    
    if available_pairs:
        print("🎯 AVAILABLE FOR TRADING:")
        for pair in available_pairs:
            print(f"   • {pair}")
        
        print("\n🚀 RECOMMENDED STARTING PAIRS:")
        print("   1. BTC/USD - Highest liquidity")
        print("   2. ETH/USD - Good spreads")
        print("   3. SOL/USD - Volatile, good for arbitrage")
    
    # Check if we can get crypto prices
    print("\n💸 TESTING PRICE FETCH:")
    if available_pairs:
        test_pair = available_pairs[0]  # Try first available
        try:
            # Get latest trade
            trades = api.get_latest_trade(test_pair)
            print(f"   ✅ {test_pair}: Latest price ${trades.price}")
            
            # Get latest quote
            quote = api.get_latest_quote(test_pair)
            print(f"   📈 Bid: ${quote.bidprice}, Ask: ${quote.askprice}")
            print(f"   💰 Spread: ${quote.askprice - quote.bidprice:.4f}")
            
        except Exception as e:
            print(f"   ❌ Price fetch failed: {e}")
    
    # Check trading permissions
    print("\n🔐 TRADING PERMISSIONS:")
    print(f"   Trading Blocked: {account.trading_blocked}")
    print(f"   Account Blocked: {account.account_blocked}")
    print(f"   Pattern Day Trader: {account.pattern_day_trader}")
    
    print("\n" + "="*70)
    print("🎯 READY FOR ALPACA CRYPTO ARBITRAGE!")
    print(f"💰 Capital: ${account.cash} cash + ${account.portfolio_value} total")
    print(f"📊 Available pairs: {len(available_pairs)} crypto pairs")
    print("\n🚀 NEXT: Build arbitrage bot comparing Alpaca vs Gemini prices")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")