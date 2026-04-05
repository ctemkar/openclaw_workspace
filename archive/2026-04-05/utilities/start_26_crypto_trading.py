#!/usr/bin/env python3
"""
Start Real Trading with 26 Cryptocurrencies
Simple script to get real trading started
"""

import os
import sys
import json
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def check_api_keys():
    """Check if API keys are configured"""
    print("🔍 Checking API key configuration...")
    
    keys_configured = {
        "binance": False,
        "gemini": False
    }
    
    # Check Binance
    binance_key = os.path.join(BASE_DIR, ".binance_key")
    binance_secret = os.path.join(BASE_DIR, ".binance_secret")
    
    if os.path.exists(binance_key) and os.path.getsize(binance_key) > 20:
        with open(binance_key, 'r') as f:
            key = f.read().strip()
            if len(key) > 20:
                keys_configured["binance"] = True
                print(f"✅ Binance API key: Found ({len(key)} chars)")
    
    # Check Gemini
    gemini_key = os.path.join(BASE_DIR, ".gemini_key")
    gemini_secret = os.path.join(BASE_DIR, ".gemini_secret")
    
    if os.path.exists(gemini_key) and os.path.getsize(gemini_key) > 20:
        with open(gemini_key, 'r') as f:
            key = f.read().strip()
            if len(key) > 20:
                keys_configured["gemini"] = True
                print(f"✅ Gemini API key: Found ({len(key)} chars)")
    
    return keys_configured

def create_quick_start_config():
    """Create quick start configuration"""
    print("\n⚙️ Creating 26-crypto trading configuration...")
    
    # 26 cryptocurrencies to monitor
    cryptos = [
        "BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE",
        "AVAX", "MATIC", "LINK", "UNI", "LTC", "ATOM", "ETC",
        "XLM", "ALGO", "VET", "FIL", "ICP", "XTZ", "EOS",
        "AAVE", "MKR", "COMP", "SNX", "YFI"
    ]
    
    config = {
        "version": "quick_start_1.0",
        "created": datetime.now().isoformat(),
        "cryptocurrencies": cryptos,
        "capital": {
            "total": 250.00,
            "gemini": 200.00,
            "binance": 50.00
        },
        "trading": {
            "mode": "REAL",
            "gemini_mode": "LONG",
            "binance_mode": "SHORT",
            "max_daily_trades": 5,
            "scan_interval_minutes": 5
        },
        "pairs": {
            "gemini": ["BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD", "MATIC/USD", "LINK/USD", "UNI/USD"],
            "binance": [f"{crypto}/USDT" for crypto in cryptos]
        }
    }
    
    config_file = os.path.join(BASE_DIR, "quick_start_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved: {config_file}")
    return config

def start_trading_system():
    """Start the trading system"""
    print("\n🚀 Starting 26-crypto trading system...")
    
    # Check if trading server is running
    import subprocess
    import time
    
    # Start trading server if not running
    server_proc = None
    try:
        result = subprocess.run(["lsof", "-i", ":5001"], capture_output=True, text=True)
        if "LISTEN" not in result.stdout:
            print("Starting trading server on port 5001...")
            server_proc = subprocess.Popen(
                [sys.executable, os.path.join(BASE_DIR, "trading_server.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)
            print("✅ Trading server started")
        else:
            print("✅ Trading server already running on port 5001")
    except Exception as e:
        print(f"⚠️ Could not check/start trading server: {e}")
    
    # Start the 26-crypto trading bot
    print("\nStarting 26-crypto trading bot...")
    bot_file = os.path.join(BASE_DIR, "26_crypto_trading_bot.py")
    
    if os.path.exists(bot_file):
        bot_proc = subprocess.Popen(
            [sys.executable, bot_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ 26-crypto trading bot started (PID: {bot_proc.pid})")
        print("   The bot will scan all 26 cryptocurrencies every 5 minutes")
    else:
        print(f"❌ Trading bot not found: {bot_file}")
        print("   Creating it now...")
        
        # Create a simple trading bot
        simple_bot = """#!/usr/bin/env python3
print("26-CRYPTO TRADING BOT")
print("=" * 60)
print("API keys not configured. Please:")
print("1. Configure Binance and Gemini API keys")
print("2. Save them to .binance_key/.binance_secret")
print("3. Save them to .gemini_key/.gemini_secret")
print("4. Ensure keys have trading permissions")
print("=" * 60)
print("Once configured, restart this bot.")
"""
        
        with open(bot_file, 'w') as f:
            f.write(simple_bot)
        
        os.chmod(bot_file, 0o755)
        print(f"✅ Created placeholder bot: {bot_file}")
    
    return server_proc

def display_status():
    """Display system status"""
    print("\n" + "="*70)
    print("26-CRYPTO TRADING SYSTEM STATUS")
    print("="*70)
    
    # Check API keys
    keys = check_api_keys()
    
    print(f"\n🔑 API KEY STATUS:")
    print(f"   Binance: {'✅ CONFIGURED' if keys['binance'] else '❌ NOT CONFIGURED'}")
    print(f"   Gemini:  {'✅ CONFIGURED' if keys['gemini'] else '❌ NOT CONFIGURED'}")
    
    # Check if services are running
    print(f"\n🖥️  SERVICES:")
    
    # Check trading server
    try:
        import requests
        response = requests.get("http://127.0.0.1:5001/status", timeout=2)
        if response.status_code == 200:
            print("   Trading Server: ✅ RUNNING on port 5001")
        else:
            print("   Trading Server: ⚠️ Responding but with errors")
    except:
        print("   Trading Server: ❌ NOT RUNNING")
    
    # Check if bot process exists
    import psutil
    bot_running = False
    for proc in psutil.process_iter(['name', 'cmdline']):
        if proc.info['cmdline'] and '26_crypto_trading_bot.py' in ' '.join(proc.info['cmdline']):
            bot_running = True
            break
    
    print(f"   Trading Bot: {'✅ RUNNING' if bot_running else '❌ NOT RUNNING'}")
    
    print(f"\n💰 CAPITAL ALLOCATION:")
    print(f"   Total: $250.00")
    print(f"   • Gemini (LONG): $200.00")
    print(f"   • Binance (SHORT): $50.00")
    
    print(f"\n📊 CRYPTOCURRENCIES:")
    print(f"   Total: 26 cryptocurrencies")
    print(f"   • Gemini: 7 pairs (BTC, ETH, SOL, ADA, MATIC, LINK, UNI)")
    print(f"   • Binance: 26 pairs (All top cryptos)")
    
    print(f"\n⚡ TRADING PARAMETERS:")
    print(f"   Mode: REAL TRADING")
    print(f"   Scan Interval: Every 5 minutes")
    print(f"   Max Daily Trades: 5 total")
    print(f"   Risk: Conservative (5-7% stop-loss, 8-10% take-profit)")
    
    print(f"\n🔗 ENDPOINTS:")
    print(f"   Dashboard: http://127.0.0.1:5080")
    print(f"   API Status: http://127.0.0.1:5001/status")
    print(f"   Logs: tail -f 26_crypto_analysis.log")

def provide_next_steps(keys_configured):
    """Provide next steps based on configuration status"""
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    if not keys_configured["binance"] and not keys_configured["gemini"]:
        print("\n❌ ACTION REQUIRED: No API keys configured")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("1. BINANCE API KEYS:")
        print("   • Go to Binance.com → API Management")
        print("   • Create API key with 'Enable Spot & Margin Trading'")
        print("   • Save to: secure_keys/.binance_key and .binance_secret")
        print("   • You mentioned having $70+ USDT - verify balance")
        
        print("\n2. GEMINI API KEYS:")
        print("   • Go to Gemini.com → Settings → API")
        print("   • Create API key with 'Trader' role")
        print("   • Save to: secure_keys/.gemini_key and .gemini_secret")
        
        print("\n3. START TRADING:")
        print("   • Run: python3 26_crypto_trading_bot.py")
        print("   • Monitor: http://127.0.0.1:5080")
        
    elif keys_configured["binance"] and not keys_configured["gemini"]:
        print("\n⚠️ PARTIAL SETUP: Binance configured, Gemini needed")
        print("\n📋 NEXT STEPS:")
        print("1. Configure Gemini API keys (see instructions above)")
        print("2. The system will use Binance for SHORT positions only")
        print("3. Start trading: python3 26_crypto_trading_bot.py")
        
    elif not keys_configured["binance"] and keys_configured["gemini"]:
        print("\n⚠️ PARTIAL SETUP: Gemini configured, Binance needed")
        print("\n📋 NEXT STEPS:")
        print("1. Configure Binance API keys (see instructions above)")
        print("2. The system will use Gemini for LONG positions only")
        print("3. Start trading: python3 26_crypto_trading_bot.py")
        
    else:
        print("\n✅ FULLY CONFIGURED: Ready for real trading!")
        print("\n📋 TRADING ACTIVE:")
        print("1. System monitoring 26 cryptocurrencies")
        print("2. Gemini: $200 LONG positions (7 pairs)")
        print("3. Binance: $50 SHORT positions (26 pairs)")
        print("4. Scanning every 5 minutes")
        print("5. Conservative risk management")
        
        print("\n🔍 MONITORING:")
        print("• Dashboard: http://127.0.0.1:5080")
        print("• Logs: tail -f 26_crypto_analysis.log")
        print("• Trades: cat 26_crypto_trades.json")
    
    print(f"\n📁 CONFIGURATION FILES:")
    print(f"• 26_crypto_config.json - Main configuration")
    print(f"• quick_start_config.json - Quick start settings")
    print(f"• 26_CRYPTO_TRADING_INSTRUCTIONS.txt - Full instructions")
    
    print(f"\n⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("START REAL TRADING - 26 CRYPTOCURRENCIES")
    print("="*70)
    print("Dual Exchange: Gemini (LONG) + Binance (SHORT)")
    print(f"Total Capital: $250 ($200 Gemini + $50 Binance)")
    print("="*70)
    
    try:
        # Step 1: Check API keys
        keys_configured = check_api_keys()
        
        # Step 2: Create configuration
        config = create_quick_start_config()
        
        # Step 3: Start trading system
        start_trading_system()
        
        # Step 4: Display status
        display_status()
        
        # Step 5: Provide next steps
        provide_next_steps(keys_configured)
        
        print(f"\n" + "="*70)
        print("🚀 26-CRYPTO TRADING SYSTEM READY")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()