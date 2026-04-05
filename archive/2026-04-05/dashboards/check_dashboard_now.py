#!/usr/bin/env python3
import requests
import re

print("🔍 Checking dashboard at http://localhost:5002")
print("="*60)

try:
    response = requests.get("http://localhost:5002", timeout=5)
    html = response.text
    
    # Extract key information
    patterns = {
        "Execution Mode": r'Execution Mode:(.*?)</p>',
        "Max Daily Trades": r'Max Daily Trades.*?>(\d+)<',
        "Position Size": r'Position Size.*?>(\d+)%<',
        "Strategy": r'Strategy:(.*?)</p>',
        "Capital": r'Capital.*?>(\$\d+\.?\d*)<',
        "Trades Today": r'Trades Today.*?>(\d+)<'
    }
    
    for label, pattern in patterns.items():
        match = re.search(pattern, html, re.DOTALL)
        if match:
            value = match.group(1).strip()
            print(f"✅ {label}: {value}")
        else:
            print(f"❌ {label}: NOT FOUND")
    
    # Check for simulation vs real
    if "SIMULATION" in html:
        print("\n🚨 WARNING: Dashboard shows SIMULATION mode!")
    if "REAL TRADING" in html:
        print("\n✅ GOOD: Dashboard shows REAL TRADING mode!")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("If you see 'SIMULATION' or wrong values, the dashboard")
print("is showing cached/wrong data. Refresh browser or check")
print("which dashboard you're viewing!")
print("="*60)