#!/usr/bin/env python3
"""
CHECK EXACT DASHBOARD CONTENT
"""

import requests
import time

print("🔍 CHECKING EXACT DASHBOARD CONTENT")
print("="*60)

url = "http://localhost:5025"

try:
    # Make request with no cache
    response = requests.get(url, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }, timeout=5)
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)} chars")
    
    # Look for timestamps
    content = response.text
    
    print("\n🔍 SEARCHING FOR TIMESTAMPS:")
    
    # Check for 15:03 (old)
    if "15:03" in content:
        print("❌ FOUND OLD TIMESTAMP: '15:03'")
        # Show context
        idx = content.find("15:03")
        print(f"   Context: {content[max(0, idx-50):idx+50]}")
    else:
        print("✅ NO OLD TIMESTAMP '15:03' found")
    
    # Check for current time
    current_hour = time.strftime("%H")
    if f"{current_hour}:" in content:
        print(f"✅ FOUND CURRENT HOUR: '{current_hour}:'")
        # Find all timestamps
        import re
        timestamps = re.findall(r'\d{2}:\d{2}:\d{2}', content)
        if timestamps:
            print(f"   Timestamps in page: {timestamps}")
    else:
        print(f"❌ NO CURRENT HOUR '{current_hour}:' found")
    
    # Check for key phrases
    print("\n🔍 CHECKING KEY PHRASES:")
    phrases = [
        ("Dashboard Fixed", "OLD dashboard"),
        ("Trading Dashboard", "NEW dashboard"),
        ("Microsecond nonce working", "Your fix mentioned"),
        ("Symbol mismatch fixed", "Symbol fix mentioned"),
        ("Proactive fix applied", "Old message"),
    ]
    
    for phrase, description in phrases:
        if phrase in content:
            print(f"✅ '{phrase}' - {description}")
        else:
            print(f"❌ '{phrase}' NOT FOUND")
    
    # Show first 500 chars
    print(f"\n📄 FIRST 500 CHARACTERS:")
    print(content[:500])
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎯 CONCLUSION:")
print("If you see '15:03', you're either:")
print("1. Viewing a CACHED version")
print("2. On a DIFFERENT port")
print("3. The dashboard CRASHED and old one came back")
print("="*60)