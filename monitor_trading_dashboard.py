
import requests
import json
import logging

# Configuration
URL = "http://localhost:5001/"
TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
LOG_LEVEL = logging.INFO

# Setup logging for trading data
trading_logger = logging.getLogger('trading_logger')
trading_logger.setLevel(LOG_LEVEL)
trading_handler = logging.FileHandler(TRADING_LOG_FILE)
trading_formatter = logging.Formatter('%(asctime)s - %(message)s')
trading_handler.setFormatter(trading_formatter)
trading_logger.addHandler(trading_handler)

# Setup logging for critical alerts
alert_logger = logging.getLogger('alert_logger')
alert_logger.setLevel(LOG_LEVEL)
alert_handler = logging.FileHandler(CRITICAL_ALERTS_FILE)
alert_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
alert_handler.setFormatter(alert_formatter)
alert_logger.addHandler(alert_handler)

def fetch_trading_data():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        alert_logger.error(f"Failed to fetch data from {URL}: {e}")
        return None
    except json.JSONDecodeError:
        alert_logger.error(f"Failed to decode JSON response from {URL}")
        return None

def analyze_data(data):
    if not data:
        return "No data received.", []

    trading_logs = data.get("logs", [])
    status_updates = data.get("status", {})
    risk_parameters = data.get("risk", {})

    # Log all extracted data
    trading_logger.info(f"Logs: {trading_logs}")
    trading_logger.info(f"Status: {status_updates}")
    trading_logger.info(f"Risk Parameters: {risk_parameters}")

    alerts = []
    summary_lines = ["Trading Dashboard Analysis:"]
    
    summary_lines.append(f"\nStatus Updates:")
    for key, value in status_updates.items():
        summary_lines.append(f"- {key}: {value}")

    summary_lines.append(f"\nRisk Parameters:")
    capital = risk_parameters.get("capital")
    stop_loss = risk_parameters.get("stop_loss")
    take_profit = risk_parameters.get("take_profit")
    
    if capital is not None:
        summary_lines.append(f"- Capital: {capital}")
    if stop_loss is not None:
        summary_lines.append(f"- Stop Loss: {stop_loss}")
        # Example alert for stop-loss triggered (assuming a 'triggered' field)
        if isinstance(stop_loss, dict) and stop_loss.get("triggered"):
            alert_message = f"STOP-LOSS TRIGGERED: {stop_loss.get('level')}"
            alert_logger.critical(alert_message)
            alerts.append(alert_message)
            summary_lines.append(f"  - ALERT: {alert_message}")
            
    if take_profit is not None:
        summary_lines.append(f"- Take Profit: {take_profit}")
        # Example alert for take-profit triggered (assuming a 'triggered' field)
        if isinstance(take_profit, dict) and take_profit.get("triggered"):
            alert_message = f"TAKE-PROFIT TRIGGERED: {take_profit.get('level')}"
            alert_logger.critical(alert_message)
            alerts.append(alert_message)
            summary_lines.append(f"  - ALERT: {alert_message}")

    # Example alert for critical drawdown (assuming a 'drawdown' field in risk)
    drawdown = risk_parameters.get("drawdown")
    if drawdown is not None and drawdown.get("level") is not None and drawdown.get("critical"):
        alert_message = f"CRITICAL DRAWDOWN ALERT: {drawdown.get('level')}"
        alert_logger.critical(alert_message)
        alerts.append(alert_message)
        summary_lines.append(f"  - ALERT: {alert_message}")
        
    if not alerts:
        summary_lines.append("\nNo critical alerts to report.")

    return "\\n".join(summary_lines), alerts

def main():
    data = fetch_trading_data()
    summary, alerts = analyze_data(data)
    
    # The summary is automatically delivered as per the cron job configuration.
    # If it were not, we would print it here:
    # print(summary) 

if __name__ == "__main__":
    main()
