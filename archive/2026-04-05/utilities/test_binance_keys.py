#!/usr/bin/env python3
"""
Simple Binance API Key Test Script
Tests if the current Binance API keys in .env file are working
"""

import os
import sys
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

def test_binance_keys():
    """Test Binance API keys from .env file"""
    
    print("🔍 TESTING BINANCE API KEYS")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    binance_key = os.getenv('BINANCE_API_KEY')
    binance_secret = os.getenv('BINANCE_API_SECRET')
    
    print(f"📋 Key loaded: {'Yes' if binance_key else 'No'}")
    print(f"📋 Secret loaded: {'Yes' if binance_secret else 'No'}")
    
    if not binance_key or not binance_secret:
        print("❌ ERROR: Missing API key or secret in .env file")
        print("   Make sure BINANCE_API_KEY and BINANCE_API_SECRET are set")
        return False
    
    print(f"🔑 Key length: {len(binance_key)} characters")
    print(f"🔑 Secret length: {len(binance_secret)} characters")
    print(f"🔑 Key starts with: {binance_key[:10]}...")
    
    try:
        print("\n🔄 Connecting to Binance API...")
        
        # Test with testnet first (safer)
        print("1️⃣ Testing with Binance Testnet...")
        testnet_client = Client(binance_key, binance_secret, testnet=True)
        
        try:
            account = testnet_client.get_account()
            print("   ✅ Testnet connection SUCCESSFUL!")
            print(f"   📊 Testnet account type: {account.get('accountType', 'N/A')}")
            print(f"   💰 Testnet balances: {len(account.get('balances', []))} assets")
        except BinanceAPIException as e:
            print(f"   ❌ Testnet error: {e.code} - {e.message}")
            print("   ⚠️  Testnet failed, trying mainnet...")
            
            # Try mainnet
            print("\n2️⃣ Testing with Binance Mainnet...")
            mainnet_client = Client(binance_key, binance_secret)
            
            try:
                account = mainnet_client.get_account()
                print("   ✅ Mainnet connection SUCCESSFUL!")
                print(f"   📊 Account type: {account.get('accountType', 'N/A')}")
                
                # Show balances
                balances = account.get('balances', [])
                print(f"   💰 Total assets: {len(balances)}")
                
                # Show non-zero balances
                non_zero = [b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
                print(f"   📈 Non-zero balances: {len(non_zero)}")
                
                for balance in non_zero[:5]:  # Show first 5
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    if total > 0:
                        print(f"     • {balance['asset']}: {total:.8f} (free: {free:.8f}, locked: {locked:.8f})")
                
                if len(non_zero) > 5:
                    print(f"     ... and {len(non_zero) - 5} more")
                    
                # Test market data
                print("\n3️⃣ Testing market data access...")
                ticker = mainnet_client.get_symbol_ticker(symbol="BTCUSDT")
                print(f"   ✅ Market data working!")
                print(f"   📊 BTC/USDT price: ${ticker['price']}")
                
                return True
                
            except BinanceAPIException as e:
                print(f"   ❌ Mainnet error: {e.code} - {e.message}")
                
                # Common error codes
                error_guide = {
                    -2008: "Invalid Api-Key ID - Key doesn't exist or was deleted",
                    -2015: "Invalid API-key, IP, or permissions - Check IP whitelist",
                    -2014: "API-key format invalid",
                    -1022: "Signature for this request is not valid",
                    -1013: "Create order failed",
                    -1003: "Too many requests"
                }
                
                if e.code in error_guide:
                    print(f"   📖 Error meaning: {error_guide[e.code]}")
                
                return False
                
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

def check_env_file():
    """Check .env file contents"""
    print("\n📄 CHECKING .ENV FILE")
    print("=" * 50)
    
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
        binance_lines = [l for l in lines if 'BINANCE' in l.upper()]
        
        if binance_lines:
            print("✅ .env file found with Binance credentials")
            for line in binance_lines[:2]:  # Show first 2 lines
                if 'KEY' in line.upper() or 'SECRET' in line.upper():
                    # Hide full secret for security
                    parts = line.strip().split('=')
                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1]
                        if 'SECRET' in key.upper():
                            display = value[:10] + "..." + value[-4:] if len(value) > 14 else "***hidden***"
                        else:
                            display = value[:10] + "..." + value[-4:] if len(value) > 14 else value
                        print(f"   {key}={display}")
        else:
            print("❌ No Binance credentials found in .env file")
    else:
        print("❌ .env file not found")

if __name__ == "__main__":
    print("\n" + "🚀 BINANCE API KEY TESTER" + "\n" + "=" * 50)
    
    check_env_file()
    print("\n" + "=" * 50)
    
    success = test_binance_keys()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RESULT: API KEYS ARE WORKING!")
        print("   The problem might be elsewhere (bot logic, IP restrictions, etc.)")
    else:
        print("🚨 RESULT: API KEYS ARE NOT WORKING")
        print("   You need to regenerate Binance API keys on Binance.com")
        print("   Steps:")
        print("   1. Log into Binance.com")
        print("   2. Go to API Management")
        print("   3. Create new API key")
        print("   4. Update .env file with new key/secret")
        print("   5. Restart trading bots")
    
    print("\n💡 TIP: If keys work here but not in bot, check:")
    print("   • IP whitelist settings on Binance")
    print("   • Bot's trading logic/error handling")
    print("   • VPN/network restrictions")
    print("=" * 50)