import json
import requests
import time
from datetime import datetime

# Get current time
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S (Asia/Bangkok)')

print('=== TRADING MONITORING CHECK: ' + current_time + ' ===')
print('Dashboard: http://localhost:5001/')
print()

# Get system status
try:
    status = requests.get('http://localhost:5001/status', timeout=5).json()
    print('--- SYSTEM STATUS ---')
    print(json.dumps(status, indent=2))
except Exception as e:
    print(f"Error fetching status: {e}")
    status = {}

# Get trades
try:
    trades = requests.get('http://localhost:5001/trades', timeout=5).json()
    print()
    print('--- RECENT TRADES ---')
    print(f"Total trades: {trades.get('count', 0)}")
    print(json.dumps(trades.get('trades', [])[:5], indent=2))  # Show only first 5 trades
except Exception as e:
    print(f"Error fetching trades: {e}")
    trades = {'count': 0, 'trades': []}

# Get summary
try:
    summary_response = requests.get('http://localhost:5001/summary', timeout=5)
    summary = summary_response.text
    print()
    print('--- TRADING SUMMARY ---')
    print(summary[:2000])  # Limit output
except Exception as e:
    print(f"Error fetching summary: {e}")
    summary = ""

# Analyze positions from trades
print()
print('--- POSITION ANALYSIS ---')

# Parse trades to calculate positions
btc_buys = []
eth_buys = []
sol_sells = []

for trade in trades.get('trades', []):
    symbol = trade.get('symbol', '')
    side = trade.get('side', '').lower()
    amount = trade.get('amount') or trade.get('quantity', 0)
    price = trade.get('price', 0)
    
    if 'btc' in symbol.lower() or trade.get('model', '').lower().find('btc') != -1:
        if side == 'buy':
            btc_buys.append((amount, price))
    elif 'eth' in symbol.lower() or trade.get('model', '').lower().find('eth') != -1:
        if side == 'buy':
            eth_buys.append((amount, price))
    elif 'sol' in symbol.lower():
        if side == 'sell':
            sol_sells.append((amount, price))

# Calculate totals
total_btc = sum(amount for amount, _ in btc_buys)
total_btc_invested = sum(amount * price for amount, price in btc_buys)
total_eth = sum(amount for amount, _ in eth_buys)
total_eth_invested = sum(amount * price for amount, price in eth_buys)

# Current market prices (approximate)
btc_price = 72837.94  # From summary
eth_price = 2260.75   # From summary
sol_price = 94.952    # From trade

# Calculate current values
btc_current_value = total_btc * btc_price
eth_current_value = total_eth * eth_price

btc_pnl = btc_current_value - total_btc_invested
eth_pnl = eth_current_value - total_eth_invested

btc_pnl_percent = (btc_pnl / total_btc_invested * 100) if total_btc_invested > 0 else 0
eth_pnl_percent = (eth_pnl / total_eth_invested * 100) if total_eth_invested > 0 else 0

print(f'BTC Position: {total_btc:.8f} BTC')
print(f'  Invested: ${total_btc_invested:.2f}')
print(f'  Current Value: ${btc_current_value:.2f}')
print(f'  P&L: ${btc_pnl:+.2f} ({btc_pnl_percent:+.2f}%)')

print(f'ETH Position: {total_eth:.8f} ETH')
print(f'  Invested: ${total_eth_invested:.2f}')
print(f'  Current Value: ${eth_current_value:.2f}')
print(f'  P&L: ${eth_pnl:+.2f} ({eth_pnl_percent:+.2f}%)')

if sol_sells:
    total_sol_sold = sum(amount for amount, _ in sol_sells)
    total_sol_value = sum(amount * price for amount, price in sol_sells)
    print(f'SOL Sold: {total_sol_sold:.8f} SOL for ${total_sol_value:.2f}')

# Check stop loss
stop_loss_threshold = status.get('risk_parameters', {}).get('stop_loss', 0.05) * 100
print()
print('--- CRITICAL ALERTS CHECK ---')

# Check BTC stop loss
if total_btc_invested > 0 and btc_pnl_percent <= -stop_loss_threshold:
    print(f'[CURRENT_TIME] 🚨 CRITICAL - BTC STOP LOSS TRIGGERED!')
    print(f'  Loss: {btc_pnl_percent:.2f}% exceeds threshold: {stop_loss_threshold:.2f}%')
    print(f'  Current BTC price: ${btc_price:.2f}')
elif total_btc_invested > 0:
    print(f'[CURRENT_TIME] BTC Status - Loss: {abs(btc_pnl_percent):.2f}%, below {stop_loss_threshold:.2f}% threshold')

# Check ETH stop loss
if total_eth_invested > 0 and eth_pnl_percent <= -stop_loss_threshold:
    print(f'[CURRENT_TIME] 🚨 CRITICAL - ETH STOP LOSS TRIGGERED!')
    print(f'  Loss: {eth_pnl_percent:.2f}% exceeds threshold: {stop_loss_threshold:.2f}%')
    print(f'  Current ETH price: ${eth_price:.2f}')
elif total_eth_invested > 0:
    print(f'[CURRENT_TIME] ETH Status - Loss: {abs(eth_pnl_percent):.2f}%, below {stop_loss_threshold:.2f}% threshold')

# Check if max daily trades reached
if status.get('risk_parameters', {}).get('max_trades_per_day', 0) > 0:
    today_trades = len([t for t in trades.get('trades', []) if 'time' in t])
    max_trades = status['risk_parameters']['max_trades_per_day']
    if today_trades >= max_trades:
        print(f'[CURRENT_TIME] ⚠️ WARNING - Max daily trades reached ({today_trades}/{max_trades})')
    else:
        print(f'[CURRENT_TIME] INFO - Daily trades: {today_trades}/{max_trades}')

print()
print('=== END OF MONITORING CHECK ===')