#!/usr/bin/env python3
"""
EMERGENCY STOP ALL TRADING
"""

import os
import signal
import subprocess
import time
from datetime import datetime

print("🚨 EMERGENCY TRADING STOP 🚨")
print("="*60)
print("Reason: User reported BTC purchase on Gemini but")
print("        system logs show NO TRADES. MAJOR DISCREPANCY!")
print("="*60)

# List of trading bots to stop
trading_bots = [
    "simple_real_trader.py",
    "real_futures_trading_bot.py", 
    "fixed_futures_bot.py",
    "real_gemini_trader.py",
    "binance_futures_short_bot.py",
    "improved_26_crypto_bot.py",
    "26_crypto_trading_bot.py"
]

print("\n🔍 Checking for active trading bots...")
active_count = 0

for bot in trading_bots:
    # Find PIDs
    try:
        result = subprocess.run(
            ["pgrep", "-f", bot],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            pids = result.stdout.strip().split()
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"   ⏹️  Stopped {bot} (PID: {pid})")
                    active_count += 1
                    time.sleep(0.5)
                except:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"   💀 Killed {bot} (PID: {pid})")
                        active_count += 1
                    except:
                        print(f"   ❌ Could not stop {bot} (PID: {pid})")
    except:
        pass

if active_count == 0:
    print("   ✅ No active trading bots found")
else:
    print(f"\n📊 Stopped {active_count} trading bots")

# Keep monitoring/analysis tools running (but not trading)
keep_running = [
    "trading_server.py",  # API/dashboard
    "position_monitor.py",  # Monitoring only
    "enhanced_trading_dashboard.py",  # Dashboard
    "truth_dashboard.py"  # Truth dashboard
]

print("\n✅ Keeping these NON-TRADING services running:")
for service in keep_running:
    try:
        result = subprocess.run(
            ["pgrep", "-f", service],
            capture_output=True,
            text=True
        )
        if result.stdout:
            pids = result.stdout.strip().split()
            print(f"   📊 {service} (PID: {', '.join(pids)})")
    except:
        pass

print("\n" + "="*60)
print("🚫 ALL AUTOMATED TRADING HAS BEEN STOPPED")
print("")
print("NEXT STEPS:")
print("1. Check Gemini for REAL trade details")
print("2. Figure out where the trade came from")
print("3. Fix logging/tracking system")
print("4. Only restart trading AFTER discrepancy resolved")
print("="*60)
print(f"⏰ Emergency stop executed at: {datetime.now().strftime('%H:%M:%S')}")
print("="*60)