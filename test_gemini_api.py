#!/usr/bin/env python3
import requests
import json
import hmac
import hashlib
import base64
import time

api_key = 'account-OWhm4Tn1VHlfjmdKL5Cw'
api_secret = '3FKMV3amENxty5bq9ag35fFbXCSY'

# Test public endpoint first
print('Testing public endpoint...')
try:
    response = requests.get('https://api.gemini.com/v1/pubticker/btcusd', timeout=10)
    print(f'Public API status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'BTC Price: ${float(data["last"]):,.2f}')
except Exception as e:
    print(f'Public API error: {e}')

# Test private endpoint with proper payload
print('\nTesting private endpoint...')
try:
    payload = {
        'request': '/v1/balances',
        'nonce': str(int(time.time() * 1000))
    }
    
    payload_str = json.dumps(payload)
    signature = hmac.new(
        api_secret.encode(),
        payload_str.encode(),
        hashlib.sha384
    ).hexdigest()
    
    headers = {
        'Content-Type': 'text/plain',
        'Content-Length': '0',
        'X-GEMINI-APIKEY': api_key,
        'X-GEMINI-PAYLOAD': base64.b64encode(payload_str.encode()).decode(),
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': 'no-cache'
    }
    
    response = requests.post('https://api.gemini.com/v1/balances', headers=headers, timeout=30)
    print(f'Private API status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
    
    # Try to parse JSON
    if response.status_code == 200:
        try:
            data = response.json()
            print(f'Parsed JSON: {data}')
        except:
            print('Could not parse JSON')
    else:
        print(f'Error response: {response.text}')
        
except Exception as e:
    print(f'Private API error: {e}')