#!/usr/bin/env python3
"""
Check what columns the trades table has
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}'
}

print("🔍 Checking trades table structure...")

# Try to get table info
try:
    # Try to get a single row to see structure
    response = requests.get(
        f"{url}/rest/v1/trades",
        headers=headers,
        params={'limit': 1}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print("\n✅ Table structure (from sample row):")
            for key, value in data[0].items():
                print(f"  {key}: {type(value).__name__} = {value}")
        else:
            print("\n📭 Table is empty")
            
            # Try to get column info via different method
            print("\nTrying to infer columns...")
            # Make a HEAD request to get headers
            head_response = requests.head(
                f"{url}/rest/v1/trades",
                headers=headers
            )
            print(f"HEAD response: {head_response.status_code}")
            print(f"Headers: {dict(head_response.headers)}")
            
    else:
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50)
print("🎯 QUICK FIX:")
print("1. Check Supabase Dashboard → Table Editor → trades")
print("2. See what columns exist")
print("3. Either:")
print("   a) Use existing columns")
print("   b) Add missing columns via SQL:")
print()
print("-- Add missing columns")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS buy_price DECIMAL;")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS sell_price DECIMAL;")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS quantity DECIMAL;")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS profit DECIMAL;")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS profit_pct DECIMAL;")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS status TEXT;")
print("ALTER TABLE trades ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();")