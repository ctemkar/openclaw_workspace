#!/usr/bin/env python3
"""
CHECK ALL WEB PAGES - Proactive verification
"""

import requests
import time

print("🔍 CHECKING ALL WEB PAGES")
print("="*60)

pages_to_check = [
    ("Dashboard 5025", "http://localhost:5025"),
    ("Gateway 5001", "http://localhost:5001"),
    ("Dashboard 5024", "http://localhost:5024"),
    ("Dashboard 5026", "http://localhost:5026"),
    ("Dashboard 5027", "http://localhost:5027"),
    ("Bot Logs", "http://localhost:5025/logs"),
    ("Bot Status", "http://localhost:5025/status"),
]

working = []
not_working = []

for name, url in pages_to_check:
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            working.append((name, url, response.status_code))
            print(f"✅ {name}: {url} (Status: {response.status_code})")
            # Show first line of content
            first_line = response.text.split('\n')[0][:50]
            print(f"   Content: {first_line}...")
        else:
            not_working.append((name, url, response.status_code))
            print(f"⚠️ {name}: {url} (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        not_working.append((name, url, str(e)))
        print(f"❌ {name}: {url} (Error: {e})")
    
    time.sleep(0.5)

print("\n" + "="*60)
print("📊 SUMMARY:")
print(f"✅ Working: {len(working)} pages")
print(f"❌ Not working: {len(not_working)} pages")

if not_working:
    print("\n🔧 PAGES NEEDING FIX:")
    for name, url, error in not_working:
        print(f"   - {name}: {url} ({error})")

print("\n" + "="*60)
print("🎯 PROACTIVE FIXES NEEDED:")
print("1. Restart gateway on port 5001")
print("2. Restart dashboards on ports 5024, 5026, 5027")
print("3. Add proper endpoints to dashboard (logs, status)")
print("4. Test ALL pages after fixes")
print("="*60)