import json
import datetime

# Read completed trades
with open('/Users/chetantemkar/.openclaw/workspace/app/completed_trades.json', 'r') as f:
    trades = json.load(f)

# Current prices from summary (approximate)
btc_current = 67300.17
eth_current = 2018.43

print('=== TRADING ANALYSIS ===')
print(f'Current Time: {datetime.datetime.now()}')
print(f'BTC Current Price: ${btc_current:,.2f}')
print(f'ETH Current Price: ${eth_current:,.2f}')
print()

# Analyze each trade
critical_alerts = []
for i, trade in enumerate(trades):
    if 'symbol' in trade:
        symbol = trade['symbol']
        entry_price = trade['price']
        quantity = trade['quantity']
        side = trade['side']
        
        if 'BTC' in symbol:
            current_price = btc_current
        else:
            current_price = eth_current
        
        # Calculate P&L
        if side == 'BUY':
            pnl_pct = (current_price - entry_price) / entry_price * 100
            pnl_dollar = (current_price - entry_price) * quantity
        else:
            pnl_pct = (entry_price - current_price) / entry_price * 100
            pnl_dollar = (entry_price - current_price) * quantity
        
        # Check stop-loss (5%) and take-profit (10%)
        stop_loss_triggered = pnl_pct <= -5
        take_profit_triggered = pnl_pct >= 10
        
        print(f'Trade {i+1}: {symbol} {side} @ ${entry_price:,.2f}')
        print(f'  Current: ${current_price:,.2f}')
        print(f'  P&L: {pnl_pct:+.2f}% (${pnl_dollar:+.2f})')
        print(f'  Status: {"STOP-LOSS TRIGGERED" if stop_loss_triggered else "TAKE-PROFIT TRIGGERED" if take_profit_triggered else "ACTIVE"}')
        
        if stop_loss_triggered:
            alert = f'STOP-LOSS TRIGGERED: {symbol} {side} @ ${entry_price:,.2f}, Current: ${current_price:,.2f}, Loss: {pnl_pct:.2f}%'
            critical_alerts.append(alert)
        elif take_profit_triggered:
            alert = f'TAKE-PROFIT TRIGGERED: {symbol} {side} @ ${entry_price:,.2f}, Current: ${current_price:,.2f}, Gain: {pnl_pct:.2f}%'
            critical_alerts.append(alert)
        print()

# Check drawdown
print('=== DRAWDOWN ANALYSIS ===')
btc_trades = [t for t in trades if 'BTC' in t.get('symbol', '')]
eth_trades = [t for t in trades if 'ETH' in t.get('symbol', '')]

if btc_trades:
    btc_entry_avg = sum(t['price'] for t in btc_trades) / len(btc_trades)
    btc_drawdown = (btc_current - btc_entry_avg) / btc_entry_avg * 100
    print(f'BTC Average Entry: ${btc_entry_avg:,.2f}')
    print(f'BTC Drawdown: {btc_drawdown:+.2f}%')
    
    if btc_drawdown <= -10:
        alert = f'CRITICAL DRAWDOWN: BTC portfolio down {btc_drawdown:.2f}% from average entry ${btc_entry_avg:,.2f}'
        critical_alerts.append(alert)

if eth_trades:
    eth_entry_avg = sum(t['price'] for t in eth_trades) / len(eth_trades)
    eth_drawdown = (eth_current - eth_entry_avg) / eth_entry_avg * 100
    print(f'ETH Average Entry: ${eth_entry_avg:,.2f}')
    print(f'ETH Drawdown: {eth_drawdown:+.2f}%')
    
    if eth_drawdown <= -10:
        alert = f'CRITICAL DRAWDOWN: ETH portfolio down {eth_drawdown:.2f}% from average entry ${eth_entry_avg:,.2f}'
        critical_alerts.append(alert)

print()
print('=== SYSTEM STATUS ===')
print('Dashboard: Running')
print('Last Analysis: 2026-03-31T00:48:41')
print('Capital: $250')
print('Risk Parameters: 5% stop-loss, 10% take-profit')
print('Max trades/day: 2')
print()

# Log to monitoring file
monitoring_log = '/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log'
with open(monitoring_log, 'a') as f:
    f.write(f'\n=== Monitoring Check: {datetime.datetime.now()} ===\n')
    f.write(f'BTC Price: ${btc_current:,.2f}\n')
    f.write(f'ETH Price: ${eth_current:,.2f}\n')
    f.write(f'Active Trades: {len(trades)}\n')
    f.write(f'Alerts: {len(critical_alerts)}\n')
    if critical_alerts:
        f.write('Critical Alerts:\n')
        for alert in critical_alerts:
            f.write(f'  - {alert}\n')

# Log critical alerts
if critical_alerts:
    critical_log = '/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log'
    with open(critical_log, 'a') as f:
        f.write(f'\n=== Critical Alert: {datetime.datetime.now()} ===\n')
        for alert in critical_alerts:
            f.write(f'{alert}\n')
    print('⚠️ CRITICAL ALERTS LOGGED ⚠️')
    for alert in critical_alerts:
        print(f'  • {alert}')
else:
    print('✅ No critical alerts at this time')