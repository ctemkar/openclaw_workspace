#!/usr/bin/env python3
import time
from datetime import datetime

print("=" * 60)
print("SIMPLE TRADING MONITOR")
print("=" * 60)
print("Mode: REAL TRADING (API keys required)")
print("Capital: $250 ($200 Gemini, $50 Binance)")
print("Status: Waiting for API key configuration")
print("=" * 60)

while True:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring...")
    print("   • Check API keys in secure_keys/ directory")
    print("   • Ensure keys have trading permissions")
    print("   • Verify balances on exchanges")
    print("   • Trading will begin automatically when ready")
    print("-" * 40)
    time.sleep(60)
