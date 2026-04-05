#!/usr/bin/env python3
"""
TEST AUTO-RESTART FEATURE
Simulates killing a system to test if monitor auto-restarts it
"""

import subprocess
import time
import sys

print("🧪 TESTING AUTO-RESTART FEATURE")
print("="*50)

# First, let's check what's running
print("\n1. CURRENT SYSTEM STATUS:")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)

systems = [
    'arbitration_trading_dashboard.py',
    'simple_trading_dashboard.py',
    'forex_bot_with_schwab.py',
    'auto_arbitrage_bot.py',
    'practical_profit_bot.py',
    'market_maker_analyzer.py',
    'multi_llm_trading_bot_fixed_order.py'
]

for system in systems:
    if system in result.stdout:
        print(f"   ✅ {system}: RUNNING")
    else:
        print(f"   ❌ {system}: NOT RUNNING")

print("\n2. TEST PLAN:")
print("   I will kill the 'Practical Profit Bot'")
print("   The monitor should detect it's dead within 60 seconds")
print("   The monitor should AUTO-RESTART it automatically")
print("   No manual intervention needed!")

print("\n3. KILLING PRACTICAL PROFIT BOT...")
subprocess.run(['pkill', '-f', 'practical_profit_bot.py'])
time.sleep(2)

# Verify it's killed
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'practical_profit_bot.py' in result.stdout:
    print("   ❌ FAILED: Practical Profit Bot still running")
else:
    print("   ✅ SUCCESS: Practical Profit Bot killed")

print("\n4. MONITOR SHOULD NOW:")
print("   🔍 Detect the dead bot (within 60 seconds)")
print("   🚨 Send alert about the dead bot")
print("   🔄 AUTO-RESTART the bot automatically")
print("   ✅ Confirm bot is running again")

print("\n5. CHECK MONITOR LOGS:")
print("   The monitor logs are in: auto_monitor.log")
print("   Look for:")
print("   - 'Practical Profit Bot: ❌ STOPPED'")
print("   - '🔄 Attempting auto-restart for Practical Profit Bot'")
print("   - '✅ Auto-restart successful for Practical Profit Bot'")

print("\n6. MANUAL VERIFICATION (after 60 seconds):")
print("   Run: ps aux | grep practical_profit_bot.py")
print("   Should show the bot running again")

print("\n" + "="*50)
print("🎯 AUTO-RESTART TEST INITIATED!")
print("The monitor will handle everything automatically.")
print("No action needed from you! 🚀")