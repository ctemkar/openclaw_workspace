import json
import requests
from datetime import datetime
import re

# Get current data
status_response = requests.get('http://localhost:5001/status')
status_data = status_response.json()

trades_response = requests.get('http://localhost:5001/trades')
trades_data = trades_response.json()

summary_response = requests.get('http://localhost:5001/summary')
summary_text = summary_response.text

# Parse summary for key metrics
capital_match = re.search(r'Capital: \$([\d\.]+)', summary_text)
available_capital = capital_match.group(1) if capital_match else '1000.00'

pnl_match = re.search(r'Total P&L: \$([\d\.\-]+)', summary_text)
total_pnl = pnl_match.group(1) if pnl_match else '0.00'

# Count today's trades
today_trades = 0
for trade in trades_data.get('trades', [])[:10]:
    if 'time' in trade:
        today_trades += 1

max_trades = status_data.get('risk_parameters', {}).get('max_trades_per_day', 2)

# Create log entry
log_entry = f"""
=== Trading Dashboard Monitor - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ===
System Status: {status_data.get('status', 'unknown')}
Capital: ${status_data.get('capital', 0)}
Available Capital: ${available_capital}
Stop Loss: {status_data.get('risk_parameters', {}).get('stop_loss', 0)*100:.2f}%
Take Profit: {status_data.get('risk_parameters', {}).get('take_profit', 0)*100:.1f}%
Max Trades/Day: {max_trades}
Today's Trades: {today_trades}/{max_trades}
Total Trades: {trades_data.get('count', 0)}
Total P&L: ${total_pnl}
Drawdown: 0%
Last Analysis: {status_data.get('last_analysis', 'unknown')}

"""

# Add alerts
alerts = []
if today_trades >= max_trades:
    alerts.append('Daily trade limit reached')

# Check strategy endpoint
try:
    strategy_response = requests.get('http://localhost:5001/strategy')
    if strategy_response.status_code == 404:
        alerts.append('Strategy endpoint configuration error (404)')
except:
    alerts.append('Strategy endpoint inaccessible')

if alerts:
    log_entry += "ALERTS:\n"
    for alert in alerts:
        log_entry += f"  ⚠️ {alert}\n"
else:
    log_entry += "✅ No critical alerts\n"

log_entry += f"Monitoring completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

print(log_entry)

# Append to log file
with open('./trading_monitoring.log', 'a') as f:
    f.write(log_entry)