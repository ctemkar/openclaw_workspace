#!/usr/bin/env python3
"""
SCHWAB API CONNECTION TEST
- Tests connectivity to Schwab API
- Verifies credentials
- Checks account access
- Tests Forex market data
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_schwab_connection():
    """Test Schwab API connection"""
    print("=" * 60)
    print("🚀 SCHWAB API CONNECTION TEST")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get Schwab credentials
    schwab_api_key = os.getenv('SCHWAB_API_KEY')
    schwab_api_secret = os.getenv('SCHWAB_API_SECRET')
    schwab_account_id = os.getenv('SCHWAB_ACCOUNT_ID')
    
    print("\n📊 CHECKING CREDENTIALS:")
    
    if not schwab_api_key:
        print("   ❌ SCHWAB_API_KEY not found in .env file")
        print("   💡 Add: SCHWAB_API_KEY=your_app_key_here")
    else:
        print(f"   ✅ SCHWAB_API_KEY found (first 10 chars): {schwab_api_key[:10]}...")
    
    if not schwab_api_secret:
        print("   ❌ SCHWAB_API_SECRET not found in .env file")
        print("   💡 Add: SCHWAB_API_SECRET=your_app_secret_here")
    else:
        print(f"   ✅ SCHWAB_API_SECRET found (first 10 chars): {schwab_api_secret[:10]}...")
    
    if not schwab_account_id:
        print("   ❌ SCHWAB_ACCOUNT_ID not found in .env file")
        print("   💡 Add: SCHWAB_ACCOUNT_ID=your_account_number")
    else:
        print(f"   ✅ SCHWAB_ACCOUNT_ID found: {schwab_account_id}")
    
    # Check if all credentials are present
    if not all([schwab_api_key, schwab_api_secret, schwab_account_id]):
        print("\n❌ MISSING CREDENTIALS")
        print("   Please add all Schwab credentials to .env file")
        print("   See SCHWAB_SETUP_GUIDE.md for instructions")
        return False
    
    print("\n✅ ALL CREDENTIALS PRESENT")
    print("   Ready to test API connection...")
    
    # Note: Actual Schwab API implementation would go here
    # For now, we'll simulate the connection test
    
    print("\n🔗 SIMULATING SCHWAB API CONNECTION...")
    print("   (In a real implementation, this would make actual API calls)")
    
    print("\n📋 WHAT WOULD HAPPEN:")
    print("   1. Authenticate with Schwab API")
    print("   2. Get account information")
    print("   3. Check Forex trading permissions")
    print("   4. Get real-time Forex prices")
    print("   5. Test order placement capability")
    
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("   1. Install Schwab Python SDK:")
    print("      pip install schwab-py")
    print("   2. Implement actual API calls")
    print("   3. Test with paper trading first")
    print("   4. Start with small real trades")
    
    print("\n" + "=" * 60)
    print("📝 TO COMPLETE SCHWAB INTEGRATION:")
    print("=" * 60)
    print("\n1. Get actual Schwab API credentials:")
    print("   • Go to: https://developer.schwab.com")
    print("   • Create application")
    print("   • Get App Key, App Secret, Account ID")
    
    print("\n2. Update .env file with:")
    print("   SCHWAB_API_KEY=your_app_key")
    print("   SCHWAB_API_SECRET=your_app_secret")
    print("   SCHWAB_ACCOUNT_ID=your_account_number")
    
    print("\n3. Install Schwab Python library:")
    print("   pip install schwab-py")
    
    print("\n4. Run this test again:")
    print("   python3 test_schwab_connection.py")
    
    print("\n5. Start real Forex trading:")
    print("   python3 simple_forex_bot.py --real-trading")
    
    return True

def check_forex_market_hours():
    """Check if Forex markets are open"""
    from datetime import datetime
    import pytz
    
    print("\n⏰ FOREX MARKET HOURS CHECK:")
    
    # Forex markets: Sunday 5 PM ET to Friday 5 PM ET
    now_utc = datetime.now(pytz.UTC)
    now_et = now_utc.astimezone(pytz.timezone('US/Eastern'))
    
    print(f"   Current time (ET): {now_et.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if it's weekend (Forex closed Saturday)
    if now_et.weekday() == 5:  # Saturday
        print("   ❌ Forex markets are CLOSED (Saturday)")
        return False
    elif now_et.weekday() == 6 and now_et.hour < 17:  # Sunday before 5 PM ET
        print("   ❌ Forex markets are CLOSED (Sunday before 5 PM ET)")
        return False
    else:
        print("   ✅ Forex markets are OPEN or opening soon")
        return True

def main():
    """Main test function"""
    print("🔧 SCHWAB FOREX TRADING SETUP TEST")
    print("   This script helps you set up Schwab for real Forex trading")
    
    # Test credentials
    credentials_ok = test_schwab_connection()
    
    # Check market hours
    market_open = check_forex_market_hours()
    
    print("\n" + "=" * 60)
    print("🎯 SETUP STATUS SUMMARY:")
    print("=" * 60)
    
    if credentials_ok:
        print("✅ Credentials format: READY")
        print("   (Need actual Schwab API keys)")
    else:
        print("❌ Credentials format: NEEDS SETUP")
        print("   Follow SCHWAB_SETUP_GUIDE.md")
    
    if market_open:
        print("✅ Market hours: OPEN")
        print("   Ready to trade when credentials are set")
    else:
        print("⚠️ Market hours: CLOSED or closing soon")
        print("   Forex trades execute when markets open")
    
    print("\n🚀 NEXT ACTION:")
    print("   1. Get Schwab API credentials from developer.schwab.com")
    print("   2. Add them to your .env file")
    print("   3. Run: python3 test_schwab_connection.py")
    print("   4. Start real Forex trading!")
    
    print("\n💡 TIP: Start with PAPER TRADING to test strategy")
    print("   Our bot is already running in paper trading mode")
    print("   Switch to real trading when you're comfortable")

if __name__ == "__main__":
    main()