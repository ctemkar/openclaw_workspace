# Filename: monitor_trading.py
import requests
import json
import datetime
import os

# --- Configuration ---

    PORT = "5001"  # Fallback
except:
        PORT = f.read().strip()
    with open(".active_port", "r") as f:
try:
# Read current port from .active_port file

URL = f"http://localhost:{PORT}/"
TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
# Define your critical drawdown threshold here.
# This value should be set based on your risk management strategy.
# Example: A capital of 5000 or less is considered critical.
CRITICAL_DRAWDOWN_THRESHOLD = 10000 # PLEASE DEFINE THIS BASED ON YOUR NEEDS

# --- Helper function to ensure directory exists ---
def ensure_log_dir(file_path):
    log_dir = os.path.dirname(file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print(f"Created directory: {log_dir}")
        except OSError as e:
            print(f"Error creating directory {log_dir}: {e}")

# --- Main function to fetch, parse, log, and alert ---
def monitor_trading_dashboard():
    try:
        print(f"Fetching data from: {URL}")
        response = requests.get(URL, timeout=15) # Increased timeout slightly
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.Timeout:
        print(f"Error: Request to {URL} timed out after 15 seconds.")
        return
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to {URL}. Ensure the service is running. Details: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {URL}: {e}")
        return

    try:
        data = response.json() # Assuming JSON response
    except json.JSONDecodeError:
        print(f"Error: Response from {URL} is not valid JSON. Content snippet: {response.text[:200]}...") # Log snippet of response
        return

    # --- Data Extraction ---
    # IMPORTANT: Adapt these keys based on the actual JSON structure from your endpoint.
    # If the structure is different, you'll need to modify this section.
    try:
        trading_logs_data = data.get("trading_logs", [])
        status_updates_data = data.get("status_updates", [])
        risk_params = data.get("risk_parameters", {})
        
        capital = risk_params.get("capital")
        stop_loss_info = risk_params.get("stop_loss", {}) 
        take_profit_info = risk_params.get("take_profit", {})

        # Ensure stop_loss/take_profit are dicts to safely access 'triggered'
        if not isinstance(stop_loss_info, dict): stop_loss_info = {}
        if not isinstance(take_profit_info, dict): take_profit_info = {}

        stop_loss_triggered = stop_loss_info.get("triggered", False)
        take_profit_triggered = take_profit_info.get("triggered", False)

    except Exception as e:
        print(f"Error parsing data structure: {e}. Raw data might be: {data}")
        return

    # --- Logging to trading_monitoring.log ---
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "capital": capital,
        "stop_loss_triggered": stop_loss_triggered,
        "take_profit_triggered": take_profit_triggered,
        # Log counts or summaries if logs/updates are very large
        "trading_logs_count": len(trading_logs_data), 
        "status_updates_count": len(status_updates_data) 
    }
    
    ensure_log_dir(TRADING_LOG_PATH)
    try:
        with open(TRADING_LOG_PATH, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")
        print(f"Successfully logged monitoring data to {TRADING_LOG_PATH}")
    except IOError as e:
        print(f"Error writing to {TRADING_LOG_PATH}: {e}")

    # --- Alerting Logic ---
    alerts = []
    critical_data_for_alert = {}

    if stop_loss_triggered:
        alert_msg = f"ALERT: Stop-loss triggered."
        alerts.append({"type": "stop_loss_triggered", "message": alert_msg, "details": stop_loss_info})
        critical_data_for_alert.update(stop_loss_info)
        print(alert_msg)

    if take_profit_triggered:
        alert_msg = f"ALERT: Take-profit triggered."
        alerts.append({"type": "take_profit_triggered", "message": alert_msg, "details": take_profit_info})
        critical_data_for_alert.update(take_profit_info)
        print(alert_msg)

    # --- Critical Drawdown Alert ---
    # IMPORTANT: Review and define your critical drawdown logic here and set CRITICAL_DRAWDOWN_THRESHOLD.
    # This script checks if 'capital' falls below CRITICAL_DRAWDOWN_THRESHOLD.
    if capital is not None:
        try:
            capital_float = float(capital) 
            if capital_float < CRITICAL_DRAWDOWN_THRESHOLD:
                alert_msg = f"CRITICAL DRAWDOWN ALERT: Capital ({capital_float}) is below threshold ({CRITICAL_DRAWDOWN_THRESHOLD})."
                alerts.append({"type": "critical_drawdown", "message": alert_msg, "value": capital_float, "threshold": CRITICAL_DRAWDOWN_THRESHOLD})
                critical_data_for_alert.update({"capital": capital_float, "drawdown_threshold": CRITICAL_DRAWDOWN_THRESHOLD})
                print(alert_msg)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert capital value '{capital}' to a number for drawdown check.")

    # --- Logging Critical Alerts ---
    if alerts:
        alert_log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "alerts": alerts,
            "critical_data_captured": critical_data_for_alert # Captures data associated with triggered alerts
        }
        ensure_log_dir(CRITICAL_ALERT_LOG_PATH)
        try:
            with open(CRITICAL_ALERT_LOG_PATH, "a") as f:
                json.dump(alert_log_entry, f)
                f.write("\n")
            print(f"Successfully logged critical alerts to {CRITICAL_ALERT_LOG_PATH}")
        except IOError as e:
            print(f"Error writing critical alerts to {CRITICAL_ALERT_LOG_PATH}: {e}")
    else:
        print("No critical alerts triggered at this time.")

if __name__ == "__main__":
    # This script is designed to be run periodically.
    # To automate it, use your system's task scheduler (e.g., cron on Linux/macOS, Task Scheduler on Windows).
    monitor_trading_dashboard()

