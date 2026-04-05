#!/usr/bin/env python3
"""
Helper to update Binance keys in .env file
"""
import os

print("🔑 BINANCE API KEY UPDATER")
print("="*50)

# Read current .env
with open('.env', 'r') as f:
    content = f.read()

print("📄 Current .env file content (Binance section):")
for line in content.split('\n'):
    if 'BINANCE' in line:
        print(f"   {line}")

print("\n🎯 TO UPDATE:")
print("1. Please provide NEW Binance API Key:")
print("2. Please provide NEW Binance API Secret:")
print("\n📝 Or you can edit .env file manually:")
print("   - Open .env in text editor")
print("   - Replace BINANCE_API_KEY and BINANCE_API_SECRET lines")
print("   - Save file")
print("\n🚀 After updating, I'll test the new keys immediately!")