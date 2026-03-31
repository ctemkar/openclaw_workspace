#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get('http://localhost:5001/', timeout=10)
    response.raise_for_status()
    print(response.text)
except Exception as e:
    print(f"Error fetching dashboard: {e}", file=sys.stderr)
    sys.exit(1)