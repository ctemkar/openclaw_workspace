import json
import math

# Current BTC price
current_price = 73909

# Trade data from API
trades = [
    {'amount': 0.00013374340845611425, 'price': 74770.04},
    {'amount': 0.00013368983957219252, 'price': 74800.0},
    {'amount': 0.00013381716266667096, 'price': 74728.83},
    {'amount': 0.00013381716266667096, 'price': 74728.83}
]

# Calculate losses
total_investment = 0
current_value = 0

for i, trade in enumerate(trades, 1):
    investment = trade['amount'] * trade['price']
    current_val = trade['amount'] * current_price
    loss_pct = (current_val - investment) / investment * 100
    
    total_investment += investment
    current_value += current_val
    
    print(f'Trade {i}: Buy @ ${trade["price"]:.2f}, Current: ${current_price}')
    print(f'  Investment: ${investment:.2f}, Current: ${current_val:.2f}, Loss: {loss_pct:.2f}%')

total_loss = current_value - total_investment
total_loss_pct = (total_loss / total_investment) * 100

print(f'\nPORTFOLIO SUMMARY:')
print(f'Total Investment: ${total_investment:.2f}')
print(f'Current Value: ${current_value:.2f}')
print(f'Total Loss: ${total_loss:.2f} ({total_loss_pct:.2f}%)')

# Check stop loss (using 1% from analyze script)
stop_loss_threshold = -1.0
if total_loss_pct <= stop_loss_threshold:
    print(f'\n🚨 STOP LOSS TRIGGERED! Loss: {total_loss_pct:.2f}% exceeds {stop_loss_threshold}% threshold')
else:
    print(f'\nStop Loss Status: OK (Loss: {total_loss_pct:.2f}%, Threshold: {stop_loss_threshold}%)')