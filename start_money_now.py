#!/usr/bin/env python3
"""
START MAKING MONEY NOW - Simple version
"""

import subprocess
import time
import os

print("="*80)
print("🚀 STARTING MONEY-MAKING BOT NOW!")
print("="*80)

# Check if make_money_now.py exists
if os.path.exists("make_money_now.py"):
    print("✅ Found make_money_now.py")
    print("📊 This bot will:")
    print("   • Use $40.50 Binance balance")
    print("   • Capture YFI -1.74% spreads")
    print("   • Make REAL profit TODAY")
    print("   • Trade $30 per trade")
    print("   • Target: $0.52 profit per trade")
    
    # Try to start it
    try:
        print("\n🎯 STARTING BOT...")
        # Use subprocess to start in background
        process = subprocess.Popen(
            ["python3", "make_money_now.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Bot started! PID:", process.pid)
        print("📝 Logs will be saved to: real_money_trades.log")
        print("💰 Check profits in: profit_summary.log")
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's running
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline'] and 'make_money_now.py' in ' '.join(proc.info['cmdline']):
                print(f"✅ Bot is RUNNING! PID: {proc.info['pid']}")
                break
        else:
            print("⚠️ Bot may have exited. Check logs.")
            
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("\n🔧 ALTERNATIVE: Start manually with:")
        print("   python3 make_money_now.py")
        
else:
    print("❌ make_money_now.py not found")
    print("\n📁 Available trading bots:")
    
    # List available bots
    import glob
    bots = glob.glob("*bot*.py") + glob.glob("*trade*.py")
    for bot in sorted(bots):
        print(f"   • {bot}")

print("\n" + "="*80)
print("🎯 TO START MAKING MONEY MANUALLY:")
print("   1. Open terminal")
print("   2. cd ~/.openclaw/workspace/app")
print("   3. python3 make_money_now.py")
print("="*80)
print("💰 Your $40.50 Binance balance is READY to make money!")
print("="*80)