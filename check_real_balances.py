#!/usr/bin/env python3
"""
CHECK REAL BALANCES - Verify actual funds before trading
"""

import ccxt
import os
import json
import time
import base64
import hmac
import hashlib
import requests

print("💰 CHECKING REAL BALANCES")
print("="*60)

# Load Binance keys
try:
    with open('secure_keys/.binance_key', 'r') as f:
        binance_key = f.read().strip()
    with open('secure_keys/.binance_secret', 'r') as f:
        binance_secret = f.read().strip()
    print(f"✅ Loaded Binance key: {binance_key[:10]}...")
except Exception as e:
    print(f"❌ Error loading Binance keys: {e}")
    binance_key = ""
    binance_secret = ""

# Load Gemini keys
try:
    with open('secure_keys/.gemini_key', 'r') as f:
        gemini_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        gemini_secret = f.read().strip()
    print(f"✅ Loaded Gemini key: {gemini_key[:10]}...")
except Exception as e:
    print(f"❌ Error loading Gemini keys: {e}")
    gemini_key = ""
    gemini_secret = b""

# Check Binance balance
print("\n📊 BINANCE BALANCE:")
if binance_key and binance_secret:
    try:
        binance = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            'enableRateLimit': True
        })
        
        balance = binance.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        total_balance = balance.get('total', {}).get('USDT', 0)
        
        print(f"   Free USDT: ${usdt_balance:.2f}")
        print(f"   Total USDT: ${total_balance:.2f}")
        
        # Check other cryptos
        cryptos_with_balance = []
        for crypto, data in balance.get('total', {}).items():
            if data > 0 and crypto != 'USDT':
                cryptos_with_balance.append(f"{crypto}: {data}")
        
        if cryptos_with_balance:
            print(f"   Other holdings: {', '.join(cryptos_with_balance[:5])}")
        
        # Trading requirement
        MIN_TRADING_BALANCE = 30.0
        if usdt_balance >= MIN_TRADING_BALANCE:
            print(f"✅ Sufficient balance for trading (≥${MIN_TRADING_BALANCE})")
        else:
            print(f"❌ INSUFFICIENT BALANCE: ${usdt_balance:.2f} < ${MIN_TRADING_BALANCE}")
            print(f"   Need to deposit ${MIN_TRADING_BALANCE - usdt_balance:.2f} more")
            
    except Exception as e:
        print(f"❌ Error checking Binance balance: {e}")
else:
    print("❌ Binance keys not available")

# Check Gemini balance
print("\n📊 GEMINI BALANCE:")
if gemini_key and gemini_secret:
    try:
        # Gemini custom request
        def gemini_request(endpoint):
            url = f"https://api.gemini.com/v1{endpoint}"
            nonce = int(time.time() * 1000000)  # Your microsecond fix
            
            payload_json = {
                "request": f"/v1{endpoint}",
                "nonce": nonce
            }
            
            payload = base64.b64encode(json.dumps(payload_json).encode())
            signature = hmac.new(gemini_secret, payload, hashlib.sha384).hexdigest()
            
            headers = {
                "Content-Type": "text/plain",
                "Content-Length": "0",
                "X-GEMINI-APIKEY": gemini_key,
                "X-GEMINI-PAYLOAD": payload.decode(),
                "X-GEMINI-SIGNATURE": signature,
                "Cache-Control": "no-cache"
            }
            
            response = requests.post(url, headers=headers, timeout=10)
            return response.json()
        
        balances = gemini_request("/balances")
        
        if "error" in balances:
            print(f"❌ Gemini API error: {balances.get('error')}")
        elif isinstance(balances, list):
            print(f"   Found {len(balances)} accounts")
            
            usd_balance = 0
            cryptos_with_balance = []
            
            for account in balances:
                currency = account.get('currency', '')
                amount = float(account.get('amount', 0))
                available = float(account.get('available', 0))
                acc_type = account.get('type', '')
                
                if amount > 0:
                    if currency == 'USD' and acc_type == 'exchange':
                        usd_balance = available
                        print(f"   Exchange USD: ${available:.2f} (total: ${amount:.2f})")
                    elif amount > 0.001:  # Ignore tiny amounts
                        cryptos_with_balance.append(f"{currency}: {amount}")
            
            if cryptos_with_balance:
                print(f"   Crypto holdings: {', '.join(cryptos_with_balance[:5])}")
            
            # Trading requirement
            MIN_TRADING_BALANCE = 30.0
            if usd_balance >= MIN_TRADING_BALANCE:
                print(f"✅ Sufficient balance for trading (≥${MIN_TRADING_BALANCE})")
            else:
                print(f"❌ INSUFFICIENT BALANCE: ${usd_balance:.2f} < ${MIN_TRADING_BALANCE}")
                print(f"   Need to deposit ${MIN_TRADING_BALANCE - usd_balance:.2f} more")
        else:
            print(f"❌ Unexpected Gemini response: {balances}")
            
    except Exception as e:
        print(f"❌ Error checking Gemini balance: {e}")
else:
    print("❌ Gemini keys not available")

print("\n" + "="*60)
print("🎯 TRADING REQUIREMENTS:")
print("1. Binance: ≥$30 USDT available")
print("2. Gemini: ≥$30 USD available")
print("3. Both APIs: Trading enabled")
print("="*60)
print("⚠️  Without sufficient balances, NO REAL TRADING CAN OCCUR")
print("="*60)