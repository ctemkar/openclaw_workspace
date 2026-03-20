import requests
import json
import datetime
import os

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DATA_URL = "http://localhost:5001/"

def fetch_trading_data():
    try:
        response = requests.get(TRADING_DATA_URL)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trading data: {e}")
        return None

def log_data(data):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] {json.dumps(data)}\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def check_critical_alerts(data):
    triggered = False
    alert_message = ""
    alert_details = {}

    if not data or not isinstance(data, dict):
        if data is not None: # Log if data is not None but not a dict
            timestamp = datetime.datetime.now().isoformat()
            log_entry = f"[{timestamp}] Received unexpected data format: {data}\n"
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)
        return False, "", {}

    # Example checks: Replace with actual logic based on data structure
    # --- These are placeholders, you need to know the actual keys ---
    stop_loss_triggered = data.get("stop_loss_triggered", False)
    take_profit_triggered = data.get("take_profit_triggered", False)
    drawdown_critical = data.get("drawdown_critical", False)
    
    if stop_loss_triggered:
        triggered = True
        alert_message += "STOP LOSS TRIGGERED! "
        alert_details["stop_loss"] = data.get("stop_loss_details", "N/A")

    if take_profit_triggered:
        triggered = True
        alert_message += "TAKE PROFIT TRIGGERED! "
        alert_details["take_profit"] = data.get("take_profit_details", "N/A")

    if drawdown_critical:
        triggered = True
        alert_message += "DRAWDOWN CRITICAL! "
        alert_details["drawdown"] = data.get("drawdown_details", "N/A")
    # --- End of placeholders ---

    if triggered:
        timestamp = datetime.datetime.now().isoformat()
        critical_log_entry = f"[{timestamp}] CRITICAL ALERT: {alert_message.strip()}\nDetails: {json.dumps(alert_details)}\n"
        os.makedirs(os.path.dirname(CRITICAL_ALERTS_FILE), exist_ok=True)
        with open(CRITICAL_ALERTS_FILE, "a") as f:
            f.write(critical_log_entry)
        print(f"CRITICAL ALERT: {alert_message.strip()} - Details logged to {CRITICAL_ALERTS_FILE}")
    
    return triggered, alert_message.strip(), alert_details

if __name__ == "__main__":
    trading_data = fetch_trading_data()
    if trading_data is not None: # Check if fetch was successful (even if data is empty dict)
        log_data(trading_data)
        is_critical, alert_msg, alert_details = check_critical_alerts(trading_data)
        # The systemEvent will display the alert message if it's critical
        if is_critical:
            print(f"ALERT: {alert_msg}")
    else:
        log_data({"error": "Failed to fetch trading data from API."})

