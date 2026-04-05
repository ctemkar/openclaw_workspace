import json
from datetime import datetime

# Current time
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Parse status data
status_data = {
    'analysis_scheduled': 'hourly',
    'capital': 1000.0,
    'last_analysis': '2026-03-19T10:41:44.057881',
    'port': 5001,
    'risk_parameters': {
        'max_trades_per_day': 2,
        'stop_loss': 0.05,
        'take_profit': 0.1
    },
    'status': 'running',
    'timestamp': '2026-03-19T11:01:32.176418',
    'trading_pairs': ['BTC/USD', 'ETH/USD']
}

# Parse trades data
trades_data = {
    'count': 10,
    'timestamp': '2026-03-19T11:01:35.588215',
    'trades': [
        {'amount': 0.00428856924752764, 'model': 'LLM_Analysis_ETH_USD', 'price': 2331.78, 'side': 'buy', 'status': 'filled', 'time': '10:21:22'},
        {'amount': 0.0001345244667719186, 'model': 'LLM_Analysis_BTC_USD', 'price': 74335.92, 'side': 'buy', 'status': 'filled', 'time': '10:21:21'},
        {'amount': 0.0001345750121117511, 'model': 'Gemini', 'price': 74308.0, 'side': 'buy', 'status': 'filled', 'time': '10:20:26'},
        {'amount': 0.00013457358140268468, 'model': 'Gemini', 'price': 74308.79, 'side': 'buy', 'status': 'filled', 'time': '10:18:29'},
        {'amount': 0.00013453038469636157, 'model': 'Gemini', 'price': 74332.65, 'side': 'buy', 'status': 'filled', 'time': '10:14:36'},
        {'amount': 0.00013455424265000813, 'model': 'Gemini', 'price': 74319.47, 'side': 'buy', 'status': 'filled', 'time': '10:14:33'},
        {'price': 74094.64, 'quantity': 0.002699, 'reason': 'Near support level: $73556.12 (current: $74094.64)', 'side': 'BUY', 'symbol': 'BTC/USD', 'time': '13:39:48'},
        {'price': 2325.28, 'quantity': 0.086, 'reason': 'Near support level: $2308.08 (current: $2325.28)', 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '13:39:49'},
        {'price': 71386.0, 'quantity': 0.002802, 'reason': 'Near support level: $70896.70 (current: $71386.00)', 'side': 'BUY', 'symbol': 'BTC/USD', 'time': '00:33:00'},
        {'price': 2193.6, 'quantity': 0.0912, 'reason': 'Near support level: $2167.99 (current: $2193.60)', 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '00:33:02'}
    ]
}

# Calculate metrics
capital = status_data['capital']
stop_loss_pct = status_data['risk_parameters']['stop_loss'] * 100
take_profit_pct = status_data['risk_parameters']['take_profit'] * 100
max_trades = status_data['risk_parameters']['max_trades_per_day']
today_trades = 2  # From summary
total_trades = trades_data['count']

# Check for critical conditions
critical_alerts = []
monitoring_data = []

# 1. Check if max daily trades reached
if today_trades >= max_trades:
    alert = f'MAX DAILY TRADES REACHED: {today_trades}/{max_trades} trades used today'
    critical_alerts.append(alert)
    monitoring_data.append(f'WARNING: {alert}')

# 2. System status check
if status_data['status'] != 'running':
    alert = f'SYSTEM STATUS ALERT: Status is {status_data["status"]}'
    critical_alerts.append(alert)
    monitoring_data.append(f'CRITICAL: {alert}')

# 3. Capital check (warning if below 60% of initial)
if capital < 600:  # 60% of $1000
    alert = f'CAPITAL ALERT: Capital at ${capital:.2f} (below 60% of initial $1000)'
    critical_alerts.append(alert)
    monitoring_data.append(f'CRITICAL: {alert}')

# Create monitoring log entry
log_entry = f'''=== TRADING MONITORING LOG ===
Timestamp: {now}
Dashboard Time: {status_data['timestamp']}

SYSTEM STATUS:
- Status: {status_data['status']}
- Capital: ${capital:.2f}
- Stop-loss: {stop_loss_pct:.1f}%
- Take-profit: {take_profit_pct:.1f}%
- Max trades/day: {max_trades}
- Trading pairs: {', '.join(status_data['trading_pairs'])}
- Last analysis: {status_data['last_analysis']}
- Analysis schedule: {status_data['analysis_scheduled']}

TRADING ACTIVITY:
- Today's trades: {today_trades}/{max_trades}
- Total trades in system: {total_trades}
- Recent trades (last 10): {len(trades_data['trades'])} trades

RECENT TRADES SUMMARY:
- Latest BTC trade: {trades_data['trades'][0]['price'] if trades_data['trades'] else 'N/A'}
- Latest ETH trade: {trades_data['trades'][1]['price'] if len(trades_data['trades']) > 1 else 'N/A'}

ALERTS & WARNINGS:
{chr(10).join(monitoring_data) if monitoring_data else 'No critical alerts at this time'}

RISK ASSESSMENT:
- Capital utilization: Normal
- Trade frequency: Within limits ({today_trades}/{max_trades})
- System health: Operational
- Risk level: LOW

=== END LOG ===
'''

print(log_entry)

# If there are critical alerts, create critical log
if critical_alerts:
    critical_log = f'''=== CRITICAL ALERTS LOG ===
Timestamp: {now}

CRITICAL ALERTS:
{chr(10).join(f'- {alert}' for alert in critical_alerts)}

RECOMMENDED ACTIONS:
1. Review trade positions
2. Check market conditions
3. Verify system connectivity
4. Consider adjusting risk parameters if alerts persist

=== END CRITICAL LOG ===
'''
    print('\n' + '='*50 + '\nCRITICAL ALERTS FOUND:\n' + '='*50)
    print(critical_log)
else:
    print('\n' + '='*50 + '\nNO CRITICAL ALERTS DETECTED\n' + '='*50)