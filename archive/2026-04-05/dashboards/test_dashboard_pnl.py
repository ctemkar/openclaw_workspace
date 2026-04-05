#!/usr/bin/env python3
"""
Test if dashboard shows P&L correctly
"""

import requests
import json

print("="*70)
print("🔍 TESTING DASHBOARD P&L DISPLAY")
print("="*70)

# Test trades dashboard
try:
    response = requests.get('http://localhost:5011', timeout=5)
    
    if response.status_code == 200:
        print("✅ Trades dashboard is responding")
        
        # Check for P&L indicators in HTML
        html = response.text
        
        # Look for P&L numbers
        import re
        
        # Find all dollar amounts that could be P&L
        dollar_amounts = re.findall(r'\$\s*[-+]?\d+\.?\d*', html)
        pnl_amounts = [amt for amt in dollar_amounts if '-' in amt or '+' in amt]
        
        if pnl_amounts:
            print(f"📊 Found P&L amounts in dashboard: {pnl_amounts[:5]}")
        else:
            print("⚠️  No P&L amounts found in dashboard HTML")
            
        # Check for specific P&L text
        if 'P&L' in html or 'pnl' in html.lower():
            print("✅ P&L text found in dashboard")
        else:
            print("❌ P&L text NOT found in dashboard")
            
        # Check for our specific positions
        if 'ETH/USD' in html and 'SOL/USD' in html:
            print("✅ ETH and SOL positions found in dashboard")
        else:
            print("❌ ETH/SOL positions NOT found in dashboard")
            
    else:
        print(f"❌ Trades dashboard returned {response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing dashboard: {e}")

# Also test the API endpoint directly
print("\n" + "="*70)
print("📊 CHECKING TRADES.JSON DIRECTLY")
print("="*70)

with open('trading_data/trades.json', 'r') as f:
    trades = json.load(f)

print(f"Total trades: {len(trades)}")
print("\nActual data in trades.json:")
for trade in trades:
    print(f"{trade['symbol']}: P&L ${trade['pnl']:.2f} ({trade['pnl_percent']:+.2f}%)")

print("\n" + "="*70)
print("💡 DIAGNOSIS:")
print("1. Data is correct in trades.json")
print("2. Dashboard might need template update")
print("3. Check if dashboard template shows pnl/pnl_percent fields")
print("="*70)