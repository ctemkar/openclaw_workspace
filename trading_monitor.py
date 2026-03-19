
import requests
import json
import datetime
import time

# Configuration
TRADING_DASHBOARD_URL = "http://localhost:5001/"
TRADING_MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
CHECK_INTERVAL_SECONDS = 300  # 5 minutes

def log_message(message, log_file):
    with open(log_file, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("[" + timestamp + "] " + message + "\\n")

def fetch_and_parse_data():
    try:
        response = requests.get(TRADING_DASHBOARD_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching data from {TRADING_DASHBOARD_URL}: {e}", TRADING_MONITORING_LOG)
        return None
    except json.JSONDecodeError:
        log_message(f"Error decoding JSON from {TRADING_DASHBOARD_URL}", TRADING_MONITORING_LOG)
        return None

def analyze_and_alert(data):
    if data is None:
        return

    log_message(f"Data fetched: {json.dumps(data)}", TRADING_MONITORING_LOG)

    stop_loss_triggered = False
    take_profit_triggered = False
    critical_drawdown = False

    # Example: Check for stop-loss/take-profit triggers (adapt based on actual data structure)
    if "trades" in data:
        for trade in data["trades"]:
            if trade.get("status") == "stop_loss_triggered":
                stop_loss_triggered = True
                log_message(f"ALERT: Stop-loss triggered for trade ID: {trade.get('id')}", CRITICAL_ALERTS_LOG)
            if trade.get("status") == "take_profit_triggered":
                take_profit_triggered = True
                log_message(f"ALERT: Take-profit triggered for trade ID: {trade.get('id')}", CRITICAL_ALERTS_LOG)

    # Example: Check for drawdown indicators (adapt based on actual data structure)
    if "risk_parameters" in data:
        current_capital = data["risk_parameters"].get("capital")
        initial_capital = data["risk_parameters"].get("initial_capital") # Assuming initial capital is available
        if current_capital is not None and initial_capital is not None:
            drawdown_percentage = ((initial_capital - current_capital) / initial_capital) * 100
            if drawdown_percentage > 10:  # Example: 10% drawdown is critical
                critical_drawdown = True
                log_message(f"ALERT: Critical drawdown detected: {drawdown_percentage:.2f}%", CRITICAL_ALERTS_LOG)

    if stop_loss_triggered or take_profit_triggered or critical_drawdown:
        log_message("Critical alerts logged.", CRITICAL_ALERTS_LOG)

def main():
    while True:
        data = fetch_and_parse_data()
        analyze_and_alert(data)
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
