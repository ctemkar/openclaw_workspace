import requests
import re
import datetime
import os

LOG_FILE = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
CRITICAL_ALERT_FILE = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
URL = 'http://localhost:5001/'

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def parse_trading_data(html_content):
    # These are placeholder regex patterns. They will need to be adjusted based on actual content.
    # Example: Assuming logs are in <p class="log">...</p>
    logs = re.findall(r'<p class="log">(.*?)</p>', html_content)
    # Example: Assuming status updates are in <div>Status: (.*?)</div>
    status_updates = re.findall(r'<div>Status: (.*?)</div>', html_content)
    # Example: Assuming risk parameters are in specific divs or spans
    capital_match = re.search(r'Capital: (\d+\.?\d*)', html_content)
    stop_loss_match = re.search(r'Stop Loss: (\d+\.?\d*)', html_content)
    take_profit_match = re.search(r'Take Profit: (\d+\.?\d*)', html_content)
    drawdown_match = re.search(r'Drawdown Indicator: (critical|warning|normal)', html_content, re.IGNORECASE)

    capital = float(capital_match.group(1)) if capital_match else None
    stop_loss = float(stop_loss_match.group(1)) if stop_loss_match else None
    take_profit = float(take_profit_match.group(1)) if take_profit_match else None
    drawdown_status = drawdown_match.group(1).lower() if drawdown_match else 'normal'

    return {
        "logs": logs,
        "status_updates": status_updates,
        "capital": capital,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "drawdown": drawdown_status
    }

def log_data(data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        timestamp = datetime.datetime.now().isoformat()
        f.write(f"--- {timestamp} ---\n")
        f.write(f"Capital: {data.get('capital')}\n")
        f.write(f"Stop Loss: {data.get('stop_loss')}\n")
        f.write(f"Take Profit: {data.get('take_profit')}\n")
        f.write("Status Updates:\n")
        for update in data.get('status_updates', []):
            f.write(f"- {update}\n")
        f.write("Logs:\n")
        for log in data.get('logs', []):
            f.write(f"- {log}\n")
        f.write("-" * 20 + "\n")

def check_alerts(data):
    alerts = []
    is_critical = False

    # Placeholder for logic to detect triggered stop-loss/take-profit
    # This would typically involve comparing current prices/positions with SL/TP levels,
    # which are not directly available in the fetched parameters alone.
    # For now, we'll assume the fetched 'stop_loss' and 'take_profit' values themselves
    # might indicate a triggered state or we'd need current market data.
    # This is a simplification for the script structure.

    # Check for critical drawdown
    if data.get('drawdown') == 'critical':
        alerts.append("CRITICAL: Drawdown indicators are critical!")
        is_critical = True

    return alerts, is_critical

def log_critical_alerts(alerts, data):
    if alerts:
        os.makedirs(os.path.dirname(CRITICAL_ALERT_FILE), exist_ok=True)
        with open(CRITICAL_ALERT_FILE, 'a') as f:
            timestamp = datetime.datetime.now().isoformat()
            f.write(f"--- {timestamp} ---\n")
            for alert in alerts:
                f.write(f"{alert}\n")
            # Log relevant data along with the alert
            f.write(f"Capital: {data.get('capital')}\n")
            f.write(f"Stop Loss: {data.get('stop_loss')}\n")
            f.write(f"Take Profit: {data.get('take_profit')}\n")
            f.write(f"Drawdown: {data.get('drawdown')}\n")
            f.write("-" * 20 + "\n")

if __name__ == "__main__":
    print(f"[{datetime.datetime.now().isoformat()}] Starting trading dashboard monitoring...")
    html_content = fetch_data(URL)

    if html_content:
        parsed_data = parse_trading_data(html_content)
        log_data(parsed_data)
        alerts, is_critical = check_alerts(parsed_data)
        if alerts:
            print(f"CRITICAL ALERTS DETECTED: {alerts}")
            log_critical_alerts(alerts, parsed_data)
        else:
            print("No critical alerts detected.")
    else:
        print("Failed to retrieve data. Skipping analysis.")

    print(f"[{datetime.datetime.now().isoformat()}] Trading dashboard monitoring finished.")
