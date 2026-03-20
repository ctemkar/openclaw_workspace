# monitor_trading.py (corrected log_message function)
import requests
import json
from datetime import datetime
import os

TRADING_MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/"

def log_message(log_file, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Construct the message with timestamp
        log_entry = f"[{timestamp}] {message}"
        # Append the newline character explicitly
        with open(log_file, "a") as f:
            f.write(log_entry + "
")
    except Exception as e:
        print(f"Error writing to log file {log_file}: {e}")


def monitor_trading_dashboard():
    try:
        try:
            response = requests.get(URL, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.ConnectionError:
            data = {
                "trading_logs": "Connection to dashboard failed.",
                "status": "UNAVAILABLE",
                "risk_parameters": "N/A",
                "alerts": "CONNECTION_ERROR"
            }
        except requests.exceptions.Timeout:
            data = {
                "trading_logs": "Connection to dashboard timed out.",
                "status": "UNAVAILABLE",
                "risk_parameters": "N/A",
                "alerts": "TIMEOUT_ERROR"
            }
        except requests.exceptions.RequestException as e:
            data = {
                "trading_logs": f"Request error: {e}",
                "status": "ERROR",
                "risk_parameters": "N/A",
                "alerts": f"REQUEST_ERROR: {e}"
            }
        except json.JSONDecodeError:
            data = {
                "trading_logs": "Received non-JSON response.",
                "status": "ERROR",
                "risk_parameters": "N/A",
                "alerts": "INVALID_RESPONSE_FORMAT"
            }

        os.makedirs(os.path.dirname(TRADING_MONITORING_LOG), exist_ok=True)
        os.makedirs(os.path.dirname(CRITICAL_ALERTS_LOG), exist_ok=True)

        log_message(TRADING_MONITORING_LOG, f"Received data from {URL}: {json.dumps(data)}")

        trading_logs = data.get('trading_logs', 'N/A')
        status_updates = data.get('status', 'N/A')
        risk_parameters = data.get('risk_parameters', 'N/A')

        log_message(TRADING_MONITORING_LOG, f"Trading Logs: {trading_logs}")
        log_message(TRADING_MONITORING_LOG, f"Status Updates: {status_updates}")
        log_message(TRADING_MONITORING_LOG, f"Risk Parameters: {risk_parameters}")

        critical_alerts_detected = []
        alerts = data.get('alerts', [])
        if isinstance(alerts, list):
            for alert in alerts:
                 if isinstance(alert, str) and any(keyword in alert.upper() for keyword in ["STOP_LOSS_TRIGGERED", "TAKE_PROFIT_TRIGGERED", "CRITICAL_DRAWDOWN"]):
                    critical_alerts_detected.append(alert)
                    log_message(CRITICAL_ALERTS_LOG, f"CRITICAL ALERT DETECTED: {alert}")
        elif isinstance(alerts, str):
            if any(keyword in alerts.upper() for keyword in ["STOP_LOSS_TRIGGERED", "TAKE_PROFIT_TRIGGERED", "CRITICAL_DRAWDOWN"]):
                critical_alerts_detected.append(alerts)
                log_message(CRITICAL_ALERTS_LOG, f"CRITICAL ALERT DETECTED: {alerts}")

        summary = f"Trading Dashboard Analysis ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):
")
        summary += f"  URL: {URL}
")
        summary += f"  Status: {status_updates}
")
        summary += f"  Risk Parameters: {risk_parameters}
")
        if critical_alerts_detected:
            summary += f"  CRITICAL ALERTS: {'; '.join(critical_alerts_detected)}
")
        else:
            summary += "  No critical alerts detected.
")

        print(summary)

    except Exception as e:
        error_message = f"An unexpected error occurred in monitor_trading_dashboard: {e}"
        log_message(TRADING_MONITORING_LOG, error_message)
        log_message(CRITICAL_ALERTS_LOG, f"SYSTEM ERROR: {error_message}")
        print(f"Error: {error_message}")

if __name__ == "__main__":
    monitor_trading_dashboard()
