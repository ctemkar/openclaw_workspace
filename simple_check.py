#!/usr/bin/env python3
import requests

# First check trading server
print("1. Checking Trading Server (port 5001):")
try:
    resp = requests.get("http://localhost:5001/status", timeout=5)
    data = resp.json()
    print(f"   Max trades per day: {data.get('risk_parameters', {}).get('max_trades_per_day', 'NOT FOUND')}")
except:
    print("   ❌ Could not connect to trading server")

# Now start dashboard and check
print("\n2. Starting dashboard and checking...")
import subprocess
import time
import os

# Start dashboard in background
dashboard = subprocess.Popen(
    ["python3", "enhanced_trading_dashboard.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=os.path.dirname(os.path.abspath(__file__))
)

time.sleep(3)  # Give it time to start

try:
    resp = requests.get("http://localhost:5002", timeout=5)
    html = resp.text
    
    # Quick check for key values
    print("   Dashboard loaded")
    
    # Check for 999
    if '>999<' in html or '>999</div>' in html or 'value="999"' in html:
        print("   ✅ MAX DAILY TRADES: 999 (UNLIMITED)")
    else:
        print("   ❌ Max daily trades not showing 999")
        
    # Check for 20% position size
    if '>20%<' in html or '>20</div>' in html:
        print("   ✅ POSITION SIZE: 20%")
    else:
        print("   ❌ Position size not showing 20%")
        
    # Check for REAL TRADING
    if 'REAL TRADING - LIVE' in html:
        print("   ✅ REAL TRADING - LIVE")
    else:
        print("   ❌ Not showing REAL TRADING - LIVE")
        
finally:
    # Kill dashboard
    dashboard.terminate()
    dashboard.wait()
    print("\nDashboard stopped")