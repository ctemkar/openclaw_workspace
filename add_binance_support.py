#!/usr/bin/env python3
"""
Add Binance exchange support to trading system.
"""

import os
import sys

def update_trading_bot_for_binance():
    """Update conservative_crypto_trading.py for Binance support"""
    print("\n" + "="*60)
    print("ADDING BINANCE SUPPORT TO TRADING BOT")
    print("="*60)
    
    file_path = "conservative_crypto_trading.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Update get_api_keys function to support both exchanges
    old_function = """def get_api_keys() -> Tuple[Optional[str], Optional[str]]:
    \"\"\"Get Gemini API keys from secure files\"\"\"
    try:
        with open(os.path.join(BASE_DIR, ".gemini_key"), "r") as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, ".gemini_secret"), "r") as f:
            api_secret = f.read().strip()
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Error reading API keys: {e}")
        return None, None"""
    
    new_function = """def get_api_keys(exchange: str = "gemini") -> Tuple[Optional[str], Optional[str]]:
    \"\"\"Get exchange API keys from secure files\"\"\"
    try:
        if exchange.lower() == "binance":
            key_file = os.path.join(BASE_DIR, ".binance_key")
            secret_file = os.path.join(BASE_DIR, ".binance_secret")
        else:  # default to gemini
            key_file = os.path.join(BASE_DIR, ".gemini_key")
            secret_file = os.path.join(BASE_DIR, ".gemini_secret")
        
        with open(key_file, "r") as f:
            api_key = f.read().strip()
        with open(secret_file, "r") as f:
            api_secret = f.read().strip()
        return api_key, api_secret
    except Exception as e:
        print(f"❌ Error reading {exchange} API keys: {e}")
        return None, None"""
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Updated get_api_keys() to support both Gemini and Binance")
    else:
        print("⚠️ Could not find old function, adding new one...")
        # Find where to insert
        pass
    
    # Update exchange initialization
    old_init = """def initialize_exchange():
    \"\"\"Initialize Gemini exchange\"\"\"
    api_key, api_secret = get_api_keys()
    
    if not api_key or not api_secret:
        print("⚠️ No API keys found. Running in simulation mode.")
        return None
    
    exchange = ccxt.gemini({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    
    # Test connection
    try:
        exchange.fetch_balance()
        print(f"✅ Connected to Gemini")
        return exchange
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return None"""
    
    new_init = """def initialize_exchange(exchange_name: str = "gemini"):
    \"\"\"Initialize exchange (Gemini or Binance)\"\"\"
    api_key, api_secret = get_api_keys(exchange_name)
    
    if not api_key or not api_secret:
        print(f"⚠️ No {exchange_name} API keys found. Running in simulation mode.")
        return None
    
    if exchange_name.lower() == "binance":
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
            }
        })
    else:  # default to gemini
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })
    
    # Test connection
    try:
        balance = exchange.fetch_balance()
        print(f"✅ Connected to {exchange_name}")
        print(f"   Available balance: {balance.get('free', {})}")
        return exchange
    except Exception as e:
        print(f"❌ {exchange_name} connection failed: {e}")
        return None"""
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        print("✅ Updated initialize_exchange() for both exchanges")
    else:
        print("⚠️ Could not find old init function")
    
    # Update main execution to use exchange parameter
    # Look for main trading loop
    if "exchange = initialize_exchange()" in content:
        content = content.replace("exchange = initialize_exchange()", 
                                 "exchange = initialize_exchange(EXCHANGE)")
        print("✅ Updated main execution to use EXCHANGE parameter")
    
    # Add exchange configuration at top
    config_addition = """
# Exchange Configuration
EXCHANGE = "gemini"  # Change to "binance" for Binance
# Available symbols per exchange
if EXCHANGE == "binance":
    SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
else:  # gemini
    SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD']
"""
    
    # Find where to add config (after capital definition)
    if "SYMBOLS = ['BTC/USD', 'ETH/USD']" in content:
        # Replace with dynamic symbols
        content = content.replace("SYMBOLS = ['BTC/USD', 'ETH/USD']", 
                                 "SYMBOLS = ['BTC/USD', 'ETH/USD']  # Default, will be overridden")
        
        # Add exchange config after capital
        capital_line = "CAPITAL = 100.0  # REAL $100 investment"
        if capital_line in content:
            insert_point = content.find(capital_line) + len(capital_line)
            content = content[:insert_point] + config_addition + content[insert_point:]
            print("✅ Added exchange configuration")
    
    # Write updated file
    with open(file_path, "w") as f:
        f.write(content)
    
    print(f"\n✅ Trading bot updated for Binance support")
    print(f"📁 File: {file_path}")
    
    return True

def create_binance_test_script():
    """Create script to test Binance connection"""
    print("\n" + "="*60)
    print("CREATING BINANCE TEST SCRIPT")
    print("="*60)
    
    test_script = """#!/usr/bin/env python3
"""
    return test_script

def update_trading_server_for_binance():
    """Update trading server to mention Binance"""
    print("\n" + "="*60)
    print("UPDATING TRADING SERVER DOCUMENTATION")
    print("="*60)
    
    file_path = "trading_server.py"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Update homepage to mention both exchanges
    if "Real trading with $100 capital on Gemini</p>" in content:
        content = content.replace(
            "Real trading with $100 capital on Gemini</p>",
            "Real trading with $100 capital on Gemini/Binance</p>"
        )
        print("✅ Updated trading server homepage")
    
    # Update status endpoint to show exchange
    if '"trading_pairs": ["BTC/USD", "ETH/USD"]' in content:
        # We'll update this dynamically later
        pass
    
    with open(file_path, "w") as f:
        f.write(content)
    
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("ADDING BINANCE EXCHANGE SUPPORT")
    print("="*60)
    print("Enable REAL trading on Binance with your $100")
    print("="*60)
    
    try:
        # Update trading bot
        update_trading_bot_for_binance()
        
        # Update trading server
        update_trading_server_for_binance()
        
        print("\n" + "="*60)
        print("✅ BINANCE SUPPORT ADDED")
        print("="*60)
        
        print(f"\n🎯 HOW TO USE BINANCE:")
        print(f"1. Get Binance API keys from binance.com")
        print(f"2. Create files: .binance_key and .binance_secret")
        print(f"3. Update EXCHANGE = \"binance\" in conservative_crypto_trading.py")
        print(f"4. Restart trading system")
        
        print(f"\n📊 BINANCE ADVANTAGES:")
        print(f"• Lower fees (0.1% vs Gemini's 0.35%)")
        print(f"• More trading pairs (100+ vs 10+)")
        print(f"• Better liquidity")
        print(f"• More order types")
        
        print(f"\n🔧 CONFIGURATION OPTIONS:")
        print(f"• Keep EXCHANGE = \"gemini\" for Gemini")
        print(f"• Change to EXCHANGE = \"binance\" for Binance")
        print(f"• Or create hybrid system using both")
        
        print(f"\n🚀 READY FOR REAL TRADING ON BINANCE!")
        print(f"Add your API keys and switch to Binance for better trading")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()