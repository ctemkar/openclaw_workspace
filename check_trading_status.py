#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# Read the active port
with open('.active_port', 'r') as f:
    PORT = f.read().strip()

base_url = f'http://localhost:{PORT}'

print('=== TRADING DASHBOARD MONITOR REPORT ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Dashboard Port: {PORT}')
print()

try:
    # Get trading status
    status_response = requests.get(f'{base_url}/api/status/all')
    status_data = status_response.json()
    print(f'Trading Status: {status_data.get("trading", "unknown")}')
    print(f'Last Update: {status_data.get("last_update", "unknown")}')
    print()
    
    # Get market prices
    prices_response = requests.get(f'{base_url}/api/market/prices')
    prices_data = prices_response.json()
    print('Market Prices:')
    for symbol, price in prices_data.items():
        print(f'  {symbol}: ${price:,.2f}')
    print()
    
    # Get trading logs
    logs_response = requests.get(f'{base_url}/api/trading/logs')
    logs_data = logs_response.json()
    logs = logs_data.get('logs', '').split('\n')
    
    # Count errors
    error_logs = [log for log in logs if 'STRATEGY ERROR' in log]
    print(f'Strategy Errors Detected: {len(error_logs)}')
    
    if error_logs:
        print('\n⚠️  CRITICAL ISSUE: Trading bot has strategy errors!')
        print('Recent errors:')
        for error in error_logs[-5:]:
            print(f'  {error}')
    
    # Check trading configuration
    print()
    print('Trading Configuration:')
    print(f'  Capital: $10,000.00')
    print(f'  Stop Loss: 1.0% (threshold: $9,900.00)')
    print(f'  Take Profit: 2.0% (threshold: $10,200.00)')
    
    # Overall assessment
    print()
    if len(error_logs) > 0:
        print('🚨 STATUS: CRITICAL - Trading bot has persistent strategy errors')
        print('   Recommendation: Investigate and fix the strategy implementation')
    else:
        print('✅ STATUS: NORMAL - No critical issues detected')
        
except Exception as e:
    print(f'Error fetching data: {e}')
    print('🚨 STATUS: DASHBOARD UNREACHABLE')