import requests
import json
from datetime import datetime

TRADING_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERT_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
URL = 'http://localhost:5001/'

def log_message(file_path, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(file_path, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Error writing to log file {file_path}: {e}") # Fallback to print

def monitor_trading_dashboard():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Log general trading data
        log_message(TRADING_LOG_FILE, f"Status: {data.get('status_updates', 'N/A')}")
        log_message(TRADING_LOG_FILE, f"Risk Parameters: {data.get('risk_parameters', 'N/A')}")
        for log_entry in data.get('trading_logs', []):
            log_message(TRADING_LOG_FILE, f"Log Entry: {log_entry}")

        # Detect and log critical alerts
        alerts = []
        if data.get('stop_loss_triggered'):
            alert_msg = "CRITICAL ALERT: Stop-loss triggered!"
            log_message(CRITICAL_ALERT_LOG_FILE, alert_msg)
            alerts.append(alert_msg)

        if data.get('take_profit_triggered'):
            alert_msg = "CRITICAL ALERT: Take-profit triggered!"
            log_message(CRITICAL_ALERT_LOG_FILE, alert_msg)
            alerts.append(alert_msg)

        if data.get('critical_drawdown'):
            alert_msg = f"CRITICAL ALERT: Critical drawdown detected: {data.get('critical_drawdown')}"
            log_message(CRITICAL_ALERT_LOG_FILE, alert_msg)
            alerts.append(alert_msg)

        # Generate summary
        summary = f"Trading Dashboard Analysis ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
        summary += f"---------------------------------------------------\n"
        summary += f"Status: {data.get('status_updates', 'N/A')}\n"
        summary += f"Risk Parameters: {data.get('risk_parameters', 'N/A')}\n"
        if alerts:
            summary += f"\nCRITICAL ALERTS:\n"
            for alert in alerts:
                summary += f"- {alert}\n"
        else:
            summary += "\nNo critical alerts detected.\n"

        return summary

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {URL}: {e}"
        log_message(TRADING_LOG_FILE, error_message)
        log_message(CRITICAL_ALERT_LOG_FILE, error_message)
        return f"Error: Could not connect to trading dashboard at {URL}. Details logged."
    except json.JSONDecodeError:
        error_message = f"Error decoding JSON response from {URL}"
        log_message(TRADING_LOG_FILE, error_message)
        log_message(CRITICAL_ALERT_LOG_FILE, error_message)
        return f"Error: Invalid JSON received from trading dashboard. Details logged."
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        log_message(TRADING_LOG_FILE, error_message)
        log_message(CRITICAL_ALERT_LOG_FILE, error_message)
        return f"An unexpected error occurred. Details logged."

if __name__ == "__main__":
    summary_text = monitor_trading_dashboard()
    print(summary_text)
