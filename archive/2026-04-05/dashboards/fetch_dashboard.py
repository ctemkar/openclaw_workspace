#!/usr/bin/env python3
import requests
import sys
import json
from datetime import datetime

try:
    response = requests.get('http://localhost:5001/', timeout=10)
    if response.status_code == 200:
        # Try to extract meaningful content
        content = response.text
        
        # Look for trading-related patterns
        import re
        
        # Common trading dashboard patterns
        patterns = {
            'logs': r'(?:log|Log|LOG).*?(?:\n|$)',
            'status': r'(?:status|Status|STATUS).*?(?:\n|$)',
            'risk': r'(?:risk|Risk|RISK|drawdown|Drawdown|DRAWDOWN|stop-loss|take-profit|StopLoss|TakeProfit).*?(?:\n|$)',
            'orders': r'(?:order|Order|ORDER|trigger|Trigger|TRIGGER).*?(?:\n|$)',
            'critical': r'(?:critical|Critical|CRITICAL|alert|Alert|ALERT|warning|Warning|WARNING).*?(?:\n|$)',
            'positions': r'(?:position|Position|POSITION|pnl|Pnl|PNL|profit|loss).*?(?:\n|$)'
        }
        
        extracted_data = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                extracted_data[key] = matches[:10]  # Limit to first 10 matches
        
        # Also look for JSON data
        json_pattern = r'\{.*\}'
        json_matches = re.findall(json_pattern, content, re.DOTALL)
        for json_str in json_matches[:3]:  # Check first 3 potential JSON objects
            try:
                json_data = json.loads(json_str)
                if 'trading' in str(json_data).lower() or 'risk' in str(json_data).lower():
                    extracted_data['json_data'] = json_data
                    break
            except:
                pass
        
        print(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'status_code': response.status_code,
            'content_length': len(content),
            'extracted_data': extracted_data,
            'sample_content': content[:1000] if len(content) > 1000 else content
        }, indent=2))
    else:
        print(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'status_code': response.status_code,
            'error': f'HTTP {response.status_code}'
        }, indent=2))
except Exception as e:
    print(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'error': str(e)
    }, indent=2))
    sys.exit(1)