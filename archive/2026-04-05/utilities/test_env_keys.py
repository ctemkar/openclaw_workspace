#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔐 Testing Environment Variables")
print("=" * 40)

keys_to_check = [
    'GEMINI_API_KEY',
    'GEMINI_API_SECRET', 
    'BINANCE_API_KEY',
    'BINANCE_API_SECRET',
    'OPENROUTER_API_KEY'
]

for key in keys_to_check:
    value = os.getenv(key)
    if value:
        print(f"✅ {key}: {value[:10]}... (length: {len(value)})")
    else:
        print(f"❌ {key}: NOT SET")

print("\n⚠️  If keys are missing, add them to .env file")
print("⚠️  If .env doesn't exist, create it from .env.template")
