#!/usr/bin/env python3
"""
Test Alpaca API connection
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Alpaca credentials
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

print("🔍 TESTING ALPACA API CONNECTION")
print(f"API Key (first 8 chars): {api_key[:8]}...")
print(f"Secret (first 8 chars): {api_secret[:8]}...")
print()

if not api_key or not api_secret:
    print("❌ ERROR: ALPACA API keys not found in .env file")
    exit(1)

# Alpaca API endpoints
base_url = 'https://paper-api.alpaca.markets'
headers = {
    'APCA-API-KEY-ID': api_key,
    'APCA-API-SECRET-KEY': api_secret
}

try:
    print("📊 Testing: GET /v2/account...")
    response = requests.get(f'{base_url}/v2/account', headers=headers)
    
    if response.status_code == 200:
        account = response.json()
        print("✅ SUCCESS! Alpaca API is WORKING!")
        print(f"💰 Account Status: {account.get('status', 'N/A')}")
        print(f"💵 Buying Power: ${account.get('buying_power', '0')}")
        print(f"💸 Cash: ${account.get('cash', '0')}")
        print(f"📈 Portfolio Value: ${account.get('portfolio_value', '0')}")
        print(f"🏦 Equity: ${account.get('equity', '0')}")
        print()
        print("🎉 ALPACA API IS CONFIRMED WORKING!")
        print("🚀 Ready to start REAL trading!")
    else:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        print("Possible issues:")
        print("1. API keys incorrect")
        print("2. Paper trading account not enabled")
        print("3. Account restricted")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("Check internet connection and try again")