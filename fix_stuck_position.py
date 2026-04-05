#!/usr/bin/env python3
"""
Fix stuck YFI position by either:
1. Selling the YFI to free up capital, OR
2. Modifying the bot to recognize and sell the position
"""

import os
import sys
import time
from datetime import datetime

def check_bot_logs():
    """Check current bot status from logs"""
    print("📋 Checking bot logs...")
    
    try:
        with open('make_money_now.log', 'r') as f:
            lines = f.readlines()[-20:]  # Last 20 lines
        
        yfi_position = None
        usdt_balance = None
        
        for line in lines:
            if 'YFI: 0.011770' in line or '0.01177 YFI' in line:
                yfi_position = 0.01177
            if 'Binance balance: $' in line:
                # Extract balance
                import re
                match = re.search(r'\$(\d+\.\d+)', line)
                if match:
                    usdt_balance = float(match.group(1))
        
        return yfi_position, usdt_balance
        
    except FileNotFoundError:
        print("❌ make_money_now.log not found")
        return None, None

def propose_solutions(yfi_position, usdt_balance):
    """Propose solutions based on current situation"""
    print(f"\n📊 Current Situation:")
    print(f"  USDT Balance: ${usdt_balance:.2f}" if usdt_balance else "  USDT Balance: Unknown")
    print(f"  YFI Position: {yfi_position:.6f}" if yfi_position else "  YFI Position: Unknown")
    
    if yfi_position and usdt_balance:
        print(f"\n💰 Total Portfolio: ${usdt_balance + (yfi_position * 2423):.2f} (est)")
    
    print("\n🎯 Proposed Solutions:")
    print("1. MANUAL FIX: Log into Binance and sell 0.01177 YFI")
    print("2. BOT FIX: Modify make_money_now.py to:")
    print("   a. Check for existing YFI positions before buying")
    print("   b. Sell existing positions if USDT balance is low")
    print("   c. Increase settlement wait time to 30+ seconds")
    print("3. STOP & RESTART: Stop bot, sell manually, then restart with fix")
    
    return [
        "Manual sell on Binance",
        "Modify bot code",
        "Stop bot and restart"
    ]

def create_manual_instructions():
    """Create step-by-step manual instructions"""
    print("\n📝 MANUAL RESOLUTION INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to https://www.binance.com")
    print("2. Log into your account")
    print("3. Go to Spot Wallet")
    print("4. Find YFI in your assets")
    print("5. Click 'Trade' → 'Sell YFI'")
    print("6. Enter amount: 0.01177")
    print("7. Use MARKET order for quick execution")
    print("8. Confirm the sale")
    print("9. Verify USDT balance increases by ~$28.52")
    print("10. Trading bot will automatically resume")
    print("=" * 50)

def create_bot_fix():
    """Create a fix for the bot"""
    print("\n🔧 BOT FIX SCRIPT:")
    print("=" * 50)
    
    fix_code = '''
# ADD TO make_money_now.py AFTER BALANCE CHECK:

# Check for existing YFI position
yfi_balance = balance.get('YFI', {}).get('free', 0)
if yfi_balance > 0.001:
    print(f"⚠️ Found existing YFI position: {yfi_balance:.6f}")
    print("🚀 Selling existing YFI first...")
    try:
        sell_order = exchange.create_market_sell_order('YFI/USDT', yfi_balance)
        print(f"✅ YFI sold: {sell_order}")
        time.sleep(10)  # Wait for settlement
        # Refresh balance
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        print(f"💰 New USDT balance: ${usdt_balance:.2f}")
    except Exception as e:
        print(f"❌ Failed to sell YFI: {e}")
        return  # Don't proceed with new trade

# INCREASE SETTLEMENT WAIT TIME:
# Change from: time.sleep(5)
# To: time.sleep(30)  # Longer settlement for YFI
'''
    
    print(fix_code)
    print("=" * 50)
    
    # Offer to create the fix file
    response = input("\nCreate fix file? (y/n): ")
    if response.lower() == 'y':
        with open('bot_fix.py', 'w') as f:
            f.write(fix_code)
        print("✅ Created bot_fix.py")

def main():
    print("🔧 STUCK POSITION FIXER")
    print("=" * 50)
    
    yfi_position, usdt_balance = check_bot_logs()
    solutions = propose_solutions(yfi_position, usdt_balance)
    
    print("\nChoose an option:")
    for i, solution in enumerate(solutions, 1):
        print(f"{i}. {solution}")
    print("4. Show all instructions")
    
    try:
        choice = int(input("\nYour choice (1-4): "))
        
        if choice == 1:
            create_manual_instructions()
        elif choice == 2:
            create_bot_fix()
        elif choice == 3:
            print("\n🛑 STOP BOT INSTRUCTIONS:")
            print("1. Find bot PID: ps aux | grep make_money_now")
            print("2. Stop bot: kill <PID>")
            print("3. Follow manual instructions to sell YFI")
            print("4. Restart bot: python3 scripts/make_money_now.py")
        elif choice == 4:
            create_manual_instructions()
            create_bot_fix()
            print("\n🛑 STOP BOT INSTRUCTIONS (see option 3)")
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Please enter a number")

if __name__ == "__main__":
    main()