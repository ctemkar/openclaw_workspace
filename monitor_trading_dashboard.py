import requests
import json
from datetime import datetime

LOG_FILE_GENERAL = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
LOG_FILE_CRITICAL = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
ENDPOINT_URL = "http://localhost:5001/"
CRITICAL_DRAWDOWN_THRESHOLD = 0.05 # 5%

def log_message(file_path, message):
    with open(file_path, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}
")

def monitor_dashboard():
    critical_alerts_found = False
    try:
        response = requests.get(ENDPOINT_URL, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()

        # Log general data
        log_data = data.get("log_data", "No log data available")
        status = data.get("status", "Unknown status")
        log_message(LOG_FILE_GENERAL, f"Status: {status} | Log: {log_data}")

        # Check for critical alerts
        last_trade_action = data.get("last_trade_action")
        current_drawdown = data.get("current_drawdown")

        if last_trade_action in ["stop-loss", "take-profit"]:
            critical_alerts_found = True
            alert_message = f"Trade Action Alert: {last_trade_action.upper()} triggered."
            log_message(LOG_FILE_CRITICAL, alert_message)

        if current_drawdown is not None and float(current_drawdown) > CRITICAL_DRAWDOWN_THRESHOLD:
            critical_alerts_found = True
            alert_message = f"Critical Drawdown Alert: Current drawdown {float(current_drawdown)*100:.2f}% exceeds threshold of {CRITICAL_DRAWDOWN_THRESHOLD*100:.2f}%."
            log_message(LOG_FILE_CRITICAL, alert_message)

        # Generate summary
        summary = "Trading Dashboard Monitor Summary:
"
        summary += f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"
        summary += f"Status: {status}
"
        if critical_alerts_found:
            summary += "Critical Alerts: Yes. Please check critical_alerts.log for details.
"
        else:
            summary += "Critical Alerts: No critical alerts detected.
"

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {ENDPOINT_URL}: {e}"
        log_message(LOG_FILE_CRITICAL, error_message)
        summary = f"Trading Dashboard Monitor Summary:
"
        summary += f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"
        summary += f"Error: Could not connect to the trading dashboard. {e}
"
    except json.JSONDecodeError:
        error_message = f"Error decoding JSON response from {ENDPOINT_URL}."
        log_message(LOG_FILE_CRITICAL, error_message)
        summary = f"Trading Dashboard Monitor Summary:
"
        summary += f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"
        summary += f"Error: Received non-JSON response from the trading dashboard.
"
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        log_message(LOG_FILE_CRITICAL, error_message)
        summary = f"Trading Dashboard Monitor Summary:
"
        summary += f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"
        summary += f"Error: An unexpected error occurred. {e}
"

    return summary

if __name__ == "__main__":
    final_summary = monitor_dashboard()
    print(final_summary)
