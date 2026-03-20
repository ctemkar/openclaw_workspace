
import requests
import json
import os
from datetime import datetime

MONITOR_URL = "http://localhost:5001/"
TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_trading_data():
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {MONITOR_URL}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {MONITOR_URL}")
        return None

def log_data(data):
    if data:
        log_entry = f"[{datetime.now().isoformat()}] Data: {json.dumps(data)}\n"
        with open(TRADING_LOG_PATH, "a") as f:
            f.write(log_entry)

def log_alert(alert_message):
    log_entry = f"[{datetime.now().isoformat()}] ALERT: {alert_message}\n"
    with open(CRITICAL_ALERTS_LOG_PATH, "a") as f:
        f.write(log_entry)

def analyze_and_alert(data):
    alerts = []
    if not data:
        return alerts

    # Detect stop-loss/take-profit orders
    if "orders" in data and data["orders"]:
        for order in data["orders"]:
            if order.get("type") in ["stop_loss", "take_profit"]:
                alert_message = f"Order triggered: {order.get('type')}. Details: {order.get('details', 'N/A')}"
                alerts.append(alert_message)
                log_alert(alert_message)

    # Detect critical drawdown
    if "drawdown" in data and data["drawdown"] == "critical":
        alert_message = "Critical drawdown detected!"
        alerts.append(alert_message)
        log_alert(alert_message)
    elif "drawdown" in data and isinstance(data["drawdown"], (int, float)) and data["drawdown"] > 20: # Example: >20% drawdown
        alert_message = f"Significant drawdown detected: {data['drawdown']}%"
        alerts.append(alert_message)
        log_alert(alert_message)

    return alerts

def generate_summary(data, alerts):
    summary = f"Trading Analysis Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += "----------------------------------------\n"

    if not data:
        summary += "Failed to fetch trading data.\n"
        return summary

    summary += f"Status: {data.get('status', 'N/A')}\n"
    summary += f"Risk Parameters: {data.get('risk_parameters', 'N/A')}\n"
    summary += f"Number of orders: {len(data.get('orders', []))}\n"
    summary += f"Drawdown: {data.get('drawdown', 'N/A')}\n"

    if alerts:
        summary += "\nCritical Alerts:\n"
        for alert in alerts:
            summary += f"- {alert}\n"
    else:
        summary += "\nNo critical alerts detected.\n"

    return summary

def main():
    trading_data = fetch_trading_data()
    log_data(trading_data)
    alerts = analyze_and_alert(trading_data)
    summary = generate_summary(trading_data, alerts)
    print(summary) # This will be captured by the cron job's systemEvent

if __name__ == "__main__":
    main()
