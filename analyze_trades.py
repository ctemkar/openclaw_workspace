import json
from datetime import datetime

# Read completed trades
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

# Get current BTC price from API (simulated)
current_btc_price = 40927.76  # From API response

print('=== TRADE ANALYSIS ===')
print(f'Current BTC Price: ${current_btc_price:.2f}')
print(f'Number of Active Trades: {len(trades)}')
print()

total_investment = 0
total_current_value = 0

for i, trade in enumerate(trades, 1):
    if trade['side'] == 'buy':
        buy_price = trade['price']
        amount = trade['amount']
        investment = buy_price * amount
        current_value = current_btc_price * amount
        pnl = current_value - investment
        pnl_pct = (pnl / investment) * 100
        
        print(f'Trade {i}:')
        print(f'  Buy Price: ${buy_price:.2f}')
        print(f'  Amount: {amount:.8f} BTC')
        print(f'  Investment: ${investment:.2f}')
        print(f'  Current Value: ${current_value:.2f}')
        print(f'  P&L: ${pnl:.2f} ({pnl_pct:.2f}%)')
        
        # Check stop-loss and take-profit
        stop_loss_pct = 1.0  # From config
        take_profit_pct = 2.0  # From config
        
        if pnl_pct <= -stop_loss_pct:
            print(f'  ⚠️  STOP-LOSS TRIGGERED! ({pnl_pct:.2f}% <= -{stop_loss_pct}%)')
        elif pnl_pct >= take_profit_pct:
            print(f'  ✅ TAKE-PROFIT TRIGGERED! ({pnl_pct:.2f}% >= {take_profit_pct}%)')
        else:
            print(f'  Status: Active (within bounds)')
        print()
        
        total_investment += investment
        total_current_value += current_value

if total_investment > 0:
    total_pnl = total_current_value - total_investment
    total_pnl_pct = (total_pnl / total_investment) * 100
    print(f'=== SUMMARY ===')
    print(f'Total Investment: ${total_investment:.2f}')
    print(f'Total Current Value: ${total_current_value:.2f}')
    print(f'Total P&L: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)')
    
    # Check for critical drawdown
    if total_pnl_pct <= -5.0:
        print(f'🚨 CRITICAL DRAWDOWN ALERT! Total loss exceeds 5% ({total_pnl_pct:.2f}%)')
    elif total_pnl_pct <= -3.0:
        print(f'⚠️  WARNING: Drawdown approaching critical levels ({total_pnl_pct:.2f}%)')