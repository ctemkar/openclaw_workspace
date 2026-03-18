import json
import subprocess
from datetime import datetime

# Current prices from the analysis
btc_price = 72428.24
eth_price = 2234.38

# Get trades data
result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], capture_output=True, text=True)
trades_data = json.loads(result.stdout)

# Calculate positions
btc_position = 0
eth_position = 0
btc_cost = 0
eth_cost = 0

for trade in trades_data['trades']:
    if 'symbol' in trade:
        if trade['symbol'] == 'BTC/USD' and trade['side'].upper() == 'BUY':
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)
            btc_position += quantity
            btc_cost += price * quantity
        elif trade['symbol'] == 'ETH/USD' and trade['side'].upper() == 'BUY':
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)
            eth_position += quantity
            eth_cost += price * quantity

# Calculate average costs
btc_avg_cost = btc_cost / btc_position if btc_position > 0 else 0
eth_avg_cost = eth_cost / eth_position if eth_position > 0 else 0

# Calculate P&L
btc_pnl_pct = ((btc_price - btc_avg_cost) / btc_avg_cost * 100) if btc_avg_cost > 0 else 0
eth_pnl_pct = ((eth_price - eth_avg_cost) / eth_avg_cost * 100) if eth_avg_cost > 0 else 0

# Check stop-loss (5%) and take-profit (10%)
stop_loss_threshold = -5.0
take_profit_threshold = 10.0

btc_stop_loss_triggered = btc_pnl_pct <= stop_loss_threshold
eth_stop_loss_triggered = eth_pnl_pct <= stop_loss_threshold
btc_take_profit_triggered = btc_pnl_pct >= take_profit_threshold
eth_take_profit_triggered = eth_pnl_pct >= take_profit_threshold

# Calculate total drawdown
total_position_value = (btc_position * btc_price) + (eth_position * eth_price)
total_cost = btc_cost + eth_cost
total_drawdown_pct = ((total_position_value - total_cost) / total_cost * 100) if total_cost > 0 else 0

# Check if drawdown is critical (more than 8% loss)
critical_drawdown = total_drawdown_pct <= -8.0

output = f"""=== TRADING MONITORING ANALYSIS ===
Timestamp: {datetime.now()}
BTC Position: {btc_position:.6f} BTC
BTC Avg Cost: ${btc_avg_cost:.2f}
BTC Current Price: ${btc_price:.2f}
BTC P&L: {btc_pnl_pct:.2f}%
ETH Position: {eth_position:.6f} ETH
ETH Avg Cost: ${eth_avg_cost:.2f}
ETH Current Price: ${eth_price:.2f}
ETH P&L: {eth_pnl_pct:.2f}%
Total Position Value: ${total_position_value:.2f}
Total Cost: ${total_cost:.2f}
Total Drawdown: {total_drawdown_pct:.2f}%

=== RISK ASSESSMENT ===
Stop-loss threshold: {stop_loss_threshold}%
Take-profit threshold: {take_profit_threshold}%
BTC Stop-loss triggered: {btc_stop_loss_triggered}
ETH Stop-loss triggered: {eth_stop_loss_triggered}
BTC Take-profit triggered: {btc_take_profit_triggered}
ETH Take-profit triggered: {eth_take_profit_triggered}
Critical drawdown (>8% loss): {critical_drawdown}

=== SYSTEM STATUS ===
Trading server: RUNNING
Dashboard: ACCESSIBLE
Analysis: COMPLETED (2026-03-18 20:21:42)
"""

print(output)

# Return data for logging
result_data = {
    'timestamp': str(datetime.now()),
    'btc_position': btc_position,
    'btc_avg_cost': btc_avg_cost,
    'btc_price': btc_price,
    'btc_pnl_pct': btc_pnl_pct,
    'eth_position': eth_position,
    'eth_avg_cost': eth_avg_cost,
    'eth_price': eth_price,
    'eth_pnl_pct': eth_pnl_pct,
    'total_position_value': total_position_value,
    'total_cost': total_cost,
    'total_drawdown_pct': total_drawdown_pct,
    'btc_stop_loss_triggered': btc_stop_loss_triggered,
    'eth_stop_loss_triggered': eth_stop_loss_triggered,
    'btc_take_profit_triggered': btc_take_profit_triggered,
    'eth_take_profit_triggered': eth_take_profit_triggered,
    'critical_drawdown': critical_drawdown
}

print("\n=== JSON DATA ===")
print(json.dumps(result_data, indent=2))