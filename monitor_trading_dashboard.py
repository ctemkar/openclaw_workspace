
import requests
import logging
from datetime import datetime

# --- Configuration ---
DASHBOARD_URL = "http://localhost:5001/"
TRADING_LOG_FILE = "./trading_monitoring.log"
CRITICAL_ALERTS_FILE = "./critical_alerts.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# --- Logging Setup ---
# Trading Monitoring Log
trading_logger = logging.getLogger("TradingMonitor")
trading_logger.setLevel(logging.INFO)
trading_handler = logging.FileHandler(TRADING_LOG_FILE)
trading_handler.setFormatter(logging.Formatter(LOG_FORMAT))
trading_logger.addHandler(trading_handler)

# Critical Alerts Log
alerts_logger = logging.getLogger("CriticalAlerts")
alerts_logger.setLevel(logging.WARNING)
alerts_handler = logging.FileHandler(CRITICAL_ALERTS_FILE)
alerts_handler.setFormatter(logging.Formatter(LOG_FORMAT))
alerts_logger.addHandler(alerts_handler)

# --- Helper Functions ---
def fetch_dashboard_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text  # Assuming the dashboard returns HTML or text
    except requests.exceptions.RequestException as e:
        alerts_logger.error(f"Failed to fetch dashboard data from {url}: {e}")
        return None

def parse_dashboard_data(data):
    # Placeholder for actual data parsing logic.
    # This would involve extracting:
    # - Trading logs
    # - Status updates
    # - Risk parameters
    # - Stop-loss/Take-profit triggers
    # - Critical drawdown events
    # For now, we'll simulate some data.
    
    simulated_logs = [
        {"timestamp": datetime.now().isoformat(), "event": "Trade executed", "details": "Buy AAPL @ 150.00"},
        {"timestamp": datetime.now().isoformat(), "event": "Trade executed", "details": "Sell AAPL @ 152.50"},
    ]
    simulated_status = {"status": "Operational", "active_trades": 2}
    simulated_risk = {"margin_level": 0.5, "max_drawdown_today": 0.02}
    
    critical_alerts_found = []
    
    # Simulate checking for stop-loss/take-profit (example condition)
    # In a real scenario, you'd parse specific logs or status fields.
    if simulated_risk.get("max_drawdown_today", 0) > 0.05: # Example: 5% drawdown
        critical_alerts_found.append({
            "type": "Critical Drawdown",
            "details": f"Drawdown reached {simulated_risk['max_drawdown_today']:.2%}. Current risk parameters: {simulated_risk}",
            "timestamp": datetime.now().isoformat()
        })

    return simulated_logs, simulated_status, simulated_risk, critical_alerts_found

def log_data(logs, status, risk_params, critical_alerts):
    trading_logger.info("--- Trading Dashboard Monitoring ---")
    trading_logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    trading_logger.info("Status Updates:")
    for key, value in status.items():
        trading_logger.info(f"  {key}: {value}")
        
    trading_logger.info("Risk Parameters:")
    for key, value in risk_params.items():
        trading_logger.info(f"  {key}: {value}")

    trading_logger.info("Trading Logs:")
    if logs:
        for log in logs:
            trading_logger.info(f"  {log.get('timestamp', '')} - {log.get('event', '')}: {log.get('details', '')}")
    else:
        trading_logger.info("  No new trading logs found.")

    if critical_alerts:
        for alert in critical_alerts:
            alerts_logger.warning(f"ALERT [{alert.get('type', 'Unknown')}] - {alert.get('details', '')}")
    else:
        trading_logger.info("No critical alerts detected.")
    trading_logger.info("----------------------------------\n")

def generate_summary(status, risk_params, critical_alerts):
    summary = f"Trading Dashboard Summary - {datetime.now().isoformat()}

"
    summary += "System Status:
"
    for key, value in status.items():
        summary += f"- {key}: {value}
"
    
    summary += "
Current Risk Parameters:
"
    for key, value in risk_params.items():
        summary += f"- {key}: {value}
"

    if critical_alerts:
        summary += "
Critical Alerts Detected:
"
        for alert in critical_alerts:
            summary += f"- [{alert.get('type', 'Unknown')}] {alert.get('details', '')} at {alert.get('timestamp', '')}
"
    else:
        summary += "
No critical alerts detected.
"
        
    return summary

def main():
    data = fetch_dashboard_data(DASHBOARD_URL)
    if data is not None:
        logs, status, risk_params, critical_alerts = parse_dashboard_data(data)
        log_data(logs, status, risk_params, critical_alerts)
        summary = generate_summary(status, risk_params, critical_alerts)
        print(summary) # Print summary to stdout as requested

if __name__ == "__main__":
    main()
