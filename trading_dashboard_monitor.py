
import requests
import json
import logging
from datetime import datetime

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
DATA_URL = 'http://localhost:5001/'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
critical_logger = logging.getLogger('critical_alerts')
critical_handler = logging.FileHandler(CRITICAL_LOG_FILE)
critical_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
critical_logger.addHandler(critical_handler)
critical_logger.setLevel(logging.WARNING)

def fetch_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from {DATA_URL}: {e}")
        return None

def analyze_data(data):
    if not data:
        return "No data received for analysis."

    summary_lines = []
    critical_alerts = []

    capital = data.get('capital', 'N/A')
    stop_loss = data.get('stop_loss', 'N/A')
    take_profit = data.get('take_profit', 'N/A')
    drawdown_indicators = data.get('drawdown_indicators', 'N/A')
    trading_logs = data.get('trading_logs', [])
    status_updates = data.get('status_updates', [])

    # Log extracted data
    logging.info(f"Fetched data: Capital={capital}, StopLoss={stop_loss}, TakeProfit={take_profit}, Drawdown={drawdown_indicators}")
    for log in trading_logs:
        logging.info(f"Trading Log: {log}")
    for status in status_updates:
        logging.info(f"Status Update: {status}")

    summary_lines.append(f"--- Trading Dashboard Monitor Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    summary_lines.append(f"Capital: {capital}")

    # Check for stop-loss or take-profit triggers (example logic, actual might be more complex)
    if stop_loss != 'N/A' and stop_loss != 'N/A' and float(capital) <= float(stop_loss): # Example: if capital falls to or below stop_loss
        alert_msg = f"STOP-LOSS TRIGGERED: Capital ({capital}) reached or fell below stop loss ({stop_loss})."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)

    if take_profit != 'N/A' and take_profit != 'N/A' and float(capital) >= float(take_profit): # Example: if capital reaches or exceeds take_profit
        alert_msg = f"TAKE-PROFIT TRIGGERED: Capital ({capital}) reached or exceeded take profit ({take_profit})."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)

    # Check for critical drawdown indicators
    if drawdown_indicators != 'N/A' and drawdown_indicators == 'critical': # Example: if drawdown_indicators is explicitly 'critical'
        alert_msg = f"CRITICAL DRAWDOWN: Drawdown indicators are critical."
        critical_alerts.append(alert_msg)
        critical_logger.warning(alert_msg)

    if critical_alerts:
        summary_lines.append("\nCRITICAL ALERTS:")
        summary_lines.extend(critical_alerts)
    else:
        summary_lines.append("\nNo critical alerts detected.")

    summary_lines.append("\nStatus Updates:")
    if status_updates:
        for status in status_updates:
            summary_lines.append(f"- {status}")
    else:
        summary_lines.append("- No status updates available.")

    return "\\n".join(summary_lines) # Use \\n for newline in cron job message

if __name__ == "__main__":
    dashboard_data = fetch_data()
    result_summary = analyze_data(dashboard_data)
    print(result_summary) # stdout will be captured by cron tool delivery
