import requests
import json
import os
from datetime import datetime

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
ALERT_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
BASE_URL = "http://localhost:5001"

def fetch_all_data():
    """Fetch data from multiple API endpoints"""
    endpoints = {
        'status': '/api/status/all',
        'progress': '/api/trading/progress',
        # Add more endpoints as discovered
    }
    
    all_data = {}
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(BASE_URL + endpoint, timeout=5)
            response.raise_for_status()
            all_data[name] = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {name} from {endpoint}: {e}")
            all_data[name] = None
    
    return all_data

def parse_and_log(data):
    if not data:
        return

    log_entry = f"{datetime.now()}: "
    content_to_log = []
    critical_alerts = []

    # Parse status data
    status_data = data.get('status', {})
    if status_data:
        content_to_log.append("Status:")
        content_to_log.append(f"  - Last Update: {status_data.get('last_update', 'N/A')}")
        content_to_log.append(f"  - Trading Status: {status_data.get('trading', 'N/A')}")
        
        # Check if trading is not running
        if status_data.get('trading') != 'running':
            critical_alerts.append(f"Trading Status Alert: Trading is {status_data.get('trading')}")

    # Parse progress/trades data
    progress_data = data.get('progress', {})
    trades = progress_data.get('trades', [])
    if trades:
        content_to_log.append(f"Recent Trades ({len(trades)}):")
        for trade in trades:
            trade_str = f"  - {trade.get('time', 'N/A')}: {trade.get('side', 'N/A')} {trade.get('amount', 'N/A')} @ ${trade.get('price', 'N/A')} ({trade.get('status', 'N/A')})"
            content_to_log.append(trade_str)
            
            # Check for failed trades
            if trade.get('status') == 'failed':
                critical_alerts.append(f"Failed Trade Alert: {trade_str}")
            
            # Check for large trades (example threshold)
            amount = trade.get('amount')
            if isinstance(amount, (int, float)) and amount > 0.001:  # Example threshold
                critical_alerts.append(f"Large Trade Alert: {trade_str}")

    # Note: We don't have risk parameters from the current API endpoints
    # In a real implementation, we would need to find or create endpoints for:
    # - capital/balance
    # - stop loss levels
    # - take profit levels
    # - drawdown indicators
    
    # For now, we'll add a note about missing risk data
    content_to_log.append("Risk Parameters: Not available from current API endpoints")

    # Write to main log file
    log_content = "\n".join(content_to_log)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n" + log_content + "\n---\n")

    # Write critical alerts to alert file
    if critical_alerts:
        alert_entry = f"{datetime.now()}: CRITICAL ALERTS DETECTED\n" + "\n".join(critical_alerts) + "\n---\n"
        with open(ALERT_FILE, "a") as f:
            f.write(alert_entry)
        print(f"Critical alerts saved: {len(critical_alerts)} alerts")

# --- Main execution ---
if __name__ == "__main__":
    # Ensure log directories exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)

    print(f"Fetching trading data from {BASE_URL}...")
    all_data = fetch_all_data()
    
    if any(all_data.values()):  # If we got any data
        print("Data fetched successfully. Parsing and logging...")
        parse_and_log(all_data)
        print("Processing complete.")
        
        # Show what we found
        for name, data in all_data.items():
            if data:
                print(f"  - {name}: {len(str(data))} bytes of data")
            else:
                print(f"  - {name}: No data")
    else:
        print("Failed to fetch any data. Skipping processing.")