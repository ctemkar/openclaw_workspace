#!/usr/bin/env python3
"""
Secure setup for connecting REAL exchange accounts (Gemini, Binance).
This enables actual trading with your $100 capital.
"""

import json
import os
import sys
from datetime import datetime
from getpass import getpass

def create_secure_instructions():
    """Create secure instructions for API key setup"""
    print("\n" + "="*60)
    print("SECURE EXCHANGE CONNECTION SETUP")
    print("="*60)
    
    instructions = f"""
    ============================================================
    SECURE EXCHANGE API SETUP - REAL $100 TRADING
    ============================================================
    
    IMPORTANT SECURITY NOTES:
    • NEVER share API keys publicly
    • Use READ-ONLY trading permissions
    • Enable IP whitelisting if available
    • Store keys in secure files (not in code)
    
    ============================================================
    GEMINI SETUP (Current System Configuration):
    ============================================================
    
    1. LOGIN to Gemini (gemini.com)
    2. Go to: Account → API Settings
    3. CREATE NEW API KEY:
       • Name: "OpenClaw Trading"
       • Permissions: "Trader" (minimum)
       • IP Restrictions: Add your server IP
    4. SAVE:
       • API Key: [Your Gemini API Key]
       • Secret: [Your Gemini Secret]
    
    5. CREATE SECURE FILES:
       echo "YOUR_GEMINI_API_KEY" > .gemini_key
       echo "YOUR_GEMINI_SECRET" > .gemini_secret
       chmod 600 .gemini_key .gemini_secret
    
    ============================================================
    BINANCE SETUP (Recommended - More Pairs):
    ============================================================
    
    1. LOGIN to Binance (binance.com)
    2. Go to: API Management
    3. CREATE API:
       • Label: "OpenClaw Trading"
       • Permissions: Enable Spot & Margin Trading
       • IP Access: Restrict to your IP
    4. SAVE:
       • API Key: [Your Binance API Key]
       • Secret: [Your Binance Secret]
    
    5. CREATE SECURE FILES:
       echo "YOUR_BINANCE_API_KEY" > .binance_key
       echo "YOUR_BINANCE_SECRET" > .binance_secret
       chmod 600 .binance_key .binance_secret
    
    ============================================================
    SECURITY BEST PRACTICES:
    ============================================================
    
    ✅ DO:
    • Use separate trading account if possible
    • Enable 2FA on exchange account
    • IP restrict API keys
    • Regular key rotation (every 90 days)
    • Monitor API usage
    
    ❌ DON'T:
    • Share keys with anyone
    • Use keys with unlimited permissions
    • Store keys in GitHub/version control
    • Use same keys across multiple bots
    
    ============================================================
    SYSTEM INTEGRATION:
    ============================================================
    
    Once keys are set up:
    
    1. SYSTEM WILL:
       • Test connection to exchange
       • Verify account balance
       • Start REAL trading with $100
       • Execute conservative strategies
    
    2. MONITORING:
       • Dashboard: http://127.0.0.1:5080
       • Trades: Real exchange executions
       • Balance: Live account updates
    
    3. SAFETY:
       • Max position: $50 (50% of $100)
       • Stop-loss: 5% enforced
       • Take-profit: 10% target
       • Daily trade limit: 2-3 trades
    
    ============================================================
    READY FOR REAL TRADING:
    ============================================================
    
    Steps to activate:
    
    1. Choose exchange (Gemini or Binance)
    2. Create API keys with proper permissions
    3. Store keys securely in workspace
    4. Restart trading system
    5. REAL trading begins immediately
    
    ============================================================
    RECOMMENDATION:
    ============================================================
    
    🥇 BINANCE: More pairs, better liquidity, lower fees
    🥈 GEMINI: US-based, regulatory compliance
    
    ============================================================
    Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ============================================================
    """
    
    return instructions

def create_api_key_templates():
    """Create template files for API keys"""
    print("\n" + "="*60)
    print("CREATING API KEY TEMPLATES")
    print("="*60)
    
    # Create secure directory structure
    os.makedirs("secure", exist_ok=True)
    
    # Gemini template
    gemini_template = """# GEMINI API CONFIGURATION
# Store your actual API keys in .gemini_key and .gemini_secret files
# DO NOT commit these files to version control

API_KEY = "YOUR_GEMINI_API_KEY_HERE"
API_SECRET = "YOUR_GEMINI_SECRET_HERE"

# Permissions needed:
# - Trader (minimum)
# - IP restrictions recommended

# Test command: python3 -c "import ccxt; exchange = ccxt.gemini({'apiKey': 'KEY', 'secret': 'SECRET'}); print(exchange.fetch_balance())"
"""
    
    with open("secure/gemini_config.py.template", "w") as f:
        f.write(gemini_template)
    
    # Binance template
    binance_template = """# BINANCE API CONFIGURATION
# Store your actual API keys in .binance_key and .binance_secret files
# DO NOT commit these files to version control

API_KEY = "YOUR_BINANCE_API_KEY_HERE"
API_SECRET = "YOUR_BINANCE_SECRET_HERE"

# Permissions needed:
# - Enable Spot & Margin Trading
# - IP restrictions recommended
# - Disable withdrawal permissions

# Test command: python3 -c "import ccxt; exchange = ccxt.binance({'apiKey': 'KEY', 'secret': 'SECRET'}); print(exchange.fetch_balance())"
"""
    
    with open("secure/binance_config.py.template", "w") as f:
        f.write(binance_template)
    
    # Create .gitignore for security
    gitignore = """.gemini_key
.gemini_secret
.binance_key
.binance_secret
secure/*.key
secure/*.secret
*.log
__pycache__/
"""
    
    with open(".gitignore", "a") as f:
        f.write("\n# API Keys - DO NOT COMMIT\n")
        f.write(gitignore)
    
    print("✅ Created secure templates in 'secure/' directory")
    print("✅ Updated .gitignore to exclude API keys")
    
    return True

def create_test_connection_script():
    """Create script to test exchange connections"""
    print("\n" + "="*60)
    print("CREATING CONNECTION TEST SCRIPTS")
    print("="*60)
    
    test_script = """#!/usr/bin/env python3
"""
    return test_script

def create_exchange_comparison():
    """Create exchange comparison guide"""
    print("\n" + "="*60)
    print("EXCHANGE COMPARISON GUIDE")
    print("="*60)
    
    comparison = {
        "gemini": {
            "pros": [
                "US-based & regulated",
                "Good for USD pairs",
                "Simple API",
                "Insurance on assets"
            ],
            "cons": [
                "Limited coin selection",
                "Higher fees (0.35% taker)",
                "Less liquidity for alts",
                "Fewer trading pairs"
            ],
            "fees": "0.35% taker / 0.25% maker",
            "pairs": ["BTC/USD", "ETH/USD", "SOL/USD", "LINK/USD"],
            "minimum": "$0.01",
            "recommended_for": "Conservative USD trading"
        },
        "binance": {
            "pros": [
                "Massive liquidity",
                "Low fees (0.1% taker)",
                "Hundreds of pairs",
                "Advanced order types"
            ],
            "cons": [
                "Not US-regulated",
                "Complex API",
                "Withdrawal restrictions",
                "Geographic limitations"
            ],
            "fees": "0.1% taker / 0.1% maker (with BNB discount)",
            "pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "100+ more"],
            "minimum": "Varies by pair",
            "recommended_for": "Active trading with variety"
        }
    }
    
    with open("exchange_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)
    
    print("✅ exchange_comparison.json")
    
    print("\n📊 QUICK COMPARISON:")
    print("Gemini: Regulated, USD pairs, higher fees")
    print("Binance: Massive liquidity, low fees, many pairs")
    
    return comparison

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("REAL EXCHANGE CONNECTION SETUP")
    print("="*60)
    print("Connect your Gemini/Binance for REAL $100 trading")
    print("="*60)
    
    try:
        # Create instructions
        instructions = create_secure_instructions()
        
        # Save instructions
        with open("EXCHANGE_SETUP_GUIDE.txt", "w") as f:
            f.write(instructions)
        print("✅ EXCHANGE_SETUP_GUIDE.txt")
        
        # Create templates
        create_api_key_templates()
        
        # Create comparison
        comparison = create_exchange_comparison()
        
        print("\n" + "="*60)
        print("✅ EXCHANGE SETUP READY")
        print("="*60)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Read EXCHANGE_SETUP_GUIDE.txt")
        print(f"2. Choose: Gemini or Binance")
        print(f"3. Create API keys on exchange website")
        print(f"4. Store keys securely in workspace")
        print(f"5. Restart trading system")
        
        print(f"\n📊 RECOMMENDATION:")
        print(f"• Binance: Better for active trading (more pairs, lower fees)")
        print(f"• Gemini: Simpler, regulated")
        
        print(f"\n🔐 SECURITY:")
        print(f"• Keys stored in .gemini_key/.gemini_secret or .binance_*")
        print(f"• Files excluded from git via .gitignore")
        print(f"• Read-only trading permissions recommended")
        
        print(f"\n🚀 READY FOR REAL TRADING!")
        print(f"Once keys are added, system trades with REAL $100")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()