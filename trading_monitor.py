import requests
import datetime
import os

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/"

def log_message(message, log_file):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Ensure the directory exists before writing
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}
")

def monitor_trading():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.text

        log_message("--- Monitoring Run ---", LOG_FILE)
        log_message(data, LOG_FILE)

        # Detect stop-loss/take-profit orders or critical drawdown
        critical_alerts = []
        if "stop-loss triggered" in data.lower() or "take-profit triggered" in data.lower():
            critical_alerts.append("Order triggered (stop-loss/take-profit)")
        if "critical drawdown" in data.lower():
            critical_alerts.append("Critical drawdown detected")

        if critical_alerts:
            alert_message = f"Critical Alerts: {', '.join(critical_alerts)}"
            log_message(alert_message, ALERT_LOG_FILE)
            return f"Analysis complete. Critical Alerts: {', '.join(critical_alerts)}"
        else:
            return "Analysis complete. No critical alerts detected."

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {URL}: {e}"
        log_message(error_message, LOG_FILE)
        log_message(error_message, ALERT_LOG_FILE)
        return f"Error during monitoring: {e}"
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        log_message(error_message, LOG_FILE)
        log_message(error_message, ALERT_LOG_FILE)
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    summary = monitor_trading()
    print(summary)
