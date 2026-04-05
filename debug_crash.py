#!/usr/bin/env python3
"""Debug why make_money_now.py keeps crashing"""

import os
import sys
import traceback

print("="*70)
print("🔧 DEBUGGING BOT CRASH PATTERNS")
print("="*70)

# First, let's check the script for obvious issues
script_path = "scripts/make_money_now.py"
print(f"\n📄 Analyzing {script_path}...")

# Check for common crash patterns
common_issues = []

# 1. Check imports
print("\n🔍 Checking imports...")
try:
    with open(script_path, 'r') as f:
        content = f.read()
        
    # Check for problematic imports
    imports_to_check = ['ccxt', 'time', 'logging', 'json', 'datetime']
    for imp in imports_to_check:
        if f'import {imp}' in content or f'from {imp}' in content:
            print(f"   ✅ {imp} imported")
        else:
            print(f"   ⚠️  {imp} not imported (might cause issues)")
            
except Exception as e:
    print(f"   ❌ Error reading script: {e}")

# 2. Check API key loading
print("\n🔍 Checking API key loading logic...")
try:
    # Look for the load_binance_keys function
    lines = content.split('\n')
    in_load_func = False
    for i, line in enumerate(lines):
        if 'def load_binance_keys' in line:
            in_load_func = True
            print(f"   📍 Found load_binance_keys at line {i+1}")
        elif in_load_func and line.strip() == '':
            in_load_func = False
        elif in_load_func:
            if 'open(' in line and 'binance_key' in line:
                print(f"   📍 Line {i+1}: {line.strip()}")
                if '../' not in line and 'scripts/' in os.getcwd():
                    common_issues.append("PATH_ISSUE: Keys path wrong when run from scripts/")
                    
except Exception as e:
    print(f"   ❌ Error analyzing key loading: {e}")

# 3. Check balance check logic
print("\n🔍 Checking balance check logic...")
try:
    for i, line in enumerate(lines):
        if 'def check_balance' in line:
            print(f"   📍 Found check_balance at line {i+1}")
            # Show next few lines
            for j in range(i+1, min(i+10, len(lines))):
                print(f"      {j+1}: {lines[j]}")
            break
except Exception as e:
    print(f"   ❌ Error analyzing balance check: {e}")

# 4. Check main loop
print("\n🔍 Checking main trading loop...")
try:
    for i, line in enumerate(lines):
        if 'def run(' in line:
            print(f"   📍 Found run() method at line {i+1}")
            # Check for infinite loop
            loop_lines = lines[i:i+50]
            for j, loop_line in enumerate(loop_lines):
                if 'while True' in loop_line or 'while 1' in loop_line:
                    print(f"   🔄 Found infinite loop at line {i+j+1}")
                    break
            break
except Exception as e:
    print(f"   ❌ Error analyzing main loop: {e}")

# 5. Check exception handling
print("\n🔍 Checking exception handling...")
try:
    exception_count = 0
    for i, line in enumerate(lines):
        if 'try:' in line or 'except ' in line or 'finally:' in line:
            exception_count += 1
    print(f"   📊 Found {exception_count} exception handling blocks")
    
    if exception_count < 5:
        common_issues.append("INSUFFICIENT_ERROR_HANDLING: Not enough try/except blocks")
        
except Exception as e:
    print(f"   ❌ Error analyzing exception handling: {e}")

print("\n" + "="*70)
print("🚨 COMMON CRASH CAUSES IDENTIFIED:")
print("="*70)

if common_issues:
    for i, issue in enumerate(common_issues, 1):
        print(f"{i}. {issue}")
else:
    print("✅ No obvious crash patterns found in code analysis")

print("\n🎯 MOST LIKELY CRASH CAUSES:")
print("1. PATH ISSUE: Bot looks for keys in wrong location when run from scripts/")
print("2. API ERROR: Binance API returns error (rate limit, invalid key, etc.)")
print("3. NETWORK ISSUE: Connection timeout or interruption")
print("4. MEMORY LEAK: Infinite accumulation of data")
print("5. UNHANDLED EXCEPTION: Crashes without recovery")

print("\n🔧 RECOMMENDED FIXES:")
print("1. Fix path: Use absolute paths or os.path.join()")
print("2. Add retry logic: Exponential backoff for API calls")
print("3. Add heartbeat: Monitor bot health and restart if dead")
print("4. Better logging: Capture crashes with tracebacks")
print("5. Supervision: Use systemd or supervisor to auto-restart")

print("\n" + "="*70)
print("💡 IMMEDIATE ACTION: Create a supervisor script that:")
print("   1. Monitors bot process")
print("   2. Restarts on crash")
print("   3. Logs crashes with details")
print("   4. Sends alerts if crashes too frequently")
print("="*70)