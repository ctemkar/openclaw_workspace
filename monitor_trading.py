import requests
import json
from datetime import datetime

TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
MONITOR_URL = "http://localhost:5001/"

def fetch_trading_data():
    try:
        response = requests.get(MONITOR_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {MONITOR_URL}: {e}")
        return None

def log_data(data):
    timestamp = datetime.now().isoformat()
    log_entry = f"--- [{timestamp}] ---
{json.dumps(data, indent=2)}
"
    with open(TRADING_LOG_FILE, "a") as f:
        f.write(log_entry)

def log_alert(message):
    timestamp = datetime.now().isoformat()
    alert_entry = f"ALERT [{timestamp}]: {message}\n"
    with open(ALERT_LOG_FILE, "a") as f:
        f.write(alert_entry)
    return alert_entry # Return for summary

def analyze_data(data):
    alerts = []
    if not data:
        return alerts

    # Assuming 'data' is a dictionary with keys like 'logs', 'status', 'risk_parameters'
    # And that 'risk_parameters' contains 'stop_loss', 'take_profit', 'drawdown'
    
    # Example analysis logic (replace with actual logic based on data structure)
    risk_params = data.get('risk_parameters', {})
    current_drawdown = risk_params.get('current_drawdown', 0)
    stop_loss_level = risk_params.get('stop_loss_level', -float('inf'))
    take_profit_level = risk_params.get('take_profit_level', float('inf'))
    
    if current_drawdown <= stop_loss_level: # Assuming lower drawdown is worse
        alerts.append(f"Stop-loss triggered! Current drawdown: {current_drawdown}")
    if current_drawdown >= take_profit_level: # Assuming higher drawdown is good for take-profit
        alerts.append(f"Take-profit triggered! Current drawdown: {current_drawdown}")
    if current_drawdown < -0.10: # Example: Critical drawdown if more than 10% loss
        alerts.append(f"Critical drawdown detected! Current drawdown: {current_drawdown}")
        
    # Check for specific log messages indicating order execution
    logs = data.get('logs', [])
    for entry in logs:
        if "STOP_LOSS_EXECUTED" in entry:
            alerts.append(f"Stop-loss order explicitly logged: {entry}")
        if "TAKE_PROFIT_EXECUTED" in entry:
            alerts.append(f"Take-profit order explicitly logged: {entry}")
            
    return alerts

def generate_summary(fetched_data, triggered_alerts):
    summary = "Trading Monitoring Summary:\n"
    timestamp = datetime.now().isoformat()
    summary += f"Analysis ran at: {timestamp}\n\n"

    if fetched_data:
        summary += "Latest Status:\n"
        # Add relevant status details from fetched_data
        summary += f"  Current Risk Parameters: {json.dumps(fetched_data.get('risk_parameters', {}), indent=2)}\n"
        summary += f"  Recent Logs Count: {len(fetched_data.get('logs', []))}\n"
    else:
        summary += "Failed to fetch trading data.\n"

    if triggered_alerts:
        summary += "\nCritical Alerts:\n"
        for alert in triggered_alerts:
            summary += f"- {alert}\n"
    else:
        summary += "\nNo critical alerts detected.\n"

    return summary

if __name__ == "__main__":
    trading_data = fetch_trading_data()
    log_data(trading_data) # Log all data regardless of alerts

    critical_alerts_messages = []
    if trading_data:
        alerts = analyze_data(trading_data)
        for alert_msg in alerts:
            critical_alerts_messages.append(log_alert(alert_msg))

    # Extract just the message part for summary, ensuring it's not an empty string
    cleaned_alerts_for_summary = [msg.split("ALERT [")[1].split("]: ")[1] for msg in critical_alerts_messages if "ALERT [" in msg and "]: " in msg]
    summary_text = generate_summary(trading_data, cleaned_alerts_for_summary)
    print(summary_text)

