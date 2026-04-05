#!/usr/bin/env python3
"""
Check Schwab OAuth2 authorization flow requirements
"""
import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('SCHWAB_API_KEY')
api_secret = os.getenv('SCHWAB_API_SECRET')
account_id = os.getenv('SCHWAB_ACCOUNT_ID')

print("🔍 Schwab OAuth2 Flow Analysis")
print("=" * 50)

print("\n📋 Based on Schwab API documentation:")
print("1. Schwab uses OAuth2 Authorization Code Grant")
print("2. Requires user login via browser (for security)")
print("3. Steps:")
print("   a. Redirect user to Schwab authorization URL")
print("   b. User logs in and approves application")
print("   c. Schwab redirects back with authorization code")
print("   d. Exchange code for access token")
print("   e. Use token for API calls")

print("\n🔗 Authorization URL would look like:")
auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?response_type=code&client_id={api_key}&redirect_uri=http://localhost:8080/callback"
print(f"   {auth_url}")

print("\n⚠️  Current issue:")
print("   We got a token with client_credentials grant")
print("   But it doesn't work for account access (401 error)")
print("   Need authorization_code grant for account-level access")

print("\n🎯 Next steps for REAL trading:")
print("1. Implement OAuth2 authorization code flow")
print("2. Create web server for callback (localhost:8080)")
print("3. User logs in via browser once")
print("4. Get refresh token for long-term access")
print("5. Implement token refresh logic")
print("6. THEN we can make REAL API calls")

print("\n📞 Alternative: Use Schwab's 'Token Management'")
print("   Some users generate tokens via Schwab website")
print("   Then use those tokens directly")
print("   Check if you have 'Access Token' and 'Refresh Token'")
print("   in your Schwab developer dashboard")