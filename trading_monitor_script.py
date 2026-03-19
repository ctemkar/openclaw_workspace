
# trading_monitor_script.py
import requests
import json
from datetime import datetime

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DASHBOARD_URL = "http://localhost:5001/"

def log_message(message, log_file):
    timestamp = datetime.now().isoformat()
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def fetch_dashboard_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching data from {url}: {e}", LOG_FILE)
        return None
    except json.JSONDecodeError:
        log_message(f"Error decoding JSON response from {url}", LOG_FILE)
        return None

def analyze_trading_data(data):
    critical_alerts = []
    if not data:
        return critical_alerts

    # --- Extracting and Logging General Data ---
    capital = data.get("capital")
    status_updates = data.get("status_updates", [])
    trading_logs = data.get("trading_logs", [])
    risk_parameters = data.get("risk_parameters", {})

    general_log_content = f"Capital: {capital}\nStatus Updates: {json.dumps(status_updates)}\nTrading Logs: {json.dumps(trading_logs)}\nRisk Parameters: {json.dumps(risk_parameters)}\n"
    log_message(general_log_content, LOG_FILE)

    # --- Analyzing for Alerts ---
    stop_loss_triggered = risk_parameters.get("stop_loss_triggered", False)
    take_profit_triggered = risk_parameters.get("take_profit_triggered", False)
    drawdown_critical = data.get("drawdown_indicators_critical", False) # Assuming this is a key in the data

    if stop_loss_triggered:
        critical_alerts.append("STOP-LOSS IMMEDIATELY TRIGGERED!")
    if take_profit_triggered:
        critical_alerts.append("TAKE-PROFIT IMMEDIATELY TRIGGERED!")
    if drawdown_critical:
        critical_alerts.append("CRITICAL DRAWDOWN INDICATORS DETECTED!")

    # Add more complex analysis here if needed, e.g., analyzing trading_logs for patterns

    return critical_alerts

def main():
    data = fetch_dashboard_data(DASHBOARD_URL)
    critical_alerts = analyze_trading_data(data)

    if critical_alerts:
        alert_message = "\n".join(critical_alerts)
        log_message(f"CRITICAL ALERTS: {alert_message}", ALERT_FILE)
        print(f"CRITICAL ALERTS DETECTED: {alert_message}") # For immediate feedback if run manually
    else:
        print("No critical alerts detected.")

if __name__ == "__main__":
    main()
