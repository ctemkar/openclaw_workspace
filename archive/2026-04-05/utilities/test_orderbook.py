#!/usr/bin/env python3
import requests
import json

# Test Gemini order book API
def test_orderbook():
    # Try to get BTCUSD order book
    url = "https://api.gemini.com/v1/book/btcusd"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"\nOrder Book Structure:")
        print(f"Type: {type(data)}")
        print(f"Keys: {list(data.keys())}")
        
        if "bids" in data:
            print(f"\nFirst bid: {data['bids'][0] if data['bids'] else 'Empty'}")
            print(f"Type of first bid: {type(data['bids'][0]) if data['bids'] else 'N/A'}")
        
        if "asks" in data:
            print(f"\nFirst ask: {data['asks'][0] if data['asks'] else 'Empty'}")
            print(f"Type of first ask: {type(data['asks'][0]) if data['asks'] else 'N/A'}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_orderbook()