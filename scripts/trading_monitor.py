
import requests
import json
import logging

# --- Configuration ---
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"
CRITICAL_DRAWDOWN_THRESHOLD = 0.05  # 5% drawdown

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler() # Also log to console for visibility
    ]
)

def fetch_trading_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {url}")
        return None

def parse_and_log_data(data):
    if not data:
        logging.warning("No data received to parse.")
        return

    # Sample parsing logic - adjust based on actual data structure
    trading_logs = data.get("logs", [])
    status_updates = data.get("status", {})
    risk_parameters = data.get("risk", {})

    logging.info("--- Trading Logs ---")
    for log in trading_logs:
        logging.info(log)

    logging.info("--- Status Updates ---")
    logging.info(json.dumps(status_updates, indent=2))

    logging.info("--- Risk Parameters ---")
    logging.info(json.dumps(risk_parameters, indent=2))

    return status_updates, risk_parameters

def check_alerts(status_updates, risk_parameters):
    alerts = []
    if not status_updates or not risk_parameters:
        logging.warning("Insufficient data for alert checking.")
        return alerts

    # Check for triggered stop-loss or take-profit
    if status_updates.get("stop_loss_triggered"):
        alerts.append("ALERT: Stop-loss triggered!")
    if status_updates.get("take_profit_triggered"):
        alerts.append("ALERT: Take-profit triggered!")

    # Check for critical drawdown
    current_capital = risk_parameters.get("capital", 0)
    initial_capital = risk_parameters.get("initial_capital", current_capital) # Assume initial_capital is same as current if not present
    if initial_capital > 0:
        drawdown = (initial_capital - current_capital) / initial_capital
        if drawdown > CRITICAL_DRAWDOWN_THRESHOLD:
            alerts.append(f"CRITICAL ALERT: Drawdown ({drawdown:.2%}) exceeds threshold ({CRITICAL_DRAWDOWN_THRESHOLD:.2%})!")
    else:
        logging.warning("Initial capital not available or zero, cannot check drawdown.")


    return alerts

def log_critical_alerts(alerts):
    if not alerts:
        logging.info("No critical alerts to log.")
        return

    logging.warning("--- Critical Alerts ---")
    with open(CRITICAL_ALERTS_FILE, "a") as f:
        for alert in alerts:
            logging.warning(alert)
            f.write(alert + "\n")
    logging.warning("---------------------")


if __name__ == "__main__":
    logging.info("Starting trading data fetch and monitoring...")
    data = fetch_trading_data(TRADING_DASHBOARD_URL)
    if data:
        status_updates, risk_parameters = parse_and_log_data(data)
        alerts = check_alerts(status_updates, risk_parameters)
        log_critical_alerts(alerts)
    logging.info("Trading data fetch and monitoring complete.")
