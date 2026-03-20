
import requests
from datetime import datetime

# Configuration
URL = "http://localhost:5001/"
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def log_data(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

def log_critical_alert(message):
    with open(CRITICAL_ALERTS_FILE, "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

def analyze_trading_data():
    summary = ""
    critical_alerts = []
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json() # Assuming the dashboard returns JSON data

        # Extracting data (customize based on actual JSON structure)
        trading_logs = data.get("logs", [])
        status_updates = data.get("status", [])
        risk_parameters = data.get("risk", {})

        log_data(f"Fetched data: {data}")

        # Process trading logs, status updates, and risk parameters
        capital = risk_parameters.get("capital")
        stop_loss_level = risk_parameters.get("stop_loss")
        take_profit_level = risk_parameters.get("take_profit")
        current_drawdown = risk_parameters.get("drawdown") # Assuming drawdown is present

        summary += "Trading Dashboard Analysis:\n"
        summary += f"- Status: {status_updates}\n"
        summary += f"- Capital: {capital}\n"
        summary += f"- Stop Loss: {stop_loss_level}\n"
        summary += f"- Take Profit: {take_profit_level}\n"

        # Generate alerts
        if stop_loss_level is not None and capital is not None and capital <= stop_loss_level:
            alert_msg = "CRITICAL ALERT: Stop-loss triggered!"
            critical_alerts.append(alert_msg)
            log_critical_alert(alert_msg)
            summary += f"- {alert_msg}\n"

        if take_profit_level is not None and capital is not None and capital >= take_profit_level:
            alert_msg = "ALERT: Take-profit level reached."
            # Decide if this is critical; for now, just logging and summarizing
            summary += f"- {alert_msg}\n"

        if current_drawdown is not None and current_drawdown > 0.1: # Example: 10% drawdown threshold
            alert_msg = f"CRITICAL ALERT: Significant drawdown detected ({current_drawdown*100}%).\n"
            critical_alerts.append(alert_msg)
            log_critical_alert(alert_msg)
            summary += f"- {alert_msg}\n"

        # Log all extracted data (as a simplified representation)
        for log in trading_logs:
            log_data(f"Log Entry: {log}")

    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching data from {URL}: {e}"
        log_data(error_msg)
        summary += f"Error: Could not connect to trading dashboard.\n"
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        log_data(error_msg)
        summary += f"An unexpected error occurred during analysis.\n"

    return summary

if __name__ == "__main__":
    analysis_summary = analyze_trading_data()
    print(analysis_summary)

