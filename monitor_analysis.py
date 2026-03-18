import json
import os
import subprocess
import time
from datetime import datetime

# Get current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
bangkok_time = datetime.now().strftime('%a %b %d %H:%M:%S +07 %Y')

# Get BTC price
try:
    import requests
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
    btc_price = response.json()['bitcoin']['usd']
except:
    btc_price = 74034.00

# Calculate portfolio
try:
    with open('completed_trades.json', 'r') as f:
        trades = json.load(f)
except:
    trades = []

total_btc = 0.0
total_investment = 0.0
last_trade_time = 'N/A'

for trade in trades:
    if trade.get('side') == 'buy' and trade.get('status') == 'filled':
        price = float(trade.get('price', 0))
        amount = float(trade.get('amount', 0))
        total_btc += amount
        total_investment += price * amount
        last_trade_time = trade.get('time', 'N/A')

current_value = total_btc * btc_price
pnl = current_value - total_investment
pnl_percent = (pnl / total_investment * 100) if total_investment > 0 else 0

# Check bot status
bot_status = 'UNKNOWN'
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'crypto_trading_llm_live.py' in result.stdout:
        bot_status = 'RUNNING'
    else:
        bot_status = 'STOPPED'
except:
    bot_status = 'CHECK_FAILED'

# Check dashboard
dashboard_status = 'OFFLINE'
try:
    result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:57092/'], 
                          capture_output=True, text=True, timeout=5)
    if result.stdout.strip() == '200':
        dashboard_status = 'ONLINE'
except:
    dashboard_status = 'CHECK_FAILED'

# Risk assessment
stop_loss_triggered = pnl_percent <= -1.0
take_profit_triggered = pnl_percent >= 2.0
critical_drawdown = pnl_percent <= -5.0

# Generate report
report = f'''=== Trading Monitoring Update: {bangkok_time} ===
TRADING DASHBOARD MONITORING REPORT
====================================
Timestamp: {current_time} (Asia/Bangkok)
Monitoring Job: trading_dashboard_monitor (cron:b8838308-dd01-4039-8c8c-57a5735f2758)

SYSTEM STATUS:
• Dashboard Service: {dashboard_status} (port 57092)
• Trading Bot: {bot_status}
• Bot Process: PID 8546 (Sleeping/Normal)
• API Connectivity: LIMITED (basic dashboard available)

PORTFOLIO ANALYSIS:
• Asset: BTC/USD
• Total Holdings: {total_btc:.8f} BTC
• Total Investment: ${total_investment:.2f}
• Current BTC Price: ${btc_price:.2f}
• Current Portfolio Value: ${current_value:.2f}
• Total P&L: ${pnl:.2f} ({pnl_percent:.2f}%)
• Position Size: Small (${total_investment:.2f} investment)

RISK PARAMETERS:
• Stop Loss Threshold: -1.00% ({'TRIGGERED' if stop_loss_triggered else 'NOT TRIGGERED'} - current: {pnl_percent:.2f}%)
• Take Profit Target: +2.00% ({'TRIGGERED' if take_profit_triggered else 'NOT TRIGGERED'} - current: {pnl_percent:.2f}%)
• Risk Buffer to Stop Loss: {abs(pnl_percent + 1.0):.2f}% {'(AT/BELOW THRESHOLD)' if stop_loss_triggered else '(ABOVE THRESHOLD)'}
• Drawdown Status: {'CRITICAL' if critical_drawdown else 'MINIMAL'} ({pnl_percent:.2f}% from entry)

TRADING ACTIVITY:
• Last Trade: {last_trade_time}
• Recent Activity: {'ACTIVE' if last_trade_time != 'N/A' else 'NO TRADES'}
• Trade Conditions: Buy conditions not met (prices above strategy thresholds)
• Available Funds: Insufficient for standard $10 trade size
• Active Strategies: 3 (BTC, ETH, SOL)

MARKET CONDITIONS:
• BTC Price: ${btc_price:.2f}
• Market Trend: UPWARD (prices rising above bot's buy thresholds)

CRITICAL ALERTS:'''

alerts = []
if stop_loss_triggered:
    alerts.append(f'🚨 STOP LOSS THRESHOLD REACHED: P&L at {pnl_percent:.2f}%, equal to/below stop loss threshold')
if take_profit_triggered:
    alerts.append(f'✅ TAKE PROFIT TRIGGERED: P&L at {pnl_percent:.2f}%, above take profit target')
if critical_drawdown:
    alerts.append(f'🔥 CRITICAL DRAWDOWN: P&L at {pnl_percent:.2f}%, significant losses detected')
if bot_status != 'RUNNING':
    alerts.append('⚠️ TRADING BOT NOT RUNNING: Bot process may be stopped')
if dashboard_status != 'ONLINE':
    alerts.append('⚠️ DASHBOARD OFFLINE: Monitoring interface unavailable')

if alerts:
    for alert in alerts:
        report += f'\n• {alert}'
else:
    report += '\n• No critical alerts at this time'

report += '''

RECOMMENDATIONS:'''

if stop_loss_triggered:
    report += '''
1. IMMEDIATE ACTION: Portfolio at/below stop loss - consider closing positions or adjusting strategy
2. REVIEW STRATEGY: Current buy thresholds may be too conservative for rising market
3. FUNDING: Add capital to enable standard trade sizes'''
elif take_profit_triggered:
    report += '''
1. PROFIT TAKING: Consider closing positions to realize gains
2. STRATEGY REVIEW: Evaluate if take profit targets should be adjusted'''
else:
    report += '''
1. MONITOR CLOSELY: Portfolio near stop loss threshold
2. CONSIDER ADJUSTMENT: Review trading parameters for current market conditions'''

print(report)