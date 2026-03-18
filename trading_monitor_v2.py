import requests
import json
import datetime
import os
import sys

TRADING_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERT_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
BASE_URL = 'http://localhost:56478'

def fetch_all_trading_data():
    print('Fetching comprehensive trading data from dashboard...')
    endpoints = [
        '/api/trading/progress',
        '/api/status'
    ]
    
    all_data = {}
    for endpoint in endpoints:
        try:
            url = BASE_URL + endpoint
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            data = response.json()
            all_data[endpoint] = data
            print(f'✓ Successfully fetched data from {endpoint}')
        except requests.exceptions.RequestException as e:
            print(f'✗ Error fetching data from {endpoint}: {e}')
            all_data[endpoint] = None
        except json.JSONDecodeError:
            print(f'✗ Response from {endpoint} is not JSON')
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
        return True
    except Exception as e:
        print(f'Error writing to log file {file_path}: {e}')
        return False

def analyze_trading_data(data):
    summary_parts = []
    alerts = []

    if not data:
        summary_parts.append('Failed to fetch trading data.')
        return '\n'.join(summary_parts), alerts

    current_timestamp = datetime.datetime.now().isoformat()
    summary_parts.append(f'=== Trading Dashboard Analysis - {current_timestamp} ===')
    summary_parts.append('')

    # Analyze trading progress data
    progress_data = data.get('/api/trading/progress')
    status_data = data.get('/api/status')
    
    if progress_data:
        summary_parts.append('📊 TRADING PROGRESS')
        summary_parts.append('─' * 40)
        
        trading_status = progress_data.get('status', 'N/A')
        summary_parts.append(f'Status: {trading_status}')
        
        trades = progress_data.get('trades', [])
        summary_parts.append(f'Active Trades: {len(trades)}')
        
        if trades:
            total_investment = 0.0
            filled_trades = 0
            buy_trades = 0
            sell_trades = 0
            pending_trades = 0
            cancelled_trades = 0
            
            for trade in trades:
                amount = trade.get('amount', 0)
                price = trade.get('price', 0)
                investment = amount * price if amount and price else 0
                total_investment += investment
                
                trade_status = trade.get('status', 'unknown')
                if trade_status == 'filled':
                    filled_trades += 1
                elif trade_status == 'pending':
                    pending_trades += 1
                elif trade_status == 'cancelled':
                    cancelled_trades += 1
                
                if trade.get('side') == 'buy':
                    buy_trades += 1
                elif trade.get('side') == 'sell':
                    sell_trades += 1
                
                # Check for potential issues
                if trade_status not in ['filled', 'pending', 'cancelled']:
                    alert_msg = f'⚠️ Unusual trade status: {trade_status} for {trade.get("side", "unknown")} trade at {trade.get("time", "unknown time")}'
                    alerts.append(alert_msg)
            
            summary_parts.append(f'Total Investment: ${total_investment:.2f}')
            summary_parts.append(f'Filled: {filled_trades} | Pending: {pending_trades} | Cancelled: {cancelled_trades}')
            summary_parts.append(f'Buy Orders: {buy_trades} | Sell Orders: {sell_trades}')
            
            # Check for critical conditions
            if len(trades) > 15:  # High number of trades
                alert_msg = f'🚨 High number of active trades: {len(trades)}'
                alerts.append(alert_msg)
            
            if pending_trades > 5:  # Many pending trades
                alert_msg = f'⚠️ Many pending trades: {pending_trades}'
                alerts.append(alert_msg)
            
            if cancelled_trades > 3:  # Many cancelled trades
                alert_msg = f'⚠️ Multiple cancelled trades: {cancelled_trades}'
                alerts.append(alert_msg)
            
            # Log detailed trade data
            log_data_to_file(TRADING_LOG_FILE, {
                'trading_progress': progress_data,
                'summary': {
                    'total_trades': len(trades),
                    'filled_trades': filled_trades,
                    'pending_trades': pending_trades,
                    'cancelled_trades': cancelled_trades,
                    'total_investment': total_investment,
                    'buy_orders': buy_trades,
                    'sell_orders': sell_trades
                }
            })
        else:
            summary_parts.append('No active trades found.')
            log_data_to_file(TRADING_LOG_FILE, {'trading_progress': progress_data, 'note': 'No active trades'})
    else:
        summary_parts.append('✗ No trading progress data available.')
    
    summary_parts.append('')
    
    # Analyze system status
    if status_data:
        summary_parts.append('🖥️ SYSTEM STATUS')
        summary_parts.append('─' * 40)
        
        for key, value in status_data.items():
            if isinstance(value, dict):
                summary_parts.append(f'{key}:')
                for subkey, subvalue in value.items():
                    summary_parts.append(f'  {subkey}: {subvalue}')
            else:
                summary_parts.append(f'{key}: {value}')
        
        # Check for system issues
        if 'error' in str(status_data).lower():
            alert_msg = '⚠️ System error detected in status data'
            alerts.append(alert_msg)
        
        log_data_to_file(TRADING_LOG_FILE, {'system_status': status_data})
    else:
        summary_parts.append('✗ No system status data available.')
    
    summary_parts.append('')
    summary_parts.append('🔔 ALERT SUMMARY')
    summary_parts.append('─' * 40)
    
    if alerts:
        for i, alert in enumerate(alerts, 1):
            summary_parts.append(f'{i}. {alert}')
            # Log each alert to critical alerts file
            log_data_to_file(CRITICAL_ALERT_FILE, alert)
        summary_parts.append(f'\nTotal alerts: {len(alerts)}')
    else:
        summary_parts.append('✅ No critical alerts triggered at this time.')
    
    summary_parts.append('')
    summary_parts.append('📈 RECOMMENDATIONS')
    summary_parts.append('─' * 40)
    
    if progress_data and 'trades' in progress_data:
        trades = progress_data['trades']
        if len(trades) == 0:
            summary_parts.append('• No active trades - consider market analysis')
        elif len(trades) > 10:
            summary_parts.append('• High trade volume - consider risk management')
        else:
            summary_parts.append('• Trading activity within normal range')
    
    summary_parts.append('• Monitor system status regularly')
    summary_parts.append('• Review trade logs for patterns')
    
    return '\n'.join(summary_parts), alerts

def main():
    print('Starting trading dashboard monitoring...')
    print('=' * 60)
    
    ensure_log_directory_exists()
    
    try:
        trading_data = fetch_all_trading_data()
        summary, alerts = analyze_trading_data(trading_data)
        
        print(summary)
        print()
        print('=' * 60)
        print('📁 LOG FILES UPDATED')
        print(f'• Trading log: {TRADING_LOG_FILE}')
        print(f'• Critical alerts: {CRITICAL_ALERT_FILE}')
        
        # Return exit code based on alerts
        if alerts:
            print(f'\n⚠️  Monitoring completed with {len(alerts)} alert(s)')
            return 1
        else:
            print('\n✅ Monitoring completed successfully')
            return 0
            
    except Exception as e:
        print(f'\n❌ Monitoring failed with error: {e}')
        return 2

if __name__ == '__main__':
    sys.exit(main())