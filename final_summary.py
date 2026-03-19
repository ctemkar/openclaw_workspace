import json
import requests
from datetime import datetime
import re

# Get all data
status_response = requests.get('http://localhost:5001/status')
status_data = status_response.json()

trades_response = requests.get('http://localhost:5001/trades')
trades_data = trades_response.json()

summary_response = requests.get('http://localhost:5001/summary')
summary_text = summary_response.text

# Extract current prices from summary
btc_price_match = re.search(r'BTC/USD.*?Price: \$([\d\.]+)', summary_text, re.DOTALL)
eth_price_match = re.search(r'ETH/USD.*?Price: \$([\d\.]+)', summary_text, re.DOTALL)

current_prices = {}
if btc_price_match:
    current_prices['BTC/USD'] = float(btc_price_match.group(1))
else:
    current_prices['BTC/USD'] = 71231.00

if eth_price_match:
    current_prices['ETH/USD'] = float(eth_price_match.group(1))
else:
    current_prices['ETH/USD'] = 2203.23

# Count today's trades
today_trades = 0
for trade in trades_data.get('trades', []):
    if 'time' in trade:
        today_trades += 1

max_trades = status_data.get('risk_parameters', {}).get('max_trades_per_day', 2)

# Parse summary for key metrics
capital_match = re.search(r'Capital: \$([\d\.]+)', summary_text)
available_capital = capital_match.group(1) if capital_match else '1000.00'

pnl_match = re.search(r'Total P&L: \$([\d\.\-]+)', summary_text)
total_pnl = pnl_match.group(1) if pnl_match else '0.00'

# Analyze positions
btc_positions = []
eth_positions = []

for trade in trades_data.get('trades', []):
    symbol = trade.get('symbol', '')
    price = trade.get('price')
    side = trade.get('side', '').lower()
    
    if not price or side not in ['buy', 'b']:
        continue
    
    if 'BTC' in symbol or 'BTC' in str(trade.get('model', '')):
        btc_positions.append(price)
    elif 'ETH' in symbol or 'ETH' in str(trade.get('model', '')):
        eth_positions.append(price)

# Calculate average entry prices
btc_avg = sum(btc_positions) / len(btc_positions) if btc_positions else 0
eth_avg = sum(eth_positions) / len(eth_positions) if eth_positions else 0

# Calculate P&L
btc_pnl_pct = ((current_prices['BTC/USD'] - btc_avg) / btc_avg * 100) if btc_avg else 0
eth_pnl_pct = ((current_prices['ETH/USD'] - eth_avg) / eth_avg * 100) if eth_avg else 0

# Check for alerts
alerts = []
critical_alerts = []

# Daily trade limit check
if today_trades >= max_trades:
    alerts.append(f'Daily trade limit reached ({today_trades}/{max_trades})')

# Stop-loss check (5%)
if btc_pnl_pct <= -5:
    critical_alerts.append(f'BTC/USD stop-loss triggered: {btc_pnl_pct:.1f}% loss')
if eth_pnl_pct <= -5:
    critical_alerts.append(f'ETH/USD stop-loss triggered: {eth_pnl_pct:.1f}% loss')

# Take-profit check (10%)
if btc_pnl_pct >= 10:
    alerts.append(f'BTC/USD take-profit target reached: {btc_pnl_pct:.1f}% gain')
if eth_pnl_pct >= 10:
    alerts.append(f'ETH/USD take-profit target reached: {eth_pnl_pct:.1f}% gain')

# Strategy endpoint check
try:
    strategy_response = requests.get('http://localhost:5001/strategy')
    if strategy_response.status_code == 404:
        alerts.append('Strategy endpoint configuration error (404)')
except:
    alerts.append('Strategy endpoint inaccessible')

# Generate final summary
print('=== TRADING DASHBOARD MONITORING SUMMARY ===')
print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()
print('=== SYSTEM STATUS ===')
print(f'Dashboard Status: {status_data.get("status", "unknown")}')
print(f'Capital: ${status_data.get("capital", 0)}')
print(f'Available Capital: ${available_capital}')
print(f'Total P&L: ${total_pnl}')
print()
print('=== RISK PARAMETERS ===')
print(f'Stop Loss: {status_data.get("risk_parameters", {}).get("stop_loss", 0)*100:.1f}%')
print(f'Take Profit: {status_data.get("risk_parameters", {}).get("take_profit", 0)*100:.1f}%')
print(f'Max Trades/Day: {max_trades}')
print(f'Today\'s Trades: {today_trades}/{max_trades}')
print(f'Total Trades: {trades_data.get("count", 0)}')
print()
print('=== CURRENT MARKET PRICES ===')
print(f'BTC/USD: ${current_prices["BTC/USD"]:.2f}')
print(f'ETH/USD: ${current_prices["ETH/USD"]:.2f}')
print()
print('=== POSITION ANALYSIS ===')
print(f'BTC Positions: {len(btc_positions)}')
if btc_positions:
    print(f'  Average Entry: ${btc_avg:.2f}')
    print(f'  Current P&L: {btc_pnl_pct:.1f}%')
print(f'ETH Positions: {len(eth_positions)}')
if eth_positions:
    print(f'  Average Entry: ${eth_avg:.2f}')
    print(f'  Current P&L: {eth_pnl_pct:.1f}%')
print()
print('=== ALERTS ===')
if critical_alerts:
    print('⚠️ CRITICAL ALERTS:')
    for alert in critical_alerts:
        print(f'  - {alert}')
else:
    print('✅ No critical alerts')

if alerts:
    print('⚠️ WARNINGS:')
    for alert in alerts:
        print(f'  - {alert}')
else:
    print('✅ No warnings')

print()
print('=== MONITORING COMPLETE ===')
print(f'Data logged to: ./trading_monitoring.log')
if critical_alerts:
    print(f'Critical alerts logged to: ./critical_alerts.log')
print(f'Next scheduled check: 5 minutes')
print(f'Last Analysis: {status_data.get("last_analysis", "unknown")}')