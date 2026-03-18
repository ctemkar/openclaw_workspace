import requests
import json
import datetime
import os

TRADING_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERT_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
BASE_URL = 'http://localhost:56478'

def fetch_trading_data():
    print('Fetching trading data from dashboard...')
    endpoints = ['/api/trading/progress']
    
    all_data = {}
    for endpoint in endpoints:
        try:
            url = BASE_URL + endpoint
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            data = response.json()
            all_data[endpoint] = data
            print(f'Successfully fetched data from {endpoint}')
        except requests.exceptions.RequestException as e:
            print(f'Error fetching data from {endpoint}: {e}')
            all_data[endpoint] = None
        except json.JSONDecodeError:
            print(f'Response from {endpoint} is not JSON')
            all_data[endpoint] = {'error': 'Invalid JSON response'}
    
    return all_data

def ensure_log_directory_exists():
    log_dir = os.path.dirname(TRADING_LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f'Created directory: {log_dir}')

def log_data_to_file(file_path, content):
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(file_path, 'a') as f:
            f.write(f'[{timestamp}]\n')
            if isinstance(content, dict):
                json.dump(content, f, indent=2)
                f.write('\n')
            else:
                f.write(str(content) + '\n')
            f.write('---\n')
        print(f'Logged data to {file_path}')
    except Exception as e:
        print(f'Error writing to log file {file_path}: {e}')

def analyze_trading_data(data):
    summary_parts = []
    alerts = []

    if not data:
        summary_parts.append('Failed to fetch trading data.')
        return '\n'.join(summary_parts), alerts

    current_timestamp = datetime.datetime.now().isoformat()
    summary_parts.append(f'--- Trading Dashboard Analysis - {current_timestamp} ---')

    # Analyze trading progress data
    progress_data = data.get('/api/trading/progress')
    if progress_data:
        summary_parts.append(f'Trading Status: {progress_data.get("status", "N/A")}')
        
        trades = progress_data.get('trades', [])
        summary_parts.append(f'Active Trades: {len(trades)}')
        
        if trades:
            total_investment = 0.0
            filled_trades = 0
            buy_trades = 0
            sell_trades = 0
            
            for trade in trades:
                amount = trade.get('amount', 0)
                price = trade.get('price', 0)
                investment = amount * price if amount and price else 0
                total_investment += investment
                
                if trade.get('status') == 'filled':
                    filled_trades += 1
                
                if trade.get('side') == 'buy':
                    buy_trades += 1
                elif trade.get('side') == 'sell':
                    sell_trades += 1
                
                # Check for potential issues
                if trade.get('status') not in ['filled', 'pending']:
                    alert_msg = f'Unusual trade status: {trade.get("status")} for trade at {trade.get("time", "unknown time")}'
                    alerts.append(alert_msg)
                    log_data_to_file(CRITICAL_ALERT_FILE, alert_msg)
            
            summary_parts.append(f'Total Investment: ${total_investment:.2f}')
            summary_parts.append(f'Filled Trades: {filled_trades}/{len(trades)}')
            summary_parts.append(f'Buy Orders: {buy_trades}, Sell Orders: {sell_trades}')
            
            # Log detailed trade data
            log_data_to_file(TRADING_LOG_FILE, {
                'trading_progress': progress_data,
                'summary': {
                    'total_trades': len(trades),
                    'filled_trades': filled_trades,
                    'total_investment': total_investment,
                    'buy_orders': buy_trades,
                    'sell_orders': sell_trades
                }
            })
        else:
            summary_parts.append('No active trades found.')
            log_data_to_file(TRADING_LOG_FILE, {'trading_progress': progress_data, 'note': 'No active trades'})
    else:
        summary_parts.append('No trading progress data available.')
    
    # Check for critical conditions
    trades = progress_data.get('trades', []) if progress_data else []
    if len(trades) > 10:  # Arbitrary threshold for too many trades
        alert_msg = f'High number of active trades: {len(trades)}'
        alerts.append(alert_msg)
        log_data_to_file(CRITICAL_ALERT_FILE, alert_msg)
    
    if not alerts:
        summary_parts.append('No critical alerts triggered at this time.')
    else:
        summary_parts.append(f'Critical Alerts: {len(alerts)} detected')

    return '\n'.join(summary_parts), alerts

# Main execution
if __name__ == '__main__':
    ensure_log_directory_exists()
    trading_data = fetch_trading_data()
    summary, alerts = analyze_trading_data(trading_data)
    
    print(summary)
    print()
    print('--- Log Files Updated ---')
    print(f'Trading log: {TRADING_LOG_FILE}')
    print(f'Critical alerts: {CRITICAL_ALERT_FILE}')