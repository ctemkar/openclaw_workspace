
import requests
import json
import logging
from datetime import datetime

# Configuration
MONITOR_URL = "http://localhost:5001/"
GENERAL_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Placeholder for critical drawdown threshold. Please specify a value.
CRITICAL_DRAWDOWN_THRESHOLD = 0.05  # 5% drawdown

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_file_logger(filename, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    logger = logging.getLogger(filename)
    logger.setLevel(level)
    # Prevent adding multiple handlers if this function is called multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
    return logger

general_logger = setup_file_logger(GENERAL_LOG_FILE)
critical_logger = setup_file_logger(CRITICAL_ALERTS_LOG_FILE, level=logging.ERROR)

def fetch_trading_data():
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        # Assuming the response is JSON. Adjust if it's a different format.
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch data from {MONITOR_URL}: {e}"
        general_logger.error(error_message)
        critical_logger.error(error_message) # Log request errors as critical
        return None
    except json.JSONDecodeError as e:
        error_message = f"Failed to decode JSON response from {MONITOR_URL}: {e}"
        general_logger.error(error_message)
        critical_logger.error(error_message) # Log JSON decode errors as critical
        return None

def analyze_data(data):
    summary_lines = []
    alerts = []
    current_time = datetime.utcnow().isoformat() + "Z"

    if data is None:
        summary_lines.append(f"[{current_time}] Trading data could not be fetched.")
        return "\n".join(summary_lines), alerts

    # Log general data
    general_logger.info(f"Received data: {data}")
    summary_lines.append(f"[{current_time}] Data received successfully.")

    # Placeholder for analyzing various parameters
    # This part needs to be more specific based on the actual data structure
    # Example: checking for status updates, risk parameters
    status = data.get("status", "N/A")
    risk_params = data.get("risk_parameters", {{}})
    summary_lines.append(f"Status: {status}")
    summary_lines.append(f"Risk Parameters: {risk_params}")

    # Detect stop-loss/take-profit orders
    # This is a placeholder and assumes such orders are in a list called "orders"
    orders = data.get("orders", [])
    for order in orders:
        if order.get("type") == "stop-loss" or order.get("type") == "take-profit":
            alert_message = f"Order detected: Type={order.get('type')}, Symbol={order.get('symbol')}, Price={order.get('price')}"
            alerts.append(alert_message)
            critical_logger.error(alert_message)

    # Detect critical drawdown
    # This is a placeholder. Replace with actual drawdown calculation and threshold check.
    current_drawdown = data.get("current_drawdown", 0)
    if current_drawdown > CRITICAL_DRAWDOWN_THRESHOLD:
        alert_message = f"Critical drawdown detected: {current_drawdown * 100:.2f}% (Threshold: {CRITICAL_DRAWDOWN_THRESHOLD * 100:.2f}%)"
        alerts.append(alert_message)
        critical_logger.error(alert_message)

    if not alerts:
        summary_lines.append("No critical alerts detected.")

    return "\n".join(summary_lines), alerts

def main():
    data = fetch_trading_data()
    summary, alerts = analyze_data(data)

    # The summary is what needs to be returned as plain text.
    # If the cron job is configured to capture stdout, this will be the output.
    print(summary)

if __name__ == "__main__":
    main()
