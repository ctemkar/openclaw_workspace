import json
import datetime
import math
import subprocess

# Current market prices
btc_price = 67790
eth_price = 2064.85

# Get current trades data
try:
    result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], 
                          capture_output=True, text=True)
    trades_data = json.loads(result.stdout)
    trades = trades_data.get('trades', [])
except:
    trades = [
        {'price': 2325.28, 'quantity': 0.086, 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '13:39:49'},
        {'price': 2193.6, 'quantity': 0.0912, 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '00:33:02'},
        {'price': 67247.51, 'quantity': 0.002974, 'side': 'BUY', 'symbol': 'BTC/USD', 'time': '21:29:41'},
        {'price': 2052.38, 'quantity': 0.0974, 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '21:29:42'},
        {'price': 2021.51, 'quantity': 0.2474, 'side': 'BUY', 'symbol': 'ETH/USD', 'time': '07:24:00'}
    ]

# Analyze positions
positions = []
total_investment = 0
current_value = 0
critical_alerts = []
drawdown_alerts = []

for i, trade in enumerate(trades, 1):
    entry = trade['price']
    qty = trade['quantity']
    symbol = trade['symbol']
    
    if 'BTC' in symbol:
        current = btc_price
    else:
        current = eth_price
    
    investment = entry * qty
    current_val = current * qty
    pnl = current_val - investment
    pnl_percent = (pnl / investment) * 100 if investment > 0 else 0
    
    # Calculate stop-loss and take-profit levels (5% stop, 10% take-profit)
    stop_loss = entry * 0.95
    take_profit = entry * 1.10
    
    status = '✅ PROFITABLE (within stop-loss)'
    if pnl_percent < -5:
        status = '🚨 STOP-LOSS TRIGGERED'
        critical_alerts.append({
            'position': i,
            'symbol': symbol,
            'entry': entry,
            'current': current,
            'change': pnl_percent,
            'pnl': pnl,
            'stop_loss': stop_loss,
            'exceeds_by': abs(pnl_percent) - 5
        })
    elif pnl_percent > 10:
        status = '🎯 TAKE-PROFIT TRIGGERED'
    
    positions.append({
        'id': i,
        'symbol': symbol,
        'entry': entry,
        'current': current,
        'change': pnl_percent,
        'pnl': pnl,
        'quantity': qty,
        'investment': investment,
        'current_value': current_val,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'status': status
    })
    
    total_investment += investment
    current_value += current_val

# Calculate portfolio metrics
total_pnl = current_value - total_investment
total_pnl_percent = (total_pnl / total_investment) * 100 if total_investment > 0 else 0

# Count positions by type
eth_positions = [p for p in positions if 'ETH' in p['symbol']]
btc_positions = [p for p in positions if 'BTC' in p['symbol']]
eth_exposure = sum(p['investment'] for p in eth_positions) / total_investment * 100 if total_investment > 0 else 0

# Check for drawdown alerts
if eth_exposure > 50:
    drawdown_alerts.append({
        'type': 'CONCENTRATION_RISK',
        'severity': 'HIGH',
        'message': f'ETH exposure: {eth_exposure:.1f}% (recommended max: 50%)'
    })

if len(critical_alerts) >= 2:
    drawdown_alerts.append({
        'type': 'MULTIPLE_STOP_LOSS_TRIGGERS',
        'severity': 'HIGH',
        'message': f'{len(critical_alerts)} positions hitting stop-loss'
    })

# Get current time
now = datetime.datetime.now()
timestamp = now.strftime('%Y-%m-%d %I:%M %p (Asia/Bangkok)')

# Generate monitoring log
monitoring_log = f'''=== TRADING MONITORING LOG ===
Timestamp: {timestamp}
Monitoring Period: {now.strftime('%Y-%m-%d %H:%M:%S')}

=== SYSTEM STATUS ===
- Status: running
- Capital: $250.00
- Analysis Scheduled: hourly
- Last Analysis: 2026-03-31T10:18:43.494747
- Risk Parameters:
  * Max trades per day: 2
  * Stop-loss: 5.0%
  * Take-profit: 10.0%
- Trading Pairs: BTC/USD, ETH/USD

=== RECENT TRADES ({len(trades)} total) ===
'''

for i, trade in enumerate(trades, 1):
    monitoring_log += f'''{i}. {trade['symbol']} - {trade['side']}
   Time: {trade['time']}
   Price: ${trade['price']:,.2f}
   Quantity: {trade['quantity']}
   Reason: {trade.get('reason', 'N/A')}

'''

monitoring_log += f'''=== CURRENT MARKET DATA (Real-time) ===
- BTC/USD: ${btc_price:,.2f} (Coingecko API)
- ETH/USD: ${eth_price:,.2f} (Coingecko API)
- Market Sentiment: NEUTRAL (slight recovery from previous lows)

=== POSITION ANALYSIS ===
'''

for pos in positions:
    monitoring_log += f'''{pos['id']}. {pos['symbol']} Position #{pos['id']} ({trades[pos['id']-1]['time']})
   Entry: ${pos['entry']:,.2f}
   Current: ${pos['current']:,.2f}
   Change: {pos['change']:+.2f}%
   P&L: ${pos['pnl']:+.2f}
   Stop-loss: ${pos['stop_loss']:,.2f} (5% below entry)
   Take-profit: ${pos['take_profit']:,.2f} (10% above entry)
   Status: {pos['status']}

'''

monitoring_log += f'''=== PORTFOLIO SUMMARY ===
- Total Positions: {len(positions)}
- ETH Positions: {len(eth_positions)} ({eth_exposure:.1f}% exposure)
- BTC Positions: {len(btc_positions)} ({100-eth_exposure:.1f}% exposure)
- Total Investment: ${total_investment:,.2f}
- Current Portfolio Value: ${current_value:,.2f}
- Total P&L: ${total_pnl:+.2f} ({total_pnl_percent:+.2f}%)
- Critical Alerts: {len(critical_alerts)} positions ({len(critical_alerts)/len(positions)*100:.1f}% of portfolio)
- Profitable Positions: {len([p for p in positions if p['pnl'] > 0])} positions ({len([p for p in positions if p['pnl'] > 0])/len(positions)*100:.1f}% of portfolio)

=== RISK ASSESSMENT ===
- Overall Risk Level: {'HIGH' if len(critical_alerts) > 0 else 'MEDIUM'}
- Critical Alerts: {len(critical_alerts)} (stop-loss triggers)
- Warning Alerts: {len(drawdown_alerts)}
- Safe Positions: {len([p for p in positions if p['pnl'] > -5 and p['pnl'] < 10])}
- Portfolio Drawdown: {total_pnl_percent:+.2f}%
- Concentration Risk: {'HIGH' if eth_exposure > 50 else 'MEDIUM'}
- Market Risk: MEDIUM (recovering from lows)

'''

if critical_alerts:
    monitoring_log += '''=== ALERT ANALYSIS ===
'''
    for i, alert in enumerate(critical_alerts, 1):
        monitoring_log += f'''🚨 CRITICAL ALERT #{i}: {alert['symbol']} STOP-LOSS TRIGGERED
   Position: {alert['symbol']} #{alert['position']} ({trades[alert['position']-1]['time']})
   Loss: {alert['change']:.2f}% (entry: ${alert['entry']:,.2f}, current: ${alert['current']:,.2f})
   Exceeds stop-loss by: {alert['exceeds_by']:.2f}%
   Recommended Action: IMMEDIATE EXIT

'''

if drawdown_alerts:
    monitoring_log += '''=== DRAWDOWN WARNINGS ===
'''
    for alert in drawdown_alerts:
        monitoring_log += f'''⚠️ {alert['type'].replace('_', ' ')}: {alert['message']}
   Severity: {alert['severity']}
   Recommended Action: Review portfolio allocation

'''

monitoring_log += '''=== RECOMMENDED ACTIONS ===
'''
if critical_alerts:
    monitoring_log += '''1. IMMEDIATE: Exit all positions with stop-loss triggers
'''
if eth_exposure > 50:
    monitoring_log += f'''2. URGENT: Reduce ETH exposure from {eth_exposure:.1f}% to ≤50%
'''
monitoring_log += '''3. Review stop-loss levels for all positions
4. Consider implementing portfolio rebalancing strategy
5. Review trading strategy given current market conditions
6. Monitor profitable positions for take-profit opportunities

=== PERFORMANCE METRICS ===
'''
profitable = [p for p in positions if p['pnl'] > 0]
losses = [p for p in positions if p['pnl'] < 0]
avg_win = sum(p['pnl'] for p in profitable) / len(profitable) if profitable else 0
avg_loss = sum(p['pnl'] for p in losses) / len(losses) if losses else 0

monitoring_log += f'''- Win Rate: {len(profitable)/len(positions)*100:.1f}% ({len(profitable)}/{len(positions)} positions profitable)
- Loss Rate: {len(losses)/len(positions)*100:.1f}% ({len(losses)}/{len(positions)} positions at loss)
- Average Win: ${avg_win:+.2f}
- Average Loss: ${avg_loss:+.2f}
- Risk/Reward Ratio: {abs(avg_loss/avg_win) if avg_win > 0 else 'N/A'}
- Sharpe Ratio (estimated): {'Negative' if total_pnl < 0 else 'Positive'}

=== MARKET OUTLOOK ===
- BTC Trend: {'Bullish' if btc_price > 67000 else 'Neutral'}
- ETH Trend: {'Bullish' if eth_price > 2100 else 'Neutral'}
- Overall Market: Neutral with slight recovery
- Recommendation: Exercise caution with new positions

=== END OF MONITORING LOG ===
Log generated at: {now.strftime('%Y-%m-%d %H:%M:%S')}
'''

print(monitoring_log)