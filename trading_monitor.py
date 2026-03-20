
import requests
from bs4 import BeautifulSoup
import logging
import os

# Configuration
URL = "http://localhost:5001/"
TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
LOG_TRANSACTION_DATA = True # Set to False if you don't want to log all transactions
ALERT_STOP_LOSS_TAKE_PROFIT = True
ALERT_DRAWDOWN = True

# Setup logging for all extracted data
logging.basicConfig(filename=TRADING_LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Setup logging for critical alerts
critical_logger = logging.getLogger('critical_alerts')
critical_logger.setLevel(logging.CRITICAL)
critical_handler = logging.FileHandler(CRITICAL_ALERTS_FILE)
critical_formatter = logging.Formatter('%(asctime)s - CRITICAL - %(message)s')
critical_handler.setFormatter(critical_formatter)
critical_logger.addHandler(critical_handler)
# Prevent propagation to the root logger if critical_alerts messages should only go to critical_alerts.log
critical_logger.propagate = False


def fetch_trading_data(url):
    """Fetches data from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None

def parse_trading_data(html_content):
    """
    Parses the HTML content to extract trading logs, status updates,
    and risk parameters. This is a placeholder and needs to be
    adapted based on the actual HTML structure of http://localhost:5001/.
    """
    if not html_content:
        return None, None

    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = {
        "trading_logs": [],
        "status_updates": [],
        "risk_parameters": {
            "capital": None,
            "stop_loss": [],
            "take_profit": []
        }
    }

    # --- Placeholder parsing logic ---
    # This section needs to be customized based on the actual HTML content of http://localhost:5001/
    # Example: Assume logs are in a table with class 'trading-log-table'
    log_table = soup.find('table', class_='trading-log-table')
    if log_table:
        for row in log_table.find_all('tr')[1:]: # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 4: # Assuming at least 4 columns: Timestamp, Action, Amount, Details
                log_entry = {
                    "timestamp": cells[0].get_text(strip=True),
                    "action": cells[1].get_text(strip=True),
                    "amount": cells[2].get_text(strip=True),
                    "details": cells[3].get_text(strip=True)
                }
                extracted_data["trading_logs"].append(log_entry)

    # Example: Assume status updates are in divs with class 'status-update'
    status_updates = soup.find_all('div', class_='status-update')
    for update in status_updates:
        extracted_data["status_updates"].append(update.get_text(strip=True))

    # Example: Assume risk parameters are in specific divs/spans
    capital_div = soup.find('div', id='current-capital')
    if capital_div:
        extracted_data["risk_parameters"]["capital"] = capital_div.get_text(strip=True)

    stop_loss_elements = soup.find_all('span', class_='stop-loss-level')
    for sl in stop_loss_elements:
        extracted_data["risk_parameters"]["stop_loss"].append(sl.get_text(strip=True))

    take_profit_elements = soup.find_all('span', class_='take-profit-level')
    for tp in take_profit_elements:
        extracted_data["risk_parameters"]["take_profit"].append(tp.get_text(strip=True))

    # --- End of placeholder parsing logic ---

    return extracted_data

def check_alerts(data):
    """
    Checks for triggered stop-loss, take-profit, or critical drawdown indicators.
    This is a placeholder and needs to be adapted based on how these conditions
    are represented in the fetched data.
    """
    alerts = []
    if not data:
        return alerts

    # Placeholder for stop-loss/take-profit alerts
    if ALERT_STOP_LOSS_TAKE_PROFIT:
        # Example: Check if any active stop-loss or take-profit levels are met
        # This requires knowing the current market price, which is not provided here.
        # For demonstration, let's assume we're looking for specific alert text or values.
        # In a real scenario, you would compare current prices with configured levels.
        for log in data.get("trading_logs", []):
            if "STOP LOSS TRIGGERED" in log.get("details", "").upper():
                alerts.append(f"Stop loss triggered: {log}")
            if "TAKE PROFIT TRIGGERED" in log.get("details", "").upper():
                alerts.append(f"Take profit triggered: {log}")

    # Placeholder for drawdown alerts
    if ALERT_DRAWDOWN:
        # Example: Check for drawdown indicators. This would typically involve
        # calculating current drawdown based on historical performance or
        # looking for specific indicators in the status updates/logs.
        # For demonstration, let's assume a critical drawdown is indicated by a status update.
        for update in data.get("status_updates", []):
            if "CRITICAL DRAWDOWN" in update.upper():
                alerts.append(f"Critical drawdown detected: {update}")

    return alerts

def log_data(data):
    """Logs all extracted data."""
    if not data:
        return

    if LOG_TRANSACTION_DATA:
        if data.get("trading_logs"):
            for log in data["trading_logs"]:
                logging.info(f"Trading Log: {log}")
        if data.get("status_updates"):
            for update in data["status_updates"]:
                logging.info(f"Status Update: {update}")
        if data.get("risk_parameters"):
            logging.info(f"Risk Parameters: {data['risk_parameters']}")

def log_critical_alerts(alerts):
    """Logs critical alerts."""
    if alerts:
        for alert in alerts:
            critical_logger.critical(alert)
        print(f"CRITICAL ALERTS TRIGGERED: {', '.join(alerts)}") # Optional: print to stdout for immediate feedback

def main():
    """Main function to execute the trading monitoring task."""
    html_content = fetch_trading_data(URL)
    if not html_content:
        return

    parsed_data = parse_trading_data(html_content)

    log_data(parsed_data)

    alerts = check_alerts(parsed_data)
    if alerts:
        log_critical_alerts(alerts)

if __name__ == "__main__":
    main()
