#!/usr/bin/env python3
"""
Test dashboard endpoints
"""

import requests
import json
import time

def test_dashboard():
    print("🧪 TESTING DASHBOARD ENDPOINTS")
    print("=" * 60)
    
    # Test main dashboard
    try:
        response = requests.get("http://localhost:5004/", timeout=5)
        print(f"✅ Dashboard HTML: {response.status_code}")
        
        # Check for keywords
        html = response.text
        if "DOT" in html or "ETH" in html or "SOL" in html:
            print("   Contains position data")
        else:
            print("   ⚠️ May not show position data")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard not reachable: {e}")
    
    # Test data endpoint if exists
    try:
        response = requests.get("http://localhost:5004/data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data endpoint: {len(data)} bytes")
            
            # Check if it has our updated data
            if 'unrealized_positions' in str(data):
                print("   Contains unrealized positions")
            else:
                print("   ⚠️ May have old data")
    except:
        print("❌ No data endpoint")
    
    # Test the other dashboard
    try:
        response = requests.get("http://localhost:5003/", timeout=5)
        print(f"✅ Dashboard 5003: {response.status_code}")
    except:
        print("❌ Dashboard 5003 not reachable")
    
    print("\n📊 QUICK CHECK OF UPDATED DATA:")
    print("-" * 60)
    
    # Check our updated tracker file
    try:
        with open('cumulative_pnl_tracker.json', 'r') as f:
            tracker = json.load(f)
        
        last_updated = tracker['metadata']['last_updated']
        positions = tracker.get('unrealized_positions', [])
        
        print(f"Tracker last updated: {last_updated}")
        print(f"Active positions: {len(positions)}")
        
        if positions:
            print("\nCurrent positions:")
            for pos in positions[:3]:  # Show first 3
                print(f"  {pos['symbol']}: ${pos['unrealized_pnl']:.2f} ({pos['unrealized_pnl_percent']:.2f}%)")
        
        # Check win rate
        summary = tracker['performance_summary']
        print(f"\nWin rate: {summary['win_rate']:.1f}%")
        print(f"Total P&L: ${summary['total_cumulative_pnl']:.2f}")
        
    except Exception as e:
        print(f"Error reading tracker: {e}")

if __name__ == "__main__":
    test_dashboard()