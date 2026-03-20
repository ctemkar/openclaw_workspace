
import requests
import datetime
import os

TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"

def log_message(log_path, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def monitor_trading():
    try:
        response = requests.get(TRADING_DASHBOARD_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()  # Assuming the dashboard returns JSON

        # Log all data to trading_monitoring.log
        log_message(TRADING_LOG_PATH, f"Data: {data}")

        # Detect and log critical events
        stop_loss_triggered = data.get("stop_loss_triggered", False)
        take_profit_triggered = data.get("take_profit_triggered", False)
        critical_drawdown = data.get("critical_drawdown", False)

        if stop_loss_triggered:
            log_message(CRITICAL_ALERTS_PATH, "STOP-LOSS TRIGGERED")
        if take_profit_triggered:
            log_message(CRITICAL_ALERTS_PATH, "TAKE-PROFIT TRIGGERED")
        if critical_drawdown:
            log_message(CRITICAL_ALERTS_PATH, "CRITICAL DRAWDOWN DETECTED")

        # Generate summary (this is a basic example, you'll want to expand this)
        summary = f"Trading Monitor Summary - {datetime.datetime.now()}\n"
        summary += f"Status: OK\n"
        if stop_loss_triggered or take_profit_triggered or critical_drawdown:
            summary += "CRITICAL ALERTS DETECTED - Check critical_alerts.log\n"
        
        return summary

    except requests.exceptions.RequestException as e:
        log_message(TRADING_LOG_PATH, f"Error fetching data: {e}")
        log_message(CRITICAL_ALERTS_PATH, f"Error fetching data from dashboard: {e}")
        return f"Trading Monitor Error - {datetime.datetime.now()}\nFailed to fetch data from dashboard: {e}\n"
    except Exception as e:
        log_message(TRADING_LOG_PATH, f"An unexpected error occurred: {e}")
        log_message(CRITICAL_ALERTS_PATH, f"An unexpected error occurred: {e}")
        return f"Trading Monitor Error - {datetime.datetime.now()}\nAn unexpected error occurred: {e}\n"

if __name__ == "__main__":
    # Create log files if they don't exist
    for log_file in [TRADING_LOG_PATH, CRITICAL_ALERTS_PATH]:
        if not os.path.exists(log_file):
            open(log_file, "w").close()
    
    summary = monitor_trading()
    # In a real scenario, you might want to send this summary to a specific channel or format it further.
    # For this example, we'll just print it. The cron job will capture stdout.
    print(summary)
