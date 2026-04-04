#!/usr/bin/env python3
"""
MULTI-CRYPTO UPGRADE BOT - User's Genius Strategy
Trades multiple cryptos, upgrades from 0.5% to 1% opportunities
"""
import ccxt
import time
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("🚀 MULTI-CRYPTO UPGRADE BOT - USER'S GENIUS STRATEGY")
print("="*80)
print("💰 STRATEGY: Trade multiple cryptos, upgrade from 0.5% → 1%")
print("🎯 GOAL: Capital always in BEST available opportunity")
print("="*80)

# Initialize exchanges
binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

gemini = ccxt.gemini({
    'apiKey': os.getenv('GEMINI_API_KEY'),
    'secret': os.getenv('GEMINI_API_SECRET'),
    'enableRateLimit': True
})

# Trading parameters - USER'S STRATEGY
START_THRESHOLD = 0.5   # Start trading at 0.5%
UPGRADE_THRESHOLD = 1.0 # Upgrade to 1.0% when available
TRADE_SIZE_USD = 10     # $10 per trade (small for testing)

# Multiple crypto pairs for upgrade strategy
CRYPTO_PAIRS = [
    {'symbol': 'MANA/USDT', 'name': 'MANA', 'min_amount': 10},
    {'symbol': 'BTC/USDT', 'name': 'Bitcoin', 'min_amount': 0.0001},
    {'symbol': 'ETH/USDT', 'name': 'Ethereum', 'min_amount': 0.001},
    {'symbol': 'SOL/USDT', 'name': 'Solana', 'min_amount': 0.01},
    {'symbol': 'DOGE/USDT', 'name': 'Dogecoin', 'min_amount': 10},
]

# Track current position
current_position = None  # {'crypto': 'MANA', 'spread': 0.6, 'entry_time': ...}
total_profit = 0
trade_count = 0
trade_log = []

def get_prices(pair):
    """Get prices from both exchanges"""
    try:
        # Binance price
        binance_ticker = binance.fetch_ticker(pair['symbol'])
        binance_bid = float(binance_ticker['bid'])
        binance_ask = float(binance_ticker['ask'])
        
        # Gemini price (convert symbol)
        gemini_symbol = pair['symbol'].replace('USDT', 'USD')
        gemini_ticker = gemini.fetch_ticker(gemini_symbol)
        gemini_bid = float(gemini_ticker['bid'])
        gemini_ask = float(gemini_ticker['ask'])
        
        # Calculate spread (buy Gemini, sell Binance)
        spread = (binance_bid - gemini_ask) / gemini_ask * 100
        
        return {
            'binance_bid': binance_bid,
            'binance_ask': binance_ask,
            'gemini_bid': gemini_bid,
            'gemini_ask': gemini_ask,
            'spread': spread
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
                'symbol': pair['symbol'],
                'spread': best_spread,
                'binance_bid': prices['binance_bid'],
                'gemini_ask': prices['gemini_ask'],
                'min_amount': pair['min_amount']
            }
    
    return best_pair, best_spread

def should_upgrade(current_spread, new_spread):
    """Check if we should upgrade position"""
    # Upgrade if: new spread is >1% AND at least 0.3% better than current
    if new_spread >= UPGRADE_THRESHOLD and (new_spread - current_spread) >= 0.3:
        return True
    return False

def calculate_profit(spread_percent):
    """Calculate profit for a trade"""
    profit = TRADE_SIZE_USD * (spread_percent / 100)
    return profit

def log_trade(action, details):
    """Log trade to file"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details
    }
    trade_log.append(log_entry)
    
    with open('upgrade_trades.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def main():
    print(f"\n💰 TRADING PARAMETERS:")
    print(f"   Start at: {START_THRESHOLD}% spread")
    print(f"   Upgrade to: {UPGRADE_THRESHOLD}% when available")
    print(f"   Trade size: ${TRADE_SIZE_USD}")
    print(f"   Cryptos: {', '.join([p['name'] for p in CRYPTO_PAIRS])}")
    
    print(f"\n🚀 STARTING MULTI-CRYPTO UPGRADE STRATEGY...")
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
            print(f"   Best: {best_pair['name']} at {best_spread:.2f}%")
            print(f"   Buy at: ${best_pair['gemini_ask']:.4f} (Gemini)")
            print(f"   Sell at: ${best_pair['binance_bid']:.4f} (Binance)")
            
            # Show all spreads
            print(f"\n📈 ALL CRYPTO SPREADS:")
            for pair in CRYPTO_PAIRS:
                prices = get_prices(pair)
                if prices:
                    spread = prices['spread']
                    status = "✅ READY" if spread >= START_THRESHOLD else "⏳ WAITING"
                    if spread >= UPGRADE_THRESHOLD:
                        status = "🚀 UPGRADE!"
                    print(f"   {pair['name']}: {spread:.2f}% - {status}")
            
            # Check current position
            if current_position:
                print(f"\n📦 CURRENT POSITION:")
                print(f"   Holding: {current_position['crypto']}")
                print(f"   Entry spread: {current_position['spread']:.2f}%")
                print(f"   Holding for: {(time.time() - current_position['entry_time'])/60:.1f} minutes")
                
                # Check if we should upgrade
                if should_upgrade(current_position['spread'], best_spread):
                    print(f"\n🚀 UPGRADE OPPORTUNITY!")
                    print(f"   Current: {current_position['crypto']} at {current_position['spread']:.2f}%")
                    print(f"   Available: {best_pair['name']} at {best_spread:.2f}%")
                    print(f"   Improvement: {best_spread - current_position['spread']:.2f}%")
                    
                    # Calculate profit difference
                    current_profit = calculate_profit(current_position['spread'])
                    new_profit = calculate_profit(best_spread)
                    profit_increase = new_profit - current_profit
                    
                    print(f"   Profit increase: ${profit_increase:.4f} per trade")
                    print(f"   💰 ACTION: DUMP {current_position['crypto']}, SWITCH to {best_pair['name']}")
                    
                    # Update position
                    current_position = {
                        'crypto': best_pair['name'],
                        'spread': best_spread,
                        'entry_time': time.time()
                    }
                    
                    # Log the upgrade
                    global total_profit, trade_count
                    trade_count += 1
                    total_profit += profit_increase
                    
                    log_trade('UPGRADE', {
                        'from': current_position['crypto'],
                        'to': best_pair['name'],
                        'profit_increase': profit_increase
                    })
                    
                    print(f"   ✅ UPGRADED! Now holding {best_pair['name']} at {best_spread:.2f}%")
                    print(f"   📊 Total profit: ${total_profit:.4f} ({trade_count} trades)")
                    
                else:
                    print(f"   ⏳ Keep holding {current_position['crypto']} (no better opportunity)")
            
            else:
                # No current position - check if we should enter
                if best_spread >= START_THRESHOLD:
                    print(f"\n🎯 ENTRY OPPORTUNITY!")
                    print(f"   Spread: {best_spread:.2f}% (≥ {START_THRESHOLD}% threshold)")
                    
                    profit = calculate_profit(best_spread)
                    print(f"   Expected profit: ${profit:.4f} per trade")
                    print(f"   💰 ACTION: ENTER position in {best_pair['name']}")
                    
                    # Enter position
                    current_position = {
                        'crypto': best_pair['name'],
                        'spread': best_spread,
                        'entry_time': time.time()
                    }
                    
                    log_trade('ENTER', {
                        'crypto': best_pair['name'],
                        'profit': profit
                    })
                    
                    print(f"   ✅ ENTERED! Now holding {best_pair['name']} at {best_spread:.2f}%")
                    
                else:
                    print(f"\n⏳ WAITING for entry...")
                    print(f"   Best spread: {best_spread:.2f}% (need ≥ {START_THRESHOLD}%)")
                    print(f"   Short by: {START_THRESHOLD - best_spread:.2f}%")
        
        else:
            print("❌ Could not fetch prices. Check API connections.")
        
        print(f"\n📈 STRATEGY STATUS:")
        if current_position:
            print(f"   Position: {current_position['crypto']} @ {current_position['spread']:.2f}%")
        else:
            print(f"   Position: None (waiting for ≥{START_THRESHOLD}%)")
        
        print(f"   Total profit: ${total_profit:.4f}")
        print(f"   Total trades: {trade_count}")
        
        print(f"\n⏰ Next scan in 45 seconds...")
        print("="*80)
        time.sleep(45)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 BOT STOPPED")
        print(f"📊 FINAL: ${total_profit:.4f} profit, {trade_count} trades")
        print(f"📋 Trade log saved to: upgrade_trades.log")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")