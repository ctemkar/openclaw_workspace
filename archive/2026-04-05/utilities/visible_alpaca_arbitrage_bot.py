#!/usr/bin/env python3
"""
VISIBLE ALPACA ↔ GEMINI ARBITRAGE BOT
Shows real-time spread calculations and highest crypto spreads
"""
import alpaca_trade_api as tradeapi
import ccxt
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("🚀 VISIBLE ALPACA ↔ GEMINI CRYPTO ARBITRAGE BOT")
print("="*80)
print("💰 REAL MONEY TRADING WITH $355.18 CAPITAL")
print("👁️  YOU CAN SEE ALL SPREAD CALCULATIONS IN REAL-TIME!")
print("="*80)

# Initialize exchanges
alpaca = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_API_SECRET'),
    'https://api.alpaca.markets',  # LIVE trading
    api_version='v2'
)

gemini = ccxt.gemini({
    'apiKey': os.getenv('GEMINI_API_KEY'),
    'secret': os.getenv('GEMINI_API_SECRET'),
    'enableRateLimit': True
})

# Trading parameters
MIN_PROFIT_PERCENT = 0.5  # 0.5% minimum profit (USER SUGGESTION - SMART!)
TRADE_SIZE_PERCENT = 10   # 10% of available cash per trade

# Crypto pairs to monitor
CRYPTO_PAIRS = [
    {'alpaca': 'BTC/USD', 'gemini': 'BTC/USD', 'name': 'Bitcoin'},
    {'alpaca': 'ETH/USD', 'gemini': 'ETH/USD', 'name': 'Ethereum'},
    {'alpaca': 'SOL/USD', 'gemini': 'SOL/USD', 'name': 'Solana'},
    {'alpaca': 'DOGE/USD', 'gemini': 'DOGE/USD', 'name': 'Dogecoin'},
    {'alpaca': 'DOT/USD', 'gemini': 'DOT/USD', 'name': 'Polkadot'},
    {'alpaca': 'AVAX/USD', 'gemini': 'AVAX/USD', 'name': 'Avalanche'},
    {'alpaca': 'LINK/USD', 'gemini': 'LINK/USD', 'name': 'Chainlink'},
    {'alpaca': 'UNI/USD', 'gemini': 'UNI/USD', 'name': 'Uniswap'},
    {'alpaca': 'AAVE/USD', 'gemini': 'AAVE/USD', 'name': 'Aave'},
    {'alpaca': 'YFI/USD', 'gemini': 'YFI/USD', 'name': 'Yearn Finance'},
]

def get_alpaca_price(symbol):
    """Get latest price from Alpaca"""
    try:
        quote = alpaca.get_latest_quote(symbol)
        return {
            'bid': float(quote.bidprice),
            'ask': float(quote.askprice),
            'mid': (float(quote.bidprice) + float(quote.askprice)) / 2,
            'source': 'Alpaca'
        }
    except Exception as e:
        # print(f"⚠️  Alpaca price error for {symbol}: {e}")
        return None

def get_gemini_price(symbol):
    """Get latest price from Gemini"""
    try:
        ticker = gemini.fetch_ticker(symbol)
        return {
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'mid': (float(ticker['bid']) + float(ticker['ask'])) / 2,
            'source': 'Gemini'
        }
    except Exception as e:
        # print(f"⚠️  Gemini price error for {symbol}: {e}")
        return None

def display_spread_table(pair_data):
    """Display beautiful spread table"""
    print("\n" + "="*80)
    print("📊 REAL-TIME CRYPTO SPREAD ANALYSIS")
    print("="*80)
    print(f"{'CRYPTO':<12} {'GEMINI BUY':<12} {'ALPACA SELL':<12} {'SPREAD %':<10} {'STATUS':<12} {'PROFIT/$100':<12}")
    print("-"*80)
    
    for data in pair_data:
        if data['spread_percent'] >= MIN_PROFIT_PERCENT:
            status = "✅ PROFITABLE"
            emoji = "💰"
        elif data['spread_percent'] > 0:
            status = "⏳ WAITING"
            emoji = "📈"
        else:
            status = "❌ NEGATIVE"
            emoji = "📉"
        
        profit_per_100 = 100 * (data['spread_percent'] / 100)
        
        print(f"{emoji} {data['pair']:<10} ${data['gemini_buy']:<11.4f} ${data['alpaca_sell']:<11.4f} "
              f"{data['spread_percent']:<9.2f}% {status:<12} ${profit_per_100:<11.2f}")

def show_highest_spreads(pair_data):
    """Show highest spread opportunities"""
    print("\n" + "="*80)
    print("🎯 HIGHEST CRYPTO SPREADS RIGHT NOW")
    print("="*80)
    
    # Sort by spread percentage (highest first)
    sorted_data = sorted(pair_data, key=lambda x: x['spread_percent'], reverse=True)
    
    for i, data in enumerate(sorted_data[:5], 1):  # Top 5
        if data['spread_percent'] > 0:
            rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{rank} {data['pair']:<10}: {data['spread_percent']:.2f}% spread "
                  f"(Buy: ${data['gemini_buy']:.4f}, Sell: ${data['alpaca_sell']:.4f})")
    
    # Show if any are profitable
    profitable = [d for d in sorted_data if d['spread_percent'] >= MIN_PROFIT_PERCENT]
    if profitable:
        print(f"\n🚀 {len(profitable)} PROFITABLE OPPORTUNITIES FOUND!")
        for data in profitable[:3]:  # Top 3 profitable
            profit_per_trade = 355.18 * (TRADE_SIZE_PERCENT / 100) * (data['spread_percent'] / 100)
            print(f"   💰 {data['pair']}: Would make ${profit_per_trade:.2f} per trade")
    else:
        print(f"\n⏳ No spreads >{MIN_PROFIT_PERCENT}% yet. Waiting for market opportunities...")

def main():
    print("\n🔍 GETTING ALPACA ACCOUNT INFO...")
    
    try:
        account = alpaca.get_account()
        cash = float(account.cash)
        portfolio_value = float(account.portfolio_value)
        
        print(f"💰 ALPACA ACCOUNT STATUS:")
        print(f"   Cash Available: ${cash:.2f}")
        print(f"   Portfolio Value: ${portfolio_value:.2f}")
        print(f"   Buying Power: ${account.buying_power}")
        print(f"   Status: {account.status}")
        
    except Exception as e:
        print(f"❌ Failed to get Alpaca account: {e}")
        cash = 99.23  # Default from earlier check
    
    print(f"\n🎯 TRADING SETTINGS:")
    print(f"   Minimum Profit: {MIN_PROFIT_PERCENT}%")
    print(f"   Trade Size: {TRADE_SIZE_PERCENT}% of cash (${cash * (TRADE_SIZE_PERCENT/100):.2f})")
    print(f"   Monitoring {len(CRYPTO_PAIRS)} crypto pairs")
    
    print("\n🚀 STARTING REAL-TIME SPREAD SCANNING...")
    print("   (Updates every 30 seconds)")
    
    scan_count = 0
    while True:
        scan_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{'='*80}")
        print(f"📡 SCAN #{scan_count} - {current_time}")
        print(f"{'='*80}")
        
        pair_data = []
        
        # Check each pair
        for pair in CRYPTO_PAIRS:
            alpaca_price = get_alpaca_price(pair['alpaca'])
            gemini_price = get_gemini_price(pair['gemini'])
            
            if alpaca_price and gemini_price:
                # Calculate spread: Buy on Gemini (ask), Sell on Alpaca (bid)
                gemini_buy = gemini_price['ask']
                alpaca_sell = alpaca_price['bid']
                
                if gemini_buy > 0 and alpaca_sell > 0:
                    spread = alpaca_sell - gemini_buy
                    spread_percent = (spread / gemini_buy) * 100
                    
                    pair_data.append({
                        'pair': pair['name'],
                        'gemini_buy': gemini_buy,
                        'alpaca_sell': alpaca_sell,
                        'spread': spread,
                        'spread_percent': spread_percent,
                        'profitable': spread_percent >= MIN_PROFIT_PERCENT
                    })
        
        # Display results
        if pair_data:
            display_spread_table(pair_data)
            show_highest_spreads(pair_data)
        else:
            print("❌ Could not fetch prices for any pairs. Check API connections.")
        
        # Show next scan time
        next_scan = datetime.now().timestamp() + 30
        next_time = datetime.fromtimestamp(next_scan).strftime("%H:%M:%S")
        print(f"\n⏰ Next scan at: {next_time}")
        print(f"{'='*80}")
        
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 BOT STOPPED")
        print("✅ Spread scanning ended")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Please check API keys and internet connection")