#!/usr/bin/env python3
"""
Test Alpaca Paper AND Live environments
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Alpaca credentials
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

print("🔍 TESTING ALPACA API - BOTH ENVIRONMENTS")
print(f"API Key (first 8 chars): {api_key[:8]}...")
print(f"Secret (first 8 chars): {api_secret[:8]}...")
print()

if not api_key or not api_secret:
    print("❌ ERROR: ALPACA API keys not found in .env file")
    exit(1)

headers = {
    'APCA-API-KEY-ID': api_key,
    'APCA-API-SECRET-KEY': api_secret
}

# Test PAPER trading
print("📊 Testing PAPER Trading (https://paper-api.alpaca.markets)...")
try:
    response = requests.get('https://paper-api.alpaca.markets/v2/account', headers=headers, timeout=10)
    if response.status_code == 200:
        account = response.json()
        print("✅ PAPER TRADING WORKING!")
        print(f"   Status: {account.get('status', 'N/A')}")
        print(f"   Buying Power: ${account.get('buying_power', '0')}")
    else:
        print(f"❌ Paper Trading Error: {response.status_code}")
        if response.text:
            print(f"   Message: {response.text[:100]}")
except Exception as e:
    print(f"❌ Paper Trading Connection Error: {e}")

print()

# Test LIVE trading
print("📊 Testing LIVE Trading (https://api.alpaca.markets)...")
try:
    response = requests.get('https://api.alpaca.markets/v2/account', headers=headers, timeout=10)
    if response.status_code == 200:
        account = response.json()
        print("✅ LIVE TRADING WORKING!")
        print(f"   Status: {account.get('status', 'N/A')}")
        print(f"   Buying Power: ${account.get('buying_power', '0')}")
    else:
        print(f"❌ Live Trading Error: {response.status_code}")
        if response.text:
            print(f"   Message: {response.text[:100]}")
except Exception as e:
    print(f"❌ Live Trading Connection Error: {e}")

print()

# Test if keys might be for different broker
print("🔧 POSSIBLE SOLUTIONS:")
print("1. Check if you're using PAPER or LIVE trading keys")
print("2. Login to https://app.alpaca.markets")
print("3. Go to 'Paper Trading' section for paper keys")
print("4. Go to 'Live Trading' section for live keys")
print("5. Make sure account is ACTIVE (not restricted)")