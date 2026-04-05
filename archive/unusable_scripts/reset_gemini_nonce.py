#!/usr/bin/env python3
"""
RESET GEMINI NONCE - Set to VERY HIGH value to bypass Gemini's memory
"""

import json
import time

print("🔧 RESETTING GEMINI NONCE")
print("="*60)

# Current time in microseconds
current_micro = int(time.time() * 1000000)
print(f"Current time (microseconds): {current_micro:,}")

# Gemini is remembering our last successful nonce
# We need to set it to a VERY HIGH value
new_nonce = current_micro + 1000000000  # Add 1,000 seconds (16.7 minutes)

print(f"Setting nonce to: {new_nonce:,}")
print(f"That's {new_nonce - current_micro:,} microseconds in the future")

# Save to file
with open('gemini_nonce.json', 'w') as f:
    json.dump({'last_nonce': new_nonce}, f)

print(f"✅ Saved to gemini_nonce.json")
print(f"Next request will use nonce: {new_nonce:,}")

print("\n" + "="*60)
print("🎯 WHY THIS WORKS:")
print("1. Gemini remembers the LAST nonce that worked")
print("2. If we use a nonce close to that, Gemini rejects it")
print("3. By setting a VERY HIGH nonce, we bypass Gemini's memory")
print("4. Future requests will increment from this high base")
print("="*60)