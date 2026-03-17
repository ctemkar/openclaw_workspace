import requests
import json
from datetime import datetime

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERTS_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
DATA_URL = 'http://localhost:5001/'

def log_message(message, log_file=LOG_FILE):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\\n")

def fetch_and_parse_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        log_message("Successfully fetched data.")
        return data
    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching data from {DATA_URL}: {e}")
        return None
    except json.JSONDecodeError:
        log_message(f"Error decoding JSON response from {DATA_URL}")
        return None

def analyze_data(data):
    if not data:
        return

    # Log all extracted data
    log_message(f"Trading Logs: {data.get('trading_logs', 'N/A')}")
    log_message(f"Status Updates: {data.get('status_updates', 'N/A')}")
    log_message(f"Capital: {data.get('risk_parameters', {}).get('capital', 'N/A')}")
    log_message(f"Stop Loss: {data.get('risk_parameters', {}).get('stop_loss', 'N/A')}")
    log_message(f"Take Profit: {data.get('risk_parameters', {}).get('take_profit', 'N/A')}")
    log_message(f"Drawdown Indicators: {data.get('risk_parameters', {}).get('drawdown_indicators', 'N/A')}")

    critical_alerts = []
    risk_parameters = data.get('risk_parameters', {})

    # Check for triggered stop-loss or take-profit
    if risk_parameters.get('stop_loss_triggered'):
        alert_msg = "CRITICAL ALERT: Stop-loss triggered!"
        critical_alerts.append(alert_msg)
        log_message(alert_msg, CRITICAL_ALERTS_FILE)

    if risk_parameters.get('take_profit_triggered'):
        alert_msg = "CRITICAL ALERT: Take-profit triggered!"
        critical_alerts.append(alert_msg)
        log_message(alert_msg, CRITICAL_ALERTS_FILE)

    # Check for critical drawdown indicators
    drawdown = risk_parameters.get('drawdown_indicators')
    if drawdown and drawdown.get('critical'): # Assuming 'critical' is a boolean or a threshold check
        alert_msg = f"CRITICAL ALERT: Drawdown indicators are critical: {drawdown.get('value', 'N/A')}"
        critical_alerts.append(alert_msg)
        log_message(alert_msg, CRITICAL_ALERTS_FILE)

    if critical_alerts:
        log_message("Critical alerts detected and logged.")
    else:
        log_message("No critical alerts detected.")

if __name__ == "__main__":
    log_message("Starting trading monitoring task.")
    trading_data = fetch_and_parse_data()
    analyze_data(trading_data)
    log_message("Trading monitoring task finished.")
