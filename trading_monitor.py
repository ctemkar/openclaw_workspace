
import requests
import json
from datetime import datetime

TRADING_DASHBOARD_URL = "http://localhost:5001/"
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def log_to_file(filepath, message):
    with open(filepath, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

def analyze_trading_data():
    critical_alerts = []
    general_logs = []

    try:
        response = requests.get(TRADING_DASHBOARD_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        general_logs.append(f"Successfully fetched data from {TRADING_DASHBOARD_URL}")

        # Process general logs and status updates
        if "logs" in data:
            for log in data["logs"]:
                general_logs.append(f"Log: {log}")
        if "status" in data:
            general_logs.append(f"Status: {data['status']}")
        if "risk_parameters" in data:
            general_logs.append(f"Risk Parameters: {json.dumps(data['risk_parameters'])}")

        # Detect and log stop-loss/take-profit orders
        if "orders" in data:
            for order in data["orders"]:
                if order.get("type") in ["STOP_LOSS", "TAKE_PROFIT"]:
                    alert_message = f"Order Alert: {order.get("type")} detected for symbol {order.get("symbol")} at price {order.get("price")}"
                    critical_alerts.append(alert_message)
                    log_to_file(CRITICAL_ALERTS_FILE, alert_message)
                else:
                    general_logs.append(f"Order: {json.dumps(order)}")

        # Detect critical drawdown
        if "drawdown" in data:
            drawdown = data["drawdown"]
            if drawdown > 0.1:  # Example: 10% drawdown is critical
                alert_message = f"Critical Drawdown Alert: Drawdown is {drawdown*100:.2f}%"
                critical_alerts.append(alert_message)
                log_to_file(CRITICAL_ALERTS_FILE, alert_message)
            else:
                general_logs.append(f"Drawdown: {drawdown*100:.2f}%")

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {TRADING_DASHBOARD_URL}: {e}"
        general_logs.append(error_message)
        log_to_file(CRITICAL_ALERTS_FILE, error_message)
    except json.JSONDecodeError:
        error_message = f"Error decoding JSON response from {TRADING_DASHBOARD_URL}"
        general_logs.append(error_message)
        log_to_file(CRITICAL_ALERTS_FILE, error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        general_logs.append(error_message)
        log_to_file(CRITICAL_ALERTS_FILE, error_message)

    # Log general data
    for log in general_logs:
        log_to_file(LOG_FILE, log)

    # Generate summary
    summary = "Trading Dashboard Analysis Summary:\n"
    summary += f"Timestamp: {datetime.now().isoformat()}\n"
    if critical_alerts:
        summary += "\nCRITICAL ALERTS:<bos>\n"
        for alert in critical_alerts:
            summary += f"- {alert}\n"
    else:
        summary += "\nNo critical alerts detected.\n"

    summary += "\nGeneral Log Entries:\n"
    if general_logs:
        # Limit general logs in summary to avoid excessive output
        for log in general_logs[:5]: # Show first 5 general logs in summary
            summary += f"- {log}\n"
        if len(general_logs) > 5:
            summary += f"... and {len(general_logs) - 5} more general log entries.\n"
    else:
        summary += "No general log entries found.\n"

    return summary

if __name__ == "__main__":
    analysis_summary = analyze_trading_data()
    print(analysis_summary) # This will be the output of the script

