import json
import datetime

# Current market prices from CoinGecko
btc_price = 67436
eth_price = 2057.66

# Get current time
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Calculate P&L for each trade
trades = [
    {'symbol': 'ETH/USD', 'price': 2325.28, 'quantity': 0.086, 'time': '13:39:49'},
    {'symbol': 'ETH/USD', 'price': 2193.6, 'quantity': 0.0912, 'time': '00:33:02'},
    {'symbol': 'BTC/USD', 'price': 67247.51, 'quantity': 0.002974, 'time': '21:29:41'},
    {'symbol': 'ETH/USD', 'price': 2052.38, 'quantity': 0.0974, 'time': '21:29:42'},
    {'symbol': 'ETH/USD', 'price': 2021.51, 'quantity': 0.2474, 'time': '07:24:00'}
]

critical_alerts = []
total_pnl = 0
total_investment = 0

report = []
report.append('=== TRADING DASHBOARD MONITORING REPORT ===')
report.append(f'Time: {now} (Asia/Bangkok)')
report.append('Dashboard Status: running')
report.append('Last Analysis: 2026-03-31T13:21:25.096059')
report.append(f'Capital: $175.53 (DECREASED from $250.00 - 29.79% reduction)')
report.append(f'Current Prices: BTC=${btc_price}, ETH=${eth_price:.2f}')
report.append('')
report.append('Risk Parameters:')
report.append('- Stop Loss: 5.0%')
report.append('- Take Profit: 10.0%')
report.append('- Max Trades/Day: 2')
report.append('')
report.append('TRADE ANALYSIS:')
report.append('')

for i, trade in enumerate(trades, 1):
    symbol = trade['symbol']
    entry = trade['price']
    qty = trade['quantity']
    
    if 'BTC' in symbol:
        current = btc_price
    else:
        current = eth_price
    
    pnl = (current - entry) * qty
    pnl_percent = ((current - entry) / entry) * 100
    total_pnl += pnl
    total_investment += entry * qty
    
    stop_loss_price = entry * 0.95
    take_profit_price = entry * 1.10
    
    stop_triggered = current <= stop_loss_price
    take_triggered = current >= take_profit_price
    
    report.append(f'Trade {i}: {symbol} BUY @ ${entry:.2f} ({trade["time"]})')
    report.append(f'  Quantity: {qty}')
    report.append(f'  Current: ${current:.2f}')
    report.append(f'  P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)')
    report.append(f'  Stop-loss: ${stop_loss_price:.2f} (5.0%) - {"TRIGGERED" if stop_triggered else "SAFE"}')
    report.append(f'  Take-profit: ${take_profit_price:.2f} (10.0%) - {"TRIGGERED" if take_triggered else "PENDING"}')
    
    if stop_triggered:
        status = 'STOP-LOSS TRIGGERED - CRITICAL'
        critical_alerts.append({
            'trade': i,
            'symbol': symbol,
            'entry': entry,
            'current': current,
            'loss': pnl,
            'loss_percent': pnl_percent,
            'time': trade['time'],
            'type': 'STOP_LOSS'
        })
    elif take_triggered:
        status = 'TAKE-PROFIT TRIGGERED - SUCCESS'
    else:
        status = 'ACTIVE'
    
    report.append(f'  Status: {status}')
    report.append('')

# Calculate overall metrics
drawdown = (total_pnl / total_investment * 100) if total_investment > 0 else 0
capital_remaining = 175.53 + total_pnl

report.append('OVERALL PERFORMANCE:')
report.append(f'Total Investment: ${total_investment:.2f}')
report.append(f'Total P&L: ${total_pnl:+.2f}')
report.append(f'Overall Return: {drawdown:+.2f}%')
report.append(f'Capital Remaining: ${capital_remaining:.2f}')
report.append('')

# Check for critical conditions
if capital_remaining < 125:  # More than 50% drawdown from $250
    critical_alerts.append({
        'type': 'CAPITAL_DRAWDOWN',
        'current': capital_remaining,
        'original': 250.00,
        'drawdown': ((250 - capital_remaining) / 250 * 100)
    })
    report.append('⚠️  CRITICAL: Capital drawdown exceeds 50% of original!')

stop_loss_count = len([a for a in critical_alerts if a['type'] == 'STOP_LOSS'])
if stop_loss_count >= 2:
    critical_alerts.append({
        'type': 'MULTIPLE_STOP_LOSSES',
        'count': stop_loss_count
    })
    report.append(f'⚠️  CRITICAL: {stop_loss_count} stop-losses triggered!')

report.append('=' * 60)

# Print report
print('\n'.join(report))

# Print critical alerts summary
if critical_alerts:
    print('\n=== CRITICAL ALERTS DETECTED ===')
    for alert in critical_alerts:
        if alert['type'] == 'STOP_LOSS':
            print(f'STOP-LOSS TRIGGERED: Trade {alert["trade"]} - {alert["symbol"]}')
            print(f'  Entry: ${alert["entry"]:.2f}, Current: ${alert["current"]:.2f}')
            print(f'  Loss: ${alert["loss"]:.2f} ({alert["loss_percent"]:.2f}%)')
        elif alert['type'] == 'CAPITAL_DRAWDOWN':
            print(f'CAPITAL DRAWDOWN: ${alert["current"]:.2f} remaining (from ${alert["original"]:.2f})')
            print(f'  Drawdown: {alert["drawdown"]:.2f}%')
        elif alert['type'] == 'MULTIPLE_STOP_LOSSES':
            print(f'MULTIPLE STOP-LOSSES: {alert["count"]} trades hit stop-loss')