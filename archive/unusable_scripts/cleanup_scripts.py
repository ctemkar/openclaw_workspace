#!/usr/bin/env python3
"""
CLEANUP SCRIPTS - Move unusable scripts to archive
"""

import os
import shutil
from datetime import datetime

# Create archive directory
archive_dir = "archive/unusable_scripts"
os.makedirs(archive_dir, exist_ok=True)

# Scripts to KEEP (essential, currently used)
keep_scripts = [
    "gateway_5000.py",           # Gateway dashboard (port 5001)
    "truthful_dashboard.py",     # Truthful dashboard (port 5024)
    "nocache_dashboard.py",      # Sorted spreads (port 5025)
    "real_time_top10_dashboard.py",  # REAL-TIME top 10 (port 5026)
    "make_money_now.py",         # Main trading bot (ACTIVE)
    "fixed_practical_profit_bot.py",  # Practical bot (RUNNING)
    "real_26_crypto_arbitrage_bot.py",  # 26-crypto bot (RUNNING)
    "microsecond_arbitrage_bot.py",  # Microsecond bot (RUNNING)
    "practical_monitor_bot.py",  # Monitor bot (RUNNING)
    "cleanup_scripts.py",        # This script
]

# Scripts to ARCHIVE (unusable, duplicates, one-time fixes)
archive_patterns = [
    "check_*.py",      # One-time diagnostic scripts
    "verify_*.py",     # One-time verification scripts
    "test_*.py",       # Test scripts
    "fix_*.py",        # One-time fix scripts
    "reset_*.py",      # Reset scripts
    "restart_*.py",    # Restart scripts
]

# Specific scripts to archive
specific_archive = [
    "simple_working_dashboard.py",  # Duplicate dashboard
    "fixed_dashboard.py",           # Duplicate dashboard  
    "real_top_10_dashboard.py",     # Old version (replaced)
    "real_trading_bot.py",          # Old trading bot
    "start_money_now.py",           # Duplicate of make_money_now.py
]

print("="*70)
print("🧹 CLEANING UP UNUSABLE SCRIPTS")
print("="*70)

# List all Python files
all_scripts = [f for f in os.listdir('.') if f.endswith('.py')]
print(f"Found {len(all_scripts)} Python scripts")

# Archive scripts matching patterns
import glob
archived_count = 0

for pattern in archive_patterns:
    for script in glob.glob(pattern):
        if script not in keep_scripts and os.path.isfile(script):
            dest = os.path.join(archive_dir, script)
            shutil.move(script, dest)
            print(f"📦 Archived (pattern): {script}")
            archived_count += 1

# Archive specific scripts
for script in specific_archive:
    if os.path.exists(script):
        dest = os.path.join(archive_dir, script)
        shutil.move(script, dest)
        print(f"📦 Archived (specific): {script}")
        archived_count += 1

# List remaining scripts
remaining = [f for f in os.listdir('.') if f.endswith('.py')]
print(f"\n✅ Cleanup complete!")
print(f"📦 Archived: {archived_count} scripts")
print(f"📁 Remaining: {len(remaining)} scripts")

print("\n📋 REMAINING SCRIPTS (ESSENTIAL):")
for script in sorted(remaining):
    if script in keep_scripts:
        print(f"  ✅ {script} (KEPT - essential)")
    else:
        print(f"  ⚠️  {script} (Not in keep list, but not archived)")

print(f"\n📁 Archive location: {archive_dir}")
print("="*70)

# Create README in archive
readme_path = os.path.join(archive_dir, "README.md")
with open(readme_path, 'w') as f:
    f.write(f"""# Archived Scripts

## Archive Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Reason for Archive:
These scripts were archived because they are:
1. **One-time diagnostic/verification scripts**
2. **Duplicate implementations**
3. **Old versions replaced by newer scripts**
4. **Test scripts not needed for production**
5. **Temporary fix scripts**

## Current Essential Scripts (in root):
- `gateway_5000.py` - Gateway dashboard (port 5001)
- `truthful_dashboard.py` - Truthful dashboard (port 5024)
- `nocache_dashboard.py` - Sorted spreads dashboard (port 5025)
- `real_time_top10_dashboard.py` - REAL-TIME top 10 spreads (port 5026)
- `make_money_now.py` - Main trading bot (ACTIVE)
- `fixed_practical_profit_bot.py` - Practical profit bot (RUNNING)
- `real_26_crypto_arbitrage_bot.py` - 26-crypto arbitrage bot (RUNNING)
- `microsecond_arbitrage_bot.py` - Microsecond arbitrage bot (RUNNING)
- `practical_monitor_bot.py` - Practical monitor bot (RUNNING)

## Note:
Do NOT delete from archive without checking if script is truly obsolete.
Some scripts might be needed for reference or debugging.
""")

print(f"📝 Created README in archive: {readme_path}")
print("="*70)