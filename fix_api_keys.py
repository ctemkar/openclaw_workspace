#!/usr/bin/env python3
"""
Fix API keys by copying valid keys from .env to secure_keys/
"""

import os
import re

print("🔧 FIXING API KEYS")
print("="*60)

# Read .env file
with open('.env', 'r') as f:
    env_content = f.read()

# Extract keys from .env
gemini_key_match = re.search(r'GEMINI_API_KEY=([^\n]+)', env_content)
gemini_secret_match = re.search(r'GEMINI_API_SECRET=([^\n]+)', env_content)
binance_key_match = re.search(r'BINANCE_API_KEY=([^\n]+)', env_content)
binance_secret_match = re.search(r'BINANCE_API_SECRET=([^\n]+)', env_content)

if not all([gemini_key_match, gemini_secret_match, binance_key_match, binance_secret_match]):
    print("❌ Could not extract all keys from .env")
    exit(1)

gemini_key = gemini_key_match.group(1).strip()
gemini_secret = gemini_secret_match.group(1).strip()
binance_key = binance_key_match.group(1).strip()
binance_secret = binance_secret_match.group(1).strip()

print(f"✅ Extracted keys from .env:")
print(f"   Gemini Key: {gemini_key[:10]}...{gemini_key[-10:]}")
print(f"   Gemini Secret: {gemini_secret[:10]}...{gemini_secret[-10:]}")
print(f"   Binance Key: {binance_key[:10]}...{binance_key[-10:]}")
print(f"   Binance Secret: {binance_secret[:10]}...{binance_secret[-10:]}")

# Write to secure_keys/
os.makedirs('secure_keys', exist_ok=True)

with open('secure_keys/.gemini_key', 'w') as f:
    f.write(gemini_key)
    print("✅ Updated secure_keys/.gemini_key")

with open('secure_keys/.gemini_secret', 'w') as f:
    f.write(gemini_secret)
    print("✅ Updated secure_keys/.gemini_secret")

with open('secure_keys/.binance_key', 'w') as f:
    f.write(binance_key)
    print("✅ Updated secure_keys/.binance_key")

with open('secure_keys/.binance_secret', 'w') as f:
    f.write(binance_secret)
    print("✅ Updated secure_keys/.binance_secret")

print("\n" + "="*60)
print("✅ API KEYS FIXED!")
print("="*60)
print("\nThe trading system should now work with the valid API keys.")
print("You can restart the trading bot.")