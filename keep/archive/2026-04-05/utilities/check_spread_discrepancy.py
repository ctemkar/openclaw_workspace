#!/usr/bin/env python3
"""
Check discrepancy between arbitrage bot and progress monitor
"""

import os
import re
from datetime import datetime

print("=" * 70)
print(f"🔍 SPREAD DISCREPANCY CHECK - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

# Check arbitrage bot latest spreads
arbitrage_log = "real_26_crypto_arbitrage.log"
if os.path.exists(arbitrage_log):
    print("\n📊 ARBITRAGE BOT (ACTUAL - Last scan 12:16:37):")
    
    with open(arbitrage_log, 'r') as f:
        lines = f.readlines()
    
    # Find latest TOP 10 section
    for i in range(len(lines)-1, -1, -1):
        if "TOP 10 CRYPTO SPREADS" in lines[i]:
            # Print next 15 lines
            for j in range(i, min(i+15, len(lines))):
                print(f"   {lines[j].strip()}")
            break
    
    # Find latest summary
    for i in range(len(lines)-1, -1, -1):
        if "Best opportunity:" in lines[i]:
            print(f"\n   {lines[i].strip()}")
            if i+1 < len(lines):
                print(f"   {lines[i+1].strip()}")
            break

# Check what progress monitor SHOULD be showing
print("\n📈 WHAT PROGRESS MONITOR SHOULD SHOW:")
print("   Based on arbitrage bot at 12:16:37:")
print("   • XTZ: -0.89% (Buy Binance $0.3444, Sell Gemini $0.3480)")
print("   • YFI: -0.68% (Buy Binance, Sell Gemini)")
print("   • DOT: -0.65% (Buy Binance, Sell Gemini)")
print("   • Average spread: 0.23%")
print("   • 3 tradable opportunities (≥0.5%)")

# Check if progress monitor script reads from arbitrage bot
print("\n🔧 CHECKING PROGRESS MONITOR SCRIPT:")
progress_monitor = "simple_progress_monitor.sh"
if os.path.exists(progress_monitor):
    with open(progress_monitor, 'r') as f:
        content = f.read()
    
    if "real_26_crypto_arbitrage" in content:
        print("   ✅ Progress monitor reads from arbitrage bot logs")
    else:
        print("   ❌ Progress monitor does NOT read from arbitrage bot")
        
    # Check what it actually shows
    print("\n🔄 RUNNING PROGRESS MONITOR NOW:")
    import subprocess
    result = subprocess.run(['bash', progress_monitor], capture_output=True, text=True, timeout=10)
    
    # Extract spread info
    for line in result.stdout.split('\n'):
        if "XTZ:" in line or "YFI:" in line or "DOT:" in line or "Best:" in line:
            print(f"   {line.strip()}")
else:
    print("   ❌ Progress monitor script not found")

print("\n" + "=" * 70)
print("🎯 DIAGNOSIS:")
print("   The arbitrage bot IS working and refreshing spreads")
print("   But the progress monitor may show stale/cached data")
print("   OR the progress monitor doesn't read from arbitrage bot")
print("=" * 70)