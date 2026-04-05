#!/usr/bin/env python3
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
        f.write(json.dumps(status) + '\n')
    
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

