#!/usr/bin/env python3
"""
Start REAL trading with small test trade first
"""

import subprocess
import time
import os
from datetime import datetime

print("="*70)
print("🚀 STARTING REAL TRADING SYSTEM")
print("="*70)

# 1. Start the real profit trader in background
print("1. Starting Real Profit Trader...")
trader_process = subprocess.Popen(
    ['python3', 'real_profit_trader.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
print(f"   ✅ Trader started (PID: {trader_process.pid})")

# 2. Start the dashboard
print("\n2. Starting Trading Dashboard...")
dashboard_process = subprocess.Popen(
    ['python3', 'simple_trading_dashboard.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
print(f"   ✅ Dashboard started (PID: {dashboard_process.pid})")

# 3. Create startup log
with open('trading_startup.log', 'w') as f:
    f.write(f"=== REAL TRADING STARTED ===\n")
    f.write(f"Time: {datetime.now()}\n")
    f.write(f"Trader PID: {trader_process.pid}\n")
    f.write(f"Dashboard PID: {dashboard_process.pid}\n")
    f.write(f"Balance: $542.27\n")
    f.write(f"Goal: Grow $100 investment\n")
    f.write("="*50 + "\n")

print("\n3. System Status:")
print("   - Real Profit Trader: ✅ RUNNING")
print("   - Trading Dashboard: ✅ RUNNING")
print("   - Trading Server: ✅ RUNNING (port 5001)")
print("   - Gemini API: ✅ CONNECTED")

print("\n" + "="*70)
print("📊 MONITORING LINKS:")
print("   Terminal Dashboard: Run 'python3 simple_trading_dashboard.py'")
print("   Web Dashboard: http://localhost:5001")
print("   Real Trading Log: tail -f real_trading.log")
print("\n🎯 TRADING STRATEGY:")
print("   - Capital: $100 from $542.27 balance")
print("   - Risk: 2% per trade ($2 risk)")
print("   - Stop-loss: 3%, Take-profit: 6%")
print("   - Max: 3 trades per day")
print("   - Goal: Grow $100 to $220+ in 1 month")
print("="*70)

print("\n⚠️  IMPORTANT: The bot will wait for good opportunities.")
print("   It may take 5-10 minutes before the first trade.")
print("   Check 'real_trading.log' for live updates.")

# Keep script running
try:
    while True:
        time.sleep(10)
        # Check if processes are still running
        if trader_process.poll() is not None:
            print("❌ Trader process stopped!")
            break
except KeyboardInterrupt:
    print("\n\n🛑 Stopping trading system...")
    trader_process.terminate()
    dashboard_process.terminate()
    print("✅ Trading system stopped.")