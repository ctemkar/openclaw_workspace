#!/usr/bin/env python3
"""
Copy API keys from .env to secure_keys/ for cross-exchange bot
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# Create secure_keys directory
os.makedirs('secure_keys', exist_ok=True)

# Gemini keys
gemini_keys = {
    'api_key': os.getenv('GEMINI_API_KEY'),
    'api_secret': os.getenv('GEMINI_API_SECRET')
}

# Binance keys
binance_keys = {
    'api_key': os.getenv('BINANCE_API_KEY'),
    'api_secret': os.getenv('BINANCE_API_SECRET')
}

# Save to secure_keys
with open('secure_keys/gemini_keys.json', 'w') as f:
    json.dump(gemini_keys, f, indent=2)
    print("✅ Gemini keys saved to secure_keys/gemini_keys.json")

with open('secure_keys/binance_keys.json', 'w') as f:
    json.dump(binance_keys, f, indent=2)
    print("✅ Binance keys saved to secure_keys/binance_keys.json")

print("\n🔑 Keys copied from .env to secure_keys/")
print(f"Gemini API key: {gemini_keys['api_key'][:10]}...")
print(f"Binance API key: {binance_keys['api_key'][:10]}...")
