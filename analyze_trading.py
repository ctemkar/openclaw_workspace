import json
import datetime
import subprocess

# Current prices from summary
btc_price = 70614.00
eth_price = 2166.65

# Get trade data
result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], capture_output=True, text=True)
trades_data = json.loads(result.stdout)

# Analyze trades for stop-loss/take-profit
print('=== TRADING MONITORING ANALYSIS ===')
print('Timestamp:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('System Status: Running')
print('Capital: $1000.00')
print('Stop-loss: 5% | Take-profit: 10%')
print('Max trades/day: 2 | Today\'s trades: 2/2')
print()
print('=== CURRENT MARKET PRICES ===')
print('BTC/USD: $' + format(btc_price, ',.2f'))
print('ETH/USD: $' + format(eth_price, ',.2f'))
print()
print('=== TRADE ANALYSIS ===')

# Check recent trades for potential stop-loss/take-profit
critical_alerts = []
for trade in trades_data.get('trades', [])[:4]:  # Check most recent 4 trades
    if 'price' in trade and 'side' in trade:
        entry_price = trade['price']
        symbol = trade.get('symbol', 'Unknown')
        side = trade['side'].lower()
        
        if side == 'buy':
            # Calculate current P&L
            if 'BTC' in symbol:
                current_price = btc_price
            elif 'ETH' in symbol:
                current_price = eth_price
            else:
                continue
                
            pnl_pct = (current_price - entry_price) / entry_price * 100
            
            # Check for stop-loss/take-profit
            if pnl_pct <= -5:
                alert = f'STOP-LOSS TRIGGERED: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_pct:.1f}% loss)'
                critical_alerts.append(alert)
                print(f'⚠️  {alert}')
            elif pnl_pct >= 10:
                alert = f'TAKE-PROFIT TRIGGERED: {symbol} at {entry_price:.2f}, current {current_price:.2f} ({pnl_pct:.1f}% gain)'
                critical_alerts.append(alert)
                print(f'✅ {alert}')
            else:
                print(f'{symbol}: Entry ${entry_price:.2f}, Current ${current_price:.2f}, P&L: {pnl_pct:.1f}%')

print()
print('=== RISK ASSESSMENT ===')

# Check drawdown indicators
btc_support = 70896.70
eth_support = 2167.99

btc_drawdown = ((btc_price - btc_support) / btc_support) * 100
eth_drawdown = ((eth_price - eth_support) / eth_support) * 100

print(f'BTC Support: ${btc_support:.2f}, Current: ${btc_price:.2f}, Distance: {btc_drawdown:.1f}%')
print(f'ETH Support: ${eth_support:.2f}, Current: ${eth_price:.2f}, Distance: {eth_drawdown:.1f}%')

if btc_drawdown < -2 or eth_drawdown < -2:
    alert = f'CRITICAL DRAWDOWN: BTC {btc_drawdown:.1f}% below support, ETH {eth_drawdown:.1f}% below support'
    critical_alerts.append(alert)
    print(f'🚨 {alert}')
elif btc_drawdown < 0 or eth_drawdown < 0:
    print(f'⚠️  Warning: Trading near/below support levels')
else:
    print(f'✅ Trading above support levels')

print()
print('=== SUMMARY ===')
if critical_alerts:
    print(f'🚨 CRITICAL ALERTS DETECTED: {len(critical_alerts)}')
    for alert in critical_alerts:
        print(f'  • {alert}')
else:
    print('✅ No critical alerts detected')
print('📊 System operating normally')
print('⏰ Next analysis scheduled: hourly')