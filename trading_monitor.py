import requests
import json
import os
import datetime

TRADING_DATA_URL = "http://localhost:5001/"
TRADING_MONITORING_LOG_DIR = "/Users/chetantemkar/.openclaw/workspace/app/"
TRADING_MONITORING_LOG_FILE = os.path.join(TRADING_MONITORING_LOG_DIR, "trading_monitoring.log")
CRITICAL_ALERTS_LOG_FILE = os.path.join(TRADING_MONITORING_LOG_DIR, "critical_alerts.log")

def fetch_trading_data():
    try:
        response = requests.get(TRADING_DATA_URL, timeout=10) # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json() # Assuming JSON response
    except requests.exceptions.Timeout:
        print(f"Request timed out for {TRADING_DATA_URL}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trading data: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {TRADING_DATA_URL}")
        return None

def log_to_file(file_path, content):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Get current timestamp for logging
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(file_path, "a") as f:
            f.write(f"[{timestamp}] {content}\n")
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")

def identify_critical_events(data):
    # Placeholder logic: Replace with actual stop-loss/take-profit/drawdown indicators
    # Example: If 'status' is 'critical' or 'drawdown' > 5
    critical_events = []
    if data:
        current_price = data.get("current_price")
        stop_loss = data.get("stop_loss")
        take_profit = data.get("take_profit")
        drawdown = data.get("drawdown") # Assuming drawdown is a percentage

        if data.get("status") == "critical":
            critical_events.append("Critical status detected.")
        
        if stop_loss is not None and current_price is not None and current_price <= stop_loss:
            critical_events.append(f"Stop-loss triggered at price {current_price}.")
        
        if take_profit is not None and current_price is not None and current_price >= take_profit:
            critical_events.append(f"Take-profit triggered at price {current_price}.")

        if drawdown is not None and drawdown > 5: # Example threshold for drawdown
            critical_events.append(f"Critical drawdown detected: {drawdown}%.")
            
    return critical_events

def main():
    data = fetch_trading_data()

    if data:
        # Log all extracted data to trading_monitoring.log
        log_to_file(TRADING_MONITORING_LOG_FILE, f"Extracted Data: {json.dumps(data, indent=2)}")

        # Identify and log critical events
        critical_events = identify_critical_events(data)

        if critical_events:
            alert_message = "CRITICAL EVENTS: " + "\n  - ".join(critical_events)
            log_to_file(CRITICAL_ALERTS_LOG_FILE, alert_message)
            print("Critical events detected and logged.")
        else:
            # If no critical events, log extracted data to critical alerts log as per requirement
            log_to_file(CRITICAL_ALERTS_LOG_FILE, f"No critical events. Extracted Data: {json.dumps(data, indent=2)}")
            print("No critical events detected. Extracted data logged to critical alerts log.")
    else:
        log_to_file(TRADING_MONITORING_LOG_FILE, "Failed to fetch trading data.")
        log_to_file(CRITICAL_ALERTS_LOG_FILE, "Failed to fetch trading data.")
        print("Failed to fetch trading data. Logs updated accordingly.")

if __name__ == "__main__":
    main()
