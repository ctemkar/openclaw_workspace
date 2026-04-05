#!/usr/bin/env python3
"""
Test REAL exchange connections
"""
import os
import ccxt
import sys

print("🔍 TESTING REAL EXCHANGE CONNECTIONS...")
print("=" * 50)

# Test Gemini
try:
    with open('.gemini_key', 'r') as f:
        gemini_key = f.read().strip()
    with open('.gemini_secret', 'r') as f:
        gemini_secret = f.read().strip()
    
    if gemini_key and gemini_secret and 'YOUR_ACTUAL' not in gemini_key:
        exchange = ccxt.gemini({
            'apiKey': gemini_key,
            'secret': gemini_secret,
            'enableRateLimit': True
        })
        balance = exchange.fetch_balance()
        usd_balance = balance['total'].get('USD', 0)
        print(f"✅ GEMINI CONNECTED: ${usd_balance:.2f} available")
        print(f"   First 8 chars of key: {gemini_key[:8]}...")
    else:
        print("❌ GEMINI: Invalid or placeholder keys")
        
except FileNotFoundError:
    print("❌ GEMINI: Key files not found")
except Exception as e:
    print(f"❌ GEMINI ERROR: {e}")

print("-" * 30)

# Test Binance
try:
    with open('.binance_key', 'r') as f:
        binance_key = f.read().strip()
    with open('.binance_secret', 'r') as f:
        binance_secret = f.read().strip()
    
    if binance_key and binance_secret and 'YOUR_ACTUAL' not in binance_key:
        exchange = ccxt.binance({
            'apiKey': binance_key,
            'secret': binance_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        balance = exchange.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        print(f"✅ BINANCE CONNECTED: ${usdt_balance:.2f} available")
        print(f"   First 8 chars of key: {binance_key[:8]}...")
    else:
        print("❌ BINANCE: Invalid or placeholder keys")
        
except FileNotFoundError:
    print("❌ BINANCE: Key files not found")
except Exception as e:
    print(f"❌ BINANCE ERROR: {e}")

print("=" * 50)
