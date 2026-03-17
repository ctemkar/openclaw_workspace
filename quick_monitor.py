#!/usr/bin/env python3
import requests
import json
import datetime
import os
import sys

# Read the active port
try:
    with open('.active_port', 'r') as f:
        PORT = f.read().strip()
except:
    PORT = "61804"

base_url = f'http://localhost:{PORT}'

print('=== TRADING DATA MONITORING REPORT ===')
print(f'Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Dashboard Port: {PORT}')
print()

# Check dashboard status
try:
    status_response = requests.get(f'{base_url}/api/status/all', timeout=10)
    status_data = status_response.json()
    
    print(f'Dashboard Status: {status_data.get("status", "unknown")}')
    print(f'Number of Trades: {len(status_data.get("trades", []))}')
    
    if status_data.get("trades"):
        latest_trade = status_data["trades"][0]
        print(f'Latest Trade: {latest_trade.get("side", "unknown")} {latest_trade.get("amount", 0)} BTC @ ${latest_trade.get("price", 0):,.2f}')
        print(f'  Model: {latest_trade.get("model", "unknown")}')
        print(f'  Time: {latest_trade.get("time", "unknown")}')
    print()
    
    # Check if trading script is running
    if status_data.get("status") == "running":
        print('✅ Trading script is ACTIVE')
    else:
        print('⚠️  Trading script is NOT running')
    
except Exception as e:
    print(f'❌ Error fetching dashboard status: {e}')
    sys.exit(1)

# Check for any trading data files
print()
print('=== TRADING FILES CHECK ===')

trading_files = [
    "completed_trades.json",
    "trading_monitoring.log", 
    "critical_alerts.log",
    "dashboard_tasks.json",
    "llm_strategies.json"
]

for file in trading_files:
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                content = f.read()
                if file.endswith('.json'):
                    data = json.loads(content)
                    if file == "completed_trades.json":
                        print(f'✅ {file}: {len(data)} trades recorded')
                    elif file == "dashboard_tasks.json":
                        print(f'✅ {file}: {len(data.get("tasks", []))} tasks')
                    elif file == "llm_strategies.json":
                        print(f'✅ {file}: {len(data)} strategies')
                else:
                    lines = content.strip().split('\n')
                    print(f'✅ {file}: {len(lines)} lines')
        except Exception as e:
            print(f'⚠️  {file}: Error reading - {e}')
    else:
        print(f'❌ {file}: Not found')

# Check for recent critical alerts
print()
print('=== CRITICAL ALERTS CHECK ===')
if os.path.exists("critical_alerts.log"):
    try:
        with open("critical_alerts.log", 'r') as f:
            lines = f.readlines()
            recent_alerts = []
            for line in lines[-10:]:  # Check last 10 alerts
                try:
                    alert = json.loads(line.strip())
                    recent_alerts.append(alert)
                except:
                    continue
            
            if recent_alerts:
                print(f'⚠️  Found {len(recent_alerts)} recent critical alerts')
                for alert in recent_alerts[-3:]:  # Show last 3
                    timestamp = alert.get("timestamp", "unknown")
                    alerts_list = alert.get("alerts", [])
                    print(f'  {timestamp}: {len(alerts_list)} alerts')
            else:
                print('✅ No recent critical alerts found')
    except Exception as e:
        print(f'⚠️  Error reading critical alerts: {e}')
else:
    print('✅ No critical alerts log file (may be normal)')

print()
print('=== RECOMMENDATIONS ===')
if status_data.get("status") == "stopped":
    print('1. Consider starting the trading script if market conditions are favorable')
    print('2. Check trading parameters and strategy configuration')
else:
    print('1. Monitor trading performance and adjust strategies as needed')
    print('2. Review recent trades for profitability')

print()
print('=== MONITORING COMPLETE ===')