#!/usr/bin/env python3
import requests
import json
from datetime import datetime

def get_market_data(symbol):
    """Fetch market data from Gemini"""
    try:
        # Get ticker data
        ticker_url = f"https://api.gemini.com/v1/pubticker/{symbol}"
        ticker_response = requests.get(ticker_url, timeout=10)
        ticker_data = ticker_response.json()
        
        # Get order book
        book_url = f"https://api.gemini.com/v1/book/{symbol}"
        book_response = requests.get(book_url, timeout=10)
        book_data = book_response.json()
        
        return {
            "ticker": ticker_data,
            "order_book": book_data,
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Test BTC
print("Testing BTC/USD...")
btc_data = get_market_data("btcusd")
print(f"Success: {btc_data['success']}")
print(f"Ticker keys: {list(btc_data['ticker'].keys())}")
print(f"Bid value: {btc_data['ticker'].get('bid')}")
print(f"Type of bid: {type(btc_data['ticker'].get('bid'))}")

# Test analysis
ticker = btc_data["ticker"]
print(f"\nDirect access:")
print(f"ticker['bid'] = {ticker['bid']}")
print(f"type(ticker['bid']) = {type(ticker['bid'])}")
print(f"float(ticker['bid']) = {float(ticker['bid'])}")