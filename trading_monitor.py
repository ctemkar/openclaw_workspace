import requests
import json
import logging
import os

# Ensure the workspace directory exists
workspace_dir = "/Users/chetantemkar/.openclaw/workspace/app"
os.makedirs(workspace_dir, exist_ok=True)

log_file_path = os.path.join(workspace_dir, "trading_monitoring.log")
alerts_file_path = os.path.join(workspace_dir, "critical_alerts.log")

# Configure logging to go to the specified file and stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file_path),
                              logging.StreamHandler()])

# --- Configuration ---
FETCH_URL = "http://localhost:5001/status"

# --- Alert parameters (example values) ---
# These would typically be configured or derived from the fetched data.
# For this example, assuming they are set as constants or fetched.
STOP_LOSS_THRESHOLD = 0.05  # 5% loss
TAKE_PROFIT_THRESHOLD = 0.10 # 10% gain
DRAWDOWN_CRITICAL_THRESHOLD = 0.15 # 15% drawdown

def fetch_and_process_trading_data():
    try:
        # 1. Fetch data from the URL
        logging.info(f"Fetching data from {FETCH_URL}...")
        response = requests.get(FETCH_URL, timeout=10) # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        # Log raw fetched data
        logging.info(f"Raw data fetched: {json.dumps(data)}")

        # 2. Parse the fetched data
        # Actual JSON structure from /status endpoint:
        # {
        #   "status": "running",
        #   "timestamp": "2026-03-30T22:42:54.557315",
        #   "port": 5001,
        #   "analysis_scheduled": "hourly",
        #   "capital": 100.0,
        #   "risk_parameters": {
        #     "stop_loss": 0.05,
        #     "take_profit": 0.10,
        #     "max_trades_per_day": 2
        #   },
        #   "trading_pairs": ["BTC/USD", "ETH/USD"],
        #   "last_analysis": "2026-03-30T22:01:11.445599"
        # }
        
        # For monitoring purposes, we'll use the configured risk parameters
        # Note: These are the configured thresholds, not current PnL values
        risk_parameters = data.get("risk_parameters", {})
        
        # Extracting risk parameters
        capital = data.get("capital")
        # These are the configured thresholds, not current values
        stop_loss_threshold = risk_parameters.get("stop_loss")  # 0.05 = 5%
        take_profit_threshold = risk_parameters.get("take_profit")  # 0.10 = 10%
        
        # For actual monitoring, we would need current PnL values
        # Since we don't have current PnL in the status endpoint,
        # we'll use placeholder values for demonstration
        # In a real system, we would fetch actual trade PnL from another endpoint
        current_stop_loss_loss_pct = None  # Placeholder - would need actual current loss %
        current_take_profit_gain_pct = None  # Placeholder - would need actual current gain %
        current_drawdown_pct = None  # Placeholder - would need actual drawdown %

        # 3. Log all extracted data
        logging.info("--- Extracted Data ---")
        logging.info(f"System Status: {data.get('status')}")
        logging.info(f"Timestamp: {data.get('timestamp')}")
        logging.info(f"Capital: ${capital}")
        logging.info(f"Stop Loss Threshold: {stop_loss_threshold*100 if stop_loss_threshold else 'N/A'}%")
        logging.info(f"Take Profit Threshold: {take_profit_threshold*100 if take_profit_threshold else 'N/A'}%")
        logging.info(f"Max Trades/Day: {risk_parameters.get('max_trades_per_day', 'N/A')}")
        logging.info(f"Trading Pairs: {', '.join(data.get('trading_pairs', []))}")
        logging.info(f"Last Analysis: {data.get('last_analysis', 'N/A')}")
        logging.info("----------------------")
        
        # Note: Current PnL values are not available in the status endpoint
        # For actual monitoring, we would need to fetch trade data and calculate current PnL
        if current_stop_loss_loss_pct is None or current_take_profit_gain_pct is None:
            logging.warning("Current PnL values not available in status endpoint. Alert checks will be limited.")

        # 4. Implement alert conditions
        alerts_triggered = []
        alert_details = []

        # Check stop-loss: if current loss percentage is DEEPER than the threshold
        if current_stop_loss_loss_pct is not None and current_stop_loss_loss_pct <= -STOP_LOSS_THRESHOLD:
            alerts_triggered.append("STOP_LOSS_HIT")
            alert_details.append(f"Stop-loss hit. Current loss: {current_stop_loss_loss_pct*100:.2f}%. Threshold: {-STOP_LOSS_THRESHOLD*100:.2f}%.")

        # Check take-profit: if current gain percentage is HIGHER than the threshold
        if current_take_profit_gain_pct is not None and current_take_profit_gain_pct >= TAKE_PROFIT_THRESHOLD:
            alerts_triggered.append("TAKE_PROFIT_HIT")
            alert_details.append(f"Take-profit hit. Current gain: {current_take_profit_gain_pct*100:.2f}%. Threshold: {TAKE_PROFIT_THRESHOLD*100:.2f}%.")

        # Check drawdown: if current drawdown percentage is HIGHER than the threshold
        if current_drawdown_pct is not None and current_drawdown_pct >= DRAWDOWN_CRITICAL_THRESHOLD:
            alerts_triggered.append("CRITICAL_DRAWDOWN")
            alert_details.append(f"Critical drawdown. Current: {current_drawdown_pct*100:.2f}%. Threshold: {DRAWDOWN_CRITICAL_THRESHOLD*100:.2f}%.")

        # 5. If any alert condition is met, save critical data
        if alerts_triggered:
            critical_data_summary = f" Timestamp: {logging.Formatter('%(asctime)s').formatTime(logging.LogRecord('', '', '', '', '', '', ''))}\n" # Get current timestamp
            critical_data_summary += f" Alerts: {', '.join(alerts_triggered)}\n"
            critical_data_summary += f" Details: {'; '.join(alert_details)}\n"
            critical_data_summary += f" Full Data: {json.dumps(data, indent=2)}"

            # Append to critical alerts log file
            try:
                with open(alerts_file_path, 'a') as f:
                    f.write(critical_data_summary + "\n")
                logging.warning(f"CRITICAL ALERT DETECTED AND LOGGED: {', '.join(alerts_triggered)}")
            except IOError as e:
                logging.error(f"Failed to write to critical alerts log {alerts_file_path}: {e}")
        else:
            logging.info("No critical alerts triggered.")

    except requests.exceptions.ConnectionError:
        logging.error(f"Failed to connect to {FETCH_URL}. Is the server running?")
    except requests.exceptions.Timeout:
        logging.error(f"Request to {FETCH_URL} timed out.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {FETCH_URL}: {e}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON response from {FETCH_URL}. Response: {response.text}")
    except IOError as e:
        logging.error(f"File I/O error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True) # Log exception info for debugging

# Execute the function
if __name__ == "__main__":
    fetch_and_process_trading_data()
