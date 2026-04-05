#!/usr/bin/env python3
"""Test Binance balance check from correct directory"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_make_money_balance_check():
    """Test the balance check from make_money_now.py"""
    try:
        # Import the trading bot
        from scripts.make_money_now import MakeMoneyNowBot
        
        print("="*60)
        print("🔍 TESTING BINANCE BALANCE CHECK")
        print("="*60)
        
        # Create bot instance
        bot = MakeMoneyNowBot()
        
        # Check balance
        print("\n💰 Checking Binance balance...")
        has_sufficient_balance = bot.check_balance()
        
        if has_sufficient_balance:
            print("✅ SUFFICIENT BALANCE - Trading should start!")
        else:
            print("❌ INSUFFICIENT BALANCE - Trading won't start")
            
        return has_sufficient_balance
        
    except Exception as e:
        logger.error(f"❌ Error testing balance check: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_make_money_balance_check()
    print("\n" + "="*60)
    if result:
        print("🎯 RESULT: Trading SHOULD be running")
    else:
        print("🎯 RESULT: Trading WON'T start (insufficient balance)")
    print("="*60)