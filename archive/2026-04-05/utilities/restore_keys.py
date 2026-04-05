#!/usr/bin/env python3
"""
Restore API keys from known values
"""

import os

print("🔑 RESTORING API KEYS")
print("="*60)

# Your known keys (replace with actual values)
GEMINI_KEY = "account-OWhm4Tn1VHlfjmdKL5Cw"
GEMINI_SECRET = ""  # You need to provide this

BINANCE_KEY = "SdiE3ZgEYz4soJfDbKPrdBBfQnU6D9"
BINANCE_SECRET = ""  # You need to provide this

print(f"Gemini Key: {GEMINI_KEY[:10]}...")
print(f"Binance Key: {BINANCE_KEY[:10]}...")

if not GEMINI_SECRET:
    GEMINI_SECRET = input("Enter Gemini Secret: ").strip()

if not BINANCE_SECRET:
    BINANCE_SECRET = input("Enter Binance Secret: ").strip()

# Create secure directory
os.makedirs("secure_keys", exist_ok=True)

# Save Gemini keys
with open("secure_keys/.gemini_key", "w") as f:
    f.write(GEMINI_KEY)
with open("secure_keys/.gemini_secret", "w") as f:
    f.write(GEMINI_SECRET)

# Save Binance keys
with open("secure_keys/.binance_key", "w") as f:
    f.write(BINANCE_KEY)
with open("secure_keys/.binance_secret", "w") as f:
    f.write(BINANCE_SECRET)

# Set permissions
os.chmod("secure_keys/.gemini_key", 0o600)
os.chmod("secure_keys/.gemini_secret", 0o600)
os.chmod("secure_keys/.binance_key", 0o600)
os.chmod("secure_keys/.binance_secret", 0o600)

print("\n✅ KEYS RESTORED!")
print(f"Gemini Secret: {GEMINI_SECRET[:10]}... ({len(GEMINI_SECRET)} chars)")
print(f"Binance Secret: {BINANCE_SECRET[:10]}... ({len(BINANCE_SECRET)} chars)")

# Test connections
print("\n🔌 TESTING CONNECTIONS...")
import ccxt

try:
    exchange = ccxt.gemini({'apiKey': GEMINI_KEY, 'secret': GEMINI_SECRET})
    balance = exchange.fetch_balance()
    print(f"✅ Gemini: ${balance['free'].get('USD', 0):.2f} available")
except Exception as e:
    print(f"❌ Gemini: {e}")

try:
    exchange = ccxt.binance({'apiKey': BINANCE_KEY, 'secret': BINANCE_SECRET})
    balance = exchange.fetch_balance()
    print(f"✅ Binance: ${balance['free'].get('USDT', 0):.2f} available")
except Exception as e:
    print(f"❌ Binance: {e}")

print("\n🎯 READY FOR REAL TRADING!")