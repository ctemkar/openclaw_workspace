#!/usr/bin/env python3
"""
UPGRADEABLE ARBITRAGE BOT - USER'S GENIUS STRATEGY
Starts at 0.5%, upgrades to 1% when available
"""
import alpaca_trade_api as tradeapi
import ccxt
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("🚀 UPGRADEABLE ARBITRAGE BOT - USER'S GENIUS STRATEGY")
print("="*80)
print("💰 STRATEGY: Start at 0.5%, DUMP for 1% when available!")
print("🎯 MAXIMIZE profit per dollar per minute")
print("="*80)

# Initialize exchanges
alpaca = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_API_SECRET'),
    'https://api.alpaca.markets',
    api_version='v2'
)

gemini = ccxt.gemini({
    'apiKey': os.getenv('GEMINI_API_KEY'),
    'secret': os.getenv('GEMINI_API_SECRET'),
    'enableRateLimit': True
})

# Trading parameters - USER'S STRATEGY
START_THRESHOLD = 0.5   # Start trading at 0.5%
UPGRADE_THRESHOLD = 1.0 # Upgrade to 1% when available
TRADE_SIZE_PERCENT = 10  # 10% of capital

# Crypto pairs
CRYPTO_PAIRS = [
    {'alpaca': 'BTC/USD', 'gemini': 'BTC/USD', 'name': 'Bitcoin'},
    {'alpaca': 'ETH/USD', 'gemini': 'ETH/USD', 'name': 'Ethereum'},
    {'alpaca': 'SOL/USD', 'gemini': 'SOL/USD', 'name': 'Solana'},
    {'alpaca': 'DOGE/USD', 'gemini': 'DOGE/USD', 'name': 'Dogecoin'},
]

# Track current position
current_position = None  # {'pair': 'Bitcoin', 'spread': 0.6, 'entry_time': ...}
total_profit = 0
trade_count = 0

def get_prices(pair):
    """Get prices from both exchanges"""
    try:
        # Alpaca price
        quote = alpaca.get_latest_quote(pair['alpaca'])
        alpaca_bid = float(quote.bidprice)
        alpaca_ask = float(quote.askprice)
        
        # Gemini price  
        ticker = gemini.fetch_ticker(pair['gemini'])
        gemini_bid = float(ticker['bid'])
        gemini_ask = float(ticker['ask'])
        
        return {
            'alpaca_bid': alpaca_bid,
            'alpaca_ask': alpaca_ask,
            'gemini_bid': gemini_bid,
            'gemini_ask': gemini_ask,
            'spread': (alpaca_bid - gemini_ask) / gemini_ask * 100  # Buy Gemini, sell Alpaca
        }
    except Exception as e:
        # print(f"Price error for {pair['name']}: {e}")
        return None

def find_best_opportunity():
    """Find the crypto with highest spread"""
    best_pair = None
    best_spread = 0
    
    for pair in CRYPTO_PAIRS:
        prices = get_prices(pair)
        if prices and prices['spread'] > best_spread:
            best_spread = prices['spread']
            best_pair = {
                'name': pair['name'],
                'spread': best_spread,
                'alpaca_bid': prices['alpaca_bid'],
                'gemini_ask': prices['gemini_ask'],
                'profit_percent': best_spread
            }
    
    return best_pair, best_spread

def should_upgrade(current_spread, new_spread):
    """Check if we should upgrade position"""
    # Upgrade if: new spread is >1% AND at least 0.3% better than current
    if new_spread >= UPGRADE_THRESHOLD and (new_spread - current_spread) >= 0.3:
        return True
    return False

def calculate_profit(spread_percent, capital):
    """Calculate profit for a trade"""
    trade_amount = capital * (TRADE_SIZE_PERCENT / 100)
    profit = trade_amount * (spread_percent / 100)
    return profit

def main():
    print("\n🔍 GETTING ALPACA ACCOUNT...")
    
    try:
        account = alpaca.get_account()
        cash = float(account.cash)
        print(f"💰 Capital: ${cash:.2f} cash, ${account.portfolio_value:.2f} total")
    except:
        cash = 99.23  # Default
    
    print(f"\n🎯 TRADING STRATEGY:")
    print(f"   START at: {START_THRESHOLD}% spread")
    print(f"   UPGRADE to: {UPGRADE_THRESHOLD}% when available")
    print(f"   Trade size: {TRADE_SIZE_PERCENT}% (${cash * (TRADE_SIZE_PERCENT/100):.2f})")
    
    print("\n🚀 STARTING UPGRADEABLE ARBITRAGE...")
    print("="*80)
    
    scan_count = 0
    while True:
        scan_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n📡 SCAN #{scan_count} - {current_time}")
        print("-" * 80)
        
        # Find best opportunity right now
        best_pair, best_spread = find_best_opportunity()
        
        if best_pair:
            print(f"📊 MARKET ANALYSIS:")
            print(f"   Best opportunity: {best_pair['name']}")
            print(f"   Spread: {best_spread:.2f}%")
            print(f"   Buy at: ${best_pair['gemini_ask']:.4f} (Gemini)")
            print(f"   Sell at: ${best_pair['alpaca_bid']:.4f} (Alpaca)")
            
            # Check current position
            if current_position:
                print(f"\n📦 CURRENT POSITION:")
                print(f"   Holding: {current_position['pair']}")
                print(f"   Entry spread: {current_position['spread']:.2f}%")
                print(f"   Holding for: {(time.time() - current_position['entry_time'])/60:.1f} minutes")
                
                # Check if we should upgrade
                if should_upgrade(current_position['spread'], best_spread):
                    print(f"\n🚀 UPGRADE OPPORTUNITY!")
                    print(f"   Current: {current_position['spread']:.2f}% ({current_position['pair']})")
                    print(f"   Available: {best_spread:.2f}% ({best_pair['name']})")
                    print(f"   Improvement: {best_spread - current_position['spread']:.2f}%")
                    
                    # Calculate profit difference
                    current_profit = calculate_profit(current_position['spread'], cash)
                    new_profit = calculate_profit(best_spread, cash)
                    profit_increase = new_profit - current_profit
                    
                    print(f"   Profit increase: ${profit_increase:.4f} per trade")
                    print(f"   💰 ACTION: DUMP {current_position['pair']}, SWITCH to {best_pair['name']}")
                    
                    # Update position
                    current_position = {
                        'pair': best_pair['name'],
                        'spread': best_spread,
                        'entry_time': time.time()
                    }
                    
                    # Log the upgrade
                    global total_profit, trade_count
                    trade_count += 1
                    total_profit += profit_increase
                    
                    print(f"   ✅ UPGRADED! Now holding {best_pair['name']} at {best_spread:.2f}%")
                    print(f"   📊 Total profit: ${total_profit:.4f} ({trade_count} trades)")
                    
                else:
                    print(f"   ⏳ Keep holding {current_position['pair']} (no better opportunity)")
            
            else:
                # No current position - check if we should enter
                if best_spread >= START_THRESHOLD:
                    print(f"\n🎯 ENTRY OPPORTUNITY!")
                    print(f"   Spread: {best_spread:.2f}% (≥ {START_THRESHOLD}% threshold)")
                    
                    profit = calculate_profit(best_spread, cash)
                    print(f"   Expected profit: ${profit:.4f} per trade")
                    print(f"   💰 ACTION: ENTER position in {best_pair['name']}")
                    
                    # Enter position
                    current_position = {
                        'pair': best_pair['name'],
                        'spread': best_spread,
                        'entry_time': time.time()
                    }
                    
                    print(f"   ✅ ENTERED! Now holding {best_pair['name']} at {best_spread:.2f}%")
                    
                else:
                    print(f"\n⏳ WAITING for entry...")
                    print(f"   Best spread: {best_spread:.2f}% (need ≥ {START_THRESHOLD}%)")
                    print(f"   Short by: {START_THRESHOLD - best_spread:.2f}%")
        
        else:
            print("❌ Could not fetch prices. Check API connections.")
        
        print(f"\n📈 STRATEGY STATUS:")
        if current_position:
            print(f"   Position: {current_position['pair']} @ {current_position['spread']:.2f}%")
        else:
            print(f"   Position: None (waiting for ≥{START_THRESHOLD}%)")
        
        print(f"   Total profit: ${total_profit:.4f}")
        print(f"   Total trades: {trade_count}")
        
        print(f"\n⏰ Next scan in 30 seconds...")
        print("="*80)
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 BOT STOPPED")
        print(f"📊 FINAL: ${total_profit:.4f} profit, {trade_count} trades")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")