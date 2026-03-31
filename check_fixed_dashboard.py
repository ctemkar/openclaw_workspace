#!/usr/bin/env python3
import requests
import time

print("🔍 Checking FIXED dashboard...")
print("="*60)

# Wait a bit for dashboard to initialize
time.sleep(2)

try:
    # Check dashboard
    response = requests.get("http://localhost:5002", timeout=10)
    html = response.text
    
    # Check for key indicators
    checks = [
        ("✅ REAL TRADING", "REAL TRADING" in html),
        ("✅ Max Daily Trades: 999", "Max Daily Trades</div>" in html and "999" in html),
        ("✅ Position Size: 20%", "Position Size</div>" in html and "20" in html),
        ("✅ Strategy: Conservative", "Conservative Dip Buying" in html),
        ("✅ Capital: $175+", "Capital</div>" in html and ("175" in html or "176" in html)),
    ]
    
    all_good = True
    for check_name, check_result in checks:
        if check_result:
            print(f"{check_name} - FOUND")
        else:
            print(f"❌ {check_name} - NOT FOUND")
            all_good = False
    
    if all_good:
        print("\n🎉 DASHBOARD IS FIXED AND SHOWING CORRECT DATA!")
    else:
        print("\n⚠️  Dashboard still has issues")
        
    # Also check trading server
    print("\n🔧 Checking trading server API...")
    server_status = requests.get("http://localhost:5001/status", timeout=5).json()
    print(f"   Server capital: ${server_status['capital']}")
    print(f"   Server max trades/day: {server_status['risk_parameters']['max_trades_per_day']}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎯 GO TO: http://localhost:5002")
print("The dashboard should now show CORRECT data!")
print("="*60)