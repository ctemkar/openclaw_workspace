import json
import math

# Current BTC price
current_price = 73926

# Trade data from completed_trades.json
trades = [
    {'amount': 0.00013374340845611425, 'price': 74770.04},
    {'amount': 0.00013368983957219252, 'price': 74800.0},
    {'amount': 0.00013381716266667096, 'price': 74728.83},
    {'amount': 0.00013381716266667096, 'price': 74728.83}
]

# Calculate losses
total_investment = 0
current_value = 0

print(f"Current BTC Price: ${current_price}")
print(f"Number of trades: {len(trades)}")
print("-" * 50)

for i, trade in enumerate(trades, 1):
    investment = trade['amount'] * trade['price']
    current_val = trade['amount'] * current_price
    loss_pct = (current_val - investment) / investment * 100
    
    total_investment += investment
    current_value += current_val
    
    print(f'Trade {i}:')
    print(f'  Buy Price: ${trade["price"]:.2f}')
    print(f'  Amount: {trade["amount"]:.8f} BTC')
    print(f'  Investment: ${investment:.2f}')
    print(f'  Current Value: ${current_val:.2f}')
    print(f'  Loss: ${current_val - investment:.2f} ({loss_pct:.2f}%)')
    print()

total_loss = current_value - total_investment
total_loss_pct = (total_loss / total_investment) * 100

print(f'PORTFOLIO SUMMARY:')
print(f'Total Investment: ${total_investment:.2f}')
print(f'Current Value: ${current_value:.2f}')
print(f'Total Loss: ${total_loss:.2f} ({total_loss_pct:.2f}%)')

# Check stop loss thresholds
stop_loss_threshold_1 = -1.0  # From analyze script
stop_loss_threshold_3 = -3.0  # From dashboard

print(f'\nSTOP LOSS ANALYSIS:')
print(f'1% Threshold (analyze script): {stop_loss_threshold_1}%')
print(f'3% Threshold (dashboard): {stop_loss_threshold_3}%')

if total_loss_pct <= stop_loss_threshold_1:
    print(f'🚨 1% STOP LOSS TRIGGERED! Loss: {total_loss_pct:.2f}% exceeds {stop_loss_threshold_1}% threshold')
    
if total_loss_pct <= stop_loss_threshold_3:
    print(f'🚨 3% STOP LOSS TRIGGERED! Loss: {total_loss_pct:.2f}% exceeds {stop_loss_threshold_3}% threshold')

# Check if any critical drawdown
critical_drawdown = -5.0  # Arbitrary critical threshold
if total_loss_pct <= critical_drawdown:
    print(f'🚨 CRITICAL DRAWDOWN! Loss: {total_loss_pct:.2f}% exceeds critical {critical_drawdown}% threshold')