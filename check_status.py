#!/usr/bin/env python3
"""
Check trading system status
"""

import json
import urllib.request
import sys

try:
    url = "http://127.0.0.1:5001/status"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
    
    print("✅ REAL TRADING SYSTEM STATUS:")
    print(f"   Status: {data.get('status', 'unknown')}")
    print(f"   Capital: ${data.get('capital', 0):.2f}")
    print(f"   Last analysis: {data.get('last_analysis', 'just now')}")
    print(f"   Port: {data.get('port', 5001)}")
    print(f"   Trading pairs: {data.get('trading_pairs', [])}")
    
except Exception as e:
    print(f"⚠️ Status check failed: {e}")
    print("   Trying to check server process...")
    import subprocess
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    if "trading_server.py" in result.stdout:
        print("   ✅ Trading server is running")
    else:
        print("   ❌ Trading server not found")