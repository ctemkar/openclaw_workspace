#!/usr/bin/env python3
"""
Check real Gemini account balance
"""

import os
import json
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_credentials():
    """Load Gemini API credentials"""
    try:
        with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, 'secure_keys/.gemini_secret'), 'r') as f:
            api_secret = f.read().strip()
        return api_key, api_secret.encode()
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None, None

def get_account_balance(api_key, api_secret):
    """Get real account balance from Gemini"""
    try:
        # Generate payload
        payload_nonce = str(int(time.time() * 1000))
        payload = {
            "request": "/v1/balances",
            "nonce": payload_nonce
        }
        
        payload_json = json.dumps(payload)
        payload_b64 = base64.b64encode(payload_json.encode()).decode()
        
        # Generate signature
        signature = hmac.new(
            api_secret,
            payload_b64.encode(),
            hashlib.sha384
        ).hexdigest()
        
        # Make request
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': '0',
            'X-GEMINI-APIKEY': api_key,
            'X-GEMINI-PAYLOAD': payload_b64,
            'X-GEMINI-SIGNATURE': signature
        }
        
        response = requests.post(
            'https://api.gemini.com/v1/balances',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting balance: {e}")
        return None

def main():
    print("="*60)
    print("💰 REAL GEMINI ACCOUNT BALANCE CHECK")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    print()
    
    # Load credentials
    api_key, api_secret = load_credentials()
    if not api_key or not api_secret:
        print("❌ Failed to load API credentials")
        return
    
    print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-10:]}")
    
    # Get balance
    balance_data = get_account_balance(api_key, api_secret)
    if not balance_data:
        print("❌ Failed to get account balance")
        return
    
    print("\n📊 ACCOUNT BALANCES:")
    print("-"*40)
    
    total_usd_value = 0
    has_btc = False
    has_eth = False
    
    for balance in balance_data:
        currency = balance['currency']
        amount = float(balance['amount'])
        available = float(balance['available'])
        
        if amount > 0:
            print(f"{currency}:")
            print(f"  Total: {amount:.8f}")
            print(f"  Available: {available:.8f}")
            
            # Get current price for valuation
            if currency in ['USD', 'USDC', 'GUSD']:
                usd_value = amount
                print(f"  Value: ${usd_value:.2f}")
                total_usd_value += usd_value
            elif currency == 'BTC':
                has_btc = True
                # Get BTC price
                try:
                    ticker = requests.get('https://api.gemini.com/v1/pubticker/btcusd', timeout=10).json()
                    btc_price = float(ticker['last'])
                    btc_value = amount * btc_price
                    print(f"  BTC Price: ${btc_price:,.2f}")
                    print(f"  Value: ${btc_value:,.2f}")
                    total_usd_value += btc_value
                except:
                    print(f"  Value: (price unavailable)")
            elif currency == 'ETH':
                has_eth = True
                # Get ETH price
                try:
                    ticker = requests.get('https://api.gemini.com/v1/pubticker/ethusd', timeout=10).json()
                    eth_price = float(ticker['last'])
                    eth_value = amount * eth_price
                    print(f"  ETH Price: ${eth_price:,.2f}")
                    print(f"  Value: ${eth_value:,.2f}")
                    total_usd_value += eth_value
                except:
                    print(f"  Value: (price unavailable)")
    
    print("-"*40)
    print(f"💰 TOTAL PORTFOLIO VALUE: ${total_usd_value:,.2f}")
    print("="*60)
    
    return total_usd_value, has_btc, has_eth

if __name__ == "__main__":
    main()