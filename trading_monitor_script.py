
import requests
import logging
from datetime import datetime
import json

# Configuration
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_trading_data(url):
    """Fetches data from the trading dashboard URL."""
    try:
        # Use requests for simplicity within the script.
        # If this script is run by an agent with access to tools,
        # you would ideally pass the content from a tool call.
        response = requests.get(url)
        response.raise_for_status()
        # Try to parse as JSON first, then fall back to text if it fails.
        try:
            return response.json() # Return parsed JSON if possible
        except json.JSONDecodeError:
            return response.text # Return raw text if not JSON
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return None

def parse_trading_data(data):
    """
    Parses the fetched data (JSON or text) to extract trading logs,
    status updates, and risk parameters. This function needs to be adapted
    based on the actual data format returned by the URL.
    """
    if data is None:
        return None

    extracted_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "logs": [],
        "status_updates": [],
        "risk_parameters": {
            "capital": None,
            "stop_loss_triggered": False,
            "take_profit_triggered": False,
            "drawdown_critical": False
        }
    }

    # --- Parsing Logic ---
    # This logic is highly dependent on the data format.
    # Assume JSON first, then fallback to text parsing if needed.

    if isinstance(data, dict):
        # Assuming JSON data structure
        extracted_data["logs"] = data.get("logs", [])
        extracted_data["status_updates"] = data.get("status_updates", [])
        risk_params = data.get("risk_parameters", {})
        extracted_data["risk_parameters"]["capital"] = risk_params.get("capital")
        extracted_data["risk_parameters"]["stop_loss_triggered"] = risk_params.get("stop_loss_triggered", False)
        extracted_data["risk_parameters"]["take_profit_triggered"] = risk_params.get("take_profit_triggered", False)
        extracted_data["risk_parameters"]["drawdown_critical"] = risk_params.get("drawdown_critical", False)

    elif isinstance(data, str):
        # Fallback for plain text - needs specific parsing rules.
        # This is a very basic example, expecting specific keywords.
        lines = data.splitlines()
        for line in lines:
            line_lower = line.lower()
            if "log:" in line_lower:
                extracted_data["logs"].append(line.replace("log:", "").strip())
            elif "status:" in line_lower:
                extracted_data["status_updates"].append(line.replace("status:", "").strip())
            elif "capital:" in line_lower:
                try:
                    extracted_data["risk_parameters"]["capital"] = float(line.split("capital:")[1].strip().replace("$", "").replace(",", ""))
                except ValueError:
                    pass
            elif "stop loss triggered" in line_lower:
                extracted_data["risk_parameters"]["stop_loss_triggered"] = True
            elif "take profit triggered" in line_lower:
                extracted_data["risk_parameters"]["take_profit_triggered"] = True
            elif "drawdown critical" in line_lower:
                extracted_data["risk_parameters"]["drawdown_critical"] = True
    else:
        logging.error(f"Unexpected data format received: {type(data)}")
        return None
    # --- End Parsing Logic ---

    return extracted_data

def analyze_and_alert(data):
    """Analyzes extracted data for alerts and writes critical data."""
    critical_alerts_found = False
    alert_messages = []

    if not data:
        return False, []

    # Check for triggered stop-loss or take-profit
    if data["risk_parameters"].get("stop_loss_triggered", False):
        alert_messages.append(f"ALERT: Stop-loss triggered.")
        critical_alerts_found = True
    if data["risk_parameters"].get("take_profit_triggered", False):
        alert_messages.append(f"ALERT: Take-profit triggered.")
        critical_alerts_found = True

    # Check for critical drawdown indicators
    if data["risk_parameters"].get("drawdown_critical", False):
        alert_messages.append(f"ALERT: Critical drawdown indicators detected.")
        critical_alerts_found = True

    if critical_alerts_found:
        logging.warning("CRITICAL ALERTS DETECTED")
        try:
            with open(CRITICAL_ALERTS_FILE, 'a') as f:
                f.write(f"{datetime.utcnow().isoformat()} - Alerts: {'; '.join(alert_messages)}
")
            logging.info(f"Critical alerts logged to {CRITICAL_ALERTS_FILE}")
        except IOError as e:
            logging.error(f"Failed to write to critical alerts log {CRITICAL_ALERTS_FILE}: {e}")
    else:
        logging.info("No critical alerts detected.")

    return critical_alerts_found, alert_messages

def main():
    """Main function to fetch, parse, log, and alert."""
    logging.info("Starting trading monitoring task.")
    trading_data = fetch_trading_data(TRADING_DASHBOARD_URL)

    if trading_data is None:
        logging.error("Aborting task due to failed data fetch.")
        return

    extracted_data = parse_trading_data(trading_data)

    if extracted_data:
        # Log all extracted data
        log_entry = f"Timestamp: {extracted_data['timestamp']}
"
        log_entry += "Logs:
" + "\n".join(extracted_data.get('logs', [])) + "\n"
        log_entry += "Status Updates:\n" + "\n".join(extracted_data.get('status_updates', [])) + "\n"
        log_entry += "Risk Parameters:\n"
        for key, value in extracted_data.get('risk_parameters', {}).items():
            log_entry += f"  {key}: {value}\n"

        try:
            # Append to the log file
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry + "---\n")
            logging.info(f"Trading data logged to {LOG_FILE}")
        except IOError as e:
            logging.error(f"Failed to write to log file {LOG_FILE}: {e}")

        # Analyze and alert
        critical_found, alerts = analyze_and_alert(extracted_data)
        if critical_found:
            logging.warning("Critical alerts were triggered.")
    else:
        logging.warning("No data was extracted or data format is unrecognized.")

    logging.info("Trading monitoring task finished.")

if __name__ == "__main__":
    main()
