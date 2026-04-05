#!/usr/bin/env python3
import re
from datetime import datetime

# Read the trading log
with open('trading_monitoring.log', 'r') as f:
    lines = f.readlines()

print('=== TRADING ERROR ANALYSIS ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Count different types of errors
strategy_errors = []
trade_failures = []
successful_trades = []

for line in lines[-100:]:  # Check last 100 lines
    if 'STRATEGY ERROR' in line:
        strategy_errors.append(line.strip())
    elif 'TRADE FAILURE' in line:
        trade_failures.append(line.strip())
    elif 'SUCCESS:' in line and 'filled at' in line:
        successful_trades.append(line.strip())

print(f'Strategy Errors (last 100 lines): {len(strategy_errors)}')
print(f'Trade Failures (last 100 lines): {len(trade_failures)}')
print(f'Successful Trades (last 100 lines): {len(successful_trades)}')
print()

# Analyze strategy errors
if strategy_errors:
    print('=== STRATEGY ERROR PATTERNS ===')
    error_patterns = {}
    for error in strategy_errors[-10:]:  # Last 10 errors
        # Extract error message
        match = re.search(r"STRATEGY ERROR: (.*)", error)
        if match:
            error_msg = match.group(1)
            error_patterns[error_msg] = error_patterns.get(error_msg, 0) + 1
    
    for error_msg, count in error_patterns.items():
        print(f'{count}x: {error_msg}')
    
    # Check for common patterns
    if "'str' object has no attribute 'get'" in error_patterns:
        print('\n⚠️  COMMON ERROR: String object missing .get() method')
        print('   Likely issue: API response parsing error')
        print('   Recommendation: Check data structure from trading API')

print()

# Analyze trade failures
if trade_failures:
    print('=== TRADE FAILURE ANALYSIS ===')
    failure_reasons = {}
    for failure in trade_failures[-5:]:  # Last 5 failures
        # Extract reason
        if 'insufficient funds' in failure:
            failure_reasons['insufficient_funds'] = failure_reasons.get('insufficient_funds', 0) + 1
        elif 'price' in failure and 'quantity' in failure:
            failure_reasons['order_failure'] = failure_reasons.get('order_failure', 0) + 1
    
    for reason, count in failure_reasons.items():
        if reason == 'insufficient_funds':
            print(f'{count}x: Insufficient funds for trade')
            print('   Likely issue: Capital allocation or position sizing')
            print('   Recommendation: Check available capital vs. trade size')
        elif reason == 'order_failure':
            print(f'{count}x: General order placement failure')
            print('   Likely issue: API connectivity or market conditions')

print()

# Calculate error rate
total_events = len(strategy_errors) + len(trade_failures) + len(successful_trades)
if total_events > 0:
    error_rate = (len(strategy_errors) + len(trade_failures)) / total_events * 100
    print(f'=== ERROR RATE ANALYSIS ===')
    print(f'Total events analyzed: {total_events}')
    print(f'Error rate: {error_rate:.1f}%')
    
    if error_rate > 50:
        print('🚨 CRITICAL: Error rate exceeds 50% - Trading may be compromised')
    elif error_rate > 20:
        print('⚠️  WARNING: Error rate exceeds 20% - Needs investigation')
    else:
        print('✅ ACCEPTABLE: Error rate within normal range')

print()

# Check dashboard status
print('=== DASHBOARD STATUS ===')
try:
    import requests
    response = requests.get('http://localhost:61804/api/status/all', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f'Dashboard: ✅ Online (status: {data.get("status", "unknown")})')
        print(f'Active trades: {len(data.get("trades", []))}')
    else:
        print(f'Dashboard: ❌ HTTP {response.status_code}')
except Exception as e:
    print(f'Dashboard: ❌ Unreachable ({e})')

print()
print('=== RECOMMENDATIONS ===')
if len(strategy_errors) > 10:
    print('1. Investigate strategy implementation errors immediately')
    print('2. Consider pausing trading until errors are resolved')
elif len(trade_failures) > 3:
    print('1. Check capital allocation and position sizing')
    print('2. Verify API connectivity and market access')
else:
    print('1. Continue monitoring with current configuration')
    print('2. Review error logs periodically for patterns')

print()
print('=== ANALYSIS COMPLETE ===')