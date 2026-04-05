#!/usr/bin/env python3
"""Run the actual balance check from make_money_now.py"""

import os
import sys
import importlib.util

# Change to scripts directory
os.chdir('scripts')

# Load the make_money_now module
spec = importlib.util.spec_from_file_location("make_money_now", "make_money_now.py")
module = importlib.util.module_from_spec(spec)

# Execute the module to load the class
spec.loader.exec_module(module)

# Get the MakeMoneyBot class
MakeMoneyBot = module.MakeMoneyBot

print("="*60)
print("🔍 RUNNING ACTUAL BINANCE BALANCE CHECK")
print("="*60)

# Create bot instance
bot = MakeMoneyBot()

# Check balance
print("\n💰 Checking Binance balance...")
has_sufficient_balance = bot.check_balance()

print("\n" + "="*60)
if has_sufficient_balance:
    print("✅ SUFFICIENT BALANCE - Trading should start!")
    print("💰 If trading isn't starting, check the main loop logic.")
else:
    print("❌ INSUFFICIENT BALANCE - Trading won't start")
    print("💡 Need to deposit funds to reach minimum trade size")
print("="*60)