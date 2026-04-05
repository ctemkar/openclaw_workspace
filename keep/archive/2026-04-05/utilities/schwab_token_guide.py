#!/usr/bin/env python3
"""
STEP-BY-STEP GUIDE: How to get Schwab Access Token
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔑 STEP-BY-STEP GUIDE: GET SCHWAB ACCESS TOKEN")
print("=" * 60)

print("\n🎯 YOU NEED THIS FOR REAL TRADING!")
print("   Without access token → Bot is SIMULATED")
print("   With access token → Bot does REAL API calls")

print("\n📱 STEP 1: Go to Schwab Developer Portal")
print("   URL: https://developer.schwab.com")
print("   Login with your Schwab account credentials")

print("\n👤 STEP 2: Navigate to Your Application")
print("   After login, look for:")
print("   - 'My Apps' or 'Applications'")
print("   - 'API Management'")
print("   - 'Token Management'")
print("   - 'Developer Dashboard'")

print("\n🔑 STEP 3: Find Token Generation")
print("   Look for buttons like:")
print("   - 'Generate Token'")
print("   - 'Create Access Token'")
print("   - 'Get Token'")
print("   - 'OAuth2 Tokens'")

print("\n⚙️ STEP 4: Configure Token (IMPORTANT!)")
print("   When generating token, set:")
print("   - Scope: 'read_account' AND 'trade'")
print("   - Expiration: 30 days (for testing)")
print("   - Permissions: Read & Trade")

print("\n📋 STEP 5: Copy the Token")
print("   You'll see something like:")
print("   Access Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
print("   Copy the ENTIRE token (it's long!)")

print("\n📝 STEP 6: Add to Your .env File")
print("   Open .env file in this folder")
print("   Add this line:")
print("   SCHWAB_ACCESS_TOKEN=your_copied_token_here")
print("")
print("   Example:")
print("   SCHWAB_ACCESS_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")

print("\n🔄 STEP 7: Restart the Forex Bot")
print("   The bot will automatically detect the token")
print("   And attempt REAL API calls!")

print("\n🔍 CAN'T FIND TOKEN GENERATION?")
print("   Try these alternative paths:")
print("   1. Check 'API Keys' → 'Generate Token'")
print("   2. Look for 'Sandbox' vs 'Production' tokens")
print("   3. Check if app needs to be 'approved' first")
print("   4. Contact Schwab API support")

print("\n🎯 QUICK CHECK: Your Current Credentials")
api_key = os.getenv('SCHWAB_API_KEY')
account_id = os.getenv('SCHWAB_ACCOUNT_ID')
print(f"   API Key: {api_key[:20]}...")
print(f"   Account ID: {account_id}")
print(f"   ✅ These look valid!")

print("\n🚨 TROUBLESHOOTING:")
print("   If no 'Generate Token' button:")
print("   1. Make sure app is 'Active' or 'Approved'")
print("   2. Check 'Permissions' are set correctly")
print("   3. May need to enable 'Trading' permission")
print("   4. Some apps require manual approval by Schwab")

print("\n💡 PRO TIP:")
print("   Generate TWO tokens:")
print("   1. Short token (1 hour) for quick testing")
print("   2. Long token (30 days) for development")
print("   Test with short token first!")

print("\n🎉 ONCE YOU HAVE THE TOKEN:")
print("   1. Bot fetches REAL $225 balance (not hardcoded)")
print("   2. Can execute REAL trades")
print("   3. No more simulation warnings!")
print("   4. REAL trading begins!")

print("\n📞 NEED HELP?")
print("   Schwab API Documentation: https://developer.schwab.com/docs")
print("   Support: api@schwab.com")
print("   Or ask me for more specific guidance!")

# Show current .env structure
print("\n📄 YOUR CURRENT .env FILE:")
with open('.env', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if 'SCHWAB' in line:
            print(f"   {line.strip()}")

print("\n➕ ADD THIS LINE TO .env:")
print("   SCHWAB_ACCESS_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")