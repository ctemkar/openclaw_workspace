import requests
import json
from datetime import datetime

URL = "http://localhost:5001/"
TRADING_LOG_PATH = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_PATH = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Define thresholds (these are example values and might need adjustment)
CRITICAL_DRAWDOWN_THRESHOLD = 0.10  # 10%
# Note: Detecting if stop-loss/take-profit are *triggered* would require specific
# data in the API response (e.g., a 'status' field on orders).
# For now, we'll just log the presence of such orders as a potential alert.
STOP_LOSS_ORDER_PRESENT = False 
TAKE_PROFIT_ORDER_PRESENT = False

def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the trading dashboard."}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from the trading dashboard."}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

def log_data(data, log_path):
    try:
        with open(log_path, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"--- Log entry at: {timestamp} ---\n")
            json.dump(data, f, indent=2)
            f.write("\n\n")
    except IOError as e:
        print(f"Error writing to log file {log_path}: {e}")

def log_alert(alert_message, log_path):
    try:
        with open(log_path, "a") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"ALERT at {timestamp}: {alert_message}\n")
    except IOError as e:
        print(f"Error writing to alert log file {log_path}: {e}")

def analyze_and_summarize(data):
    summary_lines = []
    alert_messages = []

    if "error" in data:
        alert_messages.append(f"Monitoring failed: {data['error']}")
        summary_lines.append(f"Monitoring failed: {data['error']}")
        return "\n".join(summary_lines), "\n".join(alert_messages)

    # Log all fetched data to the general monitoring log
    log_data(data, TRADING_LOG_PATH)

    # Extract and check for critical drawdown
    current_drawdown = data.get("current_drawdown", 0)
    if current_drawdown > CRITICAL_DRAWDOWN_THRESHOLD:
        alert_msg = f"CRITICAL DRAWDOWN DETECTED: {current_drawdown*100:.2f}% (Threshold: {CRITICAL_DRAWDOWN_THRESHOLD*100:.2f}%)"
        alert_messages.append(alert_msg)
        summary_lines.append(alert_msg)

    # Check for presence of stop-loss/take-profit orders
    open_orders = data.get("open_orders", [])
    has_stop_loss = any(order.get("type") == "stop-loss" for order in open_orders)
    has_take_profit = any(order.get("type") == "take-profit" for order in open_orders)

    if has_stop_loss:
        alert_msg = "Stop-loss order is active."
        alert_messages.append(alert_msg)
        summary_lines.append(alert_msg)
        
    if has_take_profit:
        alert_msg = "Take-profit order is active."
        alert_messages.append(alert_msg)
        summary_lines.append(alert_msg)

    # Log any identified alerts to the critical alerts log
    for alert in alert_messages:
        log_alert(alert, CRITICAL_ALERTS_PATH)

    # Construct the plain text summary
    summary_lines.append(f"Trading Dashboard Monitored at {datetime.now().isoformat()}")
    summary_lines.append(f"Trading Logs Processed: {len(data.get('trading_logs', []))}")
    summary_lines.append(f"Status Updates Found: {len(data.get('status_updates', []))}")
    
    risk_params = data.get("risk_parameters")
    if risk_params:
        summary_lines.append(f"Current Risk Parameters: {risk_params}")

    if not alert_messages:
        summary_lines.append("No critical alerts detected.")

    return "\n".join(summary_lines)

if __name__ == "__main__":
    print("Starting trading dashboard monitoring script...")
    dashboard_data = fetch_data(URL)
    report_summary = analyze_and_summarize(dashboard_data)
    print("Monitoring complete. Summary generated.")
    # The summary is *returned* here, which is what the 'agentTurn' task should capture.
    # The cron tool, when configured with announce delivery, will automatically send this summary.
    # We explicitly print it for potential direct execution/debugging visibility.
    print("\n--- Summary ---")
    print(report_summary)
    print("---------------")
