import ccxt
import json
from datetime import datetime

# Load API credentials
try:
    with open('.gemini_key', 'r') as f:
        api_key = f.read().strip()
    with open('.gemini_secret', 'r') as f:
        api_secret = f.read().strip()
except FileNotFoundError:
    print('API credentials not found')
    exit(1)

# Initialize Gemini exchange
exchange = ccxt.gemini({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

# Get current prices
symbols = ['BTC/USD', 'ETH/USD']
current_prices = {}

for symbol in symbols:
    try:
        ticker = exchange.fetch_ticker(symbol)
        current_prices[symbol] = ticker['last']
    except Exception as e:
        print(f'Error fetching {symbol}: {e}')
        current_prices[symbol] = None

# Check open positions from trading history
try:
    with open('trading_history.json', 'r') as f:
        history = json.load(f)
    
    print('Position Analysis:')
    print('=' * 50)
    
    today = datetime.now().strftime('%Y-%m-%d')
    if today in history['daily_trades']:
        for trade in history['daily_trades'][today]:
            if trade['status'] == 'OPEN':
                symbol = trade['symbol']
                current_price = current_prices.get(symbol)
                
                if current_price is None:
                    print(f"⚠️  Cannot check {symbol}: price unavailable")
                    continue
                
                entry_price = trade['entry_price']
                stop_loss = trade['stop_loss']
                take_profit = trade['take_profit']
                
                # Calculate P&L percentage
                if trade['side'] == 'BUY':
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                else:
                    pnl_pct = ((entry_price - current_price) / entry_price) * 100
                
                print(f"📊 {symbol} ({trade['side']})")
                print(f"   Entry: ${entry_price:.2f}")
                print(f"   Current: ${current_price:.2f}")
                print(f"   P&L: {pnl_pct:.2f}%")
                print(f"   Stop Loss: ${stop_loss:.2f} ({((stop_loss - entry_price)/entry_price*100):.1f}%)")
                print(f"   Take Profit: ${take_profit:.2f} ({((take_profit - entry_price)/entry_price*100):.1f}%)")
                
                # Check if stop-loss or take-profit hit
                if trade['side'] == 'BUY':
                    if current_price <= stop_loss:
                        print(f"   🔴 STOP-LOSS HIT! Should close position.")
                    elif current_price >= take_profit:
                        print(f"   🟢 TAKE-PROFIT HIT! Should close position.")
                    else:
                        distance_to_sl = ((current_price - stop_loss) / current_price) * 100
                        distance_to_tp = ((take_profit - current_price) / current_price) * 100
                        print(f"   📏 Distance to SL: {distance_to_sl:.1f}%")
                        print(f"   📏 Distance to TP: {distance_to_tp:.1f}%")
                print()
    else:
        print("No trades executed today.")
        
except Exception as e:
    print(f'Error reading trading history: {e}')