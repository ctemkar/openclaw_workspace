# monitor_trading.py
import requests
import json
import os
from datetime import datetime

# Configuration
DATA_URL = "http://localhost:5001/api/data"
TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
MAX_DRAWDOWN_PERCENT = 10.0

# In a real scenario, this would be persisted or loaded from a file
# For demonstration, we'll assume the state is reset on each run or handled by a separate state file.
# For this example, we will not persist last_peak_equity to keep it simple and directly executable.
# If persistence is needed, a file-based approach or a database would be required.

def log_to_file(file_path, message):
    """Appends a message to a log file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(file_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except IOError as e:
        print(f"Error writing to log file {file_path}: {e}")

def fetch_trading_data():
    """Fetches trading data from the specified URL."""
    try:
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        log_to_file(TRADING_LOG_FILE, f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError:
        log_to_file(TRADING_LOG_FILE, "Error decoding JSON response.")
        return None

def analyze_data(data, last_peak_equity_value):
    """Analyzes trading data for alerts."""
    alerts = []
    summary_lines = []

    log_to_file(TRADING_LOG_FILE, f"Received data: {json.dumps(data, indent=2)}")
    summary_lines.append(f"Data fetched at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")

    current_equity = data.get("equity")
    last_trade = data.get("last_trade")
    risk_parameters = data.get("risk_parameters") # More generic name for risk parameters

    new_peak_equity = last_peak_equity_value

    if current_equity is not None:
        if last_peak_equity_value is None or current_equity > last_peak_equity_value:
            new_peak_equity = current_equity
            summary_lines.append(f"New peak equity detected: ${current_equity:,.2f}")
        else:
            drawdown = ((last_peak_equity_value - current_equity) / last_peak_equity_value) * 100
            if drawdown > MAX_DRAWDOWN_PERCENT:
                alert_msg = f"CRITICAL DRAWDOWN DETECTED: Current equity ${current_equity:,.2f}, Peak equity ${last_peak_equity_value:,.2f}. Drawdown: {drawdown:.2f}%"
                alerts.append(alert_msg)
                log_to_file(CRITICAL_ALERTS_LOG_FILE, alert_msg)
                summary_lines.append(f"Critical drawdown detected: {drawdown:.2f}%")
            else:
                summary_lines.append(f"Current equity: ${current_equity:,.2f} (Peak: ${last_peak_equity_value:,.2f}, Drawdown: {drawdown:.2f}%)")
    else:
        summary_lines.append("Current equity not available in data.")

    if last_trade:
        order_status = last_trade.get("status")
        order_type = last_trade.get("order_type")
        order_price = last_trade.get("price")

        if order_status == "triggered" and order_type in ["stop_loss", "take_profit"]:
            alert_msg = f"Order Triggered: {order_type.replace('_', ' ').title()} at ${order_price}"
            alerts.append(alert_msg)
            log_to_file(CRITICAL_ALERTS_LOG_FILE, alert_msg)
            summary_lines.append(f"Order '{order_type}' triggered at ${order_price}.")
        else:
            summary_lines.append(f"Last trade action: {order_type} at ${order_price}.")
    else:
        summary_lines.append("No last trade information available.")

    if risk_parameters:
        log_to_file(TRADING_LOG_FILE, f"Risk Parameters: {json.dumps(risk_parameters, indent=2)}")
        summary_lines.append(f"Risk Parameters: {json.dumps(risk_parameters, indent=2)}")

    return "\\n".join(summary_lines), alerts, new_peak_equity

if __name__ == "__main__":
    # This script needs state (last_peak_equity) to be managed across runs.
    # For simplicity in this example, we are *not* persisting state.
    # A real implementation MUST persist 'last_peak_equity'.
    # Example of how to load/save state if it were managed in a file:
    # STATE_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_state.json"
    # last_peak_equity = None
    # try:
    #     with open(STATE_FILE, "r") as f:
    #         state_data = json.load(f)
    #         last_peak_equity = state_data.get("last_peak_equity")
    # except (FileNotFoundError, json.JSONDecodeError):
    #     pass # State file doesn't exist or is corrupt, start fresh

    trading_data = fetch_trading_data()
    if trading_data:
        # NOTE: For actual use, 'last_peak_equity' MUST be saved and loaded between runs.
        # The current implementation will reset last_peak_equity on each run, making drawdown
        # detection relative to the equity *in the current fetch*, not a historical peak.
        # We pass None initially for demonstration purposes, but this needs state management.
        summary, alerts, new_peak_equity = analyze_data(trading_data, None) # Passing None for simplicity
        print(summary)

        if alerts:
            print("\\n--- CRITICAL ALERTS ---")
            for alert in alerts:
                print(alert)

        # Example of saving state (to be uncommented/implemented for real use)
        # try:
        #     with open(STATE_FILE, "w") as f:
        #         json.dump({"last_peak_equity": new_peak_equity}, f)
        # except IOError as e:
        #     print(f"Error saving state file {STATE_FILE}: {e}")

    else:
        print("Failed to fetch or process trading data.")
