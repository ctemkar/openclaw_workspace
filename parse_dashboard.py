#!/usr/bin/env python3
import re
from datetime import datetime
import json

# Read the HTML content
with open('dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Extract key information using regex patterns
def extract_info(html):
    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'system_status': {},
        'pnl': {},
        'bot_status': [],
        'risk_parameters': {},
        'market_data': [],
        'logs': [],
        'critical_alerts': []
    }
    
    # Extract System Status
    system_match = re.search(r'Total Capital.*?(\d+\.?\d*)\$', html)
    if system_match:
        data['system_status']['total_capital'] = float(system_match.group(1))
    
    active_bots_match = re.search(r'Active Bots.*?(\d+)', html)
    if active_bots_match:
        data['system_status']['active_bots'] = int(active_bots_match.group(1))
    
    trades_today_match = re.search(r'Trades Today.*?(\d+)', html)
    if trades_today_match:
        data['system_status']['trades_today'] = int(trades_today_match.group(1))
    
    max_trades_match = re.search(r'Max/Day.*?(\d+)', html)
    if max_trades_match:
        data['system_status']['max_daily_trades'] = int(max_trades_match.group(1))
    
    # Extract P&L
    total_pnl_match = re.search(r'Total P&L.*?([-\d\.]+)\$', html)
    if total_pnl_match:
        data['pnl']['total'] = float(total_pnl_match.group(1))
    
    gemini_pnl_match = re.search(r'Gemini.*?([-\d\.]+)\$', html)
    if gemini_pnl_match:
        data['pnl']['gemini'] = float(gemini_pnl_match.group(1))
    
    binance_pnl_match = re.search(r'Binance.*?([-\d\.]+)\$', html)
    if binance_pnl_match:
        data['pnl']['binance'] = float(binance_pnl_match.group(1))
    
    # Extract Bot Status
    bot_pattern = r'<strong>([^<]+)</strong>.*?status-badge status-(\w+).*?PID: (\d+).*?Uptime: ([^<]+).*?CPU: ([^<]+).*?Mem: ([^<]+)'
    bot_matches = re.findall(bot_pattern, html, re.DOTALL)
    for bot_name, status, pid, uptime, cpu, mem in bot_matches:
        data['bot_status'].append({
            'name': bot_name.strip(),
            'status': status.upper(),
            'pid': int(pid),
            'uptime': uptime.strip(),
            'cpu': cpu.strip(),
            'memory': mem.strip()
        })
    
    # Extract Risk Parameters
    stop_loss_match = re.search(r'Stop Loss.*?(\d+\.?\d*)%', html)
    if stop_loss_match:
        data['risk_parameters']['stop_loss'] = float(stop_loss_match.group(1))
    
    take_profit_match = re.search(r'Take Profit.*?(\d+\.?\d*)%', html)
    if take_profit_match:
        data['risk_parameters']['take_profit'] = float(take_profit_match.group(1))
    
    position_size_match = re.search(r'Position Size.*?(\d+\.?\d*)%', html)
    if position_size_match:
        data['risk_parameters']['position_size'] = float(position_size_match.group(1))
    
    # Extract Market Data
    market_pattern = r'<strong>([^<]+)</strong>.*?\$([\d\.]+).*?([-\d\.]+)%'
    market_matches = re.findall(market_pattern, html)
    for symbol, price, change in market_matches:
        data['market_data'].append({
            'symbol': symbol.strip(),
            'price': float(price),
            'change_percent': float(change)
        })
    
    # Extract Logs
    log_pattern = r'real_trading\.log: ([^<]+)'
    log_matches = re.findall(log_pattern, html)
    for log in log_matches:
        if 'ERROR' in log or 'WARNING' in log or 'CRITICAL' in log:
            data['logs'].append(log.strip())
    
    # Extract Critical Alerts
    alert_pattern = r'critical_alerts\.log: ([^<]+)'
    alert_matches = re.findall(alert_pattern, html)
    for alert in alert_matches:
        if 'CRITICAL' in alert or 'WARNING' in alert:
            data['critical_alerts'].append(alert.strip())
    
    return data

# Parse the data
parsed_data = extract_info(html_content)

# Write to monitoring log
with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
    f.write(f"\n=== Trading Dashboard Analysis - {parsed_data['timestamp']} ===\n")
    f.write(f"System Status: Total Capital: ${parsed_data['system_status'].get('total_capital', 0):.2f}, ")
    f.write(f"Active Bots: {parsed_data['system_status'].get('active_bots', 0)}, ")
    f.write(f"Trades Today: {parsed_data['system_status'].get('trades_today', 0)}/{parsed_data['system_status'].get('max_daily_trades', 0)}\n")
    
    f.write(f"P&L: Total: ${parsed_data['pnl'].get('total', 0):.2f}, ")
    f.write(f"Gemini: ${parsed_data['pnl'].get('gemini', 0):.2f}, ")
    f.write(f"Binance: ${parsed_data['pnl'].get('binance', 0):.2f}\n")
    
    f.write("Bot Status:\n")
    for bot in parsed_data['bot_status']:
        f.write(f"  - {bot['name']}: {bot['status']} (PID: {bot['pid']}, Uptime: {bot['uptime']})\n")
    
    f.write(f"Risk Parameters: Stop Loss: {parsed_data['risk_parameters'].get('stop_loss', 0)}%, ")
    f.write(f"Take Profit: {parsed_data['risk_parameters'].get('take_profit', 0)}%, ")
    f.write(f"Position Size: {parsed_data['risk_parameters'].get('position_size', 0)}%\n")
    
    f.write("Market Data:\n")
    for market in parsed_data['market_data']:
        f.write(f"  - {market['symbol']}: ${market['price']:.2f} ({market['change_percent']:+.2f}%)\n")
    
    if parsed_data['logs']:
        f.write("Recent Logs:\n")
        for log in parsed_data['logs'][:5]:  # Last 5 logs
            f.write(f"  - {log}\n")
    
    f.write("=" * 60 + "\n")

# Write critical alerts to separate file
critical_alerts = [alert for alert in parsed_data['critical_alerts'] if 'CRITICAL' in alert]
if critical_alerts:
    with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
        f.write(f"\n=== Critical Alerts - {parsed_data['timestamp']} ===\n")
        for alert in critical_alerts:
            f.write(f"{alert}\n")
        f.write("=" * 60 + "\n")

# Generate summary
print(f"Trading Dashboard Analysis - {parsed_data['timestamp']}")
print(f"System Status: Total Capital: ${parsed_data['system_status'].get('total_capital', 0):.2f}")
print(f"Active Bots: {parsed_data['system_status'].get('active_bots', 0)} running")
print(f"Trades Today: {parsed_data['system_status'].get('trades_today', 0)}/{parsed_data['system_status'].get('max_daily_trades', 0)}")
print(f"P&L: Total: ${parsed_data['pnl'].get('total', 0):.2f}")
print(f"Risk Parameters: SL: {parsed_data['risk_parameters'].get('stop_loss', 0)}%, TP: {parsed_data['risk_parameters'].get('take_profit', 0)}%")

if critical_alerts:
    print("\n⚠️ CRITICAL ALERTS DETECTED:")
    for alert in critical_alerts[:3]:  # Show top 3 critical alerts
        print(f"  - {alert}")
else:
    print("\n✅ No critical alerts detected.")