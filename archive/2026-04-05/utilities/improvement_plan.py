#!/usr/bin/env python3
"""
IMPROVEMENT PLAN - Fix identified issues
"""

import subprocess
import time
import os

print('🚀 TRADING SYSTEM IMPROVEMENT PLAN')
print('=' * 70)
print()

# 1. FIX MAIN DASHBOARD (PORT 5007)
print('1. 🔧 FIXING MAIN DASHBOARD (PORT 5007):')
print('   • Killing existing dashboard_common.py process...')
subprocess.run(['pkill', '-f', 'dashboard_common.py'], capture_output=True)

print('   • Checking for port conflicts...')
result = subprocess.run(['lsof', '-i', ':5007'], capture_output=True, text=True)
if 'LISTEN' in result.stdout:
    print('   ⚠️ Port 5007 still in use, killing all...')
    subprocess.run(['kill', '-9', '$(lsof -t -i:5007)'], shell=True, capture_output=True)

print('   • Restarting dashboard with debug...')
# Start dashboard with output to see errors
dashboard_proc = subprocess.Popen(
    ['python3', 'dashboard_common.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(3)

# Check if it started
result = subprocess.run(['pgrep', '-f', 'dashboard_common.py'], capture_output=True, text=True)
if result.returncode == 0:
    print('   ✅ Dashboard process started')
    
    # Check if port is listening
    result = subprocess.run(['lsof', '-i', ':5007'], capture_output=True, text=True)
    if 'LISTEN' in result.stdout:
        print('   ✅ Port 5007 is listening')
    else:
        print('   ❌ Port 5007 not listening')
else:
    print('   ❌ Dashboard failed to start')

print()

# 2. CONSOLIDATE DASHBOARDS
print('2. 📊 CONSOLIDATING DASHBOARDS:')
print('   • Current dashboards:')
dashboards = [
    ('bulletproof_dashboard.py', 'Port 5002', 'Backup'),
    ('simple_dashboard_fixed.py', 'Port 5003', 'Alternative'),
    ('simple_pnl_dashboard.py', 'Port 5008', 'P&L focused'),
    ('updated_trading_server.py', 'Port 5001', 'API server')
]

for proc_name, port, desc in dashboards:
    result = subprocess.run(['pgrep', '-f', proc_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'   • {proc_name} ({port}): {desc} - RUNNING')
    else:
        print(f'   • {proc_name} ({port}): {desc} - STOPPED')

print()
print('   💡 RECOMMENDATION: Keep only 2 dashboards:')
print('     1. Main dashboard (5007) - Full features with P&L at top')
print('     2. Trading server (5001) - API for bots and data')
print('   • Others can be stopped to save resources')

print()

# 3. IMPROVE POSITION DIVERSITY
print('3. 📈 IMPROVING POSITION DIVERSITY:')
print('   • Current: 5 positions, all SOL/USD on Gemini')
print('   • Issue: All eggs in one basket')
print()
print('   💡 IMPROVEMENT STRATEGIES:')
print('     A. Enable multi-symbol trading in bots')
print('     B. Add Binance SHORT positions when opportunities arise')
print('     C. Consider other top cryptocurrencies:')
print('        • BTC/USD - Market leader')
print('        • ETH/USD - Smart contracts')
print('        • XRP/USD, ADA/USD, DOT/USD - Already in 26-crypto list')
print('     D. Adjust position sizing for diversification')

print()

# 4. MONITOR BOT PERFORMANCE
print('4. 🤖 BOT PERFORMANCE MONITORING:')
try:
    import requests
    response = requests.get('http://localhost:5001/api/data', timeout=3)
    data = response.json()
    
    bot_status = data.get('bot_status', {})
    print(f'   • Status: {bot_status.get("status", "unknown")}')
    print(f'   • Last activity: {bot_status.get("last_activity", "None")}')
    print(f'   • Strategy: {bot_status.get("strategy", "Unknown")}')
    
    # Check for recent trades
    trades = data.get('recent_trades', [])
    today_trades = [t for t in trades if t.get('timestamp', '').startswith('2026-04-01')]
    print(f'   • Trades today: {len(today_trades)}')
    
    if len(today_trades) == 0:
        print('   ⚠️ No trades executed today - bots may be too conservative')
        print('   💡 Suggestion: Review 1.0% thresholds or market conditions')
        
except Exception as e:
    print(f'   ❌ Could not check bot performance: {e}')

print()

# 5. CREATE MONITORING SCRIPT
print('5. 📋 CREATING CONTINUOUS MONITORING:')
monitor_script = '''#!/usr/bin/env python3
"""
Continuous Trading System Monitor
Runs every 5 minutes to check system health
"""

import subprocess
import json
import time
from datetime import datetime
import requests

def check_dashboard(url, name):
    """Check if dashboard is responsive"""
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        elapsed = (time.time() - start) * 1000
        return True, elapsed, response.status_code
    except:
        return False, 0, 0

def check_bot_performance():
    """Check bot trading performance"""
    try:
        response = requests.get('http://localhost:5001/api/data', timeout=5)
        data = response.json()
        
        positions = len(data.get('positions', []))
        capital = data.get('capital', {})
        bot_status = data.get('bot_status', {})
        
        return {
            'positions': positions,
            'capital': capital.get('total_capital', 0),
            'bot_status': bot_status.get('status', 'unknown'),
            'last_activity': bot_status.get('last_activity', 'None')
        }
    except:
        return None

def log_status():
    """Log current status"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check dashboards
    dashboards = [
        ('Main', 'http://localhost:5007/'),
        ('Trading Server', 'http://localhost:5001/'),
        ('Simple P&L', 'http://localhost:5008/')
    ]
    
    status = {
        'timestamp': timestamp,
        'dashboards': {},
        'performance': {},
        'alerts': []
    }
    
    for name, url in dashboards:
        online, elapsed, code = check_dashboard(url, name)
        status['dashboards'][name] = {
            'online': online,
            'response_ms': elapsed,
            'status_code': code
        }
        if not online:
            status['alerts'].append(f'{name} dashboard offline')
    
    # Check bot performance
    perf = check_bot_performance()
    if perf:
        status['performance'] = perf
        if perf['positions'] == 0:
            status['alerts'].append('No open positions')
        if perf['bot_status'] == 'error':
            status['alerts'].append('Bot in error state')
    else:
        status['alerts'].append('Could not fetch bot performance')
    
    # Save to log file
    with open('system_monitor.log', 'a') as f:
        f.write(json.dumps(status) + '\\n')
    
    # Print summary
    print(f'[{timestamp}] System check:')
    print(f'  Dashboards: {sum(1 for d in status["dashboards"].values() if d["online"])}/{len(status["dashboards"])} online')
    if perf:
        print(f'  Positions: {perf["positions"]}, Capital: ${perf["capital"]:.2f}')
    if status['alerts']:
        print(f'  Alerts: {", ".join(status["alerts"])}')
    print()

if __name__ == '__main__':
    print('🔍 Starting continuous monitoring...')
    print('   • Checks every 5 minutes')
    print('   • Logs to system_monitor.log')
    print('   • Alerts for issues')
    print()
    
    while True:
        log_status()
        time.sleep(300)  # 5 minutes

'''

with open('continuous_monitor.py', 'w') as f:
    f.write(monitor_script)

print('   ✅ Created continuous_monitor.py')
print('   • Runs every 5 minutes')
print('   • Checks all dashboards and bot performance')
print('   • Logs to system_monitor.log')
print('   • Provides alerts for issues')

print()
print('=' * 70)
print('🎯 IMMEDIATE ACTIONS:')
print('1. Fix main dashboard on port 5007')
print('2. Stop duplicate dashboards (keep only 5001 and 5007)')
print('3. Review bot thresholds for better trade frequency')
print('4. Enable multi-symbol trading for diversification')
print('5. Start continuous monitoring')
print()
print('✅ IMPROVEMENT PLAN READY')