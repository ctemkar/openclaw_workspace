import json
import datetime

# Current time
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Current prices from dashboard summary
btc_current = 70726.13
eth_current = 2192.39

# Trades data (simplified for analysis)
trades = [
    {'symbol': 'ETH/USD', 'price': 2331.78, 'amount': 0.00428857, 'time': '10:21:22'},
    {'symbol': 'BTC/USD', 'price': 74335.92, 'amount': 0.00013452, 'time': '10:21:21'},
    {'symbol': 'BTC/USD', 'price': 74308.0, 'amount': 0.00013458, 'time': '10:20:26'},
    {'symbol': 'BTC/USD', 'price': 74308.79, 'amount': 0.00013457, 'time': '10:18:29'},
    {'symbol': 'BTC/USD', 'price': 74332.65, 'amount': 0.00013453, 'time': '10:14:36'},
    {'symbol': 'BTC/USD', 'price': 74319.47, 'amount': 0.00013455, 'time': '10:14:33'},
    {'symbol': 'BTC/USD', 'price': 74094.64, 'amount': 0.002699, 'time': '13:39:48'},
    {'symbol': 'ETH/USD', 'price': 2325.28, 'amount': 0.086, 'time': '13:39:49'},
    {'symbol': 'BTC/USD', 'price': 71386.0, 'amount': 0.002802, 'time': '00:33:00'},
    {'symbol': 'ETH/USD', 'price': 2193.6, 'amount': 0.0912, 'time': '00:33:02'}
]

print('=== POSITION ANALYSIS ===')
print(f'Analysis Time: {now}')
print(f'Current BTC Price: ${btc_current:,.2f}')
print(f'Current ETH Price: ${eth_current:,.2f}')
print()

# Analyze ETH positions
print('ETH/USD POSITIONS:')
eth_positions = [t for t in trades if 'ETH' in t['symbol']]
for i, trade in enumerate(eth_positions, 1):
    entry = trade['price']
    amount = trade['amount']
    drawdown = ((eth_current - entry) / entry) * 100
    stop_loss_price = entry * 0.95  # 5% stop-loss
    distance_to_stop = ((eth_current - stop_loss_price) / entry) * 100
    
    print(f'  Position {i}:')
    print(f'    Entry: ${entry:,.2f}')
    print(f'    Amount: {amount:.6f} ETH')
    print(f'    Current: ${eth_current:,.2f}')
    print(f'    Drawdown: {drawdown:.2f}%')
    print(f'    Stop-loss Price: ${stop_loss_price:,.2f}')
    print(f'    Distance to Stop: {distance_to_stop:.2f}%')
    if drawdown <= -5:
        print(f'    ⚠️  STOP-LOSS TRIGGERED!')
    elif drawdown <= -4.5:
        print(f'    🚨 HIGH RISK: Approaching stop-loss')
    elif drawdown <= -4:
        print(f'    ⚠️  MONITOR: Close to stop-loss')
    print()

# Analyze BTC positions
print('BTC/USD POSITIONS:')
btc_positions = [t for t in trades if 'BTC' in t['symbol']]
for i, trade in enumerate(btc_positions, 1):
    entry = trade['price']
    amount = trade['amount']
    drawdown = ((btc_current - entry) / entry) * 100
    stop_loss_price = entry * 0.95  # 5% stop-loss
    distance_to_stop = ((btc_current - stop_loss_price) / entry) * 100
    
    print(f'  Position {i}:')
    print(f'    Entry: ${entry:,.2f}')
    print(f'    Amount: {amount:.6f} BTC')
    print(f'    Current: ${btc_current:,.2f}')
    print(f'    Drawdown: {drawdown:.2f}%')
    print(f'    Stop-loss Price: ${stop_loss_price:,.2f}')
    print(f'    Distance to Stop: {distance_to_stop:.2f}%')
    if drawdown <= -5:
        print(f'    ⚠️  STOP-LOSS TRIGGERED!')
    elif drawdown <= -4.5:
        print(f'    ⚠️  MONITOR: Close to stop-loss')
    print()

# Overall risk assessment
print('=== RISK ASSESSMENT ===')
print(f'Capital: $1,000.00')
print(f'Stop-loss: 5%')
print(f'Take-profit: 10%')
print(f'Max trades/day: 2/2 (limit reached)')
print()

# Check for critical conditions
critical_eth = any(((eth_current - t['price']) / t['price']) * 100 <= -5 for t in eth_positions)
critical_btc = any(((btc_current - t['price']) / t['price']) * 100 <= -5 for t in btc_positions)

if critical_eth or critical_btc:
    print('🚨 CRITICAL ALERT: Stop-loss triggered!')
elif any(((eth_current - t['price']) / t['price']) * 100 <= -4.5 for t in eth_positions) or any(((btc_current - t['price']) / t['price']) * 100 <= -4.5 for t in btc_positions):
    print('⚠️  HIGH MONITORING: Positions approaching stop-loss')
else:
    print('✅ All positions within safe limits')