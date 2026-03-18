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
print('Current Market Prices:')
print('=' * 40)
for symbol in symbols:
    try:
        ticker = exchange.fetch_ticker(symbol)
        print(f'{symbol}: ${ticker["last"]:.2f}')
        print(f'  24h High: ${ticker["high"]:.2f}')
        print(f'  24h Low: ${ticker["low"]:.2f}')
        print(f'  24h Volume: ${ticker["quoteVolume"]:.2f}')
        print()
    except Exception as e:
        print(f'Error fetching {symbol}: {e}')

# Check open positions from trading history
try:
    with open('trading_history.json', 'r') as f:
        history = json.load(f)
    
    print('Open Positions:')
    print('=' * 40)
    
    today = datetime.now().strftime('%Y-%m-%d')
    if today in history['daily_trades']:
        for trade in history['daily_trades'][today]:
            if trade['status'] == 'OPEN':
                print(f"ID: {trade['id']}")
                print(f"Symbol: {trade['symbol']}")
                print(f"Side: {trade['side']}")
                print(f"Entry Price: ${trade['entry_price']:.2f}")
                print(f"Quantity: {trade['quantity']}")
                print(f"Stop Loss: ${trade['stop_loss']:.2f}")
                print(f"Take Profit: ${trade['take_profit']:.2f}")
                print(f"Reason: {trade['reason']}")
                print()
except Exception as e:
    print(f'Error reading trading history: {e}')