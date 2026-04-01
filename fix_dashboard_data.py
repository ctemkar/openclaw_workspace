#!/usr/bin/env python3
"""
Fix dashboard data structure to match what the dashboard expects
"""

import os
import json
from datetime import datetime

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"
TRADING_DATA_DIR = os.path.join(BASE_DIR, "trading_data")

print("🔧 FIXING DASHBOARD DATA STRUCTURE")
print("="*60)

# Read our updated data
try:
    with open(os.path.join(TRADING_DATA_DIR, "capital.json"), 'r') as f:
        capital_data = json.load(f)
    
    with open(os.path.join(TRADING_DATA_DIR, "pnl.json"), 'r') as f:
        pnl_data = json.load(f)
    
    with open(os.path.join(TRADING_DATA_DIR, "positions.json"), 'r') as f:
        positions_data = json.load(f)
    
except FileNotFoundError as e:
    print(f"❌ Missing data file: {e}")
    exit(1)

# Create the data structure the dashboard expects
dashboard_data = {
    "api": {
        "capital_allocation": {
            "total": capital_data["total_capital"],
            "gemini": capital_data["gemini_total"],
            "binance": capital_data["binance_total"],
            "deployed": capital_data["deployed"],
            "available_total": capital_data["available_gemini"] + capital_data["available_binance"],
            "available_gemini": capital_data["available_gemini"],
            "available_binance": capital_data["available_binance"],
            "position_count": capital_data["position_count"],
            "avg_position_value": capital_data["avg_position_value"],
            "pnl": capital_data["total_pnl"],  # This is what the dashboard looks for!
            "pnl_percent": capital_data["pnl_percent"],
            "last_updated": capital_data["last_updated"]
        },
        "cumulative_pnl": {
            "current": capital_data["total_capital"],
            "free_usd": capital_data["available_gemini"],
            "btc_holdings": 0,  # No BTC holdings
            "overall_pnl": capital_data["total_pnl"],
            "overall_pnl_percent": capital_data["pnl_percent"]
        },
        "positions": positions_data["positions"],
        "exchange_status": {
            "gemini": "operational",
            "binance": "operational"
        }
    },
    "timestamp": datetime.now().isoformat()
}

# Write to system_status.json (what the dashboard reads)
system_status_file = os.path.join(BASE_DIR, "system_status.json")
with open(system_status_file, 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print(f"✅ Updated {system_status_file}")
print(f"   Total capital: ${dashboard_data['api']['capital_allocation']['total']:.2f}")
print(f"   P&L: ${dashboard_data['api']['capital_allocation']['pnl']:.2f}")
print(f"   P&L %: {dashboard_data['api']['capital_allocation']['pnl_percent']:.2f}%")
print(f"   Gemini: ${dashboard_data['api']['capital_allocation']['gemini']:.2f}")
print(f"   Binance: ${dashboard_data['api']['capital_allocation']['binance']:.2f}")
print(f"   Positions: {dashboard_data['api']['capital_allocation']['position_count']}")

# Also update the old capital.json with pnl field for backward compatibility
capital_data_with_pnl = capital_data.copy()
capital_data_with_pnl["pnl"] = capital_data["total_pnl"]
capital_data_with_pnl["pnl_percent"] = capital_data["pnl_percent"]

with open(os.path.join(TRADING_DATA_DIR, "capital.json"), 'w') as f:
    json.dump(capital_data_with_pnl, f, indent=2)

print(f"\n✅ Also updated capital.json with pnl field for compatibility")

print("\n" + "="*60)
print("✅ DASHBOARD DATA STRUCTURE FIXED!")
print("="*60)
print("\nThe dashboard should now work with the updated data structure.")
print("Restart the dashboard to see the real data.")