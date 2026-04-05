#!/usr/bin/env python3
import requests
import json

# Test Gemini API directly
def test_gemini_api():
    # Try to get BTCUSD ticker
    url = "https://api.gemini.com/v1/pubticker/btcusd"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        # Create realistic mock data
        mock_ticker = {
            "last": "85000.00",
            "bid": "84950.00",
            "ask": "85050.00",
            "volume": {
                "BTC": "1500.12345678",
                "USD": "127518518.25",
                "timestamp": 1743469200000
            },
            "high": "86000.00",
            "low": "84000.00"
        }
        print(f"\nMock Ticker Data: {json.dumps(mock_ticker, indent=2)}")

if __name__ == "__main__":
    test_gemini_api()