
import requests
import time
import os
from datetime import datetime

TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/"

CRITICAL_KEYWORDS = [
    "STOP_LOSS_TRIGGERED",
    "TAKE_PROFIT_TRIGGERED",
    "CRITICAL_DRAWDOWN",
    "MARGIN CALL" # Added MARGIN CALL in upper case for case-insensitivity
]

def log_event(message, log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(log_file), exist_ok=True) # Ensure directory exists
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def check_critical_drawdown(risk_params_content):
    # This function attempts to find drawdown information within the raw content.
    # It's a more robust approach than assuming a parsed dictionary, as the format is unknown.
    lines = risk_params_content.splitlines()
    for line in lines:
        line_upper = line.upper()
        if "DRAWDOWN" in line_upper:
            if "%" in line:
                try:
                    # Find percentage value
                    parts = line.split(':')
                    if len(parts) > 1:
                        value_str = parts[1].strip()
                        # Try to extract the number before the '%' sign
                        num_part = value_str.split('%')[0].strip()
                        percent_val = float(num_part)
                        if percent_val < -10: # 10% drawdown threshold
                            return True, f"Critical Drawdown detected: {line.strip()}"
                except (ValueError, IndexError):
                    # Ignore if parsing fails for this line
                    pass
            # Fallback for numerical values that might represent drawdown directly
            elif any(keyword in line_upper for keyword in ["DRAWDOWN", "EQUITY"]):
                try:
                    # Attempt to extract a number if it's a direct value
                    parts = line.split(':')
                    if len(parts) > 1:
                        value_str = parts[1].strip()
                        if value_str.replace('.', '', 1).isdigit() or (value_str.startswith('-') and value_str[1:].replace('.', '', 1).isdigit()):
                            num_val = float(value_str)
                            if num_val < -0.10: # Interpreting as a ratio if no % sign
                                return True, f"Critical Drawdown detected: {line.strip()}"
                except (ValueError, IndexError):
                    pass
    return False, ""


def monitor():
    try:
        logs = []
        alerts = []
        critical_event_detected = False
        
        response = requests.get(URL, timeout=10) # Added timeout for requests
        response.raise_for_status()
        content = response.text.strip()
        
        logs.append(f"--- Data fetched at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
        logs.append(content)
        
        # --- Alert Detection ---
        content_upper = content.upper()
        for keyword in CRITICAL_KEYWORDS:
            if keyword in content_upper:
                alerts.append(f"Critical keyword found: {keyword}")
                critical_event_detected = True

        # Attempt to detect critical drawdown from the raw content string
        is_critical_drawdown, drawdown_message = check_critical_drawdown(content)
        if is_critical_drawdown:
            alerts.append(drawdown_message)
            critical_event_detected = True

        # Log all fetched data to trading_monitoring.log
        log_event("\n".join(logs), TRADING_LOG_FILE)

        # Log critical alerts
        if critical_event_detected:
            alert_log_message = " | ".join(alerts)
            log_event(alert_log_message, CRITICAL_ALERT_LOG_FILE)
            summary = f"CRITICAL ALERT DETECTED: {alert_log_message}"
        else:
            summary = "Monitoring session completed with no critical alerts detected."

        # Log summary to trading_monitoring.log
        log_event(f"Summary: {summary}\n", TRADING_LOG_FILE)
        
        # Print summary to stdout for potential background process capture
        print(summary) 

    except requests.exceptions.Timeout:
        error_msg = f"Error: Request to {URL} timed out."
        log_event(error_msg, TRADING_LOG_FILE)
        print(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching data from {URL}: {e}"
        log_event(error_msg, TRADING_LOG_FILE)
        print(error_msg)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        log_event(error_msg, TRADING_LOG_FILE)
        print(error_msg)

if __name__ == "__main__":
    print(f"Starting trading monitor. Logging to {TRADING_LOG_FILE} and {CRITICAL_ALERT_LOG_FILE}")
    while True:
        monitor()
        time.sleep(300) # Sleep for 5 minutes (300 seconds)
