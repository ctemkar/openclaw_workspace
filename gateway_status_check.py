#!/usr/bin/env python3
"""
Gateway Status Check
Checks if gateway service can be started on port 5000
"""

import socket
import sys
from datetime import datetime

def check_port(port):
    """Check if port is available"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', port))
        s.close()
        return result == 0  # True if port is in use
    except Exception as e:
        return f"Error checking port: {e}"

def main():
    port = 5000
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    
    print(f"🔍 Gateway Status Check - {now}")
    print(f"Port: {port}")
    
    port_in_use = check_port(port)
    
    if port_in_use is True:
        print(f"❌ Port {port} is already in use")
        print("Current service using port 5000: Control Center")
        print("\nRecommendation:")
        print("1. Use a different port for gateway service")
        print("2. Or stop Control Center service temporarily")
        print("\nExample alternative ports: 5001, 8080, 8081")
    elif isinstance(port_in_use, str):
        print(f"⚠️ {port_in_use}")
    else:
        print(f"✅ Port {port} is available")
        print("Gateway service can be started on this port")
    
    print(f"\nChecked at: {now}")
    return 0

if __name__ == "__main__":
    sys.exit(main())