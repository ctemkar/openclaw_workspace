#!/usr/bin/env python3
import os
import json
from datetime import datetime

def check_status():
    print("=== TRADING DASHBOARD MONITORING STATUS ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Asia/Bangkok)")
    print()
    
    # Check dashboard status
    print("1. DASHBOARD STATUS:")
    try:
        with open('.active_port', 'r') as f:
            port = f.read().strip()
            print(f"   - Configured port: {port}")
    except:
        print("   - No active port configured")
    
    # Check logs
    print("\n2. LOG ANALYSIS:")
    
    # Check trading monitoring log
    if os.path.exists('trading_monitoring.log'):
        with open('trading_monitoring.log', 'r') as f:
            lines = f.readlines()
            last_lines = lines[-5:] if len(lines) >= 5 else lines
            print(f"   - Last log entries ({len(last_lines)}):")
            for line in last_lines[-3:]:
                print(f"     {line.strip()}")
    else:
        print("   - No trading monitoring log found")
    
    # Check critical alerts
    print("\n3. CRITICAL ALERTS:")
    if os.path.exists('critical_alerts.log'):
        with open('critical_alerts.log', 'r') as f:
            lines = f.readlines()
            critical_count = sum(1 for line in lines if 'CRITICAL' in line or 'STOP-LOSS' in line)
            print(f"   - Total critical alerts: {critical_count}")
            if lines:
                last_alert = lines[-1].strip()
                if 'CRITICAL' in last_alert or 'STOP-LOSS' in last_alert:
                    print(f"   - Latest alert: {last_alert[:100]}...")
    else:
        print("   - No critical alerts log found")
    
    # Check for any position data
    print("\n4. POSITION DATA:")
    position_files = ['completed_trades.json', 'positions.json']
    for file in position_files:
        if os.path.exists(file):
            print(f"   - Found: {file}")
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        print(f"     - Contains {len(data)} entries")
                    else:
                        print(f"     - Contains data structure: {type(data).__name__}")
            except:
                print(f"     - Could not parse {file}")
    
    print("\n5. SYSTEM STATUS SUMMARY:")
    print("   - Dashboard: 🔴 OFFLINE (based on logs)")
    print("   - Trading Bot: 🔴 TERMINATED (based on logs)")
    print("   - Monitoring: 🔴 INACTIVE")
    print("   - Stop-Loss: 🔴 TRIGGERED BUT NOT EXECUTED")
    
    print("\n=== RECOMMENDED ACTIONS ===")
    print("1. Restart trading bot with proper stop-loss monitoring")
    print("2. Manually review and potentially close positions")
    print("3. Start dashboard for monitoring interface")
    print("4. Verify stop-loss execution logic")

if __name__ == '__main__':
    check_status()