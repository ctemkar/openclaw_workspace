#!/usr/bin/env python3
"""
Simple Supabase client using only URL and anon key.
No database credentials needed!
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SimpleSupabase:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
        
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        print(f"✅ Supabase client initialized")
        print(f"   URL: {self.url}")
    
    def test_connection(self):
        """Test if we can connect to Supabase"""
        try:
            response = requests.get(f"{self.url}/rest/v1/", headers=self.headers)
            if response.status_code == 200:
                print("✅ Supabase connection successful!")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def create_table(self, table_name, schema):
        """Create a table using REST API"""
        # Note: Table creation usually requires admin privileges
        # For now, we'll assume tables exist or use SQL editor in dashboard
        print(f"⚠️  Table creation requires SQL in Supabase dashboard")
        print(f"   Create table '{table_name}' with schema:")
        print(json.dumps(schema, indent=2))
        return False
    
    def insert_trade(self, trade_data):
        """Insert a trade record"""
        try:
            response = requests.post(
                f"{self.url}/rest/v1/trades",
                headers=self.headers,
                json=trade_data
            )
            
            if response.status_code == 201:
                print(f"✅ Trade inserted: {trade_data.get('trade_id', 'N/A')}")
                return response.json()
            else:
                print(f"❌ Failed to insert trade: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Error inserting trade: {e}")
            return None
    
    def get_trades(self, limit=100):
        """Get recent trades"""
        try:
            params = {'order': 'created_at.desc', 'limit': limit}
            response = requests.get(
                f"{self.url}/rest/v1/trades",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                trades = response.json()
                print(f"✅ Retrieved {len(trades)} trades")
                return trades
            else:
                print(f"❌ Failed to get trades: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting trades: {e}")
            return []
    
    def sync_from_sqlite(self, sqlite_db='trading_bot.db'):
        """Sync trades from SQLite to Supabase"""
        import sqlite3
        import pandas as pd
        
        try:
            # Connect to SQLite
            conn = sqlite3.connect(sqlite_db)
            df = pd.read_sql_query('SELECT * FROM trades', conn)
            conn.close()
            
            if len(df) == 0:
                print("📭 No trades to sync from SQLite")
                return 0
            
            print(f"📊 Found {len(df)} trades in SQLite")
            
            # Convert to Supabase format
            synced = 0
            for _, row in df.iterrows():
                trade_data = {
                    'trade_id': str(row.get('id', row.get('trade_id', ''))),
                    'symbol': row.get('symbol', ''),
                    'exchange': row.get('exchange', ''),
                    'side': row.get('side', ''),
                    'buy_price': float(row.get('buy_price', 0)),
                    'sell_price': float(row.get('sell_price', 0)),
                    'quantity': float(row.get('quantity', 0)),
                    'profit': float(row.get('profit', 0)),
                    'profit_pct': float(row.get('profit_pct', 0)),
                    'status': row.get('status', 'completed'),
                    'created_at': row.get('timestamp', datetime.now().isoformat())
                }
                
                # Insert to Supabase
                result = self.insert_trade(trade_data)
                if result:
                    synced += 1
            
            print(f"✅ Synced {synced}/{len(df)} trades to Supabase")
            return synced
            
        except Exception as e:
            print(f"❌ Error syncing from SQLite: {e}")
            return 0

# Quick test
def quick_test():
    """Quick test of Supabase connection"""
    print("🧪 Testing Supabase connection...")
    
    client = SimpleSupabase()
    
    # Test connection
    if client.test_connection():
        print("\n✅ READY TO USE!")
        print("\nExample usage:")
        print("""
# Initialize
from supabase_simple import SimpleSupabase
db = SimpleSupabase()

# Insert trade
db.insert_trade({
    'trade_id': 'test_001',
    'symbol': 'BTC/USDT',
    'exchange': 'binance',
    'side': 'buy',
    'buy_price': 50000.0,
    'quantity': 0.001,
    'status': 'open'
})

# Get trades
trades = db.get_trades(10)

# Sync from SQLite
db.sync_from_sqlite()
        """)
    else:
        print("\n❌ CONNECTION FAILED")
        print("Check:")
        print("1. .env file has SUPABASE_URL and SUPABASE_KEY")
        print("2. URL format: https://project.supabase.co")
        print("3. Anon key is correct")
        print("4. Internet connection")

if __name__ == "__main__":
    quick_test()