import requests
import json
from datetime import datetime

TRADING_LOG_FILE = "./trading_monitoring.log"
CRITICAL_ALERTS_FILE = "./critical_alerts.log"
URL = "http://localhost:5001/"

def fetch_trading_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None

def log_trading_data(data):
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - {json.dumps(data)}\n"
    with open(TRADING_LOG_FILE, "a") as f:
        f.write(log_entry)

def log_critical_alert(alert_type, details):
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - {alert_type.upper()}: {json.dumps(details)}\n"
    with open(CRITICAL_ALERTS_FILE, "a") as f:
        f.write(log_entry)

def generate_summary(data, critical_alerts):
    summary = f"Trading Dashboard Analysis - {datetime.now().isoformat()}\n"
    summary += "=========================================\n\n"

    if data:
        summary += "Current Trading Status:\n"
        summary += f"  - Status: {data.get('status', 'N/A')}\n"
        summary += f"  - Risk Parameters: {json.dumps(data.get('risk_parameters', {}))}\n"
        summary += f"  - Current Logs: {json.dumps(data.get('trading_logs', []))}\n\n"
    else:
        summary += "Could not fetch current trading data.\n\n"

    if critical_alerts:
        summary += "CRITICAL ALERTS DETECTED:\n"
        summary += "-------------------------\n"
        for alert in critical_alerts:
            summary += f"- {alert['type'].upper()}: {alert['details']}\n"
    else:
        summary += "No critical alerts detected.\n"

    return summary

def main():
    data = fetch_trading_data()
    critical_alerts = []

    if data:
        log_trading_data(data)

        # Detect critical alerts
        if data.get("stop_loss_triggered"):
            alert_details = {"details": "Stop-loss order was triggered."}
            log_critical_alert("stop-loss", alert_details)
            critical_alerts.append({"type": "stop-loss", "details": alert_details})

        if data.get("take_profit_triggered"):
            alert_details = {"details": "Take-profit order was triggered."}
            log_critical_alert("take-profit", alert_details)
            critical_alerts.append({"type": "take-profit", "details": alert_details})

        if data.get("critical_drawdown"):
            alert_details = {"details": "Critical drawdown event occurred."}
            log_critical_alert("critical-drawdown", alert_details)
            critical_alerts.append({"type": "critical-drawdown", "details": alert_details})

    summary = generate_summary(data, critical_alerts)
    print(summary) # This will be captured by the cron job's output

if __name__ == "__main__":
    main()
