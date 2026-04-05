#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

def parse_dashboard():
    try:
        response = requests.get('http://localhost:5009/', timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract timestamp
        timestamp_elem = soup.find('div', class_='timestamp')
        timestamp = timestamp_elem.text.strip().replace('Last updated: ', '') if timestamp_elem else 'Unknown'
        
        # Extract key data
        data = {
            'timestamp': timestamp,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dashboard_status': 'ACTIVE' if response.status_code == 200 else 'INACTIVE'
        }
        
        # Find all data cards
        data_cards = soup.find_all('div', class_='data-card')
        for card in data_cards:
            h3 = card.find('h3')
            if h3:
                key = h3.text.strip()
                value_elem = card.find('div', class_='data-value')
                if value_elem:
                    value = value_elem.text.strip()
                    # Clean up the value
                    value = re.sub(r'\s+', ' ', value)
                    data[key] = value
        
        # Extract deployed/available capital
        deployed_available = soup.find('p')
        if deployed_available and 'Deployed:' in deployed_available.text:
            text = deployed_available.text
            deployed_match = re.search(r'Deployed:\s*\$([\d.]+)', text)
            available_match = re.search(r'Available:\s*\$([\d.]+)', text)
            if deployed_match:
                data['Deployed Capital'] = f"${deployed_match.group(1)}"
            if available_match:
                data['Available Capital'] = f"${available_match.group(1)}"
        
        # Check for critical keywords in the entire page
        page_text = soup.get_text().lower()
        critical_keywords = {
            'stop_loss_triggered': 'stop_loss_triggered' in page_text,
            'take_profit_triggered': 'take_profit_triggered' in page_text,
            'critical_drawdown': 'critical_drawdown' in page_text,
            'margin is insufficient': 'margin is insufficient' in page_text,
            'error': 'error' in page_text,
            'failed': 'failed' in page_text
        }
        
        data['critical_alerts'] = {k: v for k, v in critical_keywords.items() if v}
        
        return data
    except Exception as e:
        return {
            'error': str(e),
            'dashboard_status': 'ERROR',
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

if __name__ == '__main__':
    result = parse_dashboard()
    print(json.dumps(result, indent=2))