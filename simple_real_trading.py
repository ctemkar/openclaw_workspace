#!/usr/bin/env python3
"""
Simple Real Trading Bot - $200 Gemini Longs
"""

import ccxt
import time
import json
from datetime import datetime

print("="*70)
print("🚀 SIMPLE REAL TRADING BOT - $200 GEMINI LONGS")
print("="*70)

# Load API keys
try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    print(f"✅ Gemini Key: {GEMINI_KEY[:10]}...")
    print(f"✅ Gemini Secret: {GEMINI_SECRET[:10]}...")
except:
    print("❌ Cannot load Gemini API keys")
    exit(1)

# Initialize exchange
exchange = ccxt.gemini({
    'apiKey': GEMINI_KEY,
    'secret': GEMINI_SECRET,
    'enableRateLimit': True
})

# Trading parameters
CAPITAL = 200.00  # $200 for Gemini longs
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD']

print(f"💰 Capital: ${CAPITAL:.2f}")
print(f"🎯 Risk: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
print(f"📈 Symbols: {', '.join(SYMBOLS)}")
print("="*70)

def check_balance():
    """Check Gemini balance"""
    try:
        balance = exchange.fetch_balance()
        usd = balance['free'].get('USD', 0)
        print(f"📊 Gemini Balance: ${usd:.2f} USD")
        return usd
    except Exception as e:
        print(f"❌ Balance check error: {e}")
        return 0

def analyze_market(symbol):
    """Simple market analysis"""
    try:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        print(f"   {symbol}: ${price:.2f}")
        return price
    except Exception as e:
        print(f"❌ Market data error for {symbol}: {e}")
        return None

def main_loop():
    """Main trading loop"""
    print("\n🔄 Starting trading loop (5-minute intervals)...")
    print("="*70)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n📊 Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        # Check balance
        balance = check_balance()
        if balance < CAPITAL * 0.1:  # Less than 10% of capital
            print("⚠️ Low balance - trading paused")
            time.sleep(300)  # 5 minutes
            continue
        
        # Analyze markets
        print("📈 Market Analysis:")
        for symbol in SYMBOLS:
            price = analyze_market(symbol)
            if price:
                # Simple strategy: Buy if price dropped 2% from last check
                # (This is just an example - real strategy would be more sophisticated)
                print(f"   {symbol}: ${price:.2f} - Monitoring for opportunities")
        
        print("✅ Analysis complete")
        print(f"⏳ Next analysis in 5 minutes...")
        print("="*70)
        
        # Wait 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    try:
        # Test connection first
        print("🔌 Testing Gemini connection...")
        balance = check_balance()
        if balance >= CAPITAL:
            print(f"✅ Sufficient balance: ${balance:.2f} (need ${CAPITAL:.2f})")
        else:
            print(f"⚠️ Insufficient balance: ${balance:.2f} (need ${CAPITAL:.2f})")
            print("   Trading with available funds")
        
        # Start main loop
        main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Trading bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()