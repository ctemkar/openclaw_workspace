
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

TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
SOURCE_URL = f"http://localhost:{PORT}/"

def fetch_and_analyze_trading_data():
    try:
        response = requests.get(SOURCE_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        log_data(data)
        analyze_and_alert(data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {SOURCE_URL}: {e}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {SOURCE_URL}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def log_data(data):
    timestamp = datetime.now().isoformat()
    with open(TRADING_LOG_FILE, "a") as f:
        f.write(f"--- {timestamp} ---\n")
        json.dump(data, f, indent=2)
        f.write("\n")

def analyze_and_alert(data):
    # Placeholder for actual analysis logic
    # This is where you would parse trading logs, status updates,
    # risk parameters, and implement alerting for stop-loss/take-profit triggers
    # and critical drawdown indicators.

    stop_loss_triggered = data.get("stop_loss_triggered", False)
    take_profit_triggered = data.get("take_profit_triggered", False)
    critical_drawdown = data.get("critical_drawdown", False)
    capital = data.get("capital", None)
    stop_loss = data.get("stop_loss", None)
    take_profit = data.get("take_profit", None)

    alerts = []
    if stop_loss_triggered:
        alerts.append(f"STOP-LOSS TRIGGERED at {datetime.now().isoformat()}")
    if take_profit_triggered:
        alerts.append(f"TAKE-PROFIT TRIGGERED at {datetime.now().isoformat()}")
    if critical_drawdown:
        alerts.append(f"CRITICAL DRAWDOWN DETECTED at {datetime.now().isoformat()}")

    if alerts:
        with open(CRITICAL_ALERT_FILE, "a") as f:
            for alert in alerts:
                f.write(f"{alert}\n")
        print(f"Critical alerts triggered: {', '.join(alerts)}")

    # Log risk parameters
    if capital is not None:
        print(f"Current Capital: {capital}")
    if stop_loss is not None:
        print(f"Stop Loss Level: {stop_loss}")
    if take_profit is not None:
        print(f"Take Profit Level: {take_profit}")

if __name__ == "__main__":
    fetch_and_analyze_trading_data()
