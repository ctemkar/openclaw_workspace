#!/usr/bin/env python3
"""
Setup dual-exchange strategy: Gemini for longs, Binance for shorts.
Simplified version.
"""

import json
import os
import sys
from datetime import datetime

def create_dual_exchange_config():
    """Create configuration for dual-exchange strategy"""
    print("\n" + "="*60)
    print("DUAL-EXCHANGE STRATEGY: GEMINI LONGS + BINANCE SHORTS")
    print("="*60)
    
    config = {
        "strategy": "dual_exchange_hedged",
        "total_capital": 100.00,
        "capital_allocation": {
            "gemini": {
                "amount": 70.00,
                "purpose": "LONG positions only",
                "pairs": ["BTC/USD", "ETH/USD", "SOL/USD"],
                "allowed_actions": ["BUY"],
                "risk": {"stop_loss": 0.05, "take_profit": 0.10, "max_position": 0.5}
            },
            "binance": {
                "amount": 30.00,
                "purpose": "SHORT positions only", 
                "pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
                "allowed_actions": ["SELL"],
                "risk": {"stop_loss": 0.07, "take_profit": 0.08, "max_position": 0.3}
            }
        },
        "created": datetime.now().isoformat()
    }
    
    with open("dual_exchange_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ dual_exchange_config.json")
    print(f"💰 Total: ${config['total_capital']}")
    print(f"• Gemini Longs: ${config['capital_allocation']['gemini']['amount']}")
    print(f"• Binance Shorts: ${config['capital_allocation']['binance']['amount']}")
    
    return config

def update_trading_bot_simple():
    """Simple update to trading bot for dual exchange"""
    print("\n" + "="*60)
    print("UPDATING TRADING BOT (SIMPLIFIED)")
    print("="*60)
    
    # Create a new strategy file instead of modifying existing
    strategy = {
        "name": "Gemini_Longs_Binance_Shorts",
        "description": "Gemini for conservative longs, Binance for opportunistic shorts",
        "execution": {
            "gemini": {
                "action": "Execute LONG if: price near support, RSI < 40, trend bullish",
                "max_trades_per_day": 2,
                "capital_per_trade": 35.00  # 50% of $70
            },
            "binance": {
                "action": "Execute SHORT if: price near resistance, RSI > 60, trend bearish", 
                "max_trades_per_day": 1,
                "capital_per_trade": 9.00  # 30% of $30
            }
        },
        "hedging": "Binance shorts can hedge Gemini longs during downturns",
        "created": datetime.now().isoformat()
    }
    
    with open("dual_exchange_strategy.json", "w") as f:
        json.dump(strategy, f, indent=2)
    
    print("✅ dual_exchange_strategy.json")
    
    return strategy

def create_setup_instructions():
    """Create setup instructions"""
    print("\n" + "="*60)
    print("SETUP INSTRUCTIONS")
    print("="*60)
    
    instructions = f"""
    ============================================================
    DUAL EXCHANGE SETUP: GEMINI LONGS + BINANCE SHORTS
    ============================================================
    
    STRATEGY OVERVIEW:
    • Gemini: $70 for LONG positions (conservative)
    • Binance: $30 for SHORT positions (opportunistic)
    • Total: $100 capital
    
    ============================================================
    STEP 1: API KEY SETUP
    ============================================================
    
    GEMINI (For Longs):
    1. Create API key on Gemini.com
    2. Permissions: "Trader" (minimum)
    3. Save key & secret
    
    BINANCE (For Shorts):
    1. Create API key on Binance.com  
    2. Permissions: "Spot & Margin Trading"
    3. Save key & secret
    
    ============================================================
    STEP 2: CREATE SECURE FILES
    ============================================================
    
    # Gemini keys
    echo "YOUR_GEMINI_KEY" > .gemini_key
    echo "YOUR_GEMINI_SECRET" > .gemini_secret
    chmod 600 .gemini_key .gemini_secret
    
    # Binance keys  
    echo "YOUR_BINANCE_KEY" > .binance_key
    echo "YOUR_BINANCE_SECRET" > .binance_secret
    chmod 600 .binance_key .binance_secret
    
    ============================================================
    STEP 3: UPDATE TRADING BOT
    ============================================================
    
    Edit conservative_crypto_trading.py:
    
    Change:
        EXCHANGE = "gemini"
    
    To:
        USE_DUAL_EXCHANGE = True
        GEMINI_CAPITAL = 70.00
        BINANCE_CAPITAL = 30.00
    
    ============================================================
    STEP 4: START TRADING
    ============================================================
    
    Restart system:
        pkill -f trading_server.py
        pkill -f conservative_crypto_trading.py
        python3 trading_server.py &
        python3 conservative_crypto_trading.py &
    
    ============================================================
    MONITORING:
    ============================================================
    
    • Dashboard: http://127.0.0.1:5080
    • Gemini Trades: LONG positions only
    • Binance Trades: SHORT positions only
    • Combined P&L: Net of both exchanges
    
    ============================================================
    RISK MANAGEMENT:
    ============================================================
    
    Gemini (Longs):
    • Stop-loss: 5%
    • Take-profit: 10% 
    • Max position: $35 (50% of $70)
    
    Binance (Shorts):
    • Stop-loss: 7% (higher for shorts)
    • Take-profit: 8%
    • Max position: $9 (30% of $30)
    
    ============================================================
    Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ============================================================
    """
    
    with open("DUAL_EXCHANGE_SETUP.txt", "w") as f:
        f.write(instructions)
    
    print("✅ DUAL_EXCHANGE_SETUP.txt")
    
    return instructions

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("SETTING UP: GEMINI LONGS + BINANCE SHORTS")
    print("="*60)
    print("Advanced dual-exchange hedging strategy")
    print("="*60)
    
    try:
        # Create config
        config = create_dual_exchange_config()
        
        # Create strategy
        strategy = update_trading_bot_simple()
        
        # Create instructions
        instructions = create_setup_instructions()
        
        print("\n" + "="*60)
        print("✅ DUAL EXCHANGE STRATEGY READY")
        print("="*60)
        
        print(f"\n🎯 STRATEGY SUMMARY:")
        print(f"   Total Capital: ${config['total_capital']}")
        print(f"   • Gemini Longs: ${config['capital_allocation']['gemini']['amount']}")
        print(f"   • Binance Shorts: ${config['capital_allocation']['binance']['amount']}")
        
        print(f"\n📊 RISK PARAMETERS:")
        print(f"   Gemini (Longs): 5% stop-loss, 10% take-profit")
        print(f"   Binance (Shorts): 7% stop-loss, 8% take-profit")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Read DUAL_EXCHANGE_SETUP.txt")
        print(f"   2. Get BOTH Gemini and Binance API keys")
        print(f"   3. Create .gemini_key/.gemini_secret files")
        print(f"   4. Create .binance_key/.binance_secret files")
        print(f"   5. Update trading bot configuration")
        print(f"   6. Restart system")
        
        print(f"\n💡 STRATEGY BENEFITS:")
        print(f"   • Hedge against market downturns with Binance shorts")
        print(f"   • Conservative longs on regulated Gemini")
        print(f"   • Opportunistic shorts on liquid Binance")
        print(f"   • Diversified across two exchanges")
        
        print(f"\n📁 FILES CREATED:")
        print(f"   1. dual_exchange_config.json")
        print(f"   2. dual_exchange_strategy.json")
        print(f"   3. DUAL_EXCHANGE_SETUP.txt")
        
        print(f"\n🎯 READY FOR ADVANCED DUAL-EXCHANGE TRADING!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()