#!/usr/bin/env python3
"""
Simple Alpaca test without external dependencies
"""
import os
from dotenv import load_dotenv
import requests
import json

print("🔍 SIMPLE ALPACA API TEST")
print("=" * 60)

# Load environment variables
load_dotenv()

# Get Alpaca keys
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

if not api_key or not api_secret:
    print("❌ ERROR: Alpaca API keys not found in .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")
print(f"✅ API Secret found: {api_secret[:10]}...")

# Test endpoints
endpoints = [
    ("LIVE Trading", "https://api.alpaca.markets/v2/account"),
    ("PAPER Trading", "https://paper-api.alpaca.markets/v2/account"),
]

headers = {
    "APCA-API-KEY-ID": api_key,
    "APCA-API-SECRET-KEY": api_secret
}

for name, url in endpoints:
    print(f"\n🔗 Testing {name} endpoint...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            account_data = response.json()
            print(f"✅ {name} CONNECTED SUCCESSFULLY!")
            print(f"   Account ID: {account_data.get('id', 'N/A')}")
            print(f"   Status: {account_data.get('status', 'N/A')}")
            print(f"   Buying Power: ${account_data.get('buying_power', 'N/A')}")
            print(f"   Cash: ${account_data.get('cash', 'N/A')}")
            print(f"   Portfolio Value: ${account_data.get('portfolio_value', 'N/A')}")
            print(f"   Trading Blocked: {account_data.get('trading_blocked', 'N/A')}")
            
            # Determine account type
            if "paper" in url:
                account_type = "PAPER TRADING (Not real money)"
            else:
                account_type = "LIVE TRADING (REAL MONEY)"
                
            print(f"   Account Type: {account_type}")
            
        else:
            print(f"❌ {name} failed: HTTP {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:100]}")
                
    except Exception as e:
        print(f"❌ {name} connection error: {e}")

print("\n🎯 SUMMARY:")
print("1. If LIVE trading works → REAL MONEY trading available")
print("2. If PAPER trading works → SIMULATED trading only")
print("3. If both fail → API keys invalid/expired")
print("\n🚨 IMPORTANT: Based on account type, we will:")
print("   - LIVE: Trade with REAL money (no simulations)")
print("   - PAPER: Label as 'PAPER TRADING' (no deception)")
print("   - NEVER hardcode or simulate profits")