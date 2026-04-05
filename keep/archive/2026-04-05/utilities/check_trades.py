#!/usr/bin/env python3
import json
import subprocess

# Fetch trades data
result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], 
                       capture_output=True, text=True)

if result.returncode != 0:
    print("Failed to fetch trades")
    exit(1)

try:
    data = json.loads(result.stdout)
except json.JSONDecodeError:
    print("Invalid JSON response")
    exit(1)

print('Total trades:', data.get('count', 0))
print('Timestamp:', data.get('timestamp', 'N/A'))
print()
print('Recent trades:')
trades = data.get('trades', [])
for i, trade in enumerate(trades[:3], 1):
    symbol = trade.get('symbol', 'N/A')
    side = trade.get('side', 'N/A')
    price = trade.get('price', 0)
    time = trade.get('time', 'N/A')
    reason = trade.get('reason', '')
    
    print(f'{i}. {symbol} {side} @ ${price}')
    print(f'   Time: {time}')
    if len(reason) > 80:
        reason = reason[:80] + '...'
    print(f'   Reason: {reason}')
    print()

# Check if there are new trades since last check
print(f'Total of {len(trades)} trades in history')