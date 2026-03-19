import requests
import logging
import time
import json
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration
MONITOR_URL = "http://localhost:5001/"
TRADING_LOG_FILE = os.path.join(os.environ.get('WORKSPACE_DIR', '/Users/chetantemkar/.openclaw/workspace/app'), "trading_monitoring.log")
ALERT_LOG_FILE = os.path.join(os.environ.get('WORKSPACE_DIR', '/Users/chetantemkar/.openclaw/workspace/app'), "critical_alerts.log")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Setup logging for trading data
trading_logger = logging.getLogger('trading_data')
trading_logger.setLevel(logging.INFO)
trading_handler = logging.FileHandler(TRADING_LOG_FILE)
trading_handler.setFormatter(logging.Formatter(LOG_FORMAT))
trading_logger.addHandler(trading_handler)

# Setup logging for critical alerts
alert_logger = logging.getLogger('critical_alerts')
alert_logger.setLevel(logging.CRITICAL)
alert_handler = logging.FileHandler(ALERT_LOG_FILE)
alert_handler.setFormatter(logging.Formatter(LOG_FORMAT))
alert_logger.addHandler(alert_handler)

def fetch_and_process_data():
    try:
        # Use a timeout for the request
        response = requests.get(MONITOR_URL, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            error_message = f"Error decoding JSON response from {MONITOR_URL}"
            alert_logger.critical(f"{datetime.now().isoformat()} - JSON_DECODE_ERROR - {error_message}")
            return f"Error: Invalid JSON received from trading dashboard. Details logged."

        # Extract and log trading data
        trading_data = {
            "timestamp": datetime.now().isoformat(),
            "logs": data.get("logs", []),
            "status_updates": data.get("status_updates", []),
            "risk_parameters": data.get("risk_parameters", {})
        }
        trading_logger.info(json.dumps(trading_data))

        # Detect and log critical alerts
        critical_alerts = []
        stop_loss_triggered = data.get("stop_loss_triggered", False)
        take_profit_triggered = data.get("take_profit_triggered", False)
        critical_drawdown = data.get("critical_drawdown", False)

        if stop_loss_triggered:
            critical_alerts.append("STOP_LOSS_TRIGGERED")
        if take_profit_triggered:
            critical_alerts.append("TAKE_PROFIT_TRIGGERED")
        if critical_drawdown:
            critical_alerts.append("CRITICAL_DRAWDOWN")

        if critical_alerts:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "alerts": critical_alerts,
                "details": data # Include original data for context
            }
            alert_logger.critical(json.dumps(alert_data))

        # Generate summary
        summary = f"Trading Dashboard Monitor Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
        summary += f"Status: {'OK' if not critical_alerts else 'CRITICAL'}\\n"
        if critical_alerts:
            summary += f"Critical Alerts: {', '.join(critical_alerts)}\\n"
        summary += f"Logs written to: {TRADING_LOG_FILE}\\n"
        summary += f"Alerts logged to: {ALERT_LOG_FILE}\\n"
        # Add more summary details as needed from parsed data
        # For example, if status_updates is available:
        if trading_data["status_updates"]:
            summary += f"Latest Status Update: {trading_data['status_updates'][-1]}\\n"
        if trading_data["risk_parameters"]:
            summary += f"Current Risk Parameters: {trading_data['risk_parameters']}\\n"


        return summary

    except requests.exceptions.ConnectionError:
        error_message = f"Connection error: Could not connect to {MONITOR_URL}."
        alert_logger.critical(f"{datetime.now().isoformat()} - CONNECTION_ERROR - {error_message}")
        return f"Error: Could not connect to trading dashboard at {MONITOR_URL}. Details logged."
    except requests.exceptions.Timeout:
        error_message = f"Request timed out for {MONITOR_URL}."
        alert_logger.critical(f"{datetime.now().isoformat()} - TIMEOUT_ERROR - {error_message}")
        return f"Error: Request to trading dashboard timed out. Details logged."
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {MONITOR_URL}: {e}"
        alert_logger.critical(f"{datetime.now().isoformat()} - REQUEST_ERROR - {error_message}")
        return f"Error: An issue occurred while fetching data from the trading dashboard ({type(e).__name__}). Details logged."
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        alert_logger.critical(f"{datetime.now().isoformat()} - UNEXPECTED_ERROR - {error_message}")
        return f"An unexpected error occurred. Details logged."

# Main loop for continuous monitoring
if __name__ == "__main__":
    # Print initial summary on script start
    initial_summary = fetch_and_process_data()
    print(initial_summary)

    # Continue monitoring
    while True:
        time.sleep(30) # Wait for 30 seconds before the next check
        summary = fetch_and_process_data()
        # Only print summary if it's an error message, otherwise logs are handled by the logger
        if summary.startswith("Error:") or summary.startswith("An unexpected error occurred"):
            print(summary)

