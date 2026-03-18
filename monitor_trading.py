
import requests
import logging
import json
from datetime import datetime

# --- Configuration ---
TRADING_DASHBOARD_BASE = "http://localhost:5001"
ENDPOINTS = {
    "status": "/status",
    "trades": "/trades", 
    "summary": "/summary",
    "analysis": "/analysis",
    "strategy": "/strategy"
}
TRADING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

trading_logger = logging.getLogger("trading_logger")
trading_handler = logging.FileHandler(TRADING_LOG_FILE)
trading_handler.setFormatter(logging.Formatter(LOG_FORMAT))
trading_logger.addHandler(trading_handler)

alerts_logger = logging.getLogger("alerts_logger")
alerts_handler = logging.FileHandler(CRITICAL_ALERTS_LOG_FILE)
alerts_handler.setFormatter(logging.Formatter(LOG_FORMAT))
alerts_logger.addHandler(alerts_handler)


def fetch_trading_data():
    """Fetch data from all trading dashboard endpoints"""
    data = {}
    for name, endpoint in ENDPOINTS.items():
        try:
            url = TRADING_DASHBOARD_BASE + endpoint
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Try to parse as JSON, fall back to text
            try:
                data[name] = response.json()
            except json.JSONDecodeError:
                data[name] = response.text[:500]  # Limit text length
                
        except requests.exceptions.RequestException as e:
            alerts_logger.error(f"Failed to fetch {endpoint}: {e}")
            data[name] = f"Error: {str(e)}"
    
    return data

def analyze_data(data):
    if data is None:
        return "Unable to fetch data."

    analysis_summary = []
    current_time = datetime.now().isoformat()

    # Log general data
    trading_logger.info(f"Trading data fetched at {current_time}: {data}")
    analysis_summary.append(f"Data fetched at: {current_time}")
    analysis_summary.append(f"Status Updates: {data.get('status', 'N/A')}")
    analysis_summary.append(f"Risk Parameters: {data.get('risk_parameters', 'N/A')}")

    # Detect critical alerts
    stop_loss_triggered = data.get("stop_loss_triggered", False)
    take_profit_triggered = data.get("take_profit_triggered", False)
    critical_drawdown = data.get("critical_drawdown", False)
    order_details = data.get("order_details", {})

    alert_detected = False
    if stop_loss_triggered:
        order_id = order_details.get("order_id", "N/A")
        alerts_logger.warning(f"STOP-LOSS TRIGGERED at {current_time} for order ID: {order_id}")
        analysis_summary.append(f"ALERT: STOP-LOSS TRIGGERED for order {order_id}")
        alert_detected = True

    if take_profit_triggered:
        order_id = order_details.get("order_id", "N/A")
        alerts_logger.warning(f"TAKE-PROFIT TRIGGERED at {current_time} for order ID: {order_id}")
        analysis_summary.append(f"ALERT: TAKE-PROFIT TRIGGERED for order {order_id}")
        alert_detected = True

    if critical_drawdown:
        drawdown_level = data.get("drawdown_level", "N/A")
        alerts_logger.critical(f"CRITICAL DRAWDOWN DETECTED at {current_time}: {drawdown_level}")
        analysis_summary.append(f"ALERT: CRITICAL DRAWDOWN DETECTED at {drawdown_level}")
        alert_detected = True

    if not alert_detected:
        analysis_summary.append("No critical alerts detected.")

    return "\n".join(analysis_summary)

def main():
    data = fetch_trading_data()
    summary = analyze_data(data)
    print(summary) # This will be captured by cron's output

if __name__ == "__main__":
    main()
