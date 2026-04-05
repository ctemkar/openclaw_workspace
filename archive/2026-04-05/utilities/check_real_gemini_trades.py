#!/usr/bin/env python3
"""
Check REAL Gemini trades by querying Gemini API directly
"""

import os
import json
import requests
import hmac
import hashlib
import base64
import time
from datetime import datetime

# Try to get Gemini API keys from environment or config
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_SECRET = os.environ.get('GEMINI_API_SECRET')

if not GEMINI_API_KEY or not GEMINI_API_SECRET:
    print("❌ Gemini API keys not found in environment")
    print("Checking for config files...")
    
    # Check common config files
    config_files = [
        'gemini_config.json',
        'config.json',
        '.env',
        'secrets.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    GEMINI_API_KEY = config.get('GEMINI_API_KEY') or config.get('gemini_api_key')
                    GEMINI_API_SECRET = config.get('GEMINI_API_SECRET') or config.get('gemini_api_secret')
                    if GEMINI_API_KEY and GEMINI_API_SECRET:
                        print(f"✅ Found API keys in {config_file}")
                        break
            except:
                pass

if not GEMINI_API_KEY or not GEMINI_API_SECRET:
    print("❌ Gemini API keys not found in environment")
    print("Checking secure_keys directory...")
    
    # Check secure_keys directory
    secure_dir = "secure_keys"
    if os.path.exists(secure_dir):
        gemini_key_file = os.path.join(secure_dir, ".gemini_key")
        gemini_secret_file = os.path.join(secure_dir, ".gemini_secret")
        
        if os.path.exists(gemini_key_file) and os.path.exists(gemini_secret_file):
            try:
                with open(gemini_key_file, 'r') as f:
                    GEMINI_API_KEY = f.read().strip()
                with open(gemini_secret_file, 'r') as f:
                    GEMINI_API_SECRET = f.read().strip()
                print("✅ Found API keys in secure_keys directory")
            except Exception as e:
                print(f"❌ Error reading key files: {e}")
        else:
            print(f"❌ Key files not found: {gemini_key_file}, {gemini_secret_file}")
    else:
        print(f"❌ secure_keys directory not found")

if not GEMINI_API_KEY or not GEMINI_API_SECRET:
    print("❌❌❌ CRITICAL: NO GEMINI API KEYS FOUND!")
    print("Cannot check real trades without API keys")
    exit(1)

def gemini_request(endpoint, payload=None):
    """Make authenticated request to Gemini API"""
    url = f"https://api.gemini.com/v1{endpoint}"
    
    if payload is None:
        payload = {}
    
    payload['request'] = endpoint
    payload['nonce'] = str(int(time.time() * 1000))
    
    payload_json = json.dumps(payload)
    payload_b64 = base64.b64encode(payload_json.encode())
    
    signature = hmac.new(
        GEMINI_API_SECRET.encode(),
        payload_b64,
        hashlib.sha384
    ).hexdigest()
    
    headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': GEMINI_API_KEY,
        'X-GEMINI-PAYLOAD': payload_b64.decode(),
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

print("🔍 Checking REAL Gemini trades and balances...")
print("="*60)

# 1. Check balances
print("\n💰 REAL GEMINI BALANCES:")
balances = gemini_request("/balances")
print(f"   Raw response: {balances}")
if isinstance(balances, dict) and "error" in balances:
    print(f"   ❌ Error: {balances['error']}")
elif isinstance(balances, list):
    for balance in balances:
        if isinstance(balance, dict):
            currency = balance.get('currency', 'Unknown')
            amount = float(balance.get('amount', 0))
            available = float(balance.get('available', 0))
            if amount > 0:
                print(f"   {currency}: {amount:.8f} (Available: {available:.8f})")
else:
    print(f"   ❌ Unexpected response format: {type(balances)}")

# 2. Check past trades
print("\n📊 REAL GEMINI TRADE HISTORY:")
trades = gemini_request("/mytrades", {"symbol": "btcusd", "limit_trades": 10})
if "error" in trades:
    print(f"   ❌ Error: {trades['error']}")
else:
    print(f"   Found {len(trades)} recent BTC/USD trades:")
    for trade in trades[:5]:  # Show last 5
        timestamp = datetime.fromtimestamp(trade['timestampms'] / 1000)
        side = trade['side'].upper()
        price = float(trade['price'])
        amount = float(trade['amount'])
        total = price * amount
        print(f"   • {timestamp.strftime('%H:%M:%S')} - {side} {amount:.6f} BTC @ ${price:,.2f} (${total:,.2f})")

# 3. Check open orders
print("\n📋 REAL GEMINI OPEN ORDERS:")
orders = gemini_request("/orders")
if "error" in orders:
    print(f"   ❌ Error: {orders['error']}")
else:
    open_orders = [o for o in orders if o['is_live']]
    print(f"   {len(open_orders)} open orders:")
    for order in open_orders[:3]:
        symbol = order['symbol']
        side = order['side'].upper()
        price = float(order['price'])
        amount = float(order['original_amount'])
        remaining = float(order['remaining_amount'])
        print(f"   • {symbol} {side} {remaining:.6f}/{amount:.6f} @ ${price:,.2f}")

print("\n" + "="*60)
print("⚠️  If Gemini shows trades but this script shows none,")
print("    the API keys might be wrong or permissions insufficient.")
print("="*60)