#!/usr/bin/env python3
"""
Setup dual-exchange strategy: Gemini for longs, Binance for shorts.
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
                "amount": 70.00,  # 70% for longs
                "purpose": "LONG positions only",
                "pairs": ["BTC/USD", "ETH/USD", "SOL/USD"],
                "allowed_actions": ["BUY", "HOLD"],
                "risk_parameters": {
                    "stop_loss": 0.05,
                    "take_profit": 0.10,
                    "max_position": 0.5  # 50% of gemini capital
                }
            },
            "binance": {
                "amount": 30.00,  # 30% for shorts
                "purpose": "SHORT positions only",
                "pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
                "allowed_actions": ["SELL", "SHORT"],
                "risk_parameters": {
                    "stop_loss": 0.07,  # Slightly higher for shorts
                    "take_profit": 0.08,
                    "max_position": 0.3  # 30% of binance capital
                }
            }
        },
        "hedging_strategy": {
            "enabled": True,
            "correlation_threshold": 0.7,
            "max_hedge_ratio": 0.3,  # Max 30% hedge
            "rebalance_hours": 24
        },
        "created": datetime.now().isoformat(),
        "notes": "Gemini for conservative longs, Binance for opportunistic shorts"
    }
    
    with open("dual_exchange_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ dual_exchange_config.json")
    print(f"💰 Capital: ${config['total_capital']}")
    print(f"• Gemini (Longs): ${config['capital_allocation']['gemini']['amount']}")
    print(f"• Binance (Shorts): ${config['capital_allocation']['binance']['amount']}")
    
    return config

def update_trading_bot_for_dual_exchange():
    """Update trading bot for dual-exchange strategy"""
    print("\n" + "="*60)
    print("UPDATING TRADING BOT FOR DUAL EXCHANGE")
    print("="*60)
    
    file_path = "conservative_crypto_trading.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Update exchange configuration
    old_config = """# Exchange Configuration
EXCHANGE = "gemini"  # Change to "binance" for Binance
# Available symbols per exchange
if EXCHANGE == "binance":
    SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
else:  # gemini
    SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD']"""
    
    new_config = """# DUAL EXCHANGE CONFIGURATION
# Gemini for LONGS, Binance for SHORTS
USE_DUAL_EXCHANGE = True
GEMINI_CAPITAL = 70.00  # $70 for longs on Gemini
BINANCE_CAPITAL = 30.00  # $30 for shorts on Binance

# Exchange-specific symbols
GEMINI_SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD']  # Long positions only
BINANCE_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']  # Short positions only

# Risk parameters
GEMINI_RISK = {"stop_loss": 0.05, "take_profit": 0.10, "max_position": 0.5}
BINANCE_RISK = {"stop_loss": 0.07, "take_profit": 0.08, "max_position": 0.3}"""
    
    if old_config in content:
        content = content.replace(old_config, new_config)
        print("✅ Updated to dual-exchange configuration")
    else:
        print("⚠️ Could not find old config, adding new...")
        # Find CAPITAL line and add after
        if "CAPITAL = 100.0" in content:
            insert_point = content.find("CAPITAL = 100.0") + len("CAPITAL = 100.0")
            content = content[:insert_point] + "\n\n" + new_config + content[insert_point:]
            print("✅ Added dual-exchange config after CAPITAL")
    
    # Update initialize_exchange to handle both
    # We'll create a new function for dual exchange
    dual_exchange_function = """
def initialize_dual_exchanges():
    \"\"\"Initialize both Gemini and Binance exchanges\"\"\"
    exchanges = {}
    
    # Initialize Gemini for longs
    gemini_key, gemini_secret = get_api_keys("gemini")
    if gemini_key and gemini_secret:
        try:
            gemini = ccxt.gemini({
                'apiKey': gemini_key,
                'secret': gemini_secret,
                'enableRateLimit': True,
            })
            gemini.fetch_balance()
            exchanges["gemini"] = gemini
            print(f"✅ Gemini connected (${GEMINI_CAPITAL} for longs)")
        except Exception as e:
            print(f"❌ Gemini connection failed: {e}")
            exchanges["gemini"] = None
    else:
        print("⚠️ No Gemini API keys found")
        exchanges["gemini"] = None
    
    # Initialize Binance for shorts
    binance_key, binance_secret = get_api_keys("binance")
    if binance_key and binance_secret:
        try:
            binance = ccxt.binance({
                'apiKey': binance_key,
                'secret': binance_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            binance.fetch_balance()
            exchanges["binance"] = binance
            print(f"✅ Binance connected (${BINANCE_CAPITAL} for shorts)")
        except Exception as e:
            print(f"❌ Binance connection failed: {e}")
            exchanges["binance"] = None
    else:
        print("⚠️ No Binance API keys found")
        exchanges["binance"] = None
    
    return exchanges
"""
    
    # Add after existing initialize_exchange function
    if "def initialize_exchange(" in content:
        # Find the end of that function
        func_start = content.find("def initialize_exchange(")
        func_end = content.find("\ndef", func_start + 1)
        if func_end == -1:
            func_end = len(content)
        
        # Insert new function after
        insert_point = func_end
        content = content[:insert_point] + "\n\n" + dual_exchange_function + content[insert_point:]
        print("✅ Added initialize_dual_exchanges() function")
    
    # Update main execution logic
    # We'll modify the main analysis to use dual exchanges
    main_logic_addition = """
# DUAL EXCHANGE TRADING LOGIC
if USE_DUAL_EXCHANGE:
    exchanges = initialize_dual_exchanges()
    
    if exchanges.get("gemini"):
        # Analyze for LONG opportunities on Gemini
        for symbol in GEMINI_SYMBOLS:
            analysis = analyze_market(symbol, "gemini")
            if analysis["signal"] == "BUY" and analysis["confidence"] > 0.7:
                # Check if we can trade on Gemini (longs only)
                if can_trade_today(history, "gemini"):
                    # Execute LONG on Gemini
                    execute_gemini_long(symbol, analysis, GEMINI_CAPITAL, GEMINI_RISK)
    
    if exchanges.get("binance"):
        # Analyze for SHORT opportunities on Binance
        for symbol in BINANCE_SYMBOLS:
            analysis = analyze_market(symbol, "binance")
            if analysis["signal"] == "SELL" and analysis["confidence"] > 0.7:
                # Check if we can trade on Binance (shorts only)
                if can_trade_today(history, "binance"):
                    # Execute SHORT on Binance
                    execute_binance_short(symbol, analysis, BINANCE_CAPITAL, BINANCE_RISK)
"""
    
    # We'll need to add helper functions too
    helper_functions = """
def execute_gemini_long(symbol, analysis, capital, risk_params):
    \"\"\"Execute LONG trade on Gemini\"\"\"
    print(f"🎯 GEMINI LONG: {symbol} at ${analysis.get('price', 0):.2f}")
    print(f"   Reason: {analysis.get('reason', 'Conservative buy signal')}")
    print(f"   Capital: ${capital * risk_params['max_position']:.2f}")
    print(f"   Stop-loss: {risk_params['stop_loss']*100}%, Take-profit: {risk_params['take_profit']*100}%")
    
    # In real implementation, would call Gemini API
    # For now, log the decision
    log_trade(history, symbol, "BUY", analysis.get('price', 0), 
              capital * risk_params['max_position'] / analysis.get('price', 1),
              analysis.get('price', 0) * (1 - risk_params['stop_loss']),
              analysis.get('price', 0) * (1 + risk_params['take_profit']),
              f"Gemini Long: {analysis.get('reason', '')}")

def execute_binance_short(symbol, analysis, capital, risk_params):
    \"\"\"Execute SHORT trade on Binance\"\"\"
    print(f"🎯 BINANCE SHORT: {symbol} at ${analysis.get('price', 0):.2f}")
    print(f"   Reason: {analysis.get('reason', 'Conservative short signal')}")
    print(f"   Capital: ${capital * risk_params['max_position']:.2f}")
    print(f"   Stop-loss: {risk_params['stop_loss']*100}%, Take-profit: {risk_params['take_profit']*100}%")
    
    # In real implementation, would call Binance API for short
    # Note: Spot shorts on Binance require margin trading enabled
    # For now, log the decision
    log_trade(history, symbol, "SELL", analysis.get('price', 0), 
              capital * risk_params['max_position'] / analysis.get('price', 1),
              analysis.get('price', 0) * (1 + risk_params['stop_loss']),  # Higher for shorts
              analysis.get('price', 0) * (1 - risk_params['take_profit']),  # Lower for shorts
              f"Binance Short: {analysis.get('reason', '')}")

def can_trade_today(history, exchange):
    \"\"\"Check if we can trade on specific exchange today\"\"\"
    today = datetime.now().strftime("%Y-%m-%d")
    exchange_trades = history.get("exchange_trades", {}).get(exchange, {}).get(today, [])
    
    if exchange == "gemini":
        max_trades = 2  # Conservative for longs
    else:  # binance
        max_trades = 1  # More conservative for shorts
    
    return len(exchange_trades) < max_trades
"""
    
    # Find a good place to add these (near end of file before main execution)
    if "if __name__ == \"__main__\":" in content:
        main_start = content.find("if __name__ == \"__main__\":")
        # Insert helpers before main
        content = content[:main_start] + helper_functions + "\n\n" + content[main_start:]
        print("✅ Added dual-exchange execution functions")
        
        # Update main execution block
        main_block = content[main_start:]
        if "exchange = initialize_exchange(" in main_block:
            # Replace with dual exchange logic
            new_main_block = """if __name__ == "__main__":
    print("=" * 60)
    print("DUAL EXCHANGE TRADING: Gemini Longs + Binance Shorts")
    print("=" * 60)
    
    history = load_trading_history()
    
    if USE_DUAL_EXCHANGE:
        # Run dual exchange analysis
        print(f"💰 Capital: ${GEMINI_CAPITAL + BINANCE_CAPITAL}")
        print(f"• Gemini Longs: ${GEMINI_CAPITAL}")
        print(f"• Binance Shorts: ${BINANCE_CAPITAL}")
        print()
        
        # DUAL EXCHANGE TRADING LOGIC
        exchanges = initialize_dual_exchanges()
        
        if exchanges.get("gemini"):
            # Analyze for LONG opportunities on Gemini
            print("🔍 Scanning Gemini for LONG opportunities...")
            for symbol in GEMINI_SYMBOLS:
                analysis = analyze_market(symbol, "gemini")
                if analysis["signal"] == "BUY" and analysis["confidence"] > 0.7:
                    if can_trade_today(history, "gemini"):
                        execute_gemini_long(symbol, analysis, GEMINI_CAPITAL, GEMINI_RISK)
        
        if exchanges.get("binance"):
            # Analyze for SHORT opportunities on Binance
            print("🔍 Scanning Binance for SHORT opportunities...")
            for symbol in BINANCE_SYMBOLS:
                analysis = analyze_market(symbol, "binance")
                if analysis["signal"] == "SELL" and analysis["confidence"] > 0.7:
                    if can_trade_today(history, "binance"):
                        execute_binance_short(symbol, analysis, BINANCE_CAPITAL, BINANCE_RISK)
        
        print("\\n✅ Dual exchange analysis complete")
        print(f"📊 Check dashboard: http://127.0.0.1:5080")
    
    else:
        # Fallback to single exchange mode
        print("⚠️ Running in single exchange mode")
        exchange = initialize_exchange(EXCHANGE)
        if exchange:
            run_trading_cycle(exchange, history)
"""
            
            content = content[:main_start] + new_main_block
            print("✅ Updated main execution for dual exchange")
    
    # Write updated file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"\n✅ Trading bot updated for dual-exchange strategy")
    return True

def create_api_key_setup_guide():
    """Create guide for setting up both exchange API keys"""
    print("\n" + "="*60)
    print("API KEY SETUP GUIDE FOR DUAL EXCHANGE")
    print("="*60)
    
    guide = f"""
    ============================================================
    DUAL EXCHANGE API KEY SETUP
    ============================================================
    
    You need BOTH Gemini and Binance API keys for this strategy.
    
    ============================================================
    GEMINI SETUP (For Longs):
    ============================================================
    
    1. Login to Gemini (gemini.com)
    2. Account → API Settings → Create New API Key
    3. Name: "OpenClaw Longs"
    4. Permissions: "Trader" (minimum)
    5. Save API Key & Secret
    
    6. CREATE FILES:
       echo "YOUR_GEMINI_API_KEY" > .gemini_key
       echo "YOUR_GEMINI_SECRET" > .gemini_secret
       chmod 600 .gemini_key .gemini_secret
    
    ============================================================
    BINANCE SETUP (For Shorts):
    ============================================================
    
    1. Login to Binance (binance.com)
    2. API Management → Create API
    3. Label: "OpenClaw Shorts"
    4. Permissions: Enable "Spot & Margin Trading"
       • IMPORTANT: For shorts, you need margin trading enabled
       • Consider enabling "Futures" if you want advanced shorts
    5. IP Restrictions: Add your server IP
    6. Save API Key & Secret
    
    7. CREATE FILES:
       echo "YOUR_BINANCE_API_KEY" > .binance_key
       echo "YOUR_BINANCE_SECRET" > .binance_secret
       chmod 600 .binance_key .binance_secret
    
    ============================================================
    SECURITY NOTES:
    ============================================================
    
    • Gemini: Longs only, conservative risk
    • Binance: Shorts only, slightly higher risk tolerance
    • NEVER enable withdrawal permissions
    • Use separate keys for each exchange
    • Enable 2FA on both accounts
    
    ============================================================
    CAPITAL ALLOCATION:
    ============================================================
    
    Total: $100.00
    • Gemini (Longs): $70.00
    • Binance (Shorts): $30.00
    
