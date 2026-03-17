import os
import requests
import logging
from datetime import datetime

# Read current port from .active_port file
try:
    with open(".active_port", "r") as f:
        PORT = f.read().strip()
except:
    PORT = "5001"  # Fallback

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = f"http://localhost:{PORT}/"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

critical_alert_logger = logging.getLogger('critical_alert_logger')
critical_alert_logger.setLevel(logging.CRITICAL)
critical_alert_handler = logging.FileHandler(CRITICAL_ALERT_LOG_FILE)
critical_alert_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_alert_logger.addHandler(critical_alert_handler)

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return None

def analyze_data(data):
    if not data:
        return "No data available for analysis."

    analysis_summary = f"Trading Dashboard Analysis - {datetime.now().isoformat()}\n"
    all_logs = []
    critical_alerts = []

    # Extract trading logs
    if "logs" in data:
        for log in data["logs"]:
            all_logs.append(f"Log: {log}")
        analysis_summary += f"\nExtracted {len(data['logs'])} trading logs.\n"
    else:
        analysis_summary += "\nNo trading logs found.\n"

    # Extract status updates
    if "status" in data:
        all_logs.append(f"Status: {data['status']}" )
        analysis_summary += f"Status Update: {data['status']}\n"
    else:
        analysis_summary += "No status update found.\n"

    # Extract risk parameters
    risk_params = {}
    if "risk_parameters" in data:
        risk_params = data["risk_parameters"]
        analysis_summary += f"Risk Parameters: {risk_params}\n"
    else:
        analysis_summary += "No risk parameters found.\n"

    # Generate alerts
    stop_loss_triggered = risk_params.get("stop_loss_triggered", False)
    take_profit_triggered = risk_params.get("take_profit_triggered", False)
    drawdown_critical = risk_params.get("drawdown_critical", False)

    if stop_loss_triggered:
        alert_msg = "CRITICAL ALERT: Stop Loss triggered!"
        critical_alerts.append(alert_msg)
        critical_alert_logger.critical(alert_msg)
        analysis_summary += f"ALERT: {alert_msg}\n"
    if take_profit_triggered:
        alert_msg = "ALERT: Take Profit triggered."
        critical_alerts.append(alert_msg)
        analysis_summary += f"ALERT: {alert_msg}\n"
    if drawdown_critical:
        alert_msg = "CRITICAL ALERT: Drawdown indicator critical!"
        critical_alerts.append(alert_msg)
        critical_alert_logger.critical(alert_msg)
        analysis_summary += f"ALERT: {alert_msg}\n"

    # Log all extracted data
    for log_entry in all_logs:
        logging.info(log_entry)

    return analysis_summary

if __name__ == "__main__":
    trading_data = fetch_data(URL)
    summary = analyze_data(trading_data)
    print(summary) # This will be captured by the ACP session
