import json
from datetime import datetime

# Load completed trades
with open('completed_trades.json', 'r') as f:
    trades = json.load(f)

# Current BTC price (from API)
current_btc_price = 74191.0

# Filter BTC trades only
btc_trades = [t for t in trades if 'BTC' in t.get('model', '') or 'Gemini' in t.get('model', '') or 'GPT' in t.get('model', '')]

# Calculate total BTC holdings and average entry price
total_btc = 0.0
total_investment = 0.0

for trade in btc_trades:
    if trade['side'] == 'buy':
        total_btc += trade['amount']
        total_investment += trade['amount'] * trade['price']
    elif trade['side'] == 'sell':
        total_btc -= trade['amount']
        total_investment -= trade['amount'] * trade['price']

if total_btc > 0:
    avg_entry_price = total_investment / total_btc
else:
    avg_entry_price = 0.0

# Calculate current value and P&L
current_value = total_btc * current_btc_price
current_pnl = current_value - total_investment
pnl_percentage = (current_pnl / total_investment * 100) if total_investment > 0 else 0.0

# Calculate stop-loss and take-profit levels
stop_loss_percentage = 5.0  # 5% stop-loss
take_profit_percentage = 10.0  # 10% take-profit

stop_loss_price = avg_entry_price * (1 - stop_loss_percentage/100)
take_profit_price = avg_entry_price * (1 + take_profit_percentage/100)

# Calculate distance to stop-loss and take-profit
distance_to_stop_loss = ((current_btc_price - stop_loss_price) / current_btc_price * 100) if current_btc_price > 0 else 0
distance_to_take_profit = ((take_profit_price - current_btc_price) / current_btc_price * 100) if current_btc_price > 0 else 0

# Check if stop-loss or take-profit triggered
stop_loss_triggered = current_btc_price <= stop_loss_price
take_profit_triggered = current_btc_price >= take_profit_price

# Count trades by model
model_counts = {}
for trade in trades:
    model = trade['model']
    model_counts[model] = model_counts.get(model, 0) + 1

# Get latest trades
latest_trades = sorted(trades, key=lambda x: x['time'], reverse=True)[:5]

print("=== TRADING ANALYSIS ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Current BTC Price: ${current_btc_price:,.2f}")
print(f"\n=== PORTFOLIO STATUS ===")
print(f"BTC Holdings: {total_btc:.8f} BTC")
print(f"Average Entry Price: ${avg_entry_price:,.2f}")
print(f"Total Investment: ${total_investment:,.2f}")
print(f"Current Value: ${current_value:,.2f}")
print(f"Current P&L: ${current_pnl:,.2f} ({pnl_percentage:.2f}%)")
print(f"\n=== RISK PARAMETERS ===")
print(f"Stop-Loss Level (5%): ${stop_loss_price:,.2f}")
print(f"Take-Profit Level (10%): ${take_profit_price:,.2f}")
print(f"Distance to Stop-Loss: {distance_to_stop_loss:.2f}%")
print(f"Distance to Take-Profit: {distance_to_take_profit:.2f}%")
print(f"\n=== ALERT STATUS ===")
print(f"Stop-Loss Triggered: {'YES ⚠️' if stop_loss_triggered else 'NO ✅'}")
print(f"Take-Profit Triggered: {'YES ⚠️' if take_profit_triggered else 'NO ✅'}")
print(f"Current Drawdown: {abs(pnl_percentage):.2f}%" if pnl_percentage < 0 else f"Current Gain: {pnl_percentage:.2f}%")
print(f"\n=== TRADING ACTIVITY ===")
print(f"Total Trades: {len(trades)}")
print(f"BTC Trades: {len(btc_trades)}")
print("\nTrades by Model:")
for model, count in model_counts.items():
    print(f"  {model}: {count} trades")
print("\nLatest 5 Trades:")
for trade in latest_trades:
    print(f"  {trade['time']} - {trade['model']} - {trade['side']} - ${trade['price']:,.2f}")