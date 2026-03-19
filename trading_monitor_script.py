
import requests
import json
from datetime import datetime

TRADING_URL = "http://localhost:5001/"
MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_trading_data():
    try:
        response = requests.get(TRADING_URL)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def parse_and_log_data(data):
    if not data:
        return

    timestamp = datetime.now().isoformat()
    
    # Log all extracted data
    log_entry = {"timestamp": timestamp, "data": data}
    with open(MONITORING_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Check for alerts
    alerts = []
    if "risk_parameters" in data:
        risk_params = data["risk_parameters"]
        if "stop_loss_triggered" in risk_params and risk_params["stop_loss_triggered"]:
            alerts.append(f"Stop loss triggered at {timestamp}")
        if "take_profit_triggered" in risk_params and risk_params["take_profit_triggered"]:
            alerts.append(f"Take profit triggered at {timestamp}")
        if "drawdown_critical" in risk_params and risk_params["drawdown_critical"]:
            alerts.append(f"Critical drawdown indicators at {timestamp}")

    if alerts:
        with open(CRITICAL_ALERTS_LOG, "a") as f:
            for alert in alerts:
                f.write(f"{alert}\n")
        print("Critical alerts triggered. See log file.")

def main():
    trading_data = fetch_trading_data()
    parse_and_log_data(trading_data)

if __name__ == "__main__":
    main()
