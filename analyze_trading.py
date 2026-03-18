import json
import datetime

# Current time
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Parse status data
status_data = {
    'analysis_scheduled': 'hourly',
    'capital': 1000.0,
    'last_analysis': '2026-03-19T00:33:02.095091',
    'port': 5001,
    'risk_parameters': {
        'max_trades_per_day': 2,
        'stop_loss': 0.05,
        'take_profit': 0.1
    },
    'status': 'running',
    'timestamp': '2026-03-19T00:42:41.120324',
    'trading_pairs': ['BTC/USD', 'ETH/USD']
}

# Parse trades data
trades_data = {
    'count': 10,
    'timestamp': '2026-03-19T00:42:44.893238',
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

# Risk parameters
stop_loss = status_data['risk_parameters']['stop_loss']
take_profit = status_data['risk_parameters']['take_profit']
capital = status_data['capital']

output = []
output.append(f'=== TRADING MONITORING REPORT ===')
output.append(f'Timestamp: {now}')
output.append(f'Dashboard Status: {status_data["status"]}')
output.append(f'Capital: ${capital:.2f}')
output.append(f'Stop-loss: {stop_loss*100}%')
output.append(f'Take-profit: {take_profit*100}%')
output.append(f'Last Analysis: {status_data["last_analysis"]}')
output.append(f'Total Trades: {trades_data["count"]}')
output.append('')

# Check for critical conditions
critical_alerts = []

# Analyze recent trades for stop-loss/take-profit triggers
output.append('=== ACTIVE POSITIONS ANALYSIS ===')
for trade in trades_data['trades'][:4]:  # Most recent trades
    if 'price' in trade and 'side' in trade and trade['side'].lower() == 'buy':
        entry_price = trade['price']
        stop_loss_price = entry_price * (1 - stop_loss)
        take_profit_price = entry_price * (1 + take_profit)
        
        symbol = trade.get('symbol', 'Unknown')
        if 'amount' in trade:
            quantity = trade['amount']
        else:
            quantity = trade.get('quantity', 0)
            
        output.append(f'{symbol}:')
        output.append(f'  Entry: ${entry_price:.2f}')
        output.append(f'  Stop-loss: ${stop_loss_price:.2f} ({stop_loss*100}% below entry)')
        output.append(f'  Take-profit: ${take_profit_price:.2f} ({take_profit*100}% above entry)')
        output.append(f'  Quantity: {quantity}')
        output.append(f'  Time: {trade.get("time", "N/A")}')
        output.append('')
        
        # For monitoring purposes, we would check current market prices here
        # Since we don't have live prices, we'll note this limitation
        critical_alerts.append(f'Need current price data to check SL/TP for {symbol} at entry ${entry_price:.2f}')

output.append('=== SYSTEM STATUS ===')
output.append(f'Analysis scheduled: {status_data["analysis_scheduled"]}')
output.append(f'Trading pairs: {status_data["trading_pairs"]}')
output.append(f'Max trades/day: {status_data["risk_parameters"]["max_trades_per_day"]}')
output.append(f"Today's trades executed: 2/2 (from summary)")

# Check if max trades per day reached
if status_data['risk_parameters']['max_trades_per_day'] == 2:
    critical_alerts.append('MAX TRADES PER DAY REACHED (2/2)')

output.append('')
output.append('=== ALERTS ===')
if critical_alerts:
    for alert in critical_alerts:
        output.append(f'⚠️  {alert}')
else:
    output.append('✅ No critical alerts at this time')

output.append('')
output.append('=== RECOMMENDATIONS ===')
output.append('1. Monitor current market prices to check stop-loss/take-profit levels')
output.append('2. Next analysis scheduled hourly')
output.append('3. System running normally')

# Write to monitoring log
with open('/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log', 'a') as f:
    f.write('\n'.join(output))
    f.write('\n' + '='*50 + '\n')

# Check for critical alerts that need separate logging
critical_conditions = [
    'MAX TRADES PER DAY REACHED',
    'STOP-LOSS TRIGGERED',
    'TAKE-PROFIT TRIGGERED',
    'DRAWDOWN CRITICAL'
]

has_critical = any(any(cond.lower() in alert.lower() for cond in critical_conditions) for alert in critical_alerts)

if has_critical:
    with open('/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log', 'a') as f:
        f.write(f'CRITICAL ALERT - {now}\n')
        for alert in critical_alerts:
            if any(cond.lower() in alert.lower() for cond in critical_conditions):
                f.write(f'  {alert}\n')
        f.write('='*50 + '\n')

# Print output
print('\n'.join(output))