#!/usr/bin/env python3
"""
Test REAL Schwab API with provided credentials
"""
import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

# Get credentials
api_key = os.getenv('SCHWAB_API_KEY')
api_secret = os.getenv('SCHWAB_API_SECRET')
account_id = os.getenv('SCHWAB_ACCOUNT_ID')

print("🔍 Testing REAL Schwab API credentials...")
print(f"API Key (first 20 chars): {api_key[:20]}...")
print(f"API Secret (first 20 chars): {api_secret[:20]}...")
print(f"Account ID: {account_id}")

# Check if these look like real Schwab credentials
# Schwab typically uses OAuth2 with client_id (App Key) format
# Example: C1234567890abcdef1234567890abcdef

print("\n📋 Checking credential format:")
if api_key.startswith('C') and len(api_key) == 32:
    print("✅ API Key format looks like Schwab App Key (32 chars, starts with C)")
else:
    print(f"⚠️  API Key format unusual: {len(api_key)} chars, starts with '{api_key[:1]}'")

if len(api_secret) > 30:
    print(f"✅ API Secret length looks reasonable: {len(api_secret)} chars")
else:
    print(f"⚠️  API Secret length unusual: {len(api_secret)} chars")

# Schwab OAuth2 endpoints
token_url = "https://api.schwabapi.com/v1/oauth/token"
base_url = "https://api.schwabapi.com"

print("\n🔗 Attempting OAuth2 token request...")
print("Note: Schwab API requires OAuth2 authorization code flow")
print("We need to:")
print("1. Get authorization code (user login via browser)")
print("2. Exchange code for access token")
print("3. Use token for API calls")

# Basic test - try to get token with client credentials
try:
    # Encode client credentials
    credentials = f"{api_key}:{api_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "read_account"
    }
    
    print(f"\n📤 Sending request to: {token_url}")
    response = requests.post(token_url, headers=headers, data=data, timeout=10)
    
    print(f"📥 Response status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print("🎉 SUCCESS! Got access token!")
        print(f"Token type: {token_data.get('token_type')}")
        print(f"Expires in: {token_data.get('expires_in')} seconds")
        
        # Now try to get account info
        access_token = token_data['access_token']
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        accounts_url = f"{base_url}/trader/v1/accounts/{account_id}"
        print(f"\n🔗 Fetching account info: {accounts_url}")
        account_response = requests.get(accounts_url, headers=headers, timeout=10)
        
        print(f"Account response: {account_response.status_code}")
        if account_response.status_code == 200:
            account_data = account_response.json()
            print("🎉 SUCCESS! Got account data!")
            print(f"Account: {json.dumps(account_data, indent=2)[:500]}...")
        else:
            print(f"Account error: {account_response.text[:200]}")
            
    else:
        print(f"❌ Token request failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📋 Next steps:")
    print("1. Check if credentials need to be activated on developer.schwab.com")
    print("2. May need authorization code flow (user login via browser)")
    print("3. Check API documentation for correct grant_type")