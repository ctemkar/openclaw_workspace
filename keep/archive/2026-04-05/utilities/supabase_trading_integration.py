#!/usr/bin/env python3
"""
Supabase integration for crypto trading system
Matches existing table schema
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SupabaseTrading:
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
        
        print(f"✅ Supabase Trading Client Initialized")
        print(f"   Project: {self.url}")
    
    def log_trade(self, trade_data):
        """
        Log a trade to Supabase
        Expected trade_data format:
        {
            'symbol': 'BTC/USDT',
            'side': 'buy' or 'sell',
            'action': 'open' or 'close',
            'qty': 0.001,
            'price': 50000.0,
            'entry_price': 50000.0,  # for opening
            'exit_price': 51000.0,   # for closing
            'status': 'open' or 'closed',
            'pnl': 10.0,  # profit/loss
            'realized_pnl': 10.0,  # if closed
            'market_type': 'CRYPTO',
            'notes': 'Optional notes'
        }
        """
        # Prepare data matching table schema
        supabase_trade = {
            'symbol': trade_data.get('symbol', ''),
            'side': trade_data.get('side'),
            'action': trade_data.get('action'),
            'qty': trade_data.get('qty', 0),
            'price': trade_data.get('price'),
            'entry_price': trade_data.get('entry_price'),
            'exit_price': trade_data.get('exit_price'),
            'status': trade_data.get('status', 'open'),
            'pnl': trade_data.get('pnl', 0),
            'realized_pnl': trade_data.get('realized_pnl'),
            'market_type': trade_data.get('market_type', 'CRYPTO'),
            'notes': trade_data.get('notes', ''),
            'created_at': datetime.now().isoformat(),
            'executed_at': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.url}/rest/v1/trades",
                headers=self.headers,
                json=supabase_trade
            )
            
            if response.status_code == 201:
                print(f"✅ Trade logged: {trade_data.get('symbol')} {trade_data.get('side')}")
                return response.json()
            else:
                print(f"❌ Failed to log trade: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Error logging trade: {e}")
            return None
    
    def log_buy_order(self, symbol, qty, price, exchange='binance'):
        """Log a buy order (opening a position)"""
        trade_data = {
            'symbol': f"{exchange}_{symbol}".replace('/', ''),
            'side': 'buy',
            'action': 'open',
            'qty': qty,
            'price': price,
            'entry_price': price,
            'status': 'open',
            'pnl': 0,
            'market_type': 'CRYPTO',
            'notes': f'Buy {qty} {symbol} at {price} on {exchange}'
        }
        return self.log_trade(trade_data)
    
    def log_sell_order(self, symbol, qty, price, entry_price, exchange='binance'):
        """Log a sell order (closing a position)"""
        pnl = (price - entry_price) * qty
        pnl_percent = ((price - entry_price) / entry_price) * 100
        
        trade_data = {
            'symbol': f"{exchange}_{symbol}".replace('/', ''),
            'side': 'sell',
            'action': 'close',
            'qty': qty,
            'price': price,
            'entry_price': entry_price,
            'exit_price': price,
            'status': 'closed',
            'pnl': pnl,
            'realized_pnl': pnl,
            'market_type': 'CRYPTO',
            'notes': f'Sell {qty} {symbol} at {price} | PnL: ${pnl:.2f} ({pnl_percent:.2f}%)'
        }
        return self.log_trade(trade_data)
    
    def get_open_positions(self):
        """Get all open positions"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/trades",
                headers=self.headers,
                params={
                    'status': 'eq.open',
                    'order': 'created_at.desc'
                }
            )
            
            if response.status_code == 200:
                positions = response.json()
                print(f"✅ Found {len(positions)} open positions")
                return positions
            else:
                print(f"❌ Failed to get positions: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def get_trade_history(self, limit=50):
        """Get recent trade history"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/trades",
                headers=self.headers,
                params={
                    'order': 'created_at.desc',
                    'limit': limit
                }
            )
            
            if response.status_code == 200:
                trades = response.json()
                print(f"✅ Retrieved {len(trades)} trades")
                return trades
            else:
                print(f"❌ Failed to get history: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting history: {e}")
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
            
            # Convert and sync
            synced = 0
            for _, row in df.iterrows():
                # Map SQLite columns to Supabase schema
                symbol = row.get('symbol', '')
                exchange = row.get('exchange', 'binance')
                
                # Determine side and action
                buy_price = row.get('buy_price', 0)
                sell_price = row.get('sell_price', 0)
                
                if buy_price > 0 and sell_price == 0:
                    # Open position
                    trade_data = {
                        'symbol': f"{exchange}_{symbol}".replace('/', ''),
                        'side': 'buy',
                        'action': 'open',
                        'qty': row.get('quantity', 0),
                        'price': buy_price,
                        'entry_price': buy_price,
                        'status': 'open' if row.get('status') != 'closed' else 'closed',
                        'pnl': row.get('profit', 0),
                        'market_type': 'CRYPTO',
                        'notes': f'Synced from SQLite: {symbol}'
                    }
                elif sell_price > 0:
                    # Closed position
                    trade_data = {
                        'symbol': f"{exchange}_{symbol}".replace('/', ''),
                        'side': 'sell',
                        'action': 'close',
                        'qty': row.get('quantity', 0),
                        'price': sell_price,
                        'entry_price': buy_price,
                        'exit_price': sell_price,
                        'status': 'closed',
                        'pnl': row.get('profit', 0),
                        'realized_pnl': row.get('profit', 0),
                        'market_type': 'CRYPTO',
                        'notes': f'Synced from SQLite: {symbol} PnL: {row.get("profit_pct", 0):.2f}%'
                    }
                else:
                    continue
                
                # Add to Supabase
                result = self.log_trade(trade_data)
                if result:
                    synced += 1
            
            print(f"✅ Synced {synced}/{len(df)} trades to Supabase")
            return synced
            
        except Exception as e:
            print(f"❌ Error syncing from SQLite: {e}")
            return 0

# Quick test
def test_integration():
    """Test the integration"""
    print("🧪 Testing Supabase Trading Integration...")
    
    try:
        db = SupabaseTrading()
        
        # Test 1: Log a buy order
        print("\n1. Testing buy order...")
        buy_result = db.log_buy_order('BTC/USDT', 0.001, 50000.0)
        
        # Test 2: Get open positions
        print("\n2. Getting open positions...")
        positions = db.get_open_positions()
        
        # Test 3: Get history
        print("\n3. Getting trade history...")
        history = db.get_trade_history(5)
        
        print("\n" + "="*50)
        print("✅ INTEGRATION READY!")
        print("\nUsage in your trading bots:")
        print("""
# Add to your trading script
from supabase_trading_integration import SupabaseTrading

# Initialize
db = SupabaseTrading()

# When you buy
db.log_buy_order('BTC/USDT', 0.001, 50000.0, exchange='binance')

# When you sell  
db.log_sell_order('BTC/USDT', 0.001, 51000.0, 50000.0, exchange='binance')

# Get current positions
positions = db.get_open_positions()

# Sync existing SQLite data
db.sync_from_sqlite()
        """)
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

if __name__ == "__main__":
    test_integration()