#!/usr/bin/env python3
import requests

print("Debugging dashboard data...")

# Check what the trading server returns
try:
    print("\n1. Trading Server API (/status):")
    response = requests.get("http://localhost:5001/status", timeout=5)
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Risk params: {data.get('risk_parameters', {})}")
    print(f"   Max trades per day: {data.get('risk_parameters', {}).get('max_trades_per_day', 'NOT FOUND')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check what dashboard endpoint returns
try:
    print("\n2. Dashboard API (/api/risk-parameters):")
    response = requests.get("http://localhost:5002/api/risk-parameters", timeout=5)
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Data: {data}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check dashboard HTML
try:
    print("\n3. Dashboard HTML (checking for 'Max Daily Trades'):")
    response = requests.get("http://localhost:5002", timeout=5)
    html = response.text
    
    # Look for max daily trades in HTML
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if "Max Daily Trades" in line:
            print(f"   Found on line ~{i}: {line.strip()}")
            # Check surrounding lines
            for j in range(max(0, i-3), min(len(lines), i+4)):
                print(f"   {j}: {lines[j].strip()}")
            break
except Exception as e:
    print(f"   ❌ Error: {e}")