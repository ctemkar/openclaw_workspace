import requests
import json
import os
from datetime import datetime

TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DASHBOARD_URL = "http://localhost:5001/"
ALERT_THRESHOLD_DRAWDOWN = 0.10 # Example: 10% drawdown

def fetch_dashboard_data():
    try:
        response = requests.get(DASHBOARD_URL)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {DASHBOARD_URL}: {e}")
        return None

def parse_and_log_data(data):
    if not data:
        return

    log_entry = f"[{datetime.now().isoformat()}] "
    risk_params = data.get("risk_parameters", {})
    status_updates = data.get("status_updates", [])
    trading_logs = data.get("trading_logs", [])

    log_entry += f"Capital: {risk_params.get('capital', 'N/A')}, "
    log_entry += f"Stop Loss: {risk_params.get('stop_loss', 'N/A')}, "
    log_entry += f"Take Profit: {risk_params.get('take_profit', 'N/A')}\n"

    # Simple logging for now, could be more detailed
    for update in status_updates:
        log_entry += f"Status Update: {update}\n"
    for log in trading_logs:
        log_entry += f"Trading Log: {log}\n"

    with open(TRADING_LOG_PATH, "a") as f:
        f.write(log_entry)

def check_alerts(data):
    if not data:
        return False

    critical_alert_triggered = False
    alerts = []

    risk_params = data.get("risk_parameters", {})
    stop_loss = risk_params.get("stop_loss")
    take_profit = risk_params.get("take_profit")
    capital = risk_params.get("capital")

    # Check stop loss
    if capital is not None and stop_loss is not None and capital <= stop_loss:
        alerts.append(f"ALERT: Stop Loss triggered at {stop_loss} (Capital: {capital})")
        critical_alert_triggered = True

    # Check take profit
    if capital is not None and take_profit is not None and capital >= take_profit:
        alerts.append(f"ALERT: Take Profit triggered at {take_profit} (Capital: {capital})")
        critical_alert_triggered = True

    # Check drawdown indicators (example)
    # This would require more context, e.g., historical capital to calculate drawdown
    # For now, a placeholder: if capital drops below a certain percentage of initial capital
    # Assuming initial capital is stored somewhere or can be inferred.
    # For simplicity, let's imagine a 'current_drawdown' field in risk_parameters
    current_drawdown = risk_params.get("current_drawdown")
    if current_drawdown is not None and current_drawdown >= ALERT_THRESHOLD_DRAWDOWN:
        alerts.append(f"CRITICAL ALERT: Drawdown ({current_drawdown*100:.2f}%) exceeds threshold ({ALERT_THRESHOLD_DRAWDOWN*100:.2f}%)")
        critical_alert_triggered = True


    if alerts:
        alert_log_entry = f"[{datetime.now().isoformat()}] " + "\\n".join(alerts) + "\\n"
        with open(CRITICAL_ALERTS_PATH, "a") as f:
            f.write(alert_log_entry)
    
    return critical_alert_triggered

def main():
    data = fetch_dashboard_data()
    parse_and_log_data(data)
    critical_alert_triggered = check_alerts(data)

    if critical_alert_triggered:
        print("Critical alerts generated. Check critical_alerts.log.")
    else:
        print("Monitoring successful. No critical alerts.")

if __name__ == "__main__":
    main()
