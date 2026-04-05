import requests
import logging
import json
from datetime import datetime

LOG_FILE_TRADING = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
LOG_FILE_ALERTS = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
URL = "http://localhost:5001/"

def setup_logger(file_path, name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

trading_logger = setup_logger(LOG_FILE_TRADING, 'Trading')
alert_logger = setup_logger(LOG_FILE_ALERTS, 'Alerts')

def monitor_trading_dashboard():
    summary_lines = []
    critical_alerts_list = []

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        
        try:
            data = response.json() # Assuming JSON response
            trading_logger.info(f"Successfully fetched data from {URL}")
            summary_lines.append(f"Data fetched successfully at {datetime.now().isoformat()}.")

            # Log all data to trading_monitoring.log
            try:
                trading_logger.info(json.dumps(data, indent=2))
            except TypeError as e:
                trading_logger.warning(f"Could not JSON dump entire data: {e}. Logging raw response text.")
                try:
                    trading_logger.info(response.text) # Fallback to raw text
                except Exception as text_e:
                    trading_logger.error(f"Could not log raw response text either: {text_e}")

            # --- Analysis and Alert Detection ---
            status_update = data.get("status", "N/A")
            risk_parameters = data.get("risk_parameters", {})
            trading_logs = data.get("logs", [])

            summary_lines.append(f"Status: {status_update}")
            summary_lines.append(f"Risk Parameters: {risk_parameters}")

            # Detect stop-loss/take-profit orders
            for log_entry in trading_logs:
                if isinstance(log_entry, dict):
                    if log_entry.get("type") == "order_triggered" and ("stop_loss" in log_entry.get("details", "").lower() or "take_profit" in log_entry.get("details", "").lower()):
                        alert_message = f"Order triggered: {log_entry.get('details', 'N/A')}"
                        alert_logger.warning(alert_message)
                        critical_alerts_list.append(alert_message)
                else:
                    trading_logger.warning(f"Skipping malformed log entry: {log_entry}")

            # Detect critical drawdown
            current_drawdown = data.get("drawdown", 0)
            CRITICAL_DRAWDOWN_THRESHOLD = 0.10 # 10%
            if isinstance(current_drawdown, (int, float)) and current_drawdown > CRITICAL_DRAWDOWN_THRESHOLD:
                alert_message = f"Critical drawdown detected: {current_drawdown*100:.2f}%"
                alert_logger.error(alert_message)
                critical_alerts_list.append(alert_message)
            
        except json.JSONDecodeError:
            error_message = f"Error decoding JSON response from {URL}"
            trading_logger.error(error_message)
            summary_lines.append(f"Error: Received non-JSON response from {URL}.")
            alert_logger.error(error_message)
            critical_alerts_list.append(f"Invalid response format from monitoring endpoint.")

    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from {URL}: {e}"
        trading_logger.error(error_message)
        summary_lines.append(f"Error: Could not fetch data from {URL}. Details: {e}")
        alert_logger.error(error_message)
        critical_alerts_list.append(f"Network error during monitoring: {e}")

    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        trading_logger.exception(error_message)
        summary_lines.append(f"An unexpected error occurred: {e}")
        alert_logger.exception(error_message)
        critical_alerts_list.append(f"Unexpected error during monitoring process: {e}")

    # Final summary construction
    final_summary_str = "\\n".join(summary_lines)
    if critical_alerts_list:
        final_summary_str += "\\n\\nCRITICAL ALERTS DETECTED:\\n" + "\\n".join(critical_alerts_list)
    
    print(final_summary_str)

if __name__ == "__main__":
    monitor_trading_dashboard()
