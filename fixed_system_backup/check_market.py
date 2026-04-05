import requests
import json

try:
    # Check BTC price
    btc_response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=5)
    btc_data = btc_response.json()
    btc_price = float(btc_data['price'])
    print(f"BTC/USDT: ${btc_price:,.2f}")
    
    # Check YFI price (the trading pair)
    yfi_response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=YFIUSDT', timeout=5)
    yfi_data = yfi_response.json()
    yfi_price = float(yfi_data['price'])
    print(f"YFI/USDT: ${yfi_price:,.2f}")
    
    # Check 24h change
    ticker_response = requests.get('https://api.binance.com/api/v3/ticker/24hr?symbol=YFIUSDT', timeout=5)
    ticker_data = ticker_response.json()
    price_change = float(ticker_data['priceChange'])
    price_change_percent = float(ticker_data['priceChangePercent'])
    print(f"YFI 24h Change: ${price_change:,.2f} ({price_change_percent:,.2f}%)")
    
except Exception as e:
    print(f"Error fetching market data: {e}")