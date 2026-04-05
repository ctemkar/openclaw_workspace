#!/usr/bin/env python3
"""
Diagnose Schwab credentials and find where tokens are
"""
import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SCHWAB_API_KEY')
api_secret = os.getenv('SCHWAB_API_SECRET')
account_id = os.getenv('SCHWAB_ACCOUNT_ID')

print("🔍 DIAGNOSING SCHWAB CREDENTIALS")
print("=" * 60)

print(f"\n📋 Your credentials from .env:")
print(f"   API Key: {api_key[:20]}... ({len(api_key)} chars)")
print(f"   API Secret: {api_secret[:20]}... ({len(api_secret)} chars)")
print(f"   Account ID: {account_id}")

print("\n🎯 ANALYSIS:")
print("1. These look like OAuth2 'Client ID' and 'Client Secret'")
print("2. NOT like 'Access Token' (Access tokens start with 'eyJ' - JWT format)")
print("3. You need to EXCHANGE these for an Access Token")

print("\n🚨 THE PROBLEM:")
print("   Schwab website might not show 'Generate Token' because:")
print("   - These ARE the tokens (Client ID/Secret)")
print("   - You need to USE them to GET Access Token via OAuth2")
print("   - Not a button to click, but code to write")

print("\n🔧 WHAT'S ACTUALLY NEEDED:")
print("   OAuth2 Authorization Code Flow:")
print("   1. User goes to authorization URL (browser)")
print("   2. Logs in and approves app")
print("   3. Gets redirected with 'code'")
print("   4. Exchange 'code' for Access Token")
print("   5. Use Access Token for API calls")

print("\n🎯 LET ME TEST YOUR CREDENTIALS:")
try:
    # Try to get token with different grant types
    token_url = "https://api.schwabapi.com/v1/oauth/token"
    
    # Test 1: Client Credentials (we know this works but gives limited token)
    print("\n🔗 Test 1: Client Credentials Grant")
    credentials = f"{api_key}:{api_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials", "scope": "read_account"}
    
    response = requests.post(token_url, headers=headers, data=data, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"   ✅ Got token! Type: {token_data.get('token_type')}")
        print(f"   ⚠️  But this token may not work for account access")
        
        # Test if it works for account
        access_token = token_data['access_token']
        account_url = f"https://api.schwabapi.com/trader/v1/accounts/{account_id}"
        account_headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
        
        account_response = requests.get(account_url, headers=account_headers, timeout=10)
        print(f"   Account test: {account_response.status_code}")
        if account_response.status_code == 200:
            print("   🎉 SUCCESS! Token WORKS for account access!")
            print("   ⚠️  Wait... this contradicts earlier. Let me check...")
            print(f"   Response: {account_response.text[:200]}")
        else:
            print(f"   ❌ Account access failed: {account_response.status_code}")
            print(f"   Error: {account_response.text[:200]}")
    else:
        print(f"   ❌ Failed: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 POSSIBLE SOLUTIONS:")

print("\nOPTION A: Manual Token Generation (Easiest if available)")
print("   1. Check Schwab website for ANY token generation")
print("   2. Look in 'Sandbox' vs 'Production' sections")
print("   3. Check 'My Apps' → 'Trading Permissions'")

print("\nOPTION B: OAuth2 Flow Implementation (More work)")
print("   1. We implement browser login flow")
print("   2. You login once via browser")
print("   3. We get Access Token automatically")

print("\nOPTION C: Check Email from Schwab")
print("   1. When you registered app, Schwab might have emailed tokens")
print("   2. Check email for 'Schwab API Credentials'")
print("   3. Look for 'Access Token' or 'Refresh Token'")

print("\n🔍 LET'S CHECK: What DO you see on Schwab website?")
print("   Describe what you see after login:")
print("   - What menu options?")
print("   - What's in 'My Apps'?")
print("   - Any 'API Keys' section?")
print("   - Any 'Token Management'?")

print("\n📞 QUICK FIX: Contact Schwab Support")
print("   Email: api@schwab.com")
print("   Ask: 'I have Client ID/Secret but need Access Token for trading'")
print("   Include: Your App Name and these credentials")

print("\n💡 IMMEDIATE WORKAROUND:")
print("   While we figure this out, the bot will:")
print("   1. Continue simulated trading with $225")
print("   2. Be transparent about simulation")
print("   3. Ready to switch to REAL when we get token")