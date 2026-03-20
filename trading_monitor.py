import requests
import datetime
import os

LOG_FILE_GENERAL = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
LOG_FILE_CRITICAL = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"

def log_message(message, log_file):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp} - {message}\\n"
    try:
        with open(log_file, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file {log_file}: {e}")

def monitor_trading_dashboard():
    critical_alerts = []
    try:
        response = requests.get(TRADING_DASHBOARD_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json() # Assuming the response is JSON

        log_message(f"Received data: {data}", LOG_FILE_GENERAL)

        # Analyze data for critical alerts
        # This is a placeholder and would need to be adapted based on the actual data structure
        if "stop_loss" in data and data["stop_loss"]:
            alert = "STOP-LOSS ORDER EXECUTED"
            critical_alerts.append(alert)
            log_message(alert, LOG_FILE_CRITICAL)

        if "take_profit" in data and data["take_profit"]:
            alert = "TAKE-PROFIT ORDER EXECUTED"
            critical_alerts.append(alert)
            log_message(alert, LOG_FILE_CRITICAL)

        if "drawdown" in data and data["drawdown"] > 0.10: # Example: 10% drawdown
            alert = f"CRITICAL DRAWDOWN DETECTED: {data['drawdown'] * 100:.2f}%"
            critical_alerts.append(alert)
            log_message(alert, LOG_FILE_CRITICAL)

    except requests.exceptions.ConnectionError:
        log_message("Failed to connect to trading dashboard.", LOG_FILE_GENERAL)
        critical_alerts.append("Failed to connect to trading dashboard.")
    except requests.exceptions.Timeout:
        log_message("Request to trading dashboard timed out.", LOG_FILE_GENERAL)
        critical_alerts.append("Request to trading dashboard timed out.")
    except requests.exceptions.RequestException as e:
        log_message(f"An error occurred while fetching data: {e}", LOG_FILE_GENERAL)
        critical_alerts.append(f"An error occurred while fetching data: {e}")
    except Exception as e:
        log_message(f"An unexpected error occurred: {e}", LOG_FILE_GENERAL)
        critical_alerts.append(f"An unexpected error occurred: {e}")

    summary = "Trading Dashboard Monitoring Summary:\\n"
    if critical_alerts:
        summary += "Critical Alerts:\\n"
        for alert in critical_alerts:
            summary += f"- {alert}\\n"
    else:
        summary += "No critical alerts detected.\\n"

    # Ensure log files exist
    for log_file in [LOG_FILE_GENERAL, LOG_FILE_CRITICAL]:
        if not os.path.exists(log_file):
            try:
                with open(log_file, "w") as f:
                    pass # Create empty file
                log_message(f"Created log file: {log_file}", LOG_FILE_GENERAL)
            except Exception as e:
                print(f"Error creating log file {log_file}: {e}")

    print(summary) # This will be captured by the exec tool's stdout

if __name__ == "__main__":
    monitor_trading_dashboard()
