import requests
import json
import os
from datetime import datetime

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/"

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_and_log(data):
    if not data:
        return

    log_entry = f"{datetime.now()}: "
    content_to_log = []
    critical_alerts = []

    # Extract and log trading logs
    trading_logs = data.get('trading_logs', [])
    if trading_logs:
        content_to_log.append("Trading Logs:")
        for log in trading_logs:
            content_to_log.append(f"  - {log}")
            # Basic check for any keyword that might indicate a triggered event in logs
            if any(keyword in str(log).lower() for keyword in ["triggered", "executed", "closed"]):
                critical_alerts.append(f"Potential trading event in logs: {log}")

    # Extract and log status updates
    status_updates = data.get('status_updates', {})
    if status_updates:
        content_to_log.append("Status Updates:")
        for key, value in status_updates.items():
            content_to_log.append(f"  - {key}: {value}")

    # Extract and log risk parameters and check for alerts
    risk_parameters = data.get('risk_parameters', {})
    capital = risk_parameters.get('capital')
    stop_loss = risk_parameters.get('stop_loss')
    take_profit = risk_parameters.get('take_profit')
    drawdown_indicators = risk_parameters.get('drawdown_indicators') # Assuming this is a dict or list

    if capital is not None:
        content_to_log.append(f"Risk Parameters:")
        content_to_log.append(f"  - Capital: {capital}")
        # Example: check if capital is below a threshold
        if isinstance(capital, (int, float)) and capital < 1000: # Example threshold
            critical_alerts.append(f"Critical Capital Alert: Capital is {capital}")

    if stop_loss is not None:
        content_to_log.append(f"  - Stop Loss: {stop_loss}")
        # Placeholder for stop-loss trigger logic - needs more context on how SL is represented
        if "triggered" in str(stop_loss).lower(): # Example check
            critical_alerts.append(f"Stop Loss triggered: {stop_loss}")

    if take_profit is not None:
        content_to_log.append(f"  - Take Profit: {take_profit}")
        # Placeholder for take-profit trigger logic
        if "triggered" in str(take_profit).lower(): # Example check
            critical_alerts.append(f"Take Profit triggered: {take_profit}")

    if drawdown_indicators is not None:
        content_to_log.append(f"  - Drawdown Indicators: {drawdown_indicators}")
        # Example: check for critical drawdown
        if isinstance(drawdown_indicators, (int, float)) and drawdown_indicators > 0.20: # Example threshold for 20% drawdown
            critical_alerts.append(f"Critical Drawdown Alert: Drawdown is {drawdown_indicators * 100:.2f}%")
        elif isinstance(drawdown_indicators, dict) and any(val > 0.20 for val in drawdown_indicators.values()):
            critical_alerts.append(f"Critical Drawdown Alert detected in indicators: {drawdown_indicators}")


    # Write to main log file
    log_content = "\n".join(content_to_log)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n" + log_content + "\n---\n")

    # Write critical alerts to alert file
    if critical_alerts:
        alert_entry = f"{datetime.now()}: CRITICAL ALERTS DETECTED\n" + "\n".join(critical_alerts) + "\n---\n"
        with open(ALERT_FILE, "a") as f:
            f.write(alert_entry)
        print("Critical alerts saved.")

# --- Main execution ---
if __name__ == "__main__":
    # Ensure log directories exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)

    print(f"Fetching data from {URL}...")
    data = fetch_data(URL)
    if data:
        print("Data fetched successfully. Parsing and logging...")
        parse_and_log(data)
        print("Processing complete.")
    else:
        print("Failed to fetch data. Skipping processing.")