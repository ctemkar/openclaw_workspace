# trading_monitor.py
import requests
import datetime
import logging

# --- Configuration ---
TRADING_DASHBOARD_URL = "http://localhost:5001/"
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler() # Also log to console for immediate feedback
    ]
)

def fetch_data(url):
    """Fetches data from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text # Assuming text/html or text/plain for now. Adjust if JSON.
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None

def parse_data(data):
    """Parses the fetched data to extract relevant information."""
    # This is a placeholder. You'll need to adapt this based on the actual
    # content of http://localhost:5001/ (e.g., HTML parsing, JSON parsing).
    # For now, we'll just look for keywords.
    
    trading_logs = []
    status_updates = []
    risk_parameters = {}
    critical_alerts = []

    if data:
        lines = data.splitlines()
        for line in lines:
            log_entry = line.strip()
            if log_entry:
                # Example parsing: adapt these conditions
                if "STOP-LOSS TRIGGERED" in log_entry.upper():
                    critical_alerts.append(f"STOP-LOSS TRIGGERED: {log_entry}")
                elif "TAKE-PROFIT TRIGGERED" in log_entry.upper():
                    critical_alerts.append(f"TAKE-PROFIT TRIGGERED: {log_entry}")
                elif "CRITICAL DRAWDOWN" in log_entry.upper():
                    critical_alerts.append(f"CRITICAL DRAWDOWN: {log_entry}")
                elif "TRADE:" in log_entry.upper():
                    trading_logs.append(log_entry)
                elif "STATUS:" in log_entry.upper():
                    status_updates.append(log_entry)
                # Example for risk parameters (very basic)
                if "RISK_LEVEL=" in log_entry:
                    parts = log_entry.split("RISK_LEVEL=")
                    if len(parts) > 1:
                        risk_parameters['risk_level'] = parts[1].split(';')[0].strip()
                if "PARAM_A=" in log_entry:
                    parts = log_entry.split("PARAM_A=")
                    if len(parts) > 1:
                        risk_parameters['param_a'] = parts[1].split(';')[0].strip()
    
    return {
        "trading_logs": trading_logs,
        "status_updates": status_updates,
        "risk_parameters": risk_parameters,
        "critical_alerts": critical_alerts
    }

def log_critical_alerts(alerts):
    """Logs critical alerts to a separate file."""
    if not alerts:
        return

    alert_logger = logging.getLogger('alert_logger')
    if not alert_logger.handlers:
        alert_handler = logging.FileHandler(ALERT_LOG_FILE)
        alert_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        alert_logger.addHandler(alert_handler)
        alert_logger.setLevel(logging.WARNING)

    for alert in alerts:
        alert_logger.warning(alert)
    logging.warning(f"Logged {len(alerts)} critical alerts to {ALERT_LOG_FILE}")

def generate_summary(parsed_data):
    """Generates a plain text summary."""
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    summary = f"Trading Dashboard Analysis Summary - {current_time}\n"
    summary += "===============================================\n\n"

    if not parsed_data:
        summary += "Failed to fetch or parse data.\n"
        return summary

    # Trading Logs Summary
    if parsed_data["trading_logs"]:
        summary += f"Trading Logs ({len(parsed_data['trading_logs'])} entries):\n"
        for i, log in enumerate(parsed_data["trading_logs"][:3]): # Show first 3 as example
            summary += f"- {log}\n"
        if len(parsed_data["trading_logs"]) > 3:
            summary += f"... and {len(parsed_data['trading_logs']) - 3} more.\n"
        summary += "\n"
    else:
        summary += "No trading logs found.\n\n"
        
    # Status Updates Summary
    if parsed_data["status_updates"]:
        summary += f"Status Updates ({len(parsed_data['status_updates'])} entries):\n"
        for i, status in enumerate(parsed_data["status_updates"][:3]): # Show first 3 as example
            summary += f"- {status}\n"
        if len(parsed_data["status_updates"]) > 3:
            summary += f"... and {len(parsed_data['status_updates']) - 3} more.\n"
        summary += "\n"
    else:
        summary += "No status updates found.\n\n"
        
    # Risk Parameters Summary
    if parsed_data["risk_parameters"]:
        summary += "Risk Parameters:\n"
        for key, value in parsed_data["risk_parameters"].items():
            summary += f"- {key.upper()}: {value}\n"
        summary += "\n"
    else:
        summary += "No risk parameters found.\n\n"

    # Critical Alerts Summary
    if parsed_data["critical_alerts"]:
        summary += f"CRITICAL ALERTS DETECTED ({len(parsed_data['critical_alerts'])}):\n"
        for alert in parsed_data["critical_alerts"]:
            summary += f"- {alert}\n"
        summary += f"\nCritical alerts have been logged to: {ALERT_LOG_FILE}\n"
    else:
        summary += "No critical alerts detected.\n"

    return summary

def main():
    """Main execution function."""
    logging.info("Starting trading dashboard monitor run.")
    page_data = fetch_data(TRADING_DASHBOARD_URL)
    parsed_data = parse_data(page_data)
    
    if parsed_data["critical_alerts"]:
        log_critical_alerts(parsed_data["critical_alerts"])
        
    summary = generate_summary(parsed_data)
    
    # Log the final summary to the main log file as well
    logging.info("----- ANALYSIS SUMMARY -----")
    logging.info(summary)
    logging.info("Trading dashboard monitor run finished.")

    # The summary is printed to stdout, which will be captured by the cron job's output
    print(summary)

if __name__ == "__main__":
    main()

