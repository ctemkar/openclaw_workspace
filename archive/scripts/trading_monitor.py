# scripts/trading_monitor.py
import requests
import json
import datetime
import os

# Define paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRADING_LOG_PATH = os.path.join(SCRIPT_DIR, "..", "trading_monitoring.log")
CRITICAL_ALERT_LOG_PATH = os.path.join(SCRIPT_DIR, "..", "critical_alerts.log")
URL = "http://localhost:5001/"

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        # Attempt to parse as JSON, fall back to text if not JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Response from {url} is not valid JSON. Returning raw text.")
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def parse_and_analyze(data):
    if not data:
        return None, [], []

    alerts = []
    critical_data_payload = {} # This will store data relevant for critical alerts

    # --- Flexible Parsing Logic ---
    # Try to parse as JSON first
    parsed_json = None
    if isinstance(data, dict):
        parsed_json = data
    else: # If it's text, try to load it as JSON
        try:
            parsed_json = json.loads(data)
        except json.JSONDecodeError:
            pass # Keep data as raw text if not JSON

    if parsed_json:
        capital = parsed_json.get('capital')
        stop_loss_triggered = parsed_json.get('stop_loss_triggered', False)
        take_profit_triggered = parsed_json.get('take_profit_triggered', False)
        drawdown_critical = parsed_json.get('drawdown_critical', False)
        status_updates = parsed_json.get('status_updates', [])
        trading_logs = parsed_json.get('trading_logs', [])

        if stop_loss_triggered:
            alerts.append("STOP LOSS TRIGGERED")
        if take_profit_triggered:
            alerts.append("TAKE PROFIT TRIGGERED")
        if drawdown_critical:
            alerts.append("CRITICAL DRAWDOWN INDICATORS")

        # Prepare data for critical alert log
        critical_data_payload = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "capital": capital,
            "stop_loss_triggered": stop_loss_triggered,
            "take_profit_triggered": take_profit_triggered,
            "drawdown_critical": drawdown_critical,
            "status_updates": status_updates,
            "trading_logs": trading_logs,
            "raw_data": parsed_json # Include the parsed JSON data
        }
        # Also return the parsed data for general logging
        return parsed_json, alerts, critical_data_payload
    else:
        # If parsing as JSON failed, treat the whole response as log data
        print("Could not parse data as JSON. Logging raw text.")
        return data, [], {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "raw_data": data # Log the raw text
        }


def log_data(data_to_log, alerts, critical_data_payload):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log all extracted data
    log_entry_prefix = f"[{current_time}]"
    if alerts:
        log_entry_prefix += f" ALERT(S): {', '.join(alerts)} |"

    try:
        # Ensure log directory exists
        os.makedirs(os.path.dirname(TRADING_LOG_PATH), exist_ok=True)
        with open(TRADING_LOG_PATH, "a") as f:
            f.write(f"{log_entry_prefix} Extracted Data: {json.dumps(data_to_log, indent=2) if isinstance(data_to_log, dict) else data_to_log}\n")
    except IOError as e:
        print(f"Error writing to {TRADING_LOG_PATH}: {e}")

    # Log critical alerts and their data
    if alerts:
        try:
            # Ensure path exists
            os.makedirs(os.path.dirname(CRITICAL_ALERT_LOG_PATH), exist_ok=True)
            with open(CRITICAL_ALERT_LOG_PATH, "a") as f:
                f.write(f"--- CRITICAL ALERT at {current_time} ---\n")
                f.write(f"Triggered: {', '.join(alerts)}\n")
                f.write(f"Critical Data Payload: {json.dumps(critical_data_payload, indent=2)}\n")
                f.write("--------------------------\n")
        except IOError as e:
            print(f"Error writing to {CRITICAL_ALERT_LOG_PATH}: {e}")

if __name__ == "__main__":
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching data from {URL}...")
    fetched_data = fetch_data(URL)

    if fetched_data is not None:
        print("Data fetched. Parsing and analyzing...")
        original_data_for_log, alerts, critical_data_payload = parse_and_analyze(fetched_data)
        print("Logging data...")
        log_data(original_data_for_log, alerts, critical_data_payload)

        if alerts:
            print(f"*** Critical Alerts Triggered: {', '.join(alerts)} ***")
        else:
            print("No critical alerts triggered.")
    else:
        print("Failed to fetch data. No analysis or logging performed.")
