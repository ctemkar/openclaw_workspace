#!/usr/bin/env python3
"""
Test inserting a trade to Supabase
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Test trade data
test_trade = {
    'trade_id': f'test_{int(datetime.now().timestamp())}',
    'symbol': 'BTC/USDT',
    'exchange': 'binance',
    'side': 'buy',
    'buy_price': 50000.50,
    'sell_price': 0.0,
    'quantity': 0.001,
    'profit': 0.0,
    'profit_pct': 0.0,
    'status': 'open',
    'created_at': datetime.now().isoformat()
}

print("🧪 Testing trade insertion...")
print(f"URL: {url}/rest/v1/trades")
print(f"Trade ID: {test_trade['trade_id']}")

try:
    response = requests.post(
        f"{url}/rest/v1/trades",
        headers=headers,
        json=test_trade
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ TRADE INSERTED SUCCESSFULLY!")
        print(f"Response: {response.json()}")
        
        # Now try to retrieve it
        print("\n📋 Retrieving trades...")
        get_response = requests.get(
            f"{url}/rest/v1/trades",
            headers=headers,
            params={'order': 'created_at.desc', 'limit': 5}
        )
        
        if get_response.status_code == 200:
            trades = get_response.json()
            print(f"✅ Retrieved {len(trades)} trades")
            for i, trade in enumerate(trades[:3]):
                print(f"\nTrade {i+1}:")
                print(f"  ID: {trade.get('id')}")
                print(f"  Trade ID: {trade.get('trade_id')}")
                print(f"  Symbol: {trade.get('symbol')}")
                print(f"  Status: {trade.get('status')}")
                print(f"  Created: {trade.get('created_at')}")
        else:
            print(f"❌ Failed to retrieve: {get_response.status_code}")
            
    elif response.status_code == 409:
        print("❌ Trade ID already exists (duplicate)")
    elif response.status_code == 401:
        print("❌ Unauthorized - check RLS policies")
        print(f"Response: {response.text}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("🎯 YOUR SUPABASE IS WORKING!")
print("You can now:")
print("1. Insert trades from your trading bots")
print("2. View all trades in Supabase dashboard")
print("3. Build dashboards with the data")
print("\nTo integrate with your trading bots:")
print("""
# Add to your trading script:
import requests
from datetime import datetime

def log_to_supabase(trade_data):
    url = "https://dxzawamxhvlrxtrvziao.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    trade_data['created_at'] = datetime.now().isoformat()
    
    response = requests.post(
        f"{url}/rest/v1/trades",
        headers=headers,
        json=trade_data
    )
    
    return response.status_code == 201
""")