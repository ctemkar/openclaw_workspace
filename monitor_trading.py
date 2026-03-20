import requests
import json
from datetime import datetime

MONITORING_LOG = "./trading_monitoring.log"
CRITICAL_ALERTS_LOG = "./critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"

def log_message(message, log_file):
    timestamp = datetime.now().isoformat()
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}
")

def monitor():
    try:
        response = requests.get(TRADING_DASHBOARD_URL, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()

        # Log general monitoring data
        log_message(f"Status: OK. Data: {json.dumps(data)}", MONITORING_LOG)

        # Check for critical alerts
        critical_alerts = []
        if data.get("stop_loss_triggered"):
            critical_alerts.append("STOP-LOSS TRIGGERED")
        if data.get("take_profit_triggered"):
            critical_alerts.append("TAKE-PROFIT TRIGGERED")
        if data.get("drawdown_critical"):
            critical_alerts.append("CRITICAL DRAWDOWN DETECTED")

        if critical_alerts:
            alert_message = f"CRITICAL ALERT(S): {', '.join(critical_alerts)}. Data: {json.dumps(data)}"
            log_message(alert_message, CRITICAL_ALERTS_LOG)
            return f"CRITICAL: {' & '.join(critical_alerts)}. Analysis follows:
{json.dumps(data, indent=2)}"
        else:
            return f"Trading Dashboard Status: OK. Risk Parameters: {json.dumps(data, indent=2)}"

    except requests.exceptions.RequestException as e:
        error_message = f"ERROR connecting to {TRADING_DASHBOARD_URL}: {e}"
        log_message(error_message, MONITORING_LOG)
        log_message(f"CRITICAL ALERT: Failed to connect to trading dashboard. Error: {e}", CRITICAL_ALERTS_LOG)
        return f"CRITICAL: Failed to connect to trading dashboard ({TRADING_DASHBOARD_URL}). Error: {e}"
    except json.JSONDecodeError:
        error_message = "ERROR: Received non-JSON response from trading dashboard."
        log_message(error_message, MONITORING_LOG)
        log_message(f"CRITICAL ALERT: Invalid response from trading dashboard.", CRITICAL_ALERTS_LOG)
        return "CRITICAL: Received invalid (non-JSON) response from trading dashboard."
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        log_message(error_message, MONITORING_LOG)
        log_message(f"CRITICAL ALERT: Unexpected error during monitoring. Error: {e}", CRITICAL_ALERTS_LOG)
        return f"CRITICAL: An unexpected error occurred: {e}"

if __name__ == "__main__":
    summary = monitor()
    print(summary) # This will be captured if scheduled via cron job that outputs stdout
