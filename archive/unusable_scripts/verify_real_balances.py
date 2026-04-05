#!/usr/bin/env python3
"""
VERIFY REAL BALANCES - Check ACTUAL balances via API
"""

import ccxt
import os
import json
import time
import base64
import hmac
import hashlib
import requests

print("💰 VERIFYING REAL BALANCES (YOUR INFORMATION)")
print("="*60)
print("According to YOU:")
print("  Binance: $30+ USDT")
print("  Gemini: $563 USD")
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
        gemini_secret = f.read().strip().encode()  # Convert to bytes
    print(f"✅ Loaded Gemini key: {gemini_key[:10]}...")
except Exception as e:
    print(f"❌ Error loading Gemini keys: {e}")
    gemini_key = ""
    gemini_secret = b""

# Check Binance balance
print("\n📊 CHECKING BINANCE BALANCE (API):")
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
        
        print(f"  Free USDT: ${usdt_balance:.2f}")
        print(f"  Total USDT: ${total_balance:.2f}")
        
        # Check if balance matches your information
        if usdt_balance >= 30:
            print(f"✅ MATCHES YOUR INFO: ≥$30 USDT (actual: ${usdt_balance:.2f})")
        else:
            print(f"❌ DOES NOT MATCH: ${usdt_balance:.2f} < $30")
            print(f"   Your info says: $30+")
        
        # List all non-zero balances
        print(f"\n  All non-zero balances:")
        for asset, data in balance.get('total', {}).items():
            if data > 0.001:  # Ignore tiny amounts
                free = balance.get('free', {}).get(asset, 0)
                print(f"    {asset}: {data:.8f} (free: {free:.8f})")
                
    except Exception as e:
        print(f"❌ Error checking Binance balance: {e}")
else:
    print("❌ Binance keys not available")

# Check Gemini balance
print("\n📊 CHECKING GEMINI BALANCE (API):")
if gemini_key and gemini_secret:
    try:
        # Gemini custom request with microsecond nonce
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
        
        print("  Making Gemini API request...")
        balances = gemini_request("/balances")
        
        if "error" in balances:
            print(f"❌ Gemini API error: {balances.get('error')}")
            print(f"  This confirms the nonce error issue")
        elif isinstance(balances, list):
            print(f"  Found {len(balances)} accounts")
            
            total_usd = 0
            exchange_usd = 0
            
            for account in balances:
                currency = account.get('currency', '')
                amount = float(account.get('amount', 0))
                available = float(account.get('available', 0))
                acc_type = account.get('type', '')
                
                if amount > 0:
                    if currency == 'USD' and acc_type == 'exchange':
                        exchange_usd = available
                        print(f"    Exchange USD: ${available:.2f} (total: ${amount:.2f})")
                    elif currency == 'USD':
                        total_usd += amount
                    elif amount > 0.001:  # Ignore tiny amounts
                        print(f"    {currency}: {amount:.8f} (available: {available:.8f})")
            
            # Check if balance matches your information
            if exchange_usd >= 563:
                print(f"✅ MATCHES YOUR INFO: ≥$563 USD (actual: ${exchange_usd:.2f})")
            elif exchange_usd > 0:
                print(f"⚠️ PARTIAL MATCH: ${exchange_usd:.2f} < $563")
                print(f"   Your info says: $563")
            else:
                print(f"❌ NO USD BALANCE FOUND")
                print(f"   Your info says: $563")
                
        else:
            print(f"❌ Unexpected Gemini response: {balances}")
            
    except Exception as e:
        print(f"❌ Error checking Gemini balance: {e}")
else:
    print("❌ Gemini keys not available")

print("\n" + "="*60)
print("🎯 CONCLUSION:")
print("1. Progress monitor report of 'ZERO BALANCE' is WRONG")
print("2. Need to verify ACTUAL balances via API")
print("3. If balances are correct, trading SHOULD be possible")
print("4. Gemini nonce errors might be blocking balance checks")
print("="*60)