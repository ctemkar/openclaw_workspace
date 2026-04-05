#!/usr/bin/env python3
"""
FIX GEMINI NONCE FINAL - Reset to VERY HIGH value to bypass Gemini's memory
"""

import json
import time

print("🔧 FIXING GEMINI NONCE ISSUE FINALLY")
print("="*60)

# Current time in microseconds
current_micro = int(time.time() * 1000000)
print(f"Current time (microseconds): {current_micro:,}")

# The problem: Gemini remembers the LAST successful nonce
# Even with microseconds, if we use a value close to last used, Gemini rejects it

# Solution: Set nonce to VERY HIGH value (far in the future)
# Add 1,000,000,000 microseconds = 1,000 seconds = 16.7 minutes
new_nonce = current_micro + 1000000000

print(f"\n🎯 SETTING NONCE TO: {new_nonce:,}")
print(f"   That's {new_nonce - current_micro:,} microseconds in the future")
print(f"   (About 16.7 minutes ahead of current time)")

# Also create a nonce tracker that ALWAYS increments
nonce_tracker = {
    "last_nonce": new_nonce,
    "last_updated": time.time(),
    "increment_strategy": "always_add_1000000",
    "note": "Gemini remembers last successful nonce. Always increment by at least 1,000,000 (1 second)"
}

# Save to file
with open('gemini_nonce.json', 'w') as f:
    json.dump(nonce_tracker, f, indent=2)

print(f"\n✅ Saved to gemini_nonce.json")
print(f"Next request will use nonce: {new_nonce:,}")

print("\n" + "="*60)
print("🎯 WHY THIS SHOULD WORK:")
print("1. Gemini server remembers the LAST nonce that worked")
print("2. If we use a nonce close to that, Gemini rejects 'has not increased'")
print("3. By setting a VERY HIGH nonce (16.7 minutes in future), we bypass Gemini's memory")
print("4. Future requests will increment from this high base (+1,000,000 each time)")
print("="*60)

print("\n🔧 TESTING THE FIX...")
print("Making a test Gemini API request...")

import os
import base64
import hmac
import hashlib
import requests

try:
    # Load Gemini keys
    with open('secure_keys/.gemini_key', 'r') as f:
        gemini_key = f.read().strip()
    with open('secure_keys/.gemini_secret', 'r') as f:
        gemini_secret = f.read().strip().encode()
    
    # Use the new nonce
    nonce = new_nonce
    
    payload_json = {
        "request": "/v1/symbols",
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
    
    response = requests.post("https://api.gemini.com/v1/symbols", headers=headers, timeout=10)
    result = response.json()
    
    if "error" in result:
        print(f"❌ Still getting error: {result.get('error')}")
        print(f"   Nonce used: {nonce}")
    else:
        print(f"✅ SUCCESS! Gemini API responding")
        print(f"   Got {len(result)} symbols")
        print(f"   First 5: {result[:5]}")
        
except Exception as e:
    print(f"❌ Test error: {e}")

print("\n" + "="*60)
print("✅ FIX APPLIED")
print("Next bot request should work with the new high nonce")
print("="*60)