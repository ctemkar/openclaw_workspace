import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

class SupabaseSync:
    def __init__(self):
        # SQLite connection (local)
        self.sqlite_conn = sqlite3.connect('trading_bot.db')
        
        # Supabase PostgreSQL connection
        self.supabase_conn = None
        self.connect_supabase()
        
    def connect_supabase(self):
        """Connect to Supabase PostgreSQL database"""
        try:
            self.supabase_conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            print("✅ Connected to Supabase database")
            
            # Create tables if they don't exist
            self.create_tables()
            
        except Exception as e:
            print(f"❌ Error connecting to Supabase: {e}")
            self.supabase_conn = None
    
    def create_tables(self):
        """Create necessary tables in Supabase"""
        if not self.supabase_conn:
            return
            
        cursor = self.supabase_conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                trade_id TEXT UNIQUE,
                symbol VARCHAR(20),
                exchange VARCHAR(20),
                side VARCHAR(10),
                buy_price DECIMAL(20, 8),
                sell_price DECIMAL(20, 8),
                quantity DECIMAL(20, 8),
                profit DECIMAL(20, 8),
                profit_pct DECIMAL(10, 4),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20),
                exchange VARCHAR(20),
                quantity DECIMAL(20, 8),
                avg_price DECIMAL(20, 8),
                current_price DECIMAL(20, 8),
                pnl DECIMAL(20, 8),
                pnl_pct DECIMAL(10, 4),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id SERIAL PRIMARY KEY,
                date DATE,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                win_rate DECIMAL(10, 4),
                total_profit DECIMAL(20, 8),
                avg_profit_pct DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.supabase_conn.commit()
        cursor.close()
        print("✅ Tables created/verified in Supabase")
    
    def sync_trades(self):
        """Sync trades from SQLite to Supabase"""
        if not self.supabase_conn:
            print("❌ No Supabase connection")
            return
            
        try:
            # Read trades from SQLite
            df = pd.read_sql_query('SELECT * FROM trades', self.sqlite_conn)
            
            if len(df) == 0:
                print("📭 No trades to sync")
                return
            
            print(f"📊 Found {len(df)} trades to sync")
            
            # Sync to Supabase
            cursor = self.supabase_conn.cursor()
            
            for _, row in df.iterrows():
                # Check if trade already exists
                cursor.execute(
                    "SELECT id FROM trades WHERE trade_id = %s",
                    (str(row.get('id', row.get('trade_id', ''))),)
                )
                
                if cursor.fetchone() is None:
                    # Insert new trade
                    execute_values(cursor, '''
                        INSERT INTO trades (trade_id, symbol, exchange, side, buy_price, sell_price, 
                                          quantity, profit, profit_pct, timestamp, status)
                        VALUES %s
                    ''', [(
                        str(row.get('id', row.get('trade_id', ''))),
                        row.get('symbol', ''),
                        row.get('exchange', ''),
                        row.get('side', ''),
                        float(row.get('buy_price', 0)),
                        float(row.get('sell_price', 0)),
                        float(row.get('quantity', 0)),
                        float(row.get('profit', 0)),
                        float(row.get('profit_pct', 0)),
                        row.get('timestamp', datetime.now()),
                        row.get('status', 'completed')
                    )])
            
            self.supabase_conn.commit()
            cursor.close()
            print(f"✅ Synced {len(df)} trades to Supabase")
            
        except Exception as e:
            print(f"❌ Error syncing trades: {e}")
    
    def log_trade(self, trade_data):
        """Log a new trade to both SQLite and Supabase"""
        # First log to SQLite (local backup)
        cursor = self.sqlite_conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trades 
            (trade_id, symbol, exchange, side, buy_price, sell_price, quantity, profit, profit_pct, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data.get('trade_id'),
            trade_data.get('symbol'),
            trade_data.get('exchange'),
            trade_data.get('side'),
            trade_data.get('buy_price'),
            trade_data.get('sell_price'),
            trade_data.get('quantity'),
            trade_data.get('profit'),
            trade_data.get('profit_pct'),
            trade_data.get('timestamp', datetime.now()),
            trade_data.get('status', 'open')
        ))
        
        self.sqlite_conn.commit()
        cursor.close()
        
        # Then sync to Supabase
        if self.supabase_conn:
            try:
                cursor = self.supabase_conn.cursor()
                execute_values(cursor, '''
                    INSERT INTO trades (trade_id, symbol, exchange, side, buy_price, sell_price, 
                                      quantity, profit, profit_pct, timestamp, status)
                    VALUES %s
                    ON CONFLICT (trade_id) DO UPDATE SET
                    sell_price = EXCLUDED.sell_price,
                    profit = EXCLUDED.profit,
                    profit_pct = EXCLUDED.profit_pct,
                    status = EXCLUDED.status
                ''', [(
                    trade_data.get('trade_id'),
                    trade_data.get('symbol'),
                    trade_data.get('exchange'),
                    trade_data.get('side'),
                    float(trade_data.get('buy_price', 0)),
                    float(trade_data.get('sell_price', 0)),
                    float(trade_data.get('quantity', 0)),
                    float(trade_data.get('profit', 0)),
                    float(trade_data.get('profit_pct', 0)),
                    trade_data.get('timestamp', datetime.now()),
                    trade_data.get('status', 'open')
                )])
                
                self.supabase_conn.commit()
                cursor.close()
                print(f"✅ Trade logged to Supabase: {trade_data.get('trade_id')}")
                
            except Exception as e:
                print(f"⚠️  Could not log to Supabase: {e}")
                print("📁 Trade saved locally to SQLite only")
    
    def close(self):
        """Close all database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.supabase_conn:
            self.supabase_conn.close()
        print("🔌 Database connections closed")

# Quick test function
def test_supabase_connection():
    """Test the Supabase connection"""
    load_dotenv()
    
    print("🧪 Testing Supabase connection...")
    
    # Check if environment variables are set
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please run: source .env")
        return False
    
    try:
        # Test connection
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Supabase connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Supabase Integration Module")
    print("Use: from supabase_integration import SupabaseSync")
    print("")
    print("To test connection: python -c 'from supabase_integration import test_supabase_connection; test_supabase_connection()'")
