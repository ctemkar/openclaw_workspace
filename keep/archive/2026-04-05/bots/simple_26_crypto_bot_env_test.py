#!/usr/bin/env python3
"""
Test version - Simple 26-Crypto Trading Bot with .env support
"""

import os
import sys

# Manually load .env file
def load_env():
    """Load environment variables from .env file"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Loaded .env file")
        return True
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return False

def main():
    print("🔐 Testing .env integration for trading bot")
    print("=" * 50)
    
    # Load .env
    if not load_env():
        print("\n🚨 Cannot continue without .env file")
        return
    
    # Check critical variables
    required_vars = [
        'GEMINI_API_KEY',
        'GEMINI_API_SECRET',
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET'
    ]
    
    print("\n🔑 Checking environment variables:")
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first/last few chars
            display = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
            print(f"✅ {var}: {display} (length: {len(value)})")
        else:
            print(f"❌ {var}: MISSING")
            all_present = False
    
    if not all_present:
        print("\n🚨 Missing required API keys!")
        print("   Make sure .env has all 4 keys:")
        print("   GEMINI_API_KEY, GEMINI_API_SECRET")
        print("   BINANCE_API_KEY, BINANCE_API_SECRET")
        return
    
    print("\n🎉 SUCCESS: All API keys loaded from .env!")
    print("\n📋 Next steps:")
    print("1. Update the actual trading bot (simple_26_crypto_bot.py)")
    print("2. Replace file reading with os.getenv() calls")
    print("3. Test the bot still trades correctly")
    print("4. Update other bot files gradually")
    
    # Example of how to use in code
    print("\n💡 Example usage in trading bot:")
    print("""
# OLD WAY (insecure):
# with open('secure_keys/.gemini_key', 'r') as f:
#     api_key = f.read().strip()

# NEW WAY (secure):
import os
api_key = os.getenv('GEMINI_API_KEY')
api_secret = os.getenv('GEMINI_API_SECRET')
""")

if __name__ == "__main__":
    main()