current_price = 73926
trades = [
    {'amount': 0.00013374340845611425, 'price': 74770.04},
    {'amount': 0.00013368983957219252, 'price': 74800.0},
    {'amount': 0.00013381716266667096, 'price': 74728.83},
    {'amount': 0.00013381716266667096, 'price': 74728.83}
]

total_investment = sum(t['amount'] * t['price'] for t in trades)
current_value = sum(t['amount'] * current_price for t in trades)
total_loss_pct = (current_value - total_investment) / total_investment * 100

stop_loss_threshold_1 = -1.0
if total_loss_pct <= stop_loss_threshold_1:
    print(f'[2026-03-18 08:19:05] 🚨 STOP LOSS TRIGGERED! Loss: {total_loss_pct:.2f}% exceeds {stop_loss_threshold_1}% threshold')
    print(f'[2026-03-18 08:19:05] STOP LOSS DETAILS - BTC Price: ${current_price}, Total Loss: ${current_value - total_investment:.2f}, Loss %: {total_loss_pct:.2f}%')