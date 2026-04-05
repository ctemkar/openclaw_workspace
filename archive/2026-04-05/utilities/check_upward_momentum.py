#!/usr/bin/env python3
"""
Check what cryptos are going UP 1%+ on Gemini
"""

import ccxt

# Real available Gemini cryptos (from previous check)
REAL_GEMINI_CRYPTOS = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 'MANA', 'COMP']

def check_upward_momentum():
    print("📈 CHECKING FOR UPWARD MOMENTUM (1%+ GAINS)")
    print("===========================================")
    
    try:
        # Initialize Gemini
        exchange = ccxt.gemini({
            'enableRateLimit': True,
        })
        
        print(f"Checking {len(REAL_GEMINI_CRYPTOS)} available Gemini cryptos...")
        print("")
        
        upward_opportunities = 0
        downward_opportunities = 0
        
        for crypto in REAL_GEMINI_CRYPTOS:
            symbol = f"{crypto}/USD"
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Try to get 24h change
                change_24h = ticker.get('percentage')
                
                # If not available, use 24h high/low
                if change_24h is None:
                    high_24h = ticker.get('high')
                    low_24h = ticker.get('low')
                    if high_24h and low_24h and high_24h > 0:
                        midpoint = (high_24h + low_24h) / 2
                        change_24h = ((current_price - midpoint) / midpoint) * 100
                    else:
                        change_24h = 0
                
                # Check both directions
                is_up = change_24h >= 1.0 if change_24h else False
                is_down = change_24h <= -1.0 if change_24h else False
                
                # Format output
                change_str = f"{change_24h:+.2f}%" if change_24h else "N/A"
                
                if is_up:
                    status = "🚀 UP 1%+ (MOMENTUM)"
                    upward_opportunities += 1
                    color = "\033[92m"
                elif is_down:
                    status = "📉 DOWN 1%+ (DIP)"
                    downward_opportunities += 1
                    color = "\033[91m"
                else:
                    status = "➡️  FLAT (<1% change)"
                    color = "\033[93m"
                
                reset = "\033[0m"
                print(f"{crypto:6} | ${current_price:8.2f} | {color}{change_str:>8}{reset} | {status}")
                
            except Exception as e:
                print(f"{crypto:6} | Error: {str(e)[:40]}...")
        
        print("")
        print(f"📊 OPPORTUNITIES FOUND:")
        print(f"   📈 Upward momentum (1%+): {upward_opportunities}")
        print(f"   📉 Downward dips (1%+): {downward_opportunities}")
        print(f"   ➡️  Total: {upward_opportunities + downward_opportunities}")
        
        print("")
        print("💡 TRADING STRATEGY ANALYSIS:")
        print("   1. Current bot: Only buys DIPS (down 1%+)")
        print("   2. Missing: Momentum trades (up 1%+)")
        print("")
        print("🤔 Should the bot also trade upward momentum?")
        print("   - Pros: Catch rising trends early")
        print("   - Cons: Risk of buying at peak")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_upward_momentum()
