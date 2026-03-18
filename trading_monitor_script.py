import requests
import json
from datetime import datetime

TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/status"

def log_message(message, file_path):
    timestamp = datetime.now().isoformat()
    with open(file_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def fetch_and_parse_trading_data():
    try:
        response = requests.get(TRADING_DASHBOARD_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching data from {TRADING_DASHBOARD_URL}: {e}", TRADING_LOG_FILE)
        return None
    except json.JSONDecodeError:
        log_message(f"Error decoding JSON response from {TRADING_DASHBOARD_URL}", TRADING_LOG_FILE)
        return None

def analyze_data(data):
    if not data:
        return

    # Log extracted data
    log_message(f"Trading Data: {json.dumps(data)}", TRADING_LOG_FILE)

    # Placeholder for alert logic
    # In a real scenario, you'd parse specific fields from 'data'
    # For example: data['status_updates'], data['risk_parameters']['stop_loss_triggered'], data['drawdown_indicators']['critical']

    stop_loss_triggered = data.get('stop_loss_triggered', False) # Example field
    take_profit_triggered = data.get('take_profit_triggered', False) # Example field
    critical_drawdown = data.get('critical_drawdown', False) # Example field

    critical_events = []
    if stop_loss_triggered:
        critical_events.append("STOP LOSS TRIGGERED")
    if take_profit_triggered:
        critical_events.append("TAKE PROFIT TRIGGERED")
    if critical_drawdown:
        critical_events.append("CRITICAL DRAWDOWN INDICATORS")

    if critical_events:
        alert_message = " ".join(critical_events) + "!"
        log_message(alert_message, CRITICAL_ALERT_LOG_FILE)
        log_message(alert_message, TRADING_LOG_FILE) # Also log critical alerts to general log

# Main execution block
if __name__ == "__main__":
    trading_data = fetch_and_parse_trading_data()
    analyze_data(trading_data)
