#!/usr/bin/env python3
import requests
import json
import datetime
import sys

def fetch_endpoint(endpoint):
    try:
        response = requests.get(f'http://localhost:5001{endpoint}', timeout=10)
        if response.status_code == 200:
            # Try to parse as JSON, fall back to text for HTML endpoints
            try:
                return response.json()
            except:
                return {'content': response.text[:500]}  # Limit text length
        else:
            return {'error': f'Status {response.status_code}', 'text': response.text[:200]}
    except Exception as e:
        return {'error': str(e)}

def log_to_file(filename, data):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a') as f:
        f.write(f'[{timestamp}] {json.dumps(data, indent=2)}\n')

def check_critical_alerts(data):
    alerts = []
    
    # Check for error status
    if 'status' in data and data['status'] == 'error':
        alerts.append(f'System error: {data.get("message", "Unknown error")}')
    
    # Check for high risk parameters
    if 'risk_parameters' in data:
        risk = data['risk_parameters']
        if risk.get('current_drawdown', 0) > 15:
            alerts.append(f'High drawdown: {risk["current_drawdown"]}%')
        if risk.get('max_position_size', 0) > 50:
            alerts.append(f'Large position size: ${risk["max_position_size"]}')
    
    # Check for failed trades
    if 'recent_trades' in data:
        failed_trades = [t for t in data['recent_trades'] if t.get('status') == 'failed']
        if failed_trades:
            alerts.append(f'{len(failed_trades)} failed trades detected')
    
    return alerts

def main():
    # Fetch all endpoints
    endpoints = ['/status', '/analysis', '/trades', '/strategy', '/summary']
    all_data = {}
    
    print(f"Trading Dashboard Monitor - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    for endpoint in endpoints:
        print(f'Fetching {endpoint}...')
        data = fetch_endpoint(endpoint)
        all_data[endpoint] = data
        
        # Log to monitoring log
        log_to_file('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 
                    {'endpoint': endpoint, 'data': data})
        
        # Check for critical alerts
        alerts = check_critical_alerts(data)
        if alerts:
            for alert in alerts:
                alert_data = {
                    'endpoint': endpoint,
                    'alert': alert,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                log_to_file('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', alert_data)
                print(f'  ⚠️  ALERT: {alert}')
    
    print("\nMonitoring complete")
    print(f"Logs written to:")
    print(f"  - trading_monitoring.log")
    print(f"  - critical_alerts.log (if any alerts)")

if __name__ == '__main__':
    main()