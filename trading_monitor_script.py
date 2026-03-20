import requests
import datetime
import logging
import os

# Configuration
LOG_FILE_TRADING = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
LOG_FILE_ALERTS = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
TRADING_DASHBOARD_URL = "http://localhost:5001/"
TIMEZONE = "Asia/Bangkok"

# Setup logging for trading_monitoring.log
os.makedirs(os.path.dirname(LOG_FILE_TRADING), exist_ok=True)
trading_logger = logging.getLogger('trading_logger')
trading_logger.setLevel(logging.INFO)
if not trading_logger.handlers:
    trading_handler = logging.FileHandler(LOG_FILE_TRADING)
    trading_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    trading_logger.addHandler(trading_handler)
    trading_logger.addHandler(logging.StreamHandler()) # Also log to stdout for cron job output

# Setup logging for critical_alerts.log
alert_logger = logging.getLogger('alert_logger')
alert_logger.setLevel(logging.WARNING)
if not alert_logger.handlers:
    alert_handler = logging.FileHandler(LOG_FILE_ALERTS)
    alert_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    alert_logger.addHandler(alert_handler)

def fetch_trading_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = f"Failed to fetch data from {url}: {e}"
        trading_logger.error(error_message)
        return None
    except ValueError: # Includes JSONDecodeError
        error_message = f"Failed to decode JSON from {url}. Response: {response.text}"
        trading_logger.error(error_message)
        return None

def analyze_data(data):
    trading_logs = data.get("logs", [])
    status_updates = data.get("status", "OK")
    risk_parameters = data.get("risk", {})
    
    critical_alerts = []
    
    for log in trading_logs:
        if "STOP_LOSS_TRIGGERED" in log or "TAKE_PROFIT_TRIGGERED" in log:
            alert_message = f"Order triggered: {log}"
            critical_alerts.append(alert_message)
            alert_logger.warning(alert_message)
            
    current_drawdown = risk_parameters.get("drawdown", 0.0)
    if current_drawdown > 0.1: # Assuming 10% drawdown is critical
        alert_message = f"Critical drawdown detected: {current_drawdown:.2%}"
        critical_alerts.append(alert_message)
        alert_logger.warning(alert_message)

    return trading_logs, status_updates, risk_parameters, critical_alerts

def generate_summary(trading_logs, status_updates, risk_parameters, critical_alerts):
    summary = f"Trading Dashboard Analysis Summary ({datetime.datetime.now(datetime.timezone.utc).isoformat()}):
\n"
    summary += f"Overall Status: {status_updates}\n\n"
    summary += f"Risk Parameters: {risk_parameters}\n\n"
    
    if trading_logs:
        summary += "Recent Trading Logs:\n"
        for log in trading_logs[:5]:
            summary += f"- {log}\n"
        if len(trading_logs) > 5:
            summary += f"... and {len(trading_logs) - 5} more.\n"
    else:
        summary += "No recent trading logs found.\n"
        
    if critical_alerts:
        summary += "\nCRITICAL ALERTS:\n"
        for alert in critical_alerts:
            summary += f"- {alert}\n"
    else:
        summary += "\nNo critical alerts detected.\n"
        
    return summary

def main():
    data = fetch_trading_data(TRADING_DASHBOARD_URL)
    if data:
        trading_logs, status_updates, risk_parameters, critical_alerts = analyze_data(data)
        summary = generate_summary(trading_logs, status_updates, risk_parameters, critical_alerts)
        print(summary)
        trading_logger.info(f"Analysis complete. Summary: {summary}")
    else:
        error_message = f"Analysis failed: Could not fetch data from {TRADING_DASHBOARD_URL}."
        print(error_message)
        trading_logger.error(error_message)

if __name__ == "__main__":
    main()
