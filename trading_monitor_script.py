import requests
import json
import os
import datetime
from bs4 import BeautifulSoup
import re

TRADE_MONITORING_LOG = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_LOG = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"
DATA_URL = "http://localhost:5009/"

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
            # Parse HTML dashboard instead of expecting JSON
            soup = BeautifulSoup(raw_content, 'html.parser')
            
            # Extract timestamp
            timestamp_elem = soup.find('div', class_='timestamp')
            timestamp = timestamp_elem.text.strip().replace('Last updated: ', '') if timestamp_elem else 'Unknown'
            
            # Extract key data from data cards
            data_cards = soup.find_all('div', class_='data-card')
            dashboard_data = {}
            for card in data_cards:
                h3 = card.find('h3')
                if h3:
                    key = h3.text.strip()
                    value_elem = card.find('div', class_='data-value')
                    if value_elem:
                        value = value_elem.text.strip()
                        value = re.sub(r'\s+', ' ', value)
                        dashboard_data[key] = value
            
            # Extract deployed/available capital
            deployed_available = soup.find('p')
            if deployed_available and 'Deployed:' in deployed_available.text:
                text = deployed_available.text
                deployed_match = re.search(r'Deployed:\s*\$([\d.]+)', text)
                available_match = re.search(r'Available:\s*\$([\d.]+)', text)
                if deployed_match:
                    dashboard_data['Deployed Capital'] = f"${deployed_match.group(1)}"
                if available_match:
                    dashboard_data['Available Capital'] = f"${available_match.group(1)}"
            
            # Check for critical conditions
            page_text = soup.get_text().lower()
            
            # Check for drawdown
            if 'Cumulative P&L' in dashboard_data:
                pnl_text = dashboard_data['Cumulative P&L']
                # Extract percentage from text like "-$415.32 (-43.9%)"
                pnl_match = re.search(r'\(([-\d.]+)%\)', pnl_text)
                if pnl_match:
                    drawdown_percent = abs(float(pnl_match.group(1)))
                    if drawdown_percent > 5:  # 5% threshold
                        alerts.append(f"DRAWDOWN CRITICAL: Level reached {drawdown_percent:.1f}%")
            
            # Check for critical keywords
            if 'stop_loss_triggered' in page_text:
                alerts.append("ORDER: Stop-loss triggered")
            if 'take_profit_triggered' in page_text:
                alerts.append("ORDER: Take-profit triggered")
            if 'critical_drawdown' in page_text:
                alerts.append("CRITICAL: Extreme drawdown detected")
            if 'margin is insufficient' in page_text:
                alerts.append("CRITICAL: Insufficient margin")
            
            # Log parsed data
            log_to_file(f"--- Parsed Data ({datetime.datetime.now().isoformat()}) ---", TRADE_MONITORING_LOG)
            log_to_file(json.dumps(dashboard_data, indent=2), TRADE_MONITORING_LOG)
                
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
