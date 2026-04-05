#!/usr/bin/env python3
"""
CLEANUP ARCHIVE - Stop running scripts from archive and organize
"""

import os
import subprocess
import time

print("="*70)
print("🧹 CLEANING UP ARCHIVE SCRIPTS")
print("="*70)

# Stop scripts running from archive locations
archive_scripts = [
    "multi_llm_trading_bot_fixed_order.py",
    "market_maker_analyzer.py",
    "auto_arbitrage_bot.py",  # This might be from archive too
]

print("🛑 Stopping archive scripts that are running...")
for script in archive_scripts:
    try:
        # Find and kill processes
        result = subprocess.run(['pkill', '-f', script], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Stopped: {script}")
        else:
            print(f"  ℹ️  Not running: {script}")
    except Exception as e:
        print(f"  ❌ Error stopping {script}: {e}")

time.sleep(2)

# Check what's still running from our essential scripts
print("\n📋 Checking essential scripts status...")
essential_scripts = [
    "gateway_5000.py",
    "truthful_dashboard.py", 
    "nocache_dashboard.py",
    "real_time_top10_dashboard.py",
    "make_money_now.py",
    "fixed_practical_profit_bot.py",
    "real_26_crypto_arbitrage_bot.py",
    "microsecond_arbitrage_bot.py",
    "practical_monitor_bot.py",
]

for script in essential_scripts:
    result = subprocess.run(['pgrep', '-f', script], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        print(f"  ✅ {script}: RUNNING")
    else:
        print(f"  ❌ {script}: NOT RUNNING")

print("\n📁 Archive organization:")
print("  Current archive: archive/unusable_scripts/ (new)")
print("  Old archives: keep/archive/ (legacy)")
print("  Recommendation: Keep old archives for reference, don't run from there")

print("\n🎯 RECOMMENDED STRUCTURE:")
print("  / (root) - ONLY essential running scripts")
print("  archive/unusable_scripts/ - Archived one-time scripts")
print("  keep/archive/ - Historical archives (read-only)")
print("  keep/logs/ - Log files")
print("  secure_keys/ - API keys (secure)")

print("\n✅ Cleanup complete!")
print("="*70)

# Create a simple run script for essential services
run_script = """#!/bin/bash
# RUN ALL ESSENTIAL SERVICES
echo "Starting essential trading system services..."

# Dashboards
python3 gateway_5000.py &
python3 truthful_dashboard.py &
python3 nocache_dashboard.py &
python3 real_time_top10_dashboard.py &

# Trading bots (if needed)
# python3 make_money_now.py &
# python3 fixed_practical_profit_bot.py &
# python3 real_26_crypto_arbitrage_bot.py &
# python3 microsecond_arbitrage_bot.py &

echo "Services started. Check ports:"
echo "  Gateway: http://localhost:5001"
echo "  Truthful Dashboard: http://localhost:5024"
echo "  Sorted Spreads: http://localhost:5025"
echo "  REAL-TIME Top 10: http://localhost:5026"
"""

with open("start_essential_services.sh", "w") as f:
    f.write(run_script)
    
os.chmod("start_essential_services.sh", 0o755)
print("📝 Created: start_essential_services.sh (run all dashboards)")
print("="*70)