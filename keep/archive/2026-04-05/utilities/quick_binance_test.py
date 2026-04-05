import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("BINANCE_API_KEY")
secret = os.getenv("BINANCE_API_SECRET")

print("Testing Binance API keys...")
print(f"Key exists: {bool(key)}")
print(f"Secret exists: {bool(secret)}")

if not key or not secret:
    print("ERROR: Missing keys in .env")
    exit(1)

print(f"Key: {key[:10]}...")
print(f"Secret: {secret[:10]}...")

try:
    import ccxt
    print("\nCCXT imported successfully")
    
    exchange = ccxt.binance({
        "apiKey": key,
        "secret": secret,
        "enableRateLimit": True
    })
    
    print("\n1. Testing market data...")
    try:
        ticker = exchange.fetch_ticker("BTC/USDT")
        print(f"   OK - BTC: ${ticker['last']}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n2. Testing account access...")
    try:
        balance = exchange.fetch_balance()
        print(f"   OK - Got balance")
        total = balance.get("total", {})
        non_zero = {k:v for k,v in total.items() if v > 0}
        print(f"   Non-zero balances: {len(non_zero)}")
        for asset, amount in list(non_zero.items())[:3]:
            print(f"     {asset}: {amount}")
    except Exception as e:
        error_msg = str(e)
        print(f"   ERROR: {error_msg[:100]}")
        if "Invalid API-key" in error_msg or "invalid api-key" in error_msg.lower():
            print("\n🚨 CONFIRMED: API KEY IS INVALID!")
            print("You need to regenerate keys on Binance.com")
        elif "permissions" in error_msg.lower():
            print("\n⚠️  IP restriction or permissions issue")
            print("Check IP whitelist on Binance")
            
except ImportError:
    print("ERROR: ccxt not installed")
except Exception as e:
    print(f"ERROR: {e}")