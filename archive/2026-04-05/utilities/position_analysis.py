import json
import datetime

# Current prices from latest analysis
btc_price = 71333.47
eth_price = 2202.61

# Positions from trades data
positions = [
    # ETH positions
    {'symbol': 'ETH/USD', 'entry': 2331.78, 'amount': 0.00428856924752764, 'type': 'ETH'},
    {'symbol': 'ETH/USD', 'entry': 2325.28, 'amount': 0.086, 'type': 'ETH'},
    {'symbol': 'ETH/USD', 'entry': 2193.60, 'amount': 0.0912, 'type': 'ETH'},
    
    # BTC positions
    {'symbol': 'BTC/USD', 'entry': 74335.92, 'amount': 0.0001345244667719186, 'type': 'BTC'},
    {'symbol': 'BTC/USD', 'entry': 74308.00, 'amount': 0.0001345750121117511, 'type': 'BTC'},
    {'symbol': 'BTC/USD', 'entry': 74308.79, 'amount': 0.00013457358140268468, 'type': 'BTC'},
    {'symbol': 'BTC/USD', 'entry': 74332.65, 'amount': 0.00013453038469636157, 'type': 'BTC'},
    {'symbol': 'BTC/USD', 'entry': 74319.47, 'amount': 0.00013455424265000813, 'type': 'BTC'},
    {'symbol': 'BTC/USD', 'entry': 74094.64, 'amount': 0.002699, 'type': 'BTC'},
    {'symbol': 'BTC/USD', 'entry': 71386.00, 'amount': 0.002802, 'type': 'BTC'},
]

# Calculate current values
total_investment = 0
total_current_value = 0
eth_investment = 0
eth_current = 0
btc_investment = 0
btc_current = 0

print('POSITION ANALYSIS:')
print('=' * 60)
for i, pos in enumerate(positions, 1):
    investment = pos['entry'] * pos['amount']
    current_value = (eth_price if pos['type'] == 'ETH' else btc_price) * pos['amount']
    pnl_pct = ((current_value - investment) / investment) * 100
    
    total_investment += investment
    total_current_value += current_value
    
    if pos['type'] == 'ETH':
        eth_investment += investment
        eth_current += current_value
    else:
        btc_investment += investment
        btc_current += current_value
    
    stop_loss_triggered = pnl_pct <= -5.0
    alert = '🚨 STOP-LOSS TRIGGERED!' if stop_loss_triggered else ''
    
    print(f'{i}. {pos["symbol"]}:')
    print(f'   Entry: ${pos["entry"]:.2f}')
    print(f'   Amount: {pos["amount"]:.6f}')
    print(f'   Investment: ${investment:.2f}')
    print(f'   Current: ${current_value:.2f}')
    print(f'   P&L: {pnl_pct:.2f}% {alert}')
    print()

print('=' * 60)
print('PORTFOLIO SUMMARY:')
print(f'Total Investment: ${total_investment:.2f}')
print(f'Total Current Value: ${total_current_value:.2f}')
print(f'Total P&L: ${total_current_value - total_investment:.2f}')
print(f'Total P&L %: {((total_current_value - total_investment) / total_investment * 100):.2f}%')
print()
print(f'ETH Investment: ${eth_investment:.2f}')
print(f'ETH Current: ${eth_current:.2f}')
print(f'ETH P&L: {((eth_current - eth_investment) / eth_investment * 100):.2f}%')
print()
print(f'BTC Investment: ${btc_investment:.2f}')
print(f'BTC Current: ${btc_current:.2f}')
print(f'BTC P&L: {((btc_current - btc_investment) / btc_investment * 100):.2f}%')
print()
print(f'Capital Remaining: ${1000 - total_investment:.2f}')
print()
print('RISK ASSESSMENT:')
eth_loss_pct = ((eth_current - eth_investment) / eth_investment * 100)
btc_loss_pct = ((btc_current - btc_investment) / btc_investment * 100)

if eth_loss_pct <= -5:
    print('🚨 CRITICAL: ETH positions at or below stop-loss')
elif eth_loss_pct <= -3:
    print('⚠️ HIGH: ETH positions approaching stop-loss')
    
if btc_loss_pct <= -5:
    print('🚨 CRITICAL: BTC positions at or below stop-loss')
elif btc_loss_pct <= -3:
    print('⚠️ HIGH: BTC positions approaching stop-loss')

# Count positions at or below stop-loss
stop_loss_count = 0
for pos in positions:
    investment = pos['entry'] * pos['amount']
    current_value = (eth_price if pos['type'] == 'ETH' else btc_price) * pos['amount']
    pnl_pct = ((current_value - investment) / investment) * 100
    if pnl_pct <= -5:
        stop_loss_count += 1
        
print(f'Positions at/below stop-loss: {stop_loss_count}/{len(positions)}')

# Check if any positions need immediate attention
print()
print('IMMEDIATE CONCERNS:')
for i, pos in enumerate(positions, 1):
    investment = pos['entry'] * pos['amount']
    current_value = (eth_price if pos['type'] == 'ETH' else btc_price) * pos['amount']
    pnl_pct = ((current_value - investment) / investment) * 100
    
    if pnl_pct <= -5:
        print(f'{i}. {pos["symbol"]} at ${pos["entry"]:.2f}: {pnl_pct:.2f}% loss - STOP-LOSS TRIGGERED')
    elif -5 < pnl_pct <= -4:
        print(f'{i}. {pos["symbol"]} at ${pos["entry"]:.2f}: {pnl_pct:.2f}% loss - APPROACHING STOP-LOSS')