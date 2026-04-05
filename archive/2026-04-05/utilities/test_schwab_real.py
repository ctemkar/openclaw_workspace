#!/usr/bin/env python3
"""
Test REAL Schwab API connection
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Get credentials
api_key = os.getenv('SCHWAB_API_KEY')
api_secret = os.getenv('SCHWAB_API_SECRET')
account_id = os.getenv('SCHWAB_ACCOUNT_ID')

print(f"🔍 Testing Schwab API with:")
print(f"   API Key: {api_key[:10]}...")
print(f"   Account ID: {account_id}")

# Schwab API endpoints (from documentation)
# Note: Schwab uses OAuth2 - we need to get access token first
base_url = "https://api.schwabapi.com"

# Step 1: Get OAuth2 token
token_url = "https://api.schwabapi.com/v1/oauth/token"

# For testing, let's see if we can at least ping the API
try:
    print("🔗 Testing connection to Schwab API...")
    response = requests.get(f"{base_url}/v1/marketdata", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("   Need proper OAuth2 implementation")
    
print("\n📋 Next steps for REAL Schwab API:")
print("1. Register app at https://developer.schwab.com")
print("2. Get OAuth2 client_id and client_secret")
print("3. Implement OAuth2 flow (authorization code grant)")
print("4. Get access token")
print("5. Use token to make real API calls")
print("6. Fetch REAL balance (not hardcoded $225)")
