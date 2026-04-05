#!/usr/bin/env python3
"""
Check what's accessible in Supabase with anon key
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

print("🔍 Exploring Supabase API...")
print(f"URL: {url}")

# Try different endpoints
endpoints = [
    '/rest/v1/',
    '/auth/v1/',
    '/rest/v1/trades',
    '/rest/v1/portfolio',
    '/rest/v1/performance'
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{url}{endpoint}", headers=headers, timeout=5)
        print(f"\n{endpoint}:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Accessible")
            if endpoint == '/rest/v1/':
                # Try to list tables
                print("  Trying to list tables...")
                tables_response = requests.get(f"{url}/rest/v1/", headers=headers)
                if tables_response.status_code == 200:
                    print(f"  Tables info: {tables_response.text[:200]}")
        elif response.status_code == 401:
            print(f"  ❌ Unauthorized (need RLS policy or service key)")
        elif response.status_code == 404:
            print(f"  📭 Not found (table doesn't exist)")
        else:
            print(f"  Response: {response.text[:100]}")
            
    except Exception as e:
        print(f"\n{endpoint}:")
        print(f"  ❌ Error: {e}")

print("\n" + "="*50)
print("🎯 NEXT STEPS:")
print("1. Go to Supabase Dashboard → Authentication → Policies")
print("2. Create policy for 'trades' table to allow anon access")
print("3. OR use Service Role key (careful - full admin access)")
print("4. Create tables first in SQL Editor")

print("\n📋 Quick SQL to create tables:")
print("""
-- Run in Supabase SQL Editor
CREATE TABLE trades (
    id BIGSERIAL PRIMARY KEY,
    trade_id TEXT UNIQUE,
    symbol TEXT,
    exchange TEXT,
    side TEXT,
    buy_price DECIMAL,
    sell_price DECIMAL,
    quantity DECIMAL,
    profit DECIMAL,
    profit_pct DECIMAL,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;

-- Create policy for anon access
CREATE POLICY "Allow anon insert" ON trades
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anon select" ON trades
    FOR SELECT USING (true);
""")