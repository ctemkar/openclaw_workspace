
import requests
import logging
from datetime import datetime

# Configuration
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DASHBOARD_URL = "http://localhost:5001/"
ALERT_THRESHOLD_DRAWDOWN = -0.10  # Example: -10% drawdown is critical

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
critical_logger = logging.getLogger("CriticalAlerts")
critical_logger.setLevel(logging.CRITICAL)
critical_handler = logging.FileHandler(CRITICAL_ALERTS_FILE)
critical_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
critical_logger.addHandler(critical_handler)

def fetch_dashboard_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json() # Assuming the dashboard returns JSON
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return None

def parse_trading_data(data):
    if not data:
        return None, None # No data to parse

    # --- Placeholder Parsing Logic ---
    # This is where you would implement actual parsing based on the dashboard's JSON structure.
    # Example structure assumed:
    # {
    #   "status_updates": "...",
    #   "risk_parameters": {
    #     "capital": 10000.0,
    #     "stop_loss": 0.95, # e.g., 5% stop loss
    #     "take_profit": 1.10 # e.g., 10% take profit
    #   },
    #   "performance": {
    #     "drawdown": -0.05, # e.g., 5% drawdown
    #     "profit": 0.02 # e.g., 2% profit
    #   },
    #   "open_trades": [...]
    # }

    status_updates = data.get("status_updates", "No status updates available.")
    risk_parameters = data.get("risk_parameters", {})
    performance = data.get("performance", {})

    logging.info("Successfully parsed trading data.")
    return {
        "status_updates": status_updates,
        "risk_parameters": risk_parameters,
        "performance": performance
    }, data # Return raw data for potential use in alerts

def analyze_for_alerts(parsed_data, raw_data):
    alerts = []
    critical_data_for_log = {}

    if not parsed_data:
        return alerts, {}

    risk = parsed_data.get("risk_parameters", {})
    perf = parsed_data.get("performance", {})

    # Check for triggered stop-loss/take-profit (simplified example)
    # This would typically involve comparing current trade P/L against stop/take profit levels.
    # For this example, we can just log the parameters if they exist.
    if risk.get("stop_loss"):
        logging.info(f"Stop loss parameter set: {risk['stop_loss']}")
    if risk.get("take_profit"):
        logging.info(f"Take profit parameter set: {risk['take_profit']}")

    # Check for critical drawdown
    current_drawdown = perf.get("drawdown")
    if current_drawdown is not None and current_drawdown < ALERT_THRESHOLD_DRAWDOWN:
        alert_msg = f"CRITICAL DOWNDRAW: Current drawdown is {current_drawdown:.2%}, which is below the threshold of {ALERT_THRESHOLD_DRAWDOWN:.2%}"
        alerts.append(alert_msg)
        critical_data_for_log["drawdown"] = current_drawdown
        logging.critical(alert_msg) # Add to critical log as well

    # Add other alert conditions here based on your specific needs.
    # For example, checking open trade P/L against stop_loss/take_profit.

    # Collect critical data for saving
    if critical_data_for_log:
        critical_data_for_log["timestamp"] = datetime.utcnow().isoformat()
        # You might want to add relevant parts of raw_data here too
        if "open_trades" in raw_data:
            critical_data_for_log["open_trades_snapshot"] = raw_data["open_trades"]


    return alerts, critical_data_for_log

def main():
    logging.info("Starting trading dashboard monitor job.")
    data = fetch_dashboard_data(DASHBOARD_URL)

    if data:
        parsed_data, raw_data = parse_trading_data(data)
        if parsed_data:
            alerts, critical_data = analyze_for_alerts(parsed_data, raw_data)

            if critical_data:
                critical_logger.critical(f"CRITICAL DATA SAVED: {critical_data}")

            if alerts:
                logging.warning(f"Alerts triggered: {alerts}")
            else:
                logging.info("No critical alerts triggered.")
        else:
            logging.error("Failed to parse dashboard data.")
    else:
        logging.error("Failed to fetch data from dashboard.")

    logging.info("Trading dashboard monitor job finished.")

if __name__ == "__main__":
    main()
