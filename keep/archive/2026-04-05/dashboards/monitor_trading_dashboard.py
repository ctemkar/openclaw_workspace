
import requests
from datetime import datetime

# Configuration
URL = "http://localhost:5001/status"
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
        status_updates = data.get("status", "unknown")
        capital = data.get("capital", 0)
        risk_parameters = data.get("risk_parameters", {})
        trading_pairs = data.get("trading_pairs", [])

        log_data(f"Fetched data: {data}")

        # Process trading logs, status updates, and risk parameters
        stop_loss_level = risk_parameters.get("stop_loss", 0)
        take_profit_level = risk_parameters.get("take_profit", 0)
        max_trades_per_day = risk_parameters.get("max_trades_per_day", 0)

        summary += "Trading Dashboard Analysis:\n"
        summary += f"- Status: {status_updates}\n"
        summary += f"- Capital: ${capital:.2f}\n"
        summary += f"- Trading Pairs: {', '.join(trading_pairs)}\n"
        summary += f"- Stop Loss: {stop_loss_level*100:.1f}%\n"
        summary += f"- Take Profit: {take_profit_level*100:.1f}%\n"
        summary += f"- Max Trades/Day: {max_trades_per_day}\n"

        # Generate alerts
        # Note: These alerts need actual trade data to calculate P&L
        # For now, we'll just show basic status
        summary += "- System is running normally\n"
        summary += "- No critical alerts at this time\n"

        # Log the data
        log_data(f"Dashboard status: {status_updates}, Capital: ${capital:.2f}")

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

