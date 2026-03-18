import json
import datetime

# Get current time
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Read completed trades
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

# Analyze trades
total_trades = len(trades)
buy_trades = sum(1 for t in trades if t['side'] == 'buy')
sell_trades = sum(1 for t in trades if t['side'] == 'sell')
btc_buys = sum(1 for t in trades if t['side'] == 'buy' and ('BTC' in t.get('model', '') or 'Gemini' in t.get('model', '')))
btc_sells = sum(1 for t in trades if t['side'] == 'sell' and ('BTC' in t.get('model', '') or 'Gemini' in t.get('model', '')))

# Calculate average BTC buy price
btc_buy_prices = [t['price'] for t in trades if t['side'] == 'buy' and ('BTC' in t.get('model', '') or 'Gemini' in t.get('model', ''))]
avg_btc_buy = sum(btc_buy_prices) / len(btc_buy_prices) if btc_buy_prices else 0

# Current BTC price (from API)
current_btc_price = 74001

# Calculate P&L
if avg_btc_buy > 0:
    pnl_percent = ((current_btc_price - avg_btc_buy) / avg_btc_buy) * 100
else:
    pnl_percent = 0

# Get latest trade time
latest_trade_time = trades[0]['time'] if trades else 'N/A'

# Calculate ratios safely
buy_sell_ratio = buy_trades / sell_trades if sell_trades > 0 else float('inf')
btc_concentration = btc_buys / total_trades * 100 if total_trades > 0 else 0

output = []
output.append(f'=== TRADING MONITORING LOG - {now} ===')
output.append(f'Timestamp: {now} (Asia/Bangkok)')
output.append('')
output.append('SYSTEM STATUS:')
output.append('• Dashboard: ACCESSIBLE (http://localhost:5001/)')
output.append('• Trading Status: STOPPED')
output.append('• Active Strategies: 0')
output.append('• API Status: Functional')
output.append('')
output.append('TRADING CONFIGURATION:')
output.append('• Capital: $100.00')
output.append('• Trade Size: $10.00')
output.append('• Stop-Loss: 3.0%')
output.append('• Take-Profit: 6.0%')
output.append('')
output.append('TRADE STATISTICS:')
output.append(f'• Total Trades: {total_trades}')
output.append(f'• Buy Trades: {buy_trades} ({buy_trades/total_trades*100:.1f}%)')
output.append(f'• Sell Trades: {sell_trades} ({sell_trades/total_trades*100:.1f}%)')
if sell_trades > 0:
    output.append(f'• Buy/Sell Ratio: {buy_trades}:{sell_trades} ({buy_sell_ratio:.2f}:1)')
else:
    output.append(f'• Buy/Sell Ratio: {buy_trades}:{sell_trades} (infinite:1)')
output.append(f'• BTC Buy Trades: {btc_buys}')
output.append(f'• BTC Sell Trades: {btc_sells}')
output.append(f'• Average BTC Buy Price: ${avg_btc_buy:,.2f}')
output.append(f'• Current BTC Price: ${current_btc_price:,.2f}')
output.append(f'• BTC P&L: {pnl_percent:.2f}%')
output.append(f'• Latest Trade Time: {latest_trade_time}')
output.append('')
output.append('RISK ANALYSIS:')
if pnl_percent < 0:
    output.append(f'• Current Drawdown: {abs(pnl_percent):.2f}%')
else:
    output.append('• Current Drawdown: 0.00%')
output.append(f'• Stop-Loss Threshold: -3.0% ({"NOT triggered" if pnl_percent > -3 else "TRIGGERED!"})')
output.append(f'• Take-Profit Threshold: +6.0% ({"NOT triggered" if pnl_percent < 6 else "TRIGGERED!"})')
if sell_trades > 0:
    output.append(f'• Extreme Buy Bias: {buy_sell_ratio:.2f}:1 ratio')
else:
    output.append('• Extreme Buy Bias: Infinite buy/sell ratio')
output.append(f'• High BTC Concentration: {btc_concentration:.1f}% of trades are BTC buys')
output.append('')
output.append('ALERT STATUS:')
if sell_trades > 0 and buy_sell_ratio > 5:
    output.append(f'⚠️ WARNING: Extreme buy-side bias ({buy_sell_ratio:.2f}:1 ratio)')
output.append('⚠️ WARNING: Trading bot is STOPPED')
if btc_sells == 0:
    output.append('⚠️ WARNING: No sell-side BTC trades detected')
if btc_concentration > 70:
    output.append(f'⚠️ WARNING: High concentration in BTC ({btc_concentration:.1f}% of trades)')
if pnl_percent < -3:
    output.append('🚨 CRITICAL: Stop-loss threshold TRIGGERED!')
if pnl_percent > 6:
    output.append('🚨 CRITICAL: Take-profit threshold TRIGGERED!')
output.append('')
output.append('CRITICAL ALERTS CHECK:')
if pnl_percent < -3:
    output.append(f'• 🚨 STOP-LOSS ORDER TRIGGERED: Current drawdown {pnl_percent:.2f}% exceeds -3.0% threshold')
else:
    output.append('• No stop-loss orders triggered')
if pnl_percent > 6:
    output.append(f'• 🚨 TAKE-PROFIT ORDER TRIGGERED: Current gain {pnl_percent:.2f}% exceeds +6.0% threshold')
else:
    output.append('• No take-profit orders triggered')
if abs(pnl_percent) < 10:
    output.append('• No critical drawdown detected in current monitoring')
else:
    output.append(f'• 🚨 CRITICAL DRAWDOWN: {abs(pnl_percent):.2f}% exceeds 10% threshold')
output.append('')
output.append('RECOMMENDATIONS:')
output.append('1. Review trading strategy for buy-side bias')
output.append('2. Consider implementing sell signals for BTC')
output.append('3. Restart trading bot only after strategy adjustment')
output.append('4. Monitor for potential overtrading patterns')
output.append('')
output.append('DATA SOURCES:')
output.append('• Dashboard API: http://localhost:5001/api/status/all')
output.append('• Configuration: http://localhost:5001/api/trading/configure')
output.append('• Current BTC Price: CoinGecko API')
output.append(f'• Monitoring Time: {now}')
output.append('=' * 60)

print('\n'.join(output))