#!/usr/bin/env python3
"""
Check EVERYTHING on Gemini using API keys
"""

import os
import json
import requests
import hmac
import hashlib
import base64
import time
from datetime import datetime

print("🔍 CHECKING GEMINI - DOING THE WORK MYSELF")
print("="*60)

# Load API keys from secure_keys
try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    print("✅ Gemini API keys loaded from secure_keys")
except Exception as e:
    print(f"❌ Failed to load API keys: {e}")
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
        GEMINI_SECRET.encode(),
        payload_b64,
        hashlib.sha384
    ).hexdigest()
    
    headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': GEMINI_KEY,
        'X-GEMINI-PAYLOAD': payload_b64.decode(),
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

print("\n💰 CHECKING BALANCES...")
balances = gemini_request("/balances")
if isinstance(balances, list):
    print("✅ Balances retrieved successfully")
    total_usd = 0
    total_btc = 0
    
    for balance in balances:
        currency = balance['currency']
        amount = float(balance['amount'])
        available = float(balance['available'])
        
        if amount > 0:
            print(f"  {currency}: {amount:.8f} (Available: {available:.8f})")
            
            if currency == 'USD':
                total_usd = amount
            elif currency == 'BTC':
                total_btc = amount
else:
    print(f"❌ Failed to get balances: {balances}")

print("\n📊 CHECKING TRADE HISTORY...")
# Get today's trades
today = datetime.now().strftime('%Y-%m-%d')
trades = gemini_request("/mytrades", {"symbol": "btcusd", "limit_trades": 50})

if isinstance(trades, list):
    print(f"✅ Found {len(trades)} BTC/USD trades")
    
    today_trades = []
    for trade in trades:
        timestamp = datetime.fromtimestamp(trade['timestampms'] / 1000)
        if timestamp.strftime('%Y-%m-%d') == today:
            today_trades.append(trade)
    
    print(f"  Today's trades: {len(today_trades)}")
    
    total_buys = 0
    total_sells = 0
    btc_bought = 0
    btc_sold = 0
    
    for trade in today_trades[:10]:  # Show first 10
        timestamp = datetime.fromtimestamp(trade['timestampms'] / 1000)
        side = trade['side'].upper()
        price = float(trade['price'])
        amount = float(trade['amount'])
        fee = float(trade.get('fee_amount', 0))
        
        if side == 'BUY':
            total_buys += price * amount
            btc_bought += amount
        else:
            total_sells += price * amount
            btc_sold += amount
        
        print(f"  {timestamp.strftime('%H:%M:%S')} - {side} {amount:.6f} BTC @ ${price:,.2f}")
    
    print(f"\n  📈 Today's summary:")
    print(f"    BTC bought: {btc_bought:.6f} (${total_buys:,.2f})")
    print(f"    BTC sold: {btc_sold:.6f} (${total_sells:,.2f})")
    print(f"    Net BTC: {btc_bought - btc_sold:.6f}")
    print(f"    Net USD: ${total_sells - total_buys:,.2f}")
else:
    print(f"❌ Failed to get trades: {trades}")

print("\n📋 CHECKING OPEN ORDERS...")
orders = gemini_request("/orders")
if isinstance(orders, list):
    open_orders = [o for o in orders if o['is_live']]
    print(f"✅ Found {len(open_orders)} open orders")
    
    for order in open_orders[:5]:  # Show first 5
        symbol = order['symbol']
        side = order['side'].upper()
        price = float(order['price'])
        amount = float(order['original_amount'])
        remaining = float(order['remaining_amount'])
        print(f"  {symbol} {side} {remaining:.6f}/{amount:.6f} @ ${price:,.2f}")
else:
    print(f"❌ Failed to get orders: {orders}")

print("\n📈 CHECKING CURRENT PRICES...")
try:
    ticker = requests.get("https://api.gemini.com/v1/pubticker/btcusd", timeout=5).json()
    btc_price = float(ticker['last'])
    print(f"✅ Current BTC price: ${btc_price:,.2f}")
    
    # Calculate portfolio value if we have BTC
    if 'total_btc' in locals() and total_btc > 0:
        btc_value = total_btc * btc_price
        total_portfolio = total_usd + btc_value
        print(f"  Portfolio value:")
        print(f"    USD: ${total_usd:,.2f}")
        print(f"    BTC: {total_btc:.6f} (${btc_value:,.2f} @ ${btc_price:,.2f})")
        print(f"    TOTAL: ${total_portfolio:,.2f}")
except Exception as e:
    print(f"❌ Failed to get prices: {e}")

print("\n" + "="*60)
print("✅ DONE - I did the work myself!")
print("Now I have REAL data from Gemini API.")
print("="*60)