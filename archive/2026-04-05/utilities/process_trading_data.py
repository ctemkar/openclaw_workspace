import requests
import json
import os

# Read current port from .active_port file
try:
    with open(".active_port", "r") as f:
        port = f.read().strip()
except:
    port = "5001"  # Fallback

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERTS_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
host = 'localhost'

try:
    response = requests.get(f'http://{host}:{port}')
    response.raise_for_status()
    data = response.json()

    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    trading_logs = data.get('trading_logs', [])
    status_updates = data.get('status_updates', [])
    risk_parameters = data.get('risk_parameters', {})

    capital = risk_parameters.get('capital')
    stop_loss_level = risk_parameters.get('stop_loss')
    take_profit_level = risk_parameters.get('take_profit')
    current_drawdown = risk_parameters.get('drawdown')

    critical_conditions = []

    if stop_loss_level is not None and capital is not None and capital <= stop_loss_level:
        critical_conditions.append({
            'indicator': 'stop_loss_triggered', 
            'details': f'Capital ({capital}) fell to or below stop loss level ({stop_loss_level}).'
        })
    if take_profit_level is not None and capital is not None and capital >= take_profit_level:
        critical_conditions.append({
            'indicator': 'take_profit_triggered', 
            'details': f'Capital ({capital}) reached or exceeded take profit level ({take_profit_level}).'
        })
    if current_drawdown is not None and current_drawdown >= 0.9: # Example: 90% drawdown is critical
        critical_conditions.append({
            'indicator': 'critical_drawdown', 
            'details': f'Critical drawdown ({current_drawdown*100}%) reached.'
        })

    if critical_conditions:
        with open(CRITICAL_ALERTS_FILE, 'w') as f:
            json.dump(critical_conditions, f, indent=4)
        print(f'Critical conditions detected and saved to {CRITICAL_ALERTS_FILE}')
    else:
        print('No critical conditions met.')

except requests.exceptions.RequestException as e:
    print(f'Error fetching data from API: {e}')
except json.JSONDecodeError:
    print('Error decoding JSON response from API. The response may not be valid JSON.')
except Exception as e:
    print(f'An unexpected error occurred: {e}')
