# Supabase Integration for Crypto Trading System

## 📋 Quick Start

### Option 1: Full Setup (Recommended)
```bash
./setup_supabase.sh
```
This will:
1. Create `.env` file with your Supabase keys
2. Generate `supabase_integration.py` with database sync functions
3. Create `requirements_supabase.txt` with dependencies
4. Provide integration examples

### Option 2: Just Set Keys
```bash
./set_supabase_keys.sh
```
Quickly set only the Supabase keys in your `.env` file.

## 🔐 Where to Put Supabase Keys

### **Location: `.env` file** (in project root)
```
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key

# Database Connection
DB_HOST=your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password
DATABASE_URL=postgresql://postgres:password@your-project.supabase.co:5432/postgres
```

### **⚠️ SECURITY WARNING:**
- **NEVER** commit `.env` to git
- Add `.env` to `.gitignore`: `echo '.env' >> .gitignore`
- Keep your API keys secret

## 🛠 How to Get Your Supabase Keys

1. **Go to** [Supabase Dashboard](https://app.supabase.com)
2. **Select your project**
3. **Go to** Project Settings → Database
4. **Copy:**
   - **Connection string** (PostgreSQL URL)
   - **Project API key** (anon/public key)
   - **Database password** (if you set one)

## 📊 Integration with Trading System

### Basic Usage:
```python
from supabase_integration import SupabaseSync

# Initialize
db = SupabaseSync()

# Log a trade
trade_data = {
    'trade_id': 'binance_btc_001',
    'symbol': 'BTC/USDT',
    'exchange': 'binance',
    'side': 'buy',
    'buy_price': 50000.0,
    'quantity': 0.001,
    'status': 'open'
}
db.log_trade(trade_data)

# Sync all existing trades from SQLite
db.sync_trades()
```

### Modify Your Trading Bots:
Add this to your trading scripts (like `real_gemini_trader.py`, `fixed_futures_bot.py`):

```python
# At the top
from supabase_integration import SupabaseSync
db = SupabaseSync()

# When you execute a trade
def execute_trade(symbol, side, price, quantity):
    trade_id = f"{exchange}_{symbol}_{int(time.time())}"
    
    trade_data = {
        'trade_id': trade_id,
        'symbol': symbol,
        'exchange': exchange,
        'side': side,
        'buy_price': price if side == 'buy' else 0,
        'sell_price': price if side == 'sell' else 0,
        'quantity': quantity,
        'profit': 0.0,
        'profit_pct': 0.0,
        'status': 'open' if side == 'buy' else 'closed'
    }
    
    db.log_trade(trade_data)
```

## 📈 Benefits of Using Supabase

1. **Remote Access**: View trades from anywhere
2. **Scalability**: Handle millions of trades
3. **Real-time**: Live dashboard updates
4. **Backup**: Automatic cloud backup
5. **Analytics**: Built-in query capabilities

## 🧪 Test Your Setup

```bash
# Install dependencies
pip install -r requirements_supabase.txt

# Test connection
python -c "from supabase_integration import test_supabase_connection; test_supabase_connection()"

# Sync existing trades
python -c "from supabase_integration import SupabaseSync; db = SupabaseSync(); db.sync_trades()"
```

## 🔧 Troubleshooting

### Connection Issues:
1. Check firewall: Port 5432 must be open
2. Verify credentials in `.env`
3. Ensure Supabase project is active

### Python Errors:
```bash
# Install missing packages
pip install psycopg2-binary python-dotenv pandas supabase

# If psycopg2 fails on macOS:
brew install postgresql
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
```

## 📞 Support

- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Trading System Issues**: Check your bot logs

---

**Remember:** Your trading data is valuable. Keep your `.env` file secure and regularly backup your Supabase database!