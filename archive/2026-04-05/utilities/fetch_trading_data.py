#!/usr/bin/env python3
import requests
import json
from datetime import datetime
import sys

def fetch_endpoint(endpoint):
    try:
        response = requests.get(f'http://localhost:5001{endpoint}', timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: HTTP {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_trading_data():
    endpoints = ['/status', '/trades', '/summary', '/analysis']
    
    results = {}
    for endpoint in endpoints:
        print(f"Fetching {endpoint}...", file=sys.stderr)
        content = fetch_endpoint(endpoint)
        results[endpoint] = content
    
    # Parse and extract critical information
    critical_alerts = []
    trading_logs = []
    risk_params = {}
    
    # Check status endpoint
    status_content = results.get('/status', '')
    if 'status' in status_content.lower():
        # Look for error/warning patterns
        import re
        error_patterns = [
            r'error.*?(?:\n|$)',
            r'warning.*?(?:\n|$)',
            r'critical.*?(?:\n|$)',
            r'stop.*loss.*triggered',
            r'take.*profit.*triggered',
            r'drawdown.*exceeded',
            r'risk.*limit.*exceeded'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, status_content, re.IGNORECASE)
            for match in matches:
                critical_alerts.append(f"Status endpoint: {match.strip()}")
    
    # Check trades endpoint
    trades_content = results.get('/trades', '')
    if 'trade' in trades_content.lower() or 'position' in trades_content.lower():
        # Extract recent trades
        import re
        trade_patterns = [
            r'trade.*?(?:\n|$)',
            r'position.*?(?:\n|$)',
            r'buy.*?(?:\n|$)',
            r'sell.*?(?:\n|$)',
            r'pnl.*?(?:\n|$)',
            r'profit.*?(?:\n|$)',
            r'loss.*?(?:\n|$)'
        ]
        
        for pattern in trade_patterns:
            matches = re.findall(pattern, trades_content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:  # Avoid very short matches
                    trading_logs.append(match.strip())
    
    # Extract risk parameters from main page
    main_content = results.get('/status', '')  # Using status as main content
    risk_patterns = {
        'stop_loss': r'stop.*loss.*?(\d+%)',
        'take_profit': r'take.*profit.*?(\d+%)',
        'capital': r'capital.*?(\$\d+)',
        'max_trades': r'max.*trades.*?(\d+)',
        'drawdown': r'drawdown.*?(\d+%)'
    }
    
    for param, pattern in risk_patterns.items():
        matches = re.findall(pattern, main_content, re.IGNORECASE)
        if matches:
            risk_params[param] = matches[0]
    
    return {
        'timestamp': datetime.now().isoformat(),
        'endpoints_fetched': list(results.keys()),
        'critical_alerts': critical_alerts,
        'trading_logs': trading_logs[:20],  # Limit to 20 most recent
        'risk_parameters': risk_params,
        'raw_data_preview': {k: v[:500] for k, v in results.items()}  # First 500 chars of each
    }

if __name__ == '__main__':
    try:
        analysis = analyze_trading_data()
        print(json.dumps(analysis, indent=2))
    except Exception as e:
        print(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, indent=2))