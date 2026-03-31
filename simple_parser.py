import re
import json
from datetime import datetime
import subprocess

# Fetch the latest dashboard HTML
try:
    result = subprocess.run(['curl', '-s', 'http://localhost:5008/'], 
                          capture_output=True, text=True, timeout=10)
    html = result.stdout
except:
    print("Failed to fetch dashboard")
    html = ""

if not html:
    print("No HTML content received")
    exit(1)

# Extract data using more robust patterns
data = {}

# Extract timestamp
timestamp_match = re.search(r'<em>Updated: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</em>', html)
if timestamp_match:
    data['timestamp'] = timestamp_match.group(1)

# Extract all dollar amounts with context
dollar_pattern = r'\$([\d,]+\.?\d*)'

# Find sections and extract
sections = html.split('<div class="section">')

for section in sections:
    # Cumulative P&L section
    if 'CUMULATIVE P&L' in section:
        # Find all dollar amounts in this section
        amounts = re.findall(dollar_pattern, section)
        if len(amounts) >= 3:
            try:
                data['initial_capital'] = float(amounts[0].replace(',', ''))
                data['current_capital'] = float(amounts[1].replace(',', ''))
                # The third amount might be negative, handle it
                if amounts[2].startswith('-'):
                    data['cumulative_pnl'] = float(amounts[2].replace(',', ''))
            except:
                pass
    
    # Capital Allocation section
    elif 'CAPITAL ALLOCATION' in section:
        # Look for table rows
        rows = re.findall(r'<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>', section, re.DOTALL)
        for row in rows:
            label = re.sub(r'<.*?>', '', row[0]).strip()
            value = re.sub(r'<.*?>', '', row[1]).strip()
            
            if 'Total Capital' in label:
                match = re.search(dollar_pattern, value)
                if match:
                    data['total_capital'] = float(match.group(1).replace(',', ''))
            elif 'Gemini Capital' in label:
                match = re.search(dollar_pattern, value)
                if match:
                    data['gemini_capital'] = float(match.group(1).replace(',', ''))
            elif 'Binance Capital' in label:
                match = re.search(dollar_pattern, value)
                if match:
                    data['binance_capital'] = float(match.group(1).replace(',', ''))
            elif 'Deployed' in label:
                match = re.search(dollar_pattern, value)
                if match:
                    data['deployed_capital'] = float(match.group(1).replace(',', ''))
            elif 'Available' in label:
                match = re.search(dollar_pattern, value)
                if match:
                    data['available_capital'] = float(match.group(1).replace(',', ''))

# Extract Gemini P&L
if 'GEMINI P&L' in html:
    gemini_section = html.split('GEMINI P&L')[1].split('</div>')[0]
    gemini_match = re.search(r'\$([+-]?\d+\.?\d*)', gemini_section)
    if gemini_match:
        data['gemini_pnl'] = float(gemini_match.group(1))

# Extract short positions
short_match = re.search(r'Binance SHORT positions: (\d+)', html)
if short_match:
    data['short_positions'] = int(short_match.group(1))

# Calculate drawdown if we have the data
if 'initial_capital' in data and 'current_capital' in data:
    data['drawdown_amount'] = data['initial_capital'] - data['current_capital']
    if data['initial_capital'] > 0:
        data['drawdown_percent'] = (data['drawdown_amount'] / data['initial_capital']) * 100
    else:
        data['drawdown_percent'] = 0

# Check for critical conditions
critical_alerts = []
if data.get('drawdown_percent', 0) > 20:
    critical_alerts.append(f"CRITICAL DRAWDOWN: {data['drawdown_percent']:.2f}% (exceeds 20% threshold)")
if data.get('available_capital', 0) < 100:
    critical_alerts.append(f"LOW AVAILABLE CAPITAL: ${data.get('available_capital', 0):.2f}")

# Print monitoring report
print("=== TRADING DASHBOARD MONITORING ===")
print(f"Timestamp: {data.get('timestamp', 'N/A')}")
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

print("=== CUMULATIVE PERFORMANCE ===")
print(f"Initial Capital: ${data.get('initial_capital', 0):.2f}")
print(f"Current Capital: ${data.get('current_capital', 0):.2f}")
print(f"Drawdown: ${data.get('drawdown_amount', 0):.2f} ({data.get('drawdown_percent', 0):.2f}%)")
print()

print("=== EXCHANGE PERFORMANCE ===")
print(f"Gemini P&L: ${data.get('gemini_pnl', 0):.2f}")
print(f"Short Positions: {data.get('short_positions', 0)}")
print()

print("=== CAPITAL ALLOCATION ===")
print(f"Total Capital: ${data.get('total_capital', 0):.2f}")
print(f"Gemini Capital: ${data.get('gemini_capital', 0):.2f}")
print(f"Binance Capital: ${data.get('binance_capital', 0):.2f}")
print(f"Deployed: ${data.get('deployed_capital', 0):.2f}")
print(f"Available: ${data.get('available_capital', 0):.2f}")
print()

if critical_alerts:
    print("=== CRITICAL ALERTS ===")
    for alert in critical_alerts:
        print(f"⚠️ {alert}")
else:
    print("=== STATUS: NORMAL ===")
    print("No critical alerts detected")

# Save to monitoring log
with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
    f.write(f"\n{'='*60}\n")
    f.write(f"MONITORING CHECK: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"{'='*60}\n")
    f.write(json.dumps(data, indent=2) + "\n")
    if 'drawdown_percent' in data:
        f.write(f"\nDrawdown Analysis: {data['drawdown_percent']:.2f}%\n")
    if critical_alerts:
        f.write(f"\nCRITICAL ALERTS:\n")
        for alert in critical_alerts:
            f.write(f"  - {alert}\n")

# Save critical alerts if any
if critical_alerts:
    with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"CRITICAL ALERT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n")
        for alert in critical_alerts:
            f.write(f"{alert}\n")
        f.write(f"\nContext:\n")
        if 'drawdown_percent' in data:
            f.write(f"Drawdown: {data['drawdown_percent']:.2f}%\n")
        f.write(f"Available Capital: ${data.get('available_capital', 0):.2f}\n")