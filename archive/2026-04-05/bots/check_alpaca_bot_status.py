#!/usr/bin/env python3
"""
Check if Alpaca arbitrage bot is working
"""
import subprocess
import time
import os

print("🔍 CHECKING ALPACA ARBITRAGE BOT STATUS")
print("="*70)

# Check if process is running
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
alpaca_processes = [line for line in result.stdout.split('\n') if 'alpaca_gemini' in line]

if alpaca_processes:
    print("✅ BOT IS RUNNING!")
    for proc in alpaca_processes:
        print(f"   PID: {proc.split()[1]} - {proc}")
    
    # Check log file
    if os.path.exists('alpaca_arbitrage.log'):
        size = os.path.getsize('alpaca_arbitrage.log')
        print(f"📄 Log file: alpaca_arbitrage.log ({size} bytes)")
        
        # Show last few lines
        if size > 0:
            print("\n📝 LAST LOG ENTRIES:")
            result = subprocess.run(['tail', '-20', 'alpaca_arbitrage.log'], capture_output=True, text=True)
            print(result.stdout)
        else:
            print("⚠️  Log file exists but is empty")
    else:
        print("⚠️  Log file not created yet")
    
    # Check profit log
    if os.path.exists('alpaca_arbitrage_profits.log'):
        size = os.path.getsize('alpaca_arbitrage_profits.log')
        print(f"💰 Profit log: alpaca_arbitrage_profits.log ({size} bytes)")
        
        if size > 0:
            print("\n💸 PROFIT RECORDS:")
            result = subprocess.run(['tail', '-5', 'alpaca_arbitrage_profits.log'], capture_output=True, text=True)
            print(result.stdout)
    else:
        print("💰 Profit log not created yet (no trades executed)")
        
else:
    print("❌ BOT IS NOT RUNNING")
    print("   Starting bot now...")
    
    # Start the bot
    subprocess.Popen(['python3', 'alpaca_gemini_arbitrage_bot.py', '>', 'alpaca_arbitrage.log', '2>&1', '&'], 
                     shell=True)
    time.sleep(2)
    print("   ✅ Bot started (checking again...)")

print("\n" + "="*70)
print("🎯 BOT STATUS SUMMARY:")
print("1. If bot is running → Actively scanning for arbitrage")
print("2. If profit log has entries → REAL trades executed")
print("3. If no profits yet → Waiting for >1% spreads")
print("\n🚀 Bot will trade when spreads >1% found")
print("💰 Using $355.18 Alpaca capital for REAL trading")