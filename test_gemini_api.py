#!/usr/bin/env python3
"""
Test Gemini API connectivity
"""

import requests
import os
import json
import hmac
import hashlib
import base64
import time
from datetime import datetime

def test_public_api():
    """Test public Gemini API endpoints"""
    print("Testing public API endpoints...")
    
    endpoints = [
        ("BTC/USD", "https://api.gemini.com/v1/pubticker/btcusd"),
        ("ETH/USD", "https://api.gemini.com/v1/pubticker/ethusd"),
        ("Order Book BTC", "https://api.gemini.com/v1/book/btcusd"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            print(f"  {name}: Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if "last" in data:
                    print(f"    Price: ${float(data['last']):,.2f}")
                elif "bids" in data:
                    print(f"    Bids: {len(data['bids'])} levels")
        except Exception as e:
            print(f"  {name}: Error - {e}")

def load_credentials():
    """Load Gemini API credentials"""
    try:
        with open('/Users/chetantemkar/.openclaw/workspace/app/secure_keys/.gemini_key', 'r') as f:
            api_key = f.read().strip()
        with open('/Users/chetantemkar/.openclaw/workspace/app/secure_keys/.gemini_secret', 'r') as f:
            api_secret = f.read().strip()
        
        print(f"\nLoaded credentials:")
        print(f"  API Key: {api_key}")
        print(f"  API Secret: {api_secret[:5]}...{api_secret[-5:]}")
        
        return api_key, api_secret.encode()
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None, None

def test_private_api(api_key, api_secret):
    """Test private Gemini API endpoints"""
    if not api_key or not api_secret:
        print("No credentials available for private API test")
        return
    
    print("\nTesting private API endpoints...")
    
    # Test balances endpoint
    try:
        # Generate signature
        payload = {
            "request": "/v1/balances",
            "nonce": str(int(time.time() * 1000))
        }
        
        payload_str = json.dumps(payload)
        signature = hmac.new(
            api_secret,
            payload_str.encode(),
            hashlib.sha384
        ).hexdigest()
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": api_key,
            "X-GEMINI-PAYLOAD": base64.b64encode(payload_str.encode()).decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        url = "https://api.gemini.com/v1/balances"
        response = requests.post(url, headers=headers, timeout=30)
        
        print(f"  Balances endpoint: Status {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success! Account data received")
            for balance in data:
                print(f"    {balance['currency']}: {balance['amount']} ({balance['available']} available)")
        else:
            print(f"  Error details: {response.text}")
            
    except Exception as e:
        print(f"  Private API error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 70)
    print("GEMINI API CONNECTIVITY TEST")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    
    # Test public API
    test_public_api()
    
    # Load and test private API
    api_key, api_secret = load_credentials()
    test_private_api(api_key, api_secret)
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()