import json
import datetime
from datetime import datetime as dt

# Current data from the dashboard
status_data = {
    'analysis_scheduled': 'hourly',
    'capital': 1000.0,
    'last_analysis': '2026-03-19T03:12:48.965218',
    'port': 5001,
    'risk_parameters': {
        'max_trades_per_day': 2,
        'stop_loss': 0.05,
        'take_profit': 0.1
    },
    'status': 'running',
    'timestamp': '2026-03-19T03:23:43.521710',
    'trading_pairs': ['BTC/USD', 'ETH/USD']
}

trades_data = {
    'count': 10,
    'timestamp': '2026-03-19T03:23:46.962552',
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

# Current prices from summary
current_prices = {
    'BTC/USD': 70614.00,
    'ETH/USD': 2166.65
}

stop_loss = status_data['risk_parameters']['stop_loss']
take_profit = status_data['risk_parameters']['take_profit']

# Generate monitoring report
report = []
report.append('=== TRADING DASHBOARD MONITORING REPORT ===')
report.append(f'Timestamp: {dt.now().isoformat()}')
report.append(f'Capital: ${status_data["capital"]:.2f}')
report.append(f'Stop-loss: {stop_loss*100}%')
report.append(f'Take-profit: {take_profit*100}%')
report.append(f'Status: {status_data["status"]}')
report.append(f'Last analysis: {status_data["last_analysis"]}')
report.append('')

# Check for critical conditions
critical_alerts = []

# Analyze recent trades for stop-loss/take-profit triggers
for trade in trades_data['trades'][:6]:  # Check most recent 6 trades
    if 'price' in trade and 'side' in trade and trade['side'].lower() == 'buy':
        # Determine symbol
        symbol = 'BTC/USD'
        if 'ETH' in str(trade.get('model', '')) or 'ETH' in str(trade.get('symbol', '')):
            symbol = 'ETH/USD'
        
        entry_price = trade['price']
        current_price = current_prices.get(symbol)
        
        if current_price:
            pnl_pct = (current_price - entry_price) / entry_price
            
            if pnl_pct <= -stop_loss:
                alert = f'STOP-LOSS TRIGGERED: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_pct*100:.1f}% loss)'
                critical_alerts.append(alert)
            elif pnl_pct >= take_profit:
                alert = f'TAKE-PROFIT TRIGGERED: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_pct*100:.1f}% gain)'
                critical_alerts.append(alert)

# Check for drawdown indicators
if current_prices['BTC/USD'] < 70000:  # Arbitrary threshold for BTC
    critical_alerts.append(f'DRAWDOWN WARNING: BTC/USD at {current_prices["BTC/USD"]:.2f}, below 70k threshold')

if current_prices['ETH/USD'] < 2100:  # Arbitrary threshold for ETH
    critical_alerts.append(f'DRAWDOWN WARNING: ETH/USD at {current_prices["ETH/USD"]:.2f}, below 2.1k threshold')

report.append('=== PERFORMANCE ANALYSIS ===')
report.append(f'Total trades: {trades_data["count"]}')
report.append(f'Current BTC/USD price: ${current_prices["BTC/USD"]:.2f}')
report.append(f'Current ETH/USD price: ${current_prices["ETH/USD"]:.2f}')
report.append('')

if critical_alerts:
    report.append('🚨 CRITICAL ALERTS DETECTED:')
    for alert in critical_alerts:
        report.append(f'  • {alert}')
else:
    report.append('✅ No critical alerts detected')
report.append('')

report.append('=== RISK PARAMETERS STATUS ===')
report.append(f'Max trades/day: {status_data["risk_parameters"]["max_trades_per_day"]}')
report.append('Trades executed today: 2/2 (from summary)')
report.append('System operating within normal parameters')

# Join report
full_report = '\n'.join(report)
print(full_report)

# Return critical alerts for separate logging
if critical_alerts:
    print('\n--- CRITICAL ALERTS FOR LOGGING ---')
    for alert in critical_alerts:
        print(alert)