#!/usr/bin/env python3
import json

# Get current prices from the summary
btc_price = 71832.76
eth_price = 2202.81

# Recent trades (simplified analysis)
trades = [
    {'symbol': 'ETH/USD', 'price': 2331.78, 'amount': 0.00428857},
    {'symbol': 'BTC/USD', 'price': 74335.92, 'amount': 0.00013452},
    {'symbol': 'BTC/USD', 'price': 74308.00, 'amount': 0.00013458},
    {'symbol': 'BTC/USD', 'price': 74308.79, 'amount': 0.00013457},
    {'symbol': 'BTC/USD', 'price': 74332.65, 'amount': 0.00013453},
    {'symbol': 'BTC/USD', 'price': 74319.47, 'amount': 0.00013455},
    {'symbol': 'BTC/USD', 'price': 74094.64, 'amount': 0.002699},
    {'symbol': 'ETH/USD', 'price': 2325.28, 'amount': 0.086},
    {'symbol': 'BTC/USD', 'price': 71386.00, 'amount': 0.002802},
    {'symbol': 'ETH/USD', 'price': 2193.60, 'amount': 0.0912}
]

print('POSITION ANALYSIS:')
print('=' * 50)

btc_positions = []
eth_positions = []

for trade in trades:
    if 'BTC' in trade['symbol']:
        btc_positions.append(trade)
    elif 'ETH' in trade['symbol']:
        eth_positions.append(trade)

# Calculate average entry prices
def analyze_positions(positions, current_price, symbol):
    if not positions:
        return None
    
    total_amount = sum(p['amount'] for p in positions)
    total_value = sum(p['amount'] * p['price'] for p in positions)
    avg_entry = total_value / total_amount if total_amount > 0 else 0
    
    pnl_percent = ((current_price - avg_entry) / avg_entry * 100) if avg_entry > 0 else 0
    
    print(f'{symbol}:')
    print(f'  Current price: ${current_price:.2f}')
    print(f'  Avg entry: ${avg_entry:.2f}')
    print(f'  Total amount: {total_amount:.6f}')
    print(f'  P&L: {pnl_percent:.2f}%')
    
    # Check stop-loss (5%) and take-profit (10%)
    if pnl_percent <= -5:
        print(f'  ⚠️  STOP-LOSS TRIGGERED! ({pnl_percent:.2f}% loss)')
        return 'stop_loss'
    elif pnl_percent >= 10:
        print(f'  ✅ TAKE-PROFIT TRIGGERED! ({pnl_percent:.2f}% gain)')
        return 'take_profit'
    elif pnl_percent <= -3:
        print(f'  ⚠️  Approaching stop-loss ({pnl_percent:.2f}% loss)')
        return 'warning'
    
    return None

print()
btc_alert = analyze_positions(btc_positions, btc_price, 'BTC/USD')
print()
eth_alert = analyze_positions(eth_positions, eth_price, 'ETH/USD')
print()
print('=' * 50)