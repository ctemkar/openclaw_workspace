#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

load_dotenv()

key = os.getenv('BINANCE_API_KEY')
secret = os.getenv('BINANCE_API_SECRET')

print("Testing Binance API connection...")
print(f"Key: {key[:10]}...{key[-4:] if len(key) > 14 else ''}")
print(f"Secret: {secret[:10]}...{secret[-4:] if len(secret) > 14 else ''}")

try:
    # Try testnet first
    print("\n1. Testing Binance Testnet...")
    client = Client(key, secret, testnet=True)
    
    try:
        account = client.get_account()
        print("✅ Testnet SUCCESS!")
        print(f"   Account type: {account.get('accountType', 'N/A')}")
        print(f"   Balances: {len(account.get('balances', []))}")
        testnet_ok = True
    except BinanceAPIException as e:
        print(f"❌ Testnet error {e.code}: {e.message}")
        testnet_ok = False
    
    # Try mainnet
    print("\n2. Testing Binance Mainnet...")
    client = Client(key, secret)
    
    try:
        account = client.get_account()
        print("✅ Mainnet SUCCESS!")
        print(f"   Account type: {account.get('accountType', 'N/A')}")
        
        # Show some balances
        balances = account.get('balances', [])
        non_zero = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
        print(f"   Non-zero balances: {len(non_zero)}")
        
        for b in non_zero[:3]:
            free = float(b['free'])
            locked = float(b['locked'])
            total = free + locked
            if total > 0:
                print(f"     • {b['asset']}: {total:.8f}")
        
        # Test market data
        print("\n3. Testing market data...")
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        print(f"✅ Market data OK - BTC/USDT: ${ticker['price']}")
        
        mainnet_ok = True
        
    except BinanceAPIException as e:
        print(f"❌ Mainnet error {e.code}: {e.message}")
        
        # Error explanations
        errors = {
            -2008: "Invalid Api-Key ID - Key doesn't exist or was deleted",
            -2015: "Invalid API-key, IP, or permissions - Check IP whitelist",
            -2014: "API-key format invalid",
            -1022: "Signature invalid - Check secret key",
            -1013: "Create order failed",
            -1003: "Too many requests"
        }
        
        if e.code in errors:
            print(f"   📖 Meaning: {errors[e.code]}")
        
        mainnet_ok = False
        
except Exception as e:
    print(f"❌ General error: {type(e).__name__}: {e}")
    mainnet_ok = False

print("\n" + "="*50)
if mainnet_ok:
    print("🎉 RESULT: API KEYS ARE WORKING!")
    print("The keys are valid. The problem might be in the bot's code.")
elif testnet_ok:
    print("⚠️ RESULT: Testnet works but Mainnet doesn't")
    print("Keys might be restricted to testnet only")
else:
    print("🚨 RESULT: API KEYS ARE NOT WORKING")
    print("You need to regenerate keys on Binance.com")