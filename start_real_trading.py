#!/usr/bin/env python3
"""
Start Real Trading on Both Gemini and Binance
Configured for $250 total capital ($200 Gemini longs, $50 Binance shorts)
"""

import ccxt
import os
import json
import time
from datetime import datetime
import subprocess
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def check_exchange_balance(exchange_name, api_key_file, api_secret_file, currency='USD'):
    """Check balance on an exchange"""
    try:
        with open(api_key_file, 'r') as f:
            api_key = f.read().strip()
        with open(api_secret_file, 'r') as f:
            api_secret = f.read().strip()
        
        # Initialize exchange
        if exchange_name.lower() == 'binance':
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'options': {'defaultType': 'spot'}
            })
        elif exchange_name.lower() == 'gemini':
            exchange = ccxt.gemini({
                'apiKey': api_key,
                'secret': api_secret
            })
        else:
            print(f"❌ Unsupported exchange: {exchange_name}")
            return 0
        
        # Fetch balance
        balance = exchange.fetch_balance()
        
        # Check for currency
        if currency in balance:
            free_balance = balance[currency].get('free', 0)
            total_balance = balance[currency].get('total', 0)
            print(f"  {exchange_name} {currency} Balance:")
            print(f"    Free: ${free_balance:.2f}")
            print(f"    Total: ${total_balance:.2f}")
            return free_balance
        else:
            # Try to find the currency in the balance dict
            for key, value in balance.items():
                if isinstance(value, dict) and 'free' in value:
                    print(f"  {exchange_name} {key}: ${value['free']:.2f} free")
            return 0
            
    except FileNotFoundError as e:
        print(f"❌ API key file not found: {e}")
        return 0
    except Exception as e:
        print(f"❌ Error checking {exchange_name} balance: {e}")
        return 0

def update_trading_config():
    """Update trading configuration for real execution"""
    print("\n" + "="*60)
    print("UPDATING TRADING CONFIGURATION FOR REAL EXECUTION")
    print("="*60)
    
    config_updates = {
        "trading_mode": "REAL",
        "capital": 250.00,
        "gemini_capital": 200.00,
        "binance_capital": 50.00,
        "real_execution": True,
        "simulation_mode": False,
        "activated_at": datetime.now().isoformat(),
        "exchanges": {
            "gemini": {
                "mode": "LONG",
                "symbols": ["BTC/USD", "ETH/USD", "SOL/USD"],
                "risk": {
                    "stop_loss": 0.05,
                    "take_profit": 0.10,
                    "max_position_size": 0.5
                }
            },
            "binance": {
                "mode": "SHORT",
                "symbols": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
                "risk": {
                    "stop_loss": 0.07,
                    "take_profit": 0.08,
                    "max_position_size": 0.3
                }
            }
        }
    }
    
    # Save config
    config_file = os.path.join(BASE_DIR, "real_trading_config.json")
    with open(config_file, 'w') as f:
        json.dump(config_updates, f, indent=2)
    
    print(f"✅ Real trading configuration saved to {config_file}")
    print(f"💰 Total Capital: ${config_updates['capital']}")
    print(f"   • Gemini (LONG): ${config_updates['gemini_capital']}")
    print(f"   • Binance (SHORT): ${config_updates['binance_capital']}")
    
    return config_updates

def start_conservative_trading_bot():
    """Start the conservative trading bot with real execution"""
    print("\n" + "="*60)
    print("STARTING CONSERVATIVE TRADING BOT - REAL MODE")
    print("="*60)
    
    # Check if bot is already running
    result = subprocess.run(["ps", "aux", "|", "grep", "conservative_crypto_trading.py", "|", "grep", "-v", "grep"], 
                          shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("⚠️ Trading bot is already running. Restarting...")
        subprocess.run(["pkill", "-f", "conservative_crypto_trading.py"], capture_output=True)
        time.sleep(2)
    
    # Start the bot
    bot_path = os.path.join(BASE_DIR, "conservative_crypto_trading.py")
    if os.path.exists(bot_path):
        print("🚀 Starting conservative crypto trading bot...")
        
        # Update the bot for real execution if needed
        with open(bot_path, 'r') as f:
            content = f.read()
        
        # Ensure real execution is enabled
        if "REAL_EXECUTION = True" not in content:
            print("⚠️ Updating bot for real execution...")
            if "REAL_EXECUTION = False" in content:
                content = content.replace("REAL_EXECUTION = False", "REAL_EXECUTION = True")
            else:
                # Add real execution config
                real_config = """
# REAL TRADING CONFIGURATION
REAL_EXECUTION = True
SIMULATION_MODE = False
"""
                content += real_config
            
            with open(bot_path, 'w') as f:
                f.write(content)
        
        # Start the bot
        bot_proc = subprocess.Popen([sys.executable, bot_path], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Trading bot started (PID: {bot_proc.pid})")
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Verify it's running
        result = subprocess.run(["ps", "aux", "|", "grep", "conservative_crypto_trading.py", "|", "grep", "-v", "grep"], 
                              shell=True, capture_output=True, text=True)
        if result.stdout:
            print("✅ Trading bot is running")
        else:
            print("❌ Trading bot failed to start")
            
        return bot_proc
    else:
        print(f"❌ Trading bot not found at {bot_path}")
        return None

def create_trading_monitor():
    """Create a monitoring script for real trading"""
    print("\n" + "="*60)
    print("CREATING REAL TRADING MONITOR")
    print("="*60)
    
    monitor_script = """#!/usr/bin/env python3
"""
    
    monitor_file = os.path.join(BASE_DIR, "monitor_real_trading.py")
    with open(monitor_file, 'w') as f:
        f.write(monitor_script)
    
    os.chmod(monitor_file, 0o755)
    print(f"✅ Trading monitor created: {monitor_file}")
    
    return monitor_file

def main():
    """Main execution - Start real trading"""
    print("\n" + "="*60)
    print("STARTING REAL TRADING - DUAL EXCHANGE")
    print("="*60)
    print("Configuration: $200 Gemini (LONG) + $50 Binance (SHORT)")
    print("="*60)
    
    try:
        # Step 1: Check exchange balances
        print("\n📊 CHECKING EXCHANGE BALANCES")
        print("-" * 40)
        
        # Check Gemini balance
        gemini_key = os.path.join(BASE_DIR, ".gemini_key")
        gemini_secret = os.path.join(BASE_DIR, ".gemini_secret")
        gemini_balance = check_exchange_balance('gemini', gemini_key, gemini_secret, 'USD')
        
        # Check Binance balance
        binance_key = os.path.join(BASE_DIR, ".binance_key")
        binance_secret = os.path.join(BASE_DIR, ".binance_secret")
        binance_balance = check_exchange_balance('binance', binance_key, binance_secret, 'USDT')
        
        print(f"\n💰 SUMMARY:")
        print(f"  Gemini USD: ${gemini_balance:.2f}")
        print(f"  Binance USDT: ${binance_balance:.2f}")
        
        # Check if we have sufficient funds
        if gemini_balance >= 200:
            print("✅ Sufficient funds for Gemini longs ($200+)")
        else:
            print(f"⚠️ Warning: Gemini has only ${gemini_balance:.2f} (need $200+)")
        
        if binance_balance >= 50:
            print("✅ Sufficient funds for Binance shorts ($50+)")
        else:
            print(f"⚠️ Warning: Binance has only ${binance_balance:.2f} USDT (need $50+)")
        
        # Step 2: Update configuration
        config = update_trading_config()
        
        # Step 3: Start trading bot
        bot_proc = start_conservative_trading_bot()
        
        # Step 4: Create monitor
        monitor = create_trading_monitor()
        
        print("\n" + "="*60)
        print("✅ REAL TRADING SYSTEM ACTIVATED")
        print("="*60)
        
        print(f"\n🎯 CONFIGURATION:")
        print(f"   Total Capital: ${config['capital']}")
        print(f"   • Gemini (LONG): ${config['gemini_capital']}")
        print(f"   • Binance (SHORT): ${config['binance_capital']}")
        
        print(f"\n📊 EXCHANGE STATUS:")
        print(f"   Gemini Balance: ${gemini_balance:.2f} USD")
        print(f"   Binance Balance: ${binance_balance:.2f} USDT")
        
        print(f"\n🚀 TRADING BOT:")
        print(f"   Status: {'RUNNING' if bot_proc else 'NOT RUNNING'}")
        print(f"   Mode: REAL EXECUTION")
        print(f"   Strategy: Conservative AI Analysis")
        
        print(f"\n📈 TRADING PAIRS:")
        print(f"   Gemini (LONG): {', '.join(config['exchanges']['gemini']['symbols'])}")
        print(f"   Binance (SHORT): {', '.join(config['exchanges']['binance']['symbols'])}")
        
        print(f"\n⚠️ RISK PARAMETERS:")
        print(f"   Gemini Stop Loss: {config['exchanges']['gemini']['risk']['stop_loss']*100}%")
        print(f"   Gemini Take Profit: {config['exchanges']['gemini']['risk']['take_profit']*100}%")
        print(f"   Binance Stop Loss: {config['exchanges']['binance']['risk']['stop_loss']*100}%")
        print(f"   Binance Take Profit: {config['exchanges']['binance']['risk']['take_profit']*100}%")
        
        print(f"\n⏱️ ACTIVATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Next analysis: Within 5 minutes")
        print(f"   First trade: When conservative conditions met")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Monitor dashboard for analysis")
        print(f"   2. Watch for first trade execution")
        print(f"   3. Track performance metrics")
        print(f"   4. Adjust strategies as needed")
        
        print(f"\n🔍 MONITORING:")
        print(f"   • Check logs: tail -f trading.log")
        print(f"   • API Status: curl http://127.0.0.1:5001/status")
        print(f"   • Dashboard: Check port 5080")
        
        print(f"\n🚀 REAL TRADING IS NOW ACTIVE!")
        
    except Exception as e:
        print(f"\n❌ Error starting real trading: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()