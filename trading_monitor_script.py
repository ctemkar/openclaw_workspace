
import requests
import logging
from datetime import datetime

TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"

logging.basicConfig(filename=TRADING_LOG_PATH, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
critical_logger = logging.getLogger('critical_alerts')
critical_logger.setLevel(logging.WARNING)
critical_handler = logging.FileHandler(CRITICAL_ALERT_LOG_PATH)
critical_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_logger.addHandler(critical_handler)


def fetch_trading_data():
    try:
        response = requests.get(TRADING_DASHBOARD_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()  # Assuming the dashboard returns JSON
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from {TRADING_DASHBOARD_URL}: {e}")
        return None

def analyze_data(data):
    if not data:
        return

    # Log all extracted data
    logging.info(f"Trading data: {data}")

    # Parse risk parameters and check for alerts
    capital = data.get("capital")
    stop_loss = data.get("stop_loss")
    take_profit = data.get("take_profit")
    drawdown_indicators = data.get("drawdown_indicators")

    alerts = []
    if stop_loss and stop_loss.get("triggered", False):
        alerts.append(f"Stop-loss triggered: {stop_loss.get('details', 'N/A')}")
    if take_profit and take_profit.get("triggered", False):
        alerts.append(f"Take-profit triggered: {take_profit.get('details', 'N/A')}")
    if drawdown_indicators and drawdown_indicators.get("critical", False):
        alerts.append(f"Critical drawdown indicators appeared: {drawdown_indicators.get('details', 'N/A')}")

    if alerts:
        for alert in alerts:
            critical_logger.warning(alert)
    else:
        logging.info("No critical alerts triggered.")

def main():
    data = fetch_trading_data()
    analyze_data(data)

if __name__ == "__main__":
    main()
