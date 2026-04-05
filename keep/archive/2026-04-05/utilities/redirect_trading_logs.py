import requests
import datetime

# --- Configuration ---
URL = "http://localhost:5001/"
MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
# *** These keywords need to be confirmed/provided by the user ***
STOP_LOSS_TAKE_PROFIT_KEYWORDS = ["STOP_LOSS_TRIGGERED", "TAKE_PROFIT_TRIGGERED"]
CRITICAL_DRAWDOWN_KEYWORDS = ["CRITICAL_DRAWDOWN"]
# --- End Configuration ---

def log_event(message, log_file):
    timestamp = datetime.datetime.now().isoformat()
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

try:
    response = requests.get(URL)
    response.raise_for_status()  # Raise an exception for bad status codes
    content = response.text

    log_event(content, MONITORING_LOG)

    # --- Critical Alerts Detection ---
    critical_found = False
    for keyword in STOP_LOSS_TAKE_PROFIT_KEYWORDS + CRITICAL_DRAWDOWN_KEYWORDS:
        if keyword in content:
            log_event(f"CRITICAL EVENT DETECTED: {keyword} - {content}", CRITICAL_ALERTS_LOG)
            critical_found = True
            break

    if not critical_found:
        pass

except requests.exceptions.RequestException as e:
    log_event(f"Error fetching data from {URL}: {e}", MONITORING_LOG)
    log_event(f"Error fetching data from {URL}: {e}", CRITICAL_ALERTS_LOG)

except Exception as e:
    log_event(f"An unexpected error occurred: {e}", MONITORING_LOG)
    log_event(f"An unexpected error occurred: {e}", CRITICAL_ALERTS_LOG)
