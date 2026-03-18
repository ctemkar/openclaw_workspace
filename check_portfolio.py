#!/usr/bin/env python3
import json
from datetime import datetime

# Current BTC price from CoinGecko
btc_price = 74249

# Trading history
trades = [
    {'amount': 0.00013374340845611425, 'price': 74770.04},
    {'amount': 0.00013368983957219252, 'price': 74800.0},
    {'amount': 0.00013381716266667096, 'price': 74728.83},
    {'amount': 0.00013381716266667096, 'price': 74728.83}
]

# Calculate portfolio metrics
total_btc = sum(t['amount'] for t in trades)
total_investment = sum(t['amount'] * t['price'] for t in trades)
current_value = total_btc * btc_price
pnl = current_value - total_investment
pnl_percent = (pnl / total_investment) * 100

# Risk parameters
stop_loss_threshold = total_investment * 0.97
take_profit_threshold = total_investment * 1.02
critical_drawdown_threshold = total_investment * 0.95

# Check alerts
stop_loss_triggered = current_value < stop_loss_threshold
take_profit_triggered = current_value > take_profit_threshold
critical_drawdown = current_value < critical_drawdown_threshold

# Generate monitoring output
output = []
output.append(f"TRADING DASHBOARD MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
output.append(f"BTC Price: ${btc_price:,}")
output.append(f"Total BTC Holdings: {total_btc:.6f} BTC")
output.append(f"Total Investment: ${total_investment:.2f}")
output.append(f"Current Value: ${current_value:.2f}")
output.append(f"P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
output.append(f"Stop Loss (3%): ${stop_loss_threshold:.2f}")
output.append(f"Take Profit (2%): ${take_profit_threshold:.2f}")
output.append(f"Critical Drawdown (5%): ${critical_drawdown_threshold:.2f}")
output.append("")
output.append("ALERT STATUS:")
output.append(f"Stop Loss Triggered: {'YES' if stop_loss_triggered else 'NO'}")
output.append(f"Take Profit Triggered: {'YES' if take_profit_triggered else 'NO'}")
output.append(f"Critical Drawdown: {'YES' if critical_drawdown else 'NO'}")

# Critical alerts
critical_alerts = []
if stop_loss_triggered:
    alert_msg = f"🚨 STOP LOSS TRIGGERED! Current value ${current_value:.2f} is below stop loss threshold ${stop_loss_threshold:.2f}"
    output.append(alert_msg)
    critical_alerts.append(alert_msg)
if take_profit_triggered:
    alert_msg = f"🎯 TAKE PROFIT TRIGGERED! Current value ${current_value:.2f} is above take profit threshold ${take_profit_threshold:.2f}"
    output.append(alert_msg)
    critical_alerts.append(alert_msg)
if critical_drawdown:
    alert_msg = f"🔥 CRITICAL DRAWDOWN! Current value ${current_value:.2f} is below critical threshold ${critical_drawdown_threshold:.2f}"
    output.append(alert_msg)
    critical_alerts.append(alert_msg)

# Print to console
print("\n".join(output))

# Log to monitoring file
with open("trading_monitoring.log", "a") as f:
    f.write("\n".join(output))
    f.write("\n" + "="*80 + "\n")

# Log critical alerts if any
if critical_alerts:
    with open("critical_alerts.log", "a") as f:
        f.write(f"\nCRITICAL ALERTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n".join(critical_alerts))
        f.write("\n" + "="*80 + "\n")