import requests
import json
import os
import datetime

TRADE_MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DATA_URL = "http://localhost:5001/"

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def log_to_file(content, filepath):
    try:
        # Ensure directory exists
        log_dir = os.path.dirname(filepath)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        with open(filepath, 'a') as f: # Use 'a' for append
            f.write(content + '\n')
    except IOError as e:
        print(f"Error writing to {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during logging to {filepath}: {e}")

def fetch_and_parse(url):
    alerts = []
    raw_content = None
    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status()
        raw_content = response.text
        
        log_to_file(f"--- Raw Fetch ({datetime.datetime.now().isoformat()}) ---", TRADE_MONITORING_LOG)
        log_to_file(raw_content, TRADE_MONITORING_LOG)

        try:
            data = json.loads(raw_content)
            # Placeholder for actual parsing logic, assuming JSON structure
            if isinstance(data, dict):
                if "orders" in data and isinstance(data["orders"], list):
                    for order in data["orders"]:
                        order_type = order.get("type")
                        if order_type in ["stop-loss", "take-profit"]:
                            asset = order.get("asset", "N/A")
                            price = order.get("price", "N/A")
                            alerts.append(f"ORDER: {order_type.capitalize()} - Asset: {asset}, Price: {price}")
                
                if "drawdown" in data and isinstance(data["drawdown"], dict):
                    level = data["drawdown"].get("level")
                    if level is not None and level > 0.05: # Example: 5% drawdown
                        alerts.append(f"DRAWDOWN CRITICAL: Level reached {level:.2%}")
            else:
                alerts.append("PARSING ERROR: Unexpected data format (not JSON object).")
                
        except json.JSONDecodeError:
            alerts.append("PARSING ERROR: Invalid JSON received from API.")
        except Exception as e:
            alerts.append(f"PARSING ERROR: An unexpected error occurred: {e}")
            
    except requests.exceptions.RequestException as e:
        alerts.append(f"FETCH ERROR: Could not connect to {url}. Error: {e}")
    except Exception as e:
        alerts.append(f"UNEXPECTED SCRIPT ERROR: An unexpected error occurred. Error: {e}")
    
    return alerts, raw_content # Return raw_content to log it

if __name__ == "__main__":
    print(f"Running trading monitor script at {datetime.datetime.now().isoformat()}...")
    
    alerts, raw_content = fetch_and_parse(DATA_URL)
    
    summary = ""
    if alerts:
        log_to_file("--- Critical Alerts Processed ---", CRITICAL_ALERTS_LOG)
        for alert in alerts:
            log_to_file(alert, CRITICAL_ALERTS_LOG)
        summary = "Trading Monitor Summary:\nCritical Alerts Detected:\n" + "\n".join(alerts)
    else:
        summary = "Trading monitor check completed successfully. No critical alerts detected."
        # Optionally log the successful but alert-free run
        log_to_file(f"Trading monitor check completed successfully at {datetime.datetime.now().isoformat()}. No critical alerts.", CRITICAL_ALERTS_LOG)

    print(summary)
