#!/usr/bin/env python3
import requests
import time
import re

print("Testing dashboard fix...")
time.sleep(3)

try:
    response = requests.get("http://localhost:5002", timeout=10)
    html = response.text
    
    print("\n=== DASHBOARD STATUS ===")
    
    # Find risk parameters section
    if "Risk Parameters" in html:
        print("✅ Risk Parameters section found")
        
        # Extract using regex
        patterns = {
            "Stop Loss": r'Stop Loss.*?(\d+\.?\d*)%',
            "Take Profit": r'Take Profit.*?(\d+\.?\d*)%', 
            "Position Size": r'Position Size.*?(\d+\.?\d*)%',
            "Max Daily Trades": r'Max Daily Trades.*?(\d+)',
            "Strategy": r'Strategy:(.*?)</p>',
            "Execution Mode": r'Execution Mode:(.*?)</p>'
        }
        
        for label, pattern in patterns.items():
            match = re.search(pattern, html, re.DOTALL)
            if match:
                value = match.group(1).strip()
                print(f"  {label}: {value}")
            else:
                print(f"  {label}: NOT FOUND")
    
    # Check for "999" (unlimited trades)
    if "999" in html:
        print("\n✅ UNLIMITED TRADES (999) CONFIRMED!")
    elif "2" in re.search(r'Max Daily Trades.*?(\d+)', html, re.DOTALL).group(1) if re.search(r'Max Daily Trades.*?(\d+)', html, re.DOTALL) else "":
        print("\n❌ STILL SHOWING 2 TRADES LIMIT!")
    else:
        print("\n⚠️  Could not verify trade limit")
        
    # Check execution mode
    if "REAL TRADING - LIVE" in html:
        print("✅ REAL TRADING - LIVE confirmed")
    elif "SIMULATION" in html:
        print("❌ STILL SHOWING SIMULATION!")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== EXPECTED VALUES ===")
print("Stop Loss: 5.0%")
print("Take Profit: 10.0%")
print("Position Size: 20% (not 50%)")
print("Max Daily Trades: 999 (UNLIMITED)")
print("Strategy: Conservative Dip Buying (REAL)")
print("Execution Mode: ✅ REAL TRADING - LIVE")