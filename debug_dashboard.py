#!/usr/bin/env python3
"""
Debug the dashboard
"""
import sys
import traceback

# Import the dashboard module to check for errors
try:
    from trades_dashboard_fixed import app, init_exchanges, update_trades_with_live_prices
    import json
    from datetime import datetime
    
    print("✅ Module imports successful")
    
    # Test the route function
    with app.test_client() as client:
        print("Testing route...")
        response = client.get('/')
        
        if response.status_code == 200:
            print(f"✅ Route returns HTTP {response.status_code}")
            print(f"Content length: {len(response.data)} bytes")
            
            # Check for key content
            content = response.data.decode('utf-8')
            if 'Real-Time Trades Dashboard' in content:
                print("✅ Dashboard title found")
            
            if 'GEMINI TOTAL:' in content:
                print("✅ Gemini total row found")
            
            if 'BINANCE TOTAL:' in content:
                print("✅ Binance total row found (AFTER all Binance trades)")
            
            # Show a sample
            print("\n📋 Sample of response (first 500 chars):")
            print(content[:500])
            
        else:
            print(f"❌ Route returns HTTP {response.status_code}")
            print(f"Response: {response.data[:500]}")
            
except Exception as e:
    print(f"❌ Error loading dashboard: {e}")
    print("\nTraceback:")
    traceback.print_exc()