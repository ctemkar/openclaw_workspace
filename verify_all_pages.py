#!/usr/bin/env python3
"""
VERIFY ALL PAGES - Final check
"""

import requests
import time

print("✅ VERIFYING ALL WEB PAGES ARE WORKING")
print("="*60)

# Check dashboard
print("1. Checking dashboard (port 5025)...")
try:
    response = requests.get("http://localhost:5025", timeout=5)
    if response.status_code == 200 and "Trading Dashboard" in response.text:
        print("   ✅ Dashboard working")
    else:
        print(f"   ❌ Dashboard error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Dashboard error: {e}")

# Check gateway
print("2. Checking gateway (port 5001)...")
try:
    response = requests.get("http://localhost:5001", timeout=5)
    if response.status_code == 200:
        print("   ✅ Gateway working")
    else:
        print(f"   ❌ Gateway error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Gateway error: {e}")

# Check dashboard endpoints
print("3. Checking dashboard endpoints...")
endpoints = [
    ("/logs", "text/plain"),
    ("/status", "application/json"),
]

for endpoint, content_type in endpoints:
    try:
        response = requests.get(f"http://localhost:5025{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ {endpoint} working ({content_type})")
        else:
            print(f"   ❌ {endpoint} error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {endpoint} error: {e}")

# Check bot is running
print("4. Checking bot is running...")
try:
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    bot_count = 0
    for line in result.stdout.split('\n'):
        if 'microsecond_arbitrage_bot.py' in line:
            bot_count += 1
            print(f"   ✅ Bot running: {line[:80]}")
    
    if bot_count == 0:
        print("   ❌ No bots running")
    else:
        print(f"   ✅ {bot_count} bot(s) running")
except Exception as e:
    print(f"   ❌ Error checking bots: {e}")

print("\n" + "="*60)
print("🎯 PROACTIVE VERIFICATION COMPLETE")
print("="*60)
print("✅ What I should have done from the start:")
print("   1. TEST web pages after creating them")
print("   2. VERIFY endpoints actually work")
print("   3. CHECK for crashes or timeouts")
print("   4. FIX issues immediately")
print("="*60)