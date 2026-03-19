
import requests
import re

TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/"

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

def parse_and_log(data):
    with open(TRADING_LOG_FILE, "a") as f_trading, open(CRITICAL_ALERT_LOG_FILE, "a") as f_critical:
        f_trading.write(data + "\n")

        # Detect stop-loss/take-profit orders
        stop_loss_pattern = re.compile(r"STOP LOSS TRIGGERED|TAKE PROFIT ACHIEVED", re.IGNORECASE)
        if stop_loss_pattern.search(data):
            f_critical.write(f"ALERT: Order Triggered - {stop_loss_pattern.search(data).group(0)}\n")

        # Detect critical drawdown
        drawdown_pattern = re.compile(r"CRITICAL DRAWDOWN DETECTED", re.IGNORECASE)
        if drawdown_pattern.search(data):
            f_critical.write(f"ALERT: Critical Drawdown Detected\n")

        # Basic summary for trading log (can be expanded)
        summary = f"Monitored at {get_timestamp()}: Data logged. Critical alerts: {bool(stop_loss_pattern.search(data) or drawdown_pattern.search(data))}"
        print(summary) # This will be the plain text summary

def get_timestamp():
    from datetime import datetime
    return datetime.now().isoformat()

if __name__ == "__main__":
    fetched_data = fetch_data(URL)
    parse_and_log(fetched_data)


