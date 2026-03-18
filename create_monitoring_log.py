import json
from datetime import datetime

# Get current timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

# Parse the status data
status_data = '''{"analysis_scheduled":"hourly","capital":1000.0,"last_analysis":"2026-03-18T15:52:23.161039","port":5001,"risk_parameters":{"max_trades_per_day":2,"stop_loss":0.05,"take_profit":0.1},"status":"running","timestamp":"2026-03-18T15:56:49.745148","trading_pairs":["BTC/USD","ETH/USD"]}'''

status = json.loads(status_data)

# Parse trades data
trades_data = '''{"count":12,"timestamp":"2026-03-18T15:56:49.752741","trades":[{"amount":0.00013515202913877747,"model":"Gemini-Pro","price":73990.75,"side":"buy","status":"filled","time":"15:05:29"},{"amount":0.00013522648610865638,"model":"Gemini-Pro","price":73950.01,"side":"buy","status":"filled","time":"15:05:28"},{"amount":0.00013452624028485123,"model":"Gemini","price":74334.94,"side":"buy","status":"filled","time":"10:21:28"},{"amount":0.10531637037661135,"model":"LLM_Analysis_SOL_USD","price":94.952,"side":"sell","status":"filled","time":"10:21:23"},{"amount":0.00428856924752764,"model":"LLM_Analysis_ETH_USD","price":2331.78,"side":"buy","status":"filled","time":"10:21:22"},{"amount":0.0001345244667719186,"model":"LLM_Analysis_BTC_USD","price":74335.92,"side":"buy","status":"filled","time":"10:21:21"},{"amount":0.0001345750121117511,"model":"Gemini","price":74308.0,"side":"buy","status":"filled","time":"10:20:26"},{"amount":0.00013457358140268468,"model":"Gemini","price":74308.79,"side":"buy","status":"filled","time":"10:18:29"},{"amount":0.00013453038469636157,"model":"Gemini","price":74332.65,"side":"buy","status":"filled","time":"10:14:36"},{"amount":0.00013455424265000813,"model":"Gemini","price":74319.47,"side":"buy","status":"filled","time":"10:14:33"},{"price":74094.64,"quantity":0.002699,"reason":"Near support level: $73556.12 (current: $74094.64)","side":"BUY","symbol":"BTC/USD","time":"13:39:48"},{"price":2325.28,"quantity":0.086,"reason":"Near support level: $2308.08 (current: $2325.28)","side":"BUY","symbol":"ETH/USD","time":"13:39:49"}]}'''

trades = json.loads(trades_data)

# Current prices from summary
current_btc_price = 74083.87
current_eth_price = 2325.41

# Analyze positions
buy_trades = [t for t in trades['trades'] if t.get('side', '').lower() == 'buy']
btc_buys = [t for t in buy_trades if 'BTC' in str(t.get('symbol', '')) or 'btc' in str(t.get('model', '')).lower()]
eth_buys = [t for t in buy_trades if 'ETH' in str(t.get('symbol', '')) or 'eth' in str(t.get('model', '')).lower()]

# Check for critical conditions
critical_alerts = []
warnings = []

for trade in btc_buys:
    price = trade.get('price', 0)
    stop_loss = price * 0.95
    take_profit = price * 1.10
    
    if current_btc_price <= stop_loss:
        alert = f"CRITICAL: BTC position at ${price:.2f} has hit STOP-LOSS at ${stop_loss:.2f} (current: ${current_btc_price:.2f})"
        critical_alerts.append(alert)
    elif current_btc_price >= take_profit:
        alert = f"TAKE-PROFIT: BTC position at ${price:.2f} has reached TAKE-PROFIT at ${take_profit:.2f} (current: ${current_btc_price:.2f})"
        critical_alerts.append(alert)
    else:
        drawdown = (price - current_btc_price) / price * 100
        if drawdown > 3:
            warning = f"WARNING: BTC position at ${price:.2f} has {drawdown:.1f}% drawdown (current: ${current_btc_price:.2f})"
            warnings.append(warning)

for trade in eth_buys:
    price = trade.get('price', 0)
    stop_loss = price * 0.95
    take_profit = price * 1.10
    
    if current_eth_price <= stop_loss:
        alert = f"CRITICAL: ETH position at ${price:.2f} has hit STOP-LOSS at ${stop_loss:.2f} (current: ${current_eth_price:.2f})"
        critical_alerts.append(alert)
    elif current_eth_price >= take_profit:
        alert = f"TAKE-PROFIT: ETH position at ${price:.2f} has reached TAKE-PROFIT at ${take_profit:.2f} (current: ${current_eth_price:.2f})"
        critical_alerts.append(alert)
    else:
        drawdown = (price - current_eth_price) / price * 100
        if drawdown > 3:
            warning = f"WARNING: ETH position at ${price:.2f} has {drawdown:.1f}% drawdown (current: ${current_eth_price:.2f})"
            warnings.append(warning)

# Create monitoring log entry
log_entry = f"""=== TRADING DASHBOARD MONITORING LOG ===
Timestamp: {current_time} (Local) | {utc_time}
Dashboard URL: http://localhost:5001/

SYSTEM STATUS:
- Status: {status['status']}
- Capital: ${status['capital']:.2f}
- Last Analysis: {status['last_analysis']}
- Analysis Schedule: {status['analysis_scheduled']}
- Trading Pairs: {', '.join(status['trading_pairs'])}

RISK PARAMETERS:
- Stop-loss: {status['risk_parameters']['stop_loss']*100}%
- Take-profit: {status['risk_parameters']['take_profit']*100}%
- Max trades/day: {status['risk_parameters']['max_trades_per_day']}

TRADING ACTIVITY:
- Total trades: {trades['count']}
- Buy trades: {len(buy_trades)}
- Sell trades: {len([t for t in trades['trades'] if t.get('side', '').lower() == 'sell'])}
- Recent trades (last 2): {len([t for t in trades['trades'][:2] if 'time' in t])}

CURRENT PRICES (from analysis):
- BTC/USD: ${current_btc_price:.2f}
- ETH/USD: ${current_eth_price:.2f}

POSITION ANALYSIS:
BTC Positions: {len(btc_buys)}
ETH Positions: {len(eth_buys)}

ALERTS & WARNINGS:
Critical Alerts: {len(critical_alerts)}
Warnings: {len(warnings)}

{'='*60}
"""

# Add alerts if any
if critical_alerts:
    log_entry += "\nCRITICAL ALERTS:\n"
    for alert in critical_alerts:
        log_entry += f"  ⚠️ {alert}\n"

if warnings:
    log_entry += "\nWARNINGS:\n"
    for warning in warnings:
        log_entry += f"  ⚠️ {warning}\n"

log_entry += "\n" + "="*60 + "\n"

print(log_entry)

# Write to monitoring log
with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
    f.write(log_entry)

print(f"Monitoring log written to trading_monitoring.log")

# Write critical alerts to separate file if any
if critical_alerts:
    critical_log = f"""=== CRITICAL TRADING ALERTS ===
Timestamp: {current_time}

"""
    for alert in critical_alerts:
        critical_log += f"{alert}\n"
    
    critical_log += "\n" + "="*60 + "\n"
    
    with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
        f.write(critical_log)
    
    print(f"Critical alerts written to critical_alerts.log")
else:
    print("No critical alerts to log.")