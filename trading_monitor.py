
import requests
import json
from datetime import datetime

LOG_FILE = "./trading_monitoring.log"
ALERT_LOG_FILE = "./critical_alerts.log"
URL = "http://localhost:5001/"

def fetch_and_log_data():
    summary_lines = []
    alert_lines = []
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Log general monitoring data
        with open(LOG_FILE, "a") as f:
            f.write(f"--- {timestamp} ---\n")
            f.write(f"Status Updates: {json.dumps(data.get("status_updates", "N/A"), indent=2)}\n")
            f.write(f"Risk Parameters: {json.dumps(data.get("risk_parameters", "N/A"), indent=2)}\n")
            f.write(f"Trading Logs: {json.dumps(data.get("trading_logs", "N/A"), indent=2)}\n")
            f.write("\n")
            summary_lines.append(f"[{timestamp}] Monitored: OK.")

        # Detect and log alerts
        trading_logs = data.get("trading_logs", [])
        critical_alert_detected = False
        if isinstance(trading_logs, list):
            for log_entry in trading_logs:
                if "stop-loss" in log_entry.lower() or "take-profit" in log_entry.lower() or "critical drawdown" in log_entry.lower():
                    alert_message = f"[{timestamp}] CRITICAL ALERT: {log_entry}"
                    with open(ALERT_LOG_FILE, "a") as f:
                        f.write(alert_message + "\n")
                    alert_lines.append(f"[{timestamp}] ALERT: {log_entry}")
                    critical_alert_detected = True

        if not critical_alert_detected and isinstance(trading_logs, list) and len(trading_logs) > 0:
            summary_lines.append("No critical alerts detected in trading logs.")
        elif not isinstance(trading_logs, list):
            summary_lines.append("Trading logs data format unexpected. Cannot check for alerts.")

    except requests.exceptions.Timeout:
        error_message = f"[{timestamp}] ERROR: Request timed out while trying to reach {URL}"
        with open(ALERT_LOG_FILE, "a") as f:
            f.write(error_message + "\n")
        summary_lines.append(f"[{timestamp}] ERROR: Timeout connecting to dashboard.")
        alert_lines.append(f"[{timestamp}] ERROR: Timeout connecting to dashboard.")
    except requests.exceptions.RequestException as e:
        error_message = f"[{timestamp}] ERROR: Failed to fetch data from {URL}: {e}"
        with open(ALERT_LOG_FILE, "a") as f:
            f.write(error_message + "\n")
        summary_lines.append(f"[{timestamp}] ERROR: Failed to connect to dashboard ({e}).")
        alert_lines.append(f"[{timestamp}] ERROR: Failed to connect to dashboard ({e}).")
    except json.JSONDecodeError:
        error_message = f"[{timestamp}] ERROR: Failed to decode JSON response from {URL}"
        with open(ALERT_LOG_FILE, "a") as f:
            f.write(error_message + "\n")
        summary_lines.append(f"[{timestamp}] ERROR: Invalid JSON response from dashboard.")
        alert_lines.append(f"[{timestamp}] ERROR: Invalid JSON response from dashboard.")
    except Exception as e:
        error_message = f"[{timestamp}] UNEXPECTED ERROR: {e}"
        with open(ALERT_LOG_FILE, "a") as f:
            f.write(error_message + "\n")
        summary_lines.append(f"[{timestamp}] UNEXPECTED ERROR occurred.")
        alert_lines.append(f"[{timestamp}] UNEXPECTED ERROR occurred.")

    return "\n".join(summary_lines), "\n".join(alert_lines)

if __name__ == "__main__":
    analysis_summary, critical_alerts = fetch_and_log_data()
    print("--- Analysis Summary ---")
    print(analysis_summary)
    if critical_alerts:
        print("\n--- Critical Alerts ---")
        print(critical_alerts)
