import requests
import logging
from datetime import datetime

# --- Configuration ---
TRADING_DASHBOARD_URL = "http://localhost:5001/"
MONITORING_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
# --- End Configuration ---

# Set up logging for general monitoring
logging.basicConfig(filename=MONITORING_LOG_FILE, level=logging.INFO, format=LOG_FORMAT)

# Set up a separate logger for critical alerts to ensure they go to the specific file
alert_logger = logging.getLogger('alert_logger')
alert_logger.setLevel(logging.WARNING) # Log WARNING and above
# Prevent duplicate handlers if this script is run multiple times in the same process
if not alert_logger.handlers:
    alert_handler = logging.FileHandler(CRITICAL_ALERTS_LOG_FILE)
    alert_formatter = logging.Formatter(LOG_FORMAT)
    alert_handler.setFormatter(alert_formatter)
    alert_logger.addHandler(alert_handler)

def analyze_trading_data():
    """
    Fetches data from the trading dashboard, analyzes it, and logs results.
    Returns a plain text summary of the analysis.
    """
    summary_lines = []
    current_timestamp_str = datetime.now().isoformat()
    current_time_display = f"{datetime.now().strftime('%A, %B %dth, %Y — %I:%M %p (Asia/Bangkok) / %Y-%m-%d %H:%M UTC')}"
    summary_lines.append(f"--- Analysis Run: {current_time_display} ---")

    try:
        # Fetch data from the trading dashboard
        response = requests.get(TRADING_DASHBOARD_URL, timeout=10) # Add a timeout
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        data = response.json() # Assume the dashboard returns JSON

        # Log general data
        logging.info(f"Successfully fetched data from {TRADING_DASHBOARD_URL}")
        summary_lines.append("Successfully connected to trading dashboard.")

        # Extract and log trading logs
        trading_logs = data.get('trading_logs', [])
        logging.info(f"Extracted {len(trading_logs)} trading logs.")
        for log in trading_logs:
            logging.info(f"Trading Log Entry: {log}")
            summary_lines.append(f"Log: {log}")

        # Extract and log status updates
        status_updates = data.get('status_updates', {})
        logging.info(f"Extracted status updates: {status_updates}")
        summary_lines.append(f"Status Updates: {status_updates}")

        # Extract and log risk parameters
        risk_parameters = data.get('risk_parameters', {})
        logging.info(f"Extracted risk parameters: {risk_parameters}")
        summary_lines.append(f"Risk Parameters: {risk_parameters}")

        # Detect and log critical events
        stop_loss_triggered = data.get('stop_loss_triggered', False)
        take_profit_triggered = data.get('take_profit_triggered', False)
        critical_drawdown = data.get('critical_drawdown', False)

        critical_alerts_found = False

        if stop_loss_triggered:
            alert_message = f"STOP-LOSS TRIGGERED: A stop-loss order was activated."
            alert_logger.warning(alert_message)
            logging.warning(alert_message) # Also log to general log
            summary_lines.append(f"ALERT: {alert_message}")
            critical_alerts_found = True

        if take_profit_triggered:
            # This is typically not an alert, but informational
            info_message = f"TAKE-PROFIT TRIGGERED: A take-profit order was activated."
            logging.info(info_message)
            summary_lines.append(f"INFO: {info_message}")

        if critical_drawdown:
            alert_message = f"CRITICAL DRAWDOWN: The trading account experienced a critical drawdown."
            alert_logger.warning(alert_message)
            logging.warning(alert_message) # Also log to general log
            summary_lines.append(f"ALERT: {alert_message}")
            critical_alerts_found = True

        if not critical_alerts_found:
            summary_lines.append("No critical alerts detected.")

    except requests.exceptions.Timeout:
        error_message = f"Request timed out while trying to connect to {TRADING_DASHBOARD_URL}."
        logging.error(error_message)
        alert_logger.error(error_message) # Log connection errors as critical too
        summary_lines.append(f"ERROR: Connection to trading dashboard timed out.")
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {TRADING_DASHBOARD_URL}: {e}"
        logging.error(error_message)
        alert_logger.error(error_message) # Log connection errors as critical too
        summary_lines.append(f"ERROR: Could not connect to trading dashboard. Details: {e}")
    except Exception as e:
        # Catch any other unexpected errors during processing
        error_message = f"An unexpected error occurred during analysis: {e}"
        logging.error(error_message)
        alert_logger.error(error_message) # Log unexpected errors as critical too
        summary_lines.append(f"ERROR: An unexpected error occurred. Details: {e}")

    # Ensure at least a basic summary line is always returned
    if len(summary_lines) <= 1: # Only contains the header line
        summary_lines.append("No data processed or an error occurred.")

    # Join the summary lines into a single plain text string
    return "\n".join(summary_lines)

if __name__ == "__main__":
    # Execute the analysis and print the summary
    analysis_summary = analyze_trading_data()
    print(analysis_summary)
