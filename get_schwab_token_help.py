#!/usr/bin/env python3
"""
Help get Schwab access token for REAL trading
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🎯 HOW TO GET SCHWAB ACCESS TOKEN FOR REAL TRADING")
print("=" * 60)

print("\n📋 You said: \"these keys were provided by developer.schwab.com\"")
print("   ✅ Great! We have real credentials.")

print("\n🔧 What's needed now:")
print("1. Go to https://developer.schwab.com")
print("2. Log into your account")
print("3. Go to 'Token Management' or 'My Apps'")
print("4. Find your application")
print("5. Generate an 'Access Token'")

print("\n📝 Token options:")
print("A. Short-lived token (1 hour) - for testing")
print("B. Long-lived token (30 days) - for development")
print("C. Refresh token - for automatic renewal")

print("\n🎯 EASIEST PATH TO REAL TRADING:")
print("1. Get any access token from Schwab website")
print("2. Add to .env file:")
print("   SCHWAB_ACCESS_TOKEN=your_token_here")
print("3. Restart Forex bot")
print("4. Bot will try REAL API calls!")

print("\n🔗 If you can't find token generation:")
print("1. Check 'API Keys' section")
print("2. Look for 'Generate Token' button")
print("3. May need to enable 'Trading' permissions")
print("4. Contact Schwab support if stuck")

print("\n💡 Alternative: OAuth2 Flow (More Complex)")
print("   We can implement full browser login flow")
print("   But manual token is faster for testing")

print("\n🚀 Once you have SCHWAB_ACCESS_TOKEN in .env:")
print("   The bot will attempt REAL API calls")
print("   Will fetch REAL $225 balance (not hardcoded)")
print("   Can potentially execute REAL trades")

# Check current .env
print("\n📄 Current .env file has:")
with open('.env', 'r') as f:
    for line in f:
        if 'SCHWAB' in line:
            print(f"   {line.strip()}")

print("\n🎯 ACTION: Add this line to .env:")
print("   SCHWAB_ACCESS_TOKEN=your_actual_token_from_schwab_website")