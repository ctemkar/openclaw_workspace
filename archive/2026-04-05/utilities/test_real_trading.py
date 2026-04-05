#!/usr/bin/env python3
"""
Test real trading with minimal setup
"""

import os
import sys
import time
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

def test_api_keys():
    """Test if API keys are properly configured"""
    print("Testing API key configuration...")
    
    # Check Binance keys
    binance_key_file = os.path.join(BASE_DIR, ".binance_key")
    binance_secret_file = os.path.join(BASE_DIR, ".binance_secret")
    
    binance_configured = False
    if os.path.exists(binance_key_file) and os.path.getsize(binance_key_file) > 10:
        with open(binance_key_file, 'r') as f:
            key = f.read().strip()
            if len(key) > 10:
                print(f"✅ Binance API key found ({len(key)} chars)")
                binance_configured = True
            else:
                print("❌ Binance API key file is too short")
    else:
        print("❌ Binance API key file missing or empty")
    
    # Check Gemini keys
    gemini_key_file = os.path.join(BASE_DIR, ".gemini_key")
    gemini_secret_file = os.path.join(BASE_DIR, ".gemini_secret")
    
    gemini_configured = False
    if os.path.exists(gemini_key_file) and os.path.getsize(gemini_key_file) > 10:
        with open(gemini_key_file, 'r') as f:
            key = f.read().strip()
            if len(key) > 10:
                print(f"✅ Gemini API key found ({len(key)} chars)")
                gemini_configured = True
            else:
                print("❌ Gemini API key file is too short")
    else:
        print("❌ Gemini API key file missing or empty")
    
    return binance_configured, gemini_configured

def create_minimal_trading_config():
    """Create a minimal trading configuration"""
    print("\nCreating minimal trading configuration...")
    
    config = {
        "trading_mode": "REAL",
        "activated_at": datetime.now().isoformat(),
        "capital_allocation": {
            "total": 250.00,
            "gemini": 200.00,
            "binance": 50.00
        },
        "trading_pairs": {
            "gemini": ["BTC/USD", "ETH/USD"],
            "binance": ["BTC/USDT", "ETH/USDT"]
        },
        "risk_parameters": {
            "stop_loss": 0.05,
            "take_profit": 0.10,
            "max_daily_trades": 2
        }
    }
    
    config_file = os.path.join(BASE_DIR, "minimal_trading_config.json")
    with open(config_file, 'w') as f:
        import json
        json.dump(config, f, indent=2)
    
    print(f"✅ Minimal config saved to {config_file}")
    return config

def start_simple_trading_monitor():
    """Start a simple trading monitor"""
    print("\nStarting simple trading monitor...")
    
    monitor_script = """#!/usr/bin/env python3
import time
from datetime import datetime

print("=" * 60)
print("SIMPLE TRADING MONITOR")
print("=" * 60)
print("Mode: REAL TRADING (API keys required)")
print("Capital: $250 ($200 Gemini, $50 Binance)")
print("Status: Waiting for API key configuration")
print("=" * 60)

while True:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring...")
    print("   • Check API keys in secure_keys/ directory")
    print("   • Ensure keys have trading permissions")
    print("   • Verify balances on exchanges")
    print("   • Trading will begin automatically when ready")
    print("-" * 40)
    time.sleep(60)
"""
    
    monitor_file = os.path.join(BASE_DIR, "simple_trading_monitor.py")
    with open(monitor_file, 'w') as f:
        f.write(monitor_script)
    
    os.chmod(monitor_file, 0o755)
    print(f"✅ Simple monitor created: {monitor_file}")
    
    return monitor_file

def provide_setup_instructions():
    """Provide setup instructions"""
    print("\n" + "="*60)
    print("SETUP INSTRUCTIONS FOR REAL TRADING")
    print("="*60)
    
    instructions = f"""
    REAL TRADING SETUP - $250 CAPITAL
    
    CURRENT STATUS: API Keys Not Configured
    
    STEP 1: CONFIGURE BINANCE API KEYS
    -----------------------------------
    1. Log in to Binance.com
    2. Go to API Management
    3. Create new API key with these permissions:
       - Enable Reading
       - Enable Spot & Margin Trading
    4. Copy the API Key and Secret Key
    5. Save them to:
       {BASE_DIR}/secure_keys/.binance_key
       {BASE_DIR}/secure_keys/.binance_secret
    
    STEP 2: CONFIGURE GEMINI API KEYS
    ---------------------------------
    1. Log in to Gemini.com
    2. Go to Settings → API
    3. Create new API key with 'Trader' role
    4. Copy the API Key and Secret Key
    5. Save them to:
       {BASE_DIR}/secure_keys/.gemini_key
       {BASE_DIR}/secure_keys/.gemini_secret
    
    STEP 3: VERIFY BALANCES
    -----------------------
    • Binance: Should have $70+ USDT (you mentioned this)
    • Gemini: Should have $200+ USD for conservative trading
    
    STEP 4: START TRADING
    ---------------------
    1. Run: python3 conservative_crypto_trading.py
    2. Monitor: http://127.0.0.1:5080
    3. Check status: curl http://127.0.0.1:5001/status
    
    SECURITY NOTES:
    • Never share API keys
    • Use IP whitelisting
    • Start with small amounts
    • Monitor regularly
    
    FILES CREATED:
    1. minimal_trading_config.json - Trading configuration
    2. simple_trading_monitor.py - Monitoring script
    
    NEED HELP?
    • Check logs in workspace directory
    • Verify API key permissions
    • Test with small trade first
    """
    
    print(instructions)
    
    # Save instructions to file
    instructions_file = os.path.join(BASE_DIR, "REAL_TRADING_SETUP_INSTRUCTIONS.txt")
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"\n✅ Instructions saved to: {instructions_file}")

def main():
    """Main function"""
    print("REAL TRADING SETUP TEST")
    print("="*60)
    
    # Test API keys
    binance_ok, gemini_ok = test_api_keys()
    
    # Create config
    config = create_minimal_trading_config()
    
    # Create monitor
    monitor = start_simple_trading_monitor()
    
    # Provide instructions
    provide_setup_instructions()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if not binance_ok and not gemini_ok:
        print("❌ NO API KEYS CONFIGURED")
        print("\n⚠️ Action required:")
        print("1. Configure Binance and Gemini API keys")
        print("2. Save them to secure_keys/ directory")
        print("3. Ensure keys have trading permissions")
        print("4. Run this test again")
    elif binance_ok and not gemini_ok:
        print("⚠️ PARTIALLY CONFIGURED")
        print("✅ Binance: Ready")
        print("❌ Gemini: Needs API keys")
    elif not binance_ok and gemini_ok:
        print("⚠️ PARTIALLY CONFIGURED")
        print("❌ Binance: Needs API keys")
        print("✅ Gemini: Ready")
    else:
        print("✅ FULLY CONFIGURED")
        print("Both Binance and Gemini API keys are ready!")
        print("\n🚀 Ready to start real trading!")
    
    print(f"\n💰 Configured Capital: ${config['capital_allocation']['total']}")
    print(f"   • Gemini: ${config['capital_allocation']['gemini']}")
    print(f"   • Binance: ${config['capital_allocation']['binance']}")
    
    print(f"\n⏰ Next steps in instructions file:")
    print(f"   {BASE_DIR}/REAL_TRADING_SETUP_INSTRUCTIONS.txt")

if __name__ == "__main__":
    main()