import requests
import json
import logging
import os
from datetime import datetime

# Read current port from .active_port file
try:
    with open(".active_port", "r") as f:
        PORT = f.read().strip()
except:
    PORT = "5001"  # Fallback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TRADING_LOG_PATH = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERTS_LOG_PATH = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
API_URL = f'http://localhost:{PORT}/'

def log_to_file(log_path, message):
    with open(log_path, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")

def fetch_trading_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        log_to_file(TRADING_LOG_PATH, f"Error fetching data from {url}: {e}")
        return None
    except json.JSONDecodeError:
        log_to_file(TRADING_LOG_PATH, f"Error decoding JSON response from {url}")
        return None

def parse_and_monitor(data):
    if not data:
        return "No data received."

    try:
        # Assume data is a dictionary with keys like 'logs', 'status', 'risk_parameters'
        # and 'risk_parameters' contains 'capital', 'stop_loss', 'take_profit'

        # Log all extracted data
        log_message = f"Data received: {json.dumps(data, indent=2)}"
        log_to_file(TRADING_LOG_PATH, log_message)

        # Initialize alert flags
        stop_loss_triggered = False
        take_profit_triggered = False
        critical_drawdown = False
        alert_messages = []

        # Check for triggered stop-loss or take-profit
        if 'trades' in data: # Assuming 'trades' contains a list of active or recently closed trades
            for trade in data['trades']:
                if trade.get('status') == 'stop_loss_triggered':
                    stop_loss_triggered = True
                    alert_messages.append(f"Stop-loss triggered for trade ID: {trade.get('id')}")
                if trade.get('status') == 'take_profit_triggered':
                    take_profit_triggered = True
                    alert_messages.append(f"Take-profit triggered for trade ID: {trade.get('id')}")

        # Check for drawdown indicators
        if 'performance' in data and 'drawdown_percentage' in data['performance']:
            drawdown = data['performance']['drawdown_percentage']
            if drawdown > 10: # Example threshold for critical drawdown
                critical_drawdown = True
                alert_messages.append(f"Critical drawdown detected: {drawdown}%")

        # If any alerts are triggered, log to critical alerts file
        if alert_messages:
            critical_alert_message = "\n".join(alert_messages)
            log_to_file(CRITICAL_ALERTS_LOG_PATH, critical_alert_message)
            return f"Critical alerts triggered: {critical_alert_message}"
        else:
            return "Monitoring healthy. No critical alerts triggered."

    except Exception as e:
        log_to_file(TRADING_LOG_PATH, f"Error parsing or monitoring data: {e}")
        return "Error during data monitoring."

if __name__ == "__main__":
    trading_data = fetch_trading_data(API_URL)
    result_summary = parse_and_monitor(trading_data)
    print(result_summary) # This will be captured by the agentTurn
