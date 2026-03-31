#!/bin/bash

# Supabase Setup Script for Crypto Trading System
# This script helps you securely set up Supabase keys and configure your trading system

set -e

echo "================================================"
echo "🔐 SUPABASE SETUP FOR CRYPTO TRADING SYSTEM"
echo "================================================"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  Existing .env file found. Backing up to .env.backup..."
    cp .env .env.backup
fi

echo ""
echo "📋 STEP 1: Get your Supabase credentials"
echo "----------------------------------------"
echo "1. Go to https://app.supabase.com"
echo "2. Select your project"
echo "3. Go to Project Settings → Database"
echo "4. Copy the following:"
echo "   - Connection string (PostgreSQL URL)"
echo "   - Project API key (anon/public key)"
echo ""

echo "📋 STEP 2: Enter your Supabase credentials"
echo "------------------------------------------"

read -p "Enter Supabase Project URL (e.g., https://xyz.supabase.co): " SUPABASE_URL
read -p "Enter Supabase API Key (anon/public): " SUPABASE_KEY
read -p "Enter Supabase Database Password (if different from API key): " SUPABASE_DB_PASSWORD

# Extract database connection info from URL
if [[ $SUPABASE_URL =~ ^https://([a-z0-9]+)\.supabase\.co$ ]]; then
    DB_HOST="${BASH_REMATCH[1]}.supabase.co"
    DB_PORT="5432"
    DB_NAME="postgres"
    
    read -p "Enter Database Username [default: postgres]: " DB_USER
    DB_USER=${DB_USER:-postgres}
    
    read -p "Enter Database Name [default: CryptoTrading]: " DB_NAME_INPUT
    DB_NAME=${DB_NAME_INPUT:-CryptoTrading}
    
    # Create .env file
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_KEY=$SUPABASE_KEY

# Database Connection (PostgreSQL)
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$SUPABASE_DB_PASSWORD
DATABASE_URL=postgresql://$DB_USER:$SUPABASE_DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

# Trading System Configuration
TRADING_MODE=REAL
MAX_TRADES_PER_DAY=999
SCAN_INTERVAL_MINUTES=5

# Exchange API Keys (Add these separately if needed)
# GEMINI_API_KEY=your_gemini_key_here
# GEMINI_API_SECRET=your_gemini_secret_here
# BINANCE_API_KEY=your_binance_key_here
# BINANCE_API_SECRET=your_binance_secret_here
EOF
    
    echo ""
    echo "✅ .env file created successfully!"
    echo ""
    
    # Create Python script for Supabase integration
    cat > supabase_integration.py << 'PYEOF'
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
PYEOF
    
    echo ""
    echo "✅ Python integration script created: supabase_integration.py"
    echo ""
    
    # Create requirements file for Supabase dependencies
    cat > requirements_supabase.txt << 'REQEOF'
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.2.2
supabase==1.1.1
REQEOF
    
    echo "✅ Dependencies file created: requirements_supabase.txt"
    echo ""
    
    echo "📋 STEP 3: Install dependencies"
    echo "-------------------------------"
    echo "Run: pip install -r requirements_supabase.txt"
    echo ""
    
    echo "📋 STEP 4: Test your connection"
    echo "-------------------------------"
    echo "1. Source the environment: source .env"
    echo "2. Test connection: python -c 'from supabase_integration import test_supabase_connection; test_supabase_connection()'"
    echo ""
    
    echo "📋 STEP 5: Integrate with your trading bots"
    echo "-------------------------------------------"
    echo "Add this to your trading scripts:"
    echo ""
    cat << 'INTEOF'
# At the top of your trading script:
from supabase_integration import SupabaseSync

# Initialize
db = SupabaseSync()

# When you make a trade:
trade_data = {
    'trade_id': 'unique_trade_id',
    'symbol': 'BTC/USDT',
    'exchange': 'binance',
    'side': 'buy',
    'buy_price': 50000.0,
    'sell_price': 0.0,  # 0 if still open
    'quantity': 0.001,
    'profit': 0.0,
    'profit_pct': 0.0,
    'status': 'open'
}
db.log_trade(trade_data)

# When trade closes:
trade_data['sell_price'] = 51000.0
trade_data['profit'] = 10.0
trade_data['profit_pct'] = 2.0
trade_data['status'] = 'closed'
db.log_trade(trade_data)

# Sync all existing trades:
db.sync_trades()
INTEOF
    
    echo ""
    echo "================================================"
    echo "🎉 SETUP COMPLETE!"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Install dependencies: pip install -r requirements_supabase.txt"
    echo "2. Test connection: python -c 'from supabase_integration import test_supabase_connection; test_supabase_connection()'"
    echo "3. Modify your trading bots to use SupabaseSync()"
    echo "4. Run initial sync: python -c 'from supabase_integration import SupabaseSync; db = SupabaseSync(); db.sync_trades()'"
    echo ""
    echo "🔒 Your Supabase keys are stored in .env (add to .gitignore!)"
    
else
    echo "❌ Invalid Supabase URL format. Expected: https://xyz.supabase.co"
    echo "Please check your Supabase project URL and try again."
fi

echo ""
echo "📝 Note: Always keep your .env file secure and never commit it to git!"
echo "Add '.env' to your .gitignore file."