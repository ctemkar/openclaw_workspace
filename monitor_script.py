import requests, time, os

URL = 'http://localhost:5001/'
LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
ALERT_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)

def monitor():
    print('Starting monitoring...')
    while True:
        try:
            response = requests.get(URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f'{timestamp} - Data: {data}'
            print(f'Logging to {LOG_FILE}')
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry + '\n')

            stop_loss_triggered = data.get('stop_loss_triggered', False)
            take_profit_triggered = data.get('take_profit_triggered', False)
            critical_drawdown = data.get('critical_drawdown', False)

            alerts = []
            if stop_loss_triggered:
                alerts.append('STOP-LOSS TRIGGERED')
            if take_profit_triggered:
                alerts.append('TAKE-PROFIT TRIGGERED')
            if critical_drawdown:
                alerts.append('CRITICAL DRAWDOWN DETECTED')

            if alerts:
                alert_log_entry = f'{timestamp} - {" | ".join(alerts)}'
                print(f'Logging critical alert to {ALERT_FILE}')
                with open(ALERT_FILE, 'a') as f:
                    f.write(alert_log_entry + '\n')
                print(f'Summary: {" | ".join(alerts)}')
            else:
                print('No critical alerts at this time.')

        except requests.exceptions.RequestException as e:
            print(f'Error fetching data from {URL}: {e}')
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
        
        time.sleep(300) # Check every 5 minutes

if __name__ == '__main__':
    monitor()
