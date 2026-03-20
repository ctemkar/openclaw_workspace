import requests
import json
import datetime

# Configuration
URL = "http://localhost:5001/"
MONITORING_LOG = "./trading_monitoring.log"
CRITICAL_ALERTS_LOG = "./critical_alerts.log"
STOP_LOSS_THRESHOLD = -0.10  # Example: 10% drawdown
TAKE_PROFIT_THRESHOLD = 0.15 # Example: 15% profit
CRITICAL_DRAWDOWN_THRESHOLD = -0.20 # Example: 20% drawdown

def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {url}")
        return None

def analyze_data(data):
    timestamp = datetime.datetime.now().isoformat()
    monitoring_log_entry = f"{timestamp}: Data received.\n"
    critical_alerts = []
    summary = f"Trading Dashboard Analysis - {timestamp}\n\n"

    if data is None:
        monitoring_log_entry += "No data received.\n"
        summary += "Failed to retrieve data from the trading dashboard.\n"
        return monitoring_log_entry, critical_alerts, summary

    # Extracting general data
    trading_logs = data.get("trading_logs", [])
    status_updates = data.get("status_updates", [])
    risk_parameters = data.get("risk_parameters", {})

    monitoring_log_entry += f"Risk Parameters: {json.dumps(risk_parameters)}\n"
    monitoring_log_entry += f"Status Updates: {len(status_updates)} found.\n"
    monitoring_log_entry += f"Trading Logs: {len(trading_logs)} found.\n"

    summary += "Status Updates:\n"
    for update in status_updates:
        summary += f"- {update}\n"
    summary += "\n"

    # Detecting alerts
    for log in trading_logs:
        if 'type' in log and 'amount' in log:
            log_type = log['type']
            amount = log['amount']
            
            if log_type == "stop_loss" and amount <= STOP_LOSS_THRESHOLD:
                alert_msg = f"ALERT: Stop-loss triggered at {amount*100:.2f}% on {timestamp}"
                critical_alerts.append(alert_msg)
                monitoring_log_entry += f"CRITICAL: {alert_msg}\n"
            elif log_type == "take_profit" and amount >= TAKE_PROFIT_THRESHOLD:
                alert_msg = f"ALERT: Take-profit triggered at {amount*100:.2f}% on {timestamp}"
                critical_alerts.append(alert_msg)
                monitoring_log_entry += f"ALERT: {alert_msg}\n"

    # Check for critical drawdown
    current_drawdown = risk_parameters.get("current_drawdown", 0)
    if current_drawdown <= CRITICAL_DRAWDOWN_THRESHOLD:
        alert_msg = f"CRITICAL DRAWDOWN ALERT: Current drawdown is {current_drawdown*100:.2f}% on {timestamp}"
        critical_alerts.append(alert_msg)
        monitoring_log_entry += f"CRITICAL: {alert_msg}\n"

    if critical_alerts:
        summary += "Critical Alerts:\n"
        for alert in critical_alerts:
            summary += f"- {alert}\n"
    else:
        summary += "No critical alerts detected.\n"

    return monitoring_log_entry, critical_alerts, summary

def log_to_file(filepath, content):
    try:
        with open(filepath, "a") as f:
            f.write(content + "\n")
    except IOError as e:
        print(f"Error writing to file {filepath}: {e}")

# --- Main execution ---
if __name__ == "__main__":
    data = fetch_data(URL)
    monitoring_entry, alerts, analysis_summary = analyze_data(data)

    log_to_file(MONITORING_LOG, monitoring_entry)

    if alerts:
        for alert in alerts:
            log_to_file(CRITICAL_ALERTS_LOG, alert)

    print(analysis_summary) # This will be output by exec and can be captured
