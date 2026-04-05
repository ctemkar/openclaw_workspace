#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function directly
exec(open("enhanced_trading_dashboard.py").read())

# Call the function
print("Calling get_risk_parameters()...")
params = get_risk_parameters()
print("\n=== RETURNED VALUES ===")
for key, value in params.items():
    print(f"{key}: {value}")

print("\n=== VERIFICATION ===")
if params.get('max_daily_trades') == 999:
    print("✅ MAX DAILY TRADES: 999 (UNLIMITED)")
else:
    print(f"❌ MAX DAILY TRADES: {params.get('max_daily_trades')} (SHOULD BE 999)")

if params.get('position_size') == 20:
    print("✅ POSITION SIZE: 20% (CORRECT)")
else:
    print(f"❌ POSITION SIZE: {params.get('position_size')}% (SHOULD BE 20%)")

if params.get('real_trading') == True:
    print("✅ REAL TRADING: True")
else:
    print("❌ REAL TRADING: False (SHOULD BE TRUE)")