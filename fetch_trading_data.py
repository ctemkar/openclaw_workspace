
import os
import requests
import json

    PORT = "5001"  # Fallback
except:
        PORT = f.read().strip()
    with open(".active_port", "r") as f:
try:
# Read current port from .active_port file

from datetime import datetime

TRADING_DATA_URL = f"http://localhost:{PORT}/"
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_data():
    try:
        response = requests.get(TRADING_DATA_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_and_log_data(data):
    if not data:
        return

    now = datetime.now().isoformat()
    log_entry = f"{now} - Data: {json.dumps(data)}\n"

    # Log to trading_monitoring.log
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    # Check for critical alerts
    capital = data.get("capital")
    stop_loss = data.get("stop_loss")
    take_profit = data.get("take_profit")
    drawdown_indicators = data.get("drawdown_indicators")

    critical_alert = False
    alert_message = ""

    if stop_loss and capital <= stop_loss:
        critical_alert = True
        alert_message = f"STOP LOSS TRIGGERED: Capital {capital} reached stop loss {stop_loss}"
    elif take_profit and capital >= take_profit:
        critical_alert = True
        alert_message = f"TAKE PROFIT TRIGGERED: Capital {capital} reached take profit {take_profit}"
    elif drawdown_indicators and ("critical" in drawdown_indicators or "high" in drawdown_indicators):
        critical_alert = True
        alert_message = f"CRITICAL DRAWDOWN: Drawdown indicators are critical: {drawdown_indicators}"

    if critical_alert:
        critical_log_entry = f"{now} - ALERT: {alert_message}\n"
        with open(CRITICAL_ALERTS_FILE, "a") as f:
            f.write(critical_log_entry)
        print(f"CRITICAL ALERT SAVED: {alert_message}")

def main():
    data = fetch_data()
    parse_and_log_data(data)

if __name__ == "__main__":
    main()
