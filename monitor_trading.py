
import requests
import time
import datetime
import sys

TRADING_DASHBOARD_URL = "http://localhost:5001/"
LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

# Define stop-loss, take-profit, and drawdown thresholds (example values)
STOP_LOSS_THRESHOLD = -0.05  # 5% drawdown
TAKE_PROFIT_THRESHOLD = 0.10 # 10% profit
CRITICAL_DRAWDOWN_THRESHOLD = -0.15 # 15% drawdown

def log_message(message, log_file):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def analyze_trading_data(data):
    logs = data.get("logs", [])
    status = data.get("status", "OK")
    risk_parameters = data.get("risk_parameters", {{}})
    
    trading_log_summary = f"Trading Logs: {len(logs)} entries. Status: {status}. "
    if risk_parameters:
        trading_log_summary += f"Risk Parameters: {risk_parameters}"
        
    alerts = []
    
    # Example: Check for stop-loss/take-profit based on simulated trade data in logs
    # This is a placeholder and would need to be adapted based on actual log data structure
    for entry in logs:
        if "trade_result" in entry:
            trade_result = entry["trade_result"]
            if trade_result <= STOP_LOSS_THRESHOLD:
                alerts.append(f"STOP-LOSS TRIGGERED: Trade result {trade_result:.4f}")
            elif trade_result >= TAKE_PROFIT_THRESHOLD:
                alerts.append(f"TAKE-PROFIT TRIGGERED: Trade result {trade_result:.4f}")
                
    # Example: Check for critical drawdown based on a hypothetical "current_drawdown" in status or risk_parameters
    current_drawdown = risk_parameters.get("current_drawdown", 0)
    if current_drawdown <= CRITICAL_DRAWDOWN_THRESHOLD:
        alerts.append(f"CRITICAL DRAWDOWN DETECTED: {current_drawdown:.4f}")
        
    return trading_log_summary, alerts

def monitor():
    log_message("Starting trading dashboard monitor...", LOG_FILE)
    while True:
        try:
            response = requests.get(TRADING_DASHBOARD_URL, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            
            trading_log_summary, alerts = analyze_trading_data(data)
            
            log_message(trading_log_summary, LOG_FILE)
            
            if alerts:
                alert_message = "\n".join(alerts)
                log_message(f"*** CRITICAL ALERTS ***\n{alert_message}", ALERT_FILE)
                print(f"CRITICAL ALERTS DETECTED: {alert_message}") # Also print to stdout for visibility
            else:
                print("No critical alerts.")
                
        except requests.exceptions.RequestException as e:
            log_message(f"Error fetching data from dashboard: {e}", LOG_FILE)
            print(f"Error fetching data from dashboard: {e}")
        except Exception as e:
            log_message(f"An unexpected error occurred: {e}", LOG_FILE)
            print(f"An unexpected error occurred: {e}")
            
        time.sleep(60) # Check every 60 seconds

if __name__ == "__main__":
    monitor()
