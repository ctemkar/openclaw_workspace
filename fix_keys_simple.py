#!/usr/bin/env python3
"""
Copy API keys from .env to secure_keys/
"""

import os
import json
import re

def load_env():
    """Load .env file manually"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    except Exception as e:
        print(f"Error loading .env: {e}")
    return env_vars

env = load_env()

# Create secure_keys directory
os.makedirs('secure_keys', exist_ok=True)

# Gemini keys
gemini_keys = {
    'api_key': env.get('GEMINI_API_KEY', ''),
    'api_secret': env.get('GEMINI_API_SECRET', '')
}

# Binance keys
binance_keys = {
    'api_key': env.get('BINANCE_API_KEY', ''),
    'api_secret': env.get('BINANCE_API_SECRET', '')
}

# Save to secure_keys
with open('secure_keys/gemini_keys.json', 'w') as f:
    json.dump(gemini_keys, f, indent=2)
    print("✅ Gemini keys saved to secure_keys/gemini_keys.json")

with open('secure_keys/binance_keys.json', 'w') as f:
    json.dump(binance_keys, f, indent=2)
    print("✅ Binance keys saved to secure_keys/binance_keys.json")

print("\n🔑 Keys copied from .env to secure_keys/")
print(f"Gemini API key present: {'Yes' if gemini_keys['api_key'] else 'No'}")
print(f"Binance API key present: {'Yes' if binance_keys['api_key'] else 'No'}")
