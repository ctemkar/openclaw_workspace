import os
from dotenv import load_dotenv

load_dotenv()
print("Testing new Binance keys...")

key = os.getenv("BINANCE_API_KEY")
secret = os.getenv("BINANCE_API_SECRET")

print(f"Key: {key[:10]}...")
print(f"Secret: {secret[:10]}...")

try:
    import ccxt
    exchange = ccxt.binance({
        "apiKey": key,
        "secret": secret,
        "enableRateLimit": True
    })
    
    # Test 1: Market data
    print("\n1. Market data test:")
    ticker = exchange.fetch_ticker("BTC/USDT")
    print(f"   OK - BTC: ${ticker['last']}")
    
    # Test 2: Account access
    print("\n2. Account access test:")
    balance = exchange.fetch_balance()
    print(f"   SUCCESS! Keys work!")
    print(f"   Assets: {len(balance.get('total', {}))}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    if "Invalid API-key" in str(e):
        print("KEYS ARE INVALID!")
    elif "permissions" in str(e).lower():
        print("CHECK IP WHITELIST!")