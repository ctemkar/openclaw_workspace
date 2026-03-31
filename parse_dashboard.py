import re
import json
from datetime import datetime

# Read the HTML content
with open('/Users/chetantemkar/.openclaw/workspace/app/dashboard.html', 'r') as f:
    html_content = f.read()

# Extract key data using regex patterns
def extract_data(html):
    data = {}
    
    # Extract timestamp
    timestamp_match = re.search(r'Updated: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', html)
    if timestamp_match:
        data['timestamp'] = timestamp_match.group(1)
    
    # Extract cumulative P&L
    initial_capital_match = re.search(r'Initial Capital.*?\$([\d,]+\.?\d*)', html)
    current_capital_match = re.search(r'Current Capital.*?\$([\d,]+\.?\d*)', html)
    cumulative_pnl_match = re.search(r'Cumulative P&L.*?\$(-?\d+\.?\d*)\s*\((-?\d+\.?\d*)%\)', html)
    
    if initial_capital_match:
        data['initial_capital'] = float(initial_capital_match.group(1).replace(',', ''))
    if current_capital_match:
        data['current_capital'] = float(current_capital_match.group(1).replace(',', ''))
    if cumulative_pnl_match:
        data['cumulative_pnl_amount'] = float(cumulative_pnl_match.group(1))
        data['cumulative_pnl_percent'] = float(cumulative_pnl_match.group(2))
    
    # Extract Gemini P&L
    gemini_pnl_match = re.search(r'GEMINI P&L.*?\$\+?(-?\d+\.?\d*)', html)
    if gemini_pnl_match:
        data['gemini_pnl'] = float(gemini_pnl_match.group(1))
    
    # Extract Binance status
    binance_status_match = re.search(r'BINANCE P&L.*?\n.*?<p>(.*?)</p>', html, re.DOTALL)
    if binance_status_match:
        data['binance_status'] = binance_status_match.group(1).strip()
    
    # Extract short trades status
    short_positions_match = re.search(r'Binance SHORT positions: (\d+)', html)
    if short_positions_match:
        data['short_positions'] = int(short_positions_match.group(1))
    
    # Extract capital allocation
    total_capital_match = re.search(r'Total Capital.*?\$([\d,]+\.?\d*)', html)
    gemini_capital_match = re.search(r'Gemini Capital.*?\$([\d,]+\.?\d*)', html)
    binance_capital_match = re.search(r'Binance Capital.*?\$([\d,]+\.?\d*)', html)
    deployed_match = re.search(r'Deployed.*?\$([\d,]+\.?\d*)', html)
    available_match = re.search(r'Available.*?\$([\d,]+\.?\d*)', html)
    
    if total_capital_match:
        data['total_capital'] = float(total_capital_match.group(1).replace(',', ''))
    if gemini_capital_match:
        data['gemini_capital'] = float(gemini_capital_match.group(1).replace(',', ''))
    if binance_capital_match:
        data['binance_capital'] = float(binance_capital_match.group(1).replace(',', ''))
    if deployed_match:
        data['deployed_capital'] = float(deployed_match.group(1).replace(',', ''))
    if available_match:
        data['available_capital'] = float(available_match.group(1).replace(',', ''))
    
    return data

# Parse the data
parsed_data = extract_data(html_content)

# Calculate additional metrics
if 'initial_capital' in parsed_data and 'current_capital' in parsed_data:
    parsed_data['drawdown_amount'] = parsed_data['initial_capital'] - parsed_data['current_capital']
    parsed_data['drawdown_percent'] = (parsed_data['drawdown_amount'] / parsed_data['initial_capital']) * 100

# Check for critical conditions
critical_alerts = []
if parsed_data.get('drawdown_percent', 0) > 20:
    critical_alerts.append(f"CRITICAL DRAWDOWN: {parsed_data['drawdown_percent']:.2f}% (exceeds 20% threshold)")
if parsed_data.get('available_capital', 0) < 100:
    critical_alerts.append(f"LOW AVAILABLE CAPITAL: ${parsed_data.get('available_capital', 0):.2f}")

# Print results
print("=== TRADING DASHBOARD MONITORING ===")
print(f"Timestamp: {parsed_data.get('timestamp', 'N/A')}")
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

print("=== CUMULATIVE PERFORMANCE ===")
print(f"Initial Capital: ${parsed_data.get('initial_capital', 0):.2f}")
print(f"Current Capital: ${parsed_data.get('current_capital', 0):.2f}")
print(f"Drawdown: ${parsed_data.get('drawdown_amount', 0):.2f} ({parsed_data.get('drawdown_percent', 0):.2f}%)")
print()

print("=== EXCHANGE PERFORMANCE ===")
print(f"Gemini P&L: ${parsed_data.get('gemini_pnl', 0):.2f}")
print(f"Binance Status: {parsed_data.get('binance_status', 'N/A')}")
print(f"Short Positions: {parsed_data.get('short_positions', 0)}")
print()

print("=== CAPITAL ALLOCATION ===")
print(f"Total Capital: ${parsed_data.get('total_capital', 0):.2f}")
print(f"Gemini Capital: ${parsed_data.get('gemini_capital', 0):.2f}")
print(f"Binance Capital: ${parsed_data.get('binance_capital', 0):.2f}")
print(f"Deployed: ${parsed_data.get('deployed_capital', 0):.2f}")
print(f"Available: ${parsed_data.get('available_capital', 0):.2f}")
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
    f.write(json.dumps(parsed_data, indent=2) + "\n")
    f.write(f"\nDrawdown Analysis: {parsed_data.get('drawdown_percent', 0):.2f}%\n")
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
        f.write(f"Drawdown: {parsed_data.get('drawdown_percent', 0):.2f}%\n")
        f.write(f"Available Capital: ${parsed_data.get('available_capital', 0):.2f}\n")