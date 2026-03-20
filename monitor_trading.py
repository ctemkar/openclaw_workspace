
import requests
import time
import os

URL = "http://localhost:5001/"
TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Ensure log directories exist
for log_path in [TRADING_LOG_PATH, CRITICAL_ALERTS_LOG_PATH]:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

def fetch_data():
    try:
        response = requests.get(URL)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json() # Assuming the endpoint returns JSON
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {URL}: {e}")
        return None

def log_data(data):
    with open(TRADING_LOG_PATH, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} - {data}\n")

def check_alerts(data):
    alerts = []
    if data and isinstance(data, dict):
        # Example: Check for stop-loss/take-profit orders or critical drawdown
        # This is highly dependent on the structure of your trading data
        if data.get("stop_loss_triggered"):
            alerts.append(f"STOP LOSS TRIGGERED: {data.get('stop_loss_details', 'N/A')}")
        if data.get("take_profit_triggered"):
            alerts.append(f"TAKE PROFIT TRIGGERED: {data.get('take_profit_details', 'N/A')}")
        if data.get("critical_drawdown"):
            alerts.append(f"CRITICAL DRAWDOWN DETECTED: {data.get('drawdown_details', 'N/A')}")
        
    return alerts

def log_alerts(alerts):
    if alerts:
        with open(CRITICAL_ALERTS_LOG_PATH, "a") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            for alert in alerts:
                f.write(f"{timestamp} - ALERT: {alert}\n")

def generate_summary(data, alerts):
    summary = "Trading Dashboard Analysis:\n"
    if data:
        summary += f"- Status: {data.get('status', 'N/A')}\n"
        summary += f"- Risk Parameters: {data.get('risk_parameters', 'N/A')}\n"
        # Add more details from data as needed
    else:
        summary += "- Could not retrieve live data.\n"

    if alerts:
        summary += "\nCRITICAL ALERTS: \n"
        for alert in alerts:
            summary += f"- {alert}\n"
    else:
        summary += "\nNo critical alerts detected.\n"

    return summary

if __name__ == "__main__":
    while True:
        current_data = fetch_data()
        if current_data:
            log_data(current_data)
            critical_alerts = check_alerts(current_data)
            if critical_alerts:
                log_alerts(critical_alerts)
            
            summary = generate_summary(current_data, critical_alerts)
            print(summary) # This will be captured by the parent session
        
        time.sleep(60) # Check every 60 seconds
