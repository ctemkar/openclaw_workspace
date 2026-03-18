import os
import requests
import logging
from datetime import datetime

# Read current port from .active_port file
try:
    with open(".active_port", "r") as f:
        PORT = f.read().strip()
except:
    PORT = "5001"  # Fallback

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERT_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = f"http://localhost:{PORT}/trades"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

critical_alert_logger = logging.getLogger('critical_alert_logger')
critical_alert_logger.setLevel(logging.CRITICAL)
critical_alert_handler = logging.FileHandler(CRITICAL_ALERT_LOG_FILE)
critical_alert_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_alert_logger.addHandler(critical_alert_handler)

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return None

def analyze_data(data):
    if not data:
        return "No data available for analysis."

    analysis_summary = f"Trading Dashboard Analysis - {datetime.now().isoformat()}\n"
    all_logs = []
    critical_alerts = []

    # Extract trading data
    if "trades" in data:
        trades = data["trades"]
        analysis_summary += f"\nFound {len(trades)} trades in the system.\n"
        
        # Analyze recent trades
        recent_trades = trades[:5]  # Look at most recent 5 trades
        analysis_summary += f"\nRecent trades (last {len(recent_trades)}):\n"
        
        for i, trade in enumerate(recent_trades, 1):
            # Handle different trade formats
            if "side" in trade and "price" in trade:
                side = trade.get("side", "unknown").upper()
                price = trade.get("price", "N/A")
                amount = trade.get("amount", trade.get("quantity", "N/A"))
                symbol = trade.get("symbol", "unknown")
                time = trade.get("time", "unknown")
                
                log_entry = f"Trade {i}: {side} {amount} {symbol} @ ${price} at {time}"
                all_logs.append(log_entry)
                analysis_summary += f"  {log_entry}\n"
                
                # Check for potential issues
                if side == "SELL" and float(price) < 0:
                    alert_msg = f"CRITICAL ALERT: Negative price in sell trade! Price: ${price}"
                    critical_alerts.append(alert_msg)
                    critical_alert_logger.critical(alert_msg)
                    analysis_summary += f"  ⚠️ {alert_msg}\n"
    else:
        analysis_summary += "\nNo trades found in the data.\n"

    # Extract count and timestamp
    if "count" in data:
        analysis_summary += f"\nTotal trade count: {data['count']}\n"
    
    if "timestamp" in data:
        analysis_summary += f"Data timestamp: {data['timestamp']}\n"

    # Check for system health
    if len(data.get("trades", [])) == 0:
        alert_msg = "ALERT: No trades found in the system. Check if trading is active."
        critical_alerts.append(alert_msg)
        analysis_summary += f"\n⚠️ {alert_msg}\n"
    
    # Check for excessive trades (more than 10 in a short period)
    if len(data.get("trades", [])) > 10:
        alert_msg = f"ALERT: High trade volume detected ({len(data['trades'])} trades)."
        critical_alerts.append(alert_msg)
        analysis_summary += f"\n⚠️ {alert_msg}\n"

    # Log all extracted data
    for log_entry in all_logs:
        logging.info(log_entry)

    # Add summary of alerts
    if critical_alerts:
        analysis_summary += f"\n⚠️ Generated {len(critical_alerts)} alert(s).\n"
    else:
        analysis_summary += "\n✅ No critical alerts detected.\n"

    return analysis_summary

if __name__ == "__main__":
    trading_data = fetch_data(URL)
    summary = analyze_data(trading_data)
    print(summary) # This will be captured by the ACP session
