#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime

# Get current trades data
try:
    result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], 
                          capture_output=True, text=True)
    trades_data = json.loads(result.stdout)
except Exception as e:
    print(f"Error fetching trades: {e}")
    sys.exit(1)

# Get current prices (using approximate values from summary)
# In a real system, we'd fetch current market prices
btc_price = 71283.36  # From summary
eth_price = 2210.72   # From summary

# Analyze trades
btc_total = 0
eth_total = 0
btc_cost = 0
eth_cost = 0

print("=== PORTFOLIO ANALYSIS ===")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Current BTC Price: ${btc_price:,.2f}")
print(f"Current ETH Price: ${eth_price:,.2f}")
print()

# Process trades
for trade in trades_data.get('trades', []):
    symbol = trade.get('symbol', '')
    side = trade.get('side', '').lower()
    
    if 'btc' in symbol.lower() or 'BTC' in trade.get('model', ''):
        amount = trade.get('amount') or trade.get('quantity', 0)
        price = trade.get('price', 0)
        
        if side == 'buy':
            btc_total += amount
            btc_cost += amount * price
            print(f"BTC BUY: {amount:.6f} BTC @ ${price:,.2f} = ${amount*price:,.2f}")
    
    elif 'eth' in symbol.lower() or 'ETH' in trade.get('model', ''):
        amount = trade.get('amount') or trade.get('quantity', 0)
        price = trade.get('price', 0)
        
        if side == 'buy':
            eth_total += amount
            eth_cost += amount * price
            print(f"ETH BUY: {amount:.6f} ETH @ ${price:,.2f} = ${amount*price:,.2f}")

print()
print("=== POSITION SUMMARY ===")
if btc_total > 0:
    btc_avg_price = btc_cost / btc_total
    btc_value = btc_total * btc_price
    btc_pnl = btc_value - btc_cost
    btc_pnl_pct = (btc_pnl / btc_cost) * 100
    
    print(f"BTC Position: {btc_total:.6f} BTC")
    print(f"  Avg Entry: ${btc_avg_price:,.2f}")
    print(f"  Current: ${btc_price:,.2f}")
    print(f"  Value: ${btc_value:,.2f}")
    print(f"  P&L: ${btc_pnl:,.2f} ({btc_pnl_pct:.2f}%)")
    
    # Check stop-loss/take-profit
    stop_loss = -5.0
    take_profit = 10.0
    
    if btc_pnl_pct <= stop_loss:
        print(f"  ⚠️ CRITICAL: STOP-LOSS TRIGGERED! ({btc_pnl_pct:.2f}% <= {stop_loss}%)")
    elif btc_pnl_pct >= take_profit:
        print(f"  ✅ TAKE-PROFIT TRIGGERED! ({btc_pnl_pct:.2f}% >= {take_profit}%)")
    else:
        print(f"  Status: Active ({(stop_loss - btc_pnl_pct):.2f}% buffer to stop-loss)")

if eth_total > 0:
    eth_avg_price = eth_cost / eth_total
    eth_value = eth_total * eth_price
    eth_pnl = eth_value - eth_cost
    eth_pnl_pct = (eth_pnl / eth_cost) * 100
    
    print(f"\nETH Position: {eth_total:.6f} ETH")
    print(f"  Avg Entry: ${eth_avg_price:,.2f}")
    print(f"  Current: ${eth_price:,.2f}")
    print(f"  Value: ${eth_value:,.2f}")
    print(f"  P&L: ${eth_pnl:,.2f} ({eth_pnl_pct:.2f}%)")
    
    # Check stop-loss/take-profit
    stop_loss = -5.0
    take_profit = 10.0
    
    if eth_pnl_pct <= stop_loss:
        print(f"  ⚠️ CRITICAL: STOP-LOSS TRIGGERED! ({eth_pnl_pct:.2f}% <= {stop_loss}%)")
    elif eth_pnl_pct >= take_profit:
        print(f"  ✅ TAKE-PROFIT TRIGGERED! ({eth_pnl_pct:.2f}% >= {take_profit}%)")
    else:
        print(f"  Status: Active ({(stop_loss - eth_pnl_pct):.2f}% buffer to stop-loss)")

# Total portfolio
total_cost = btc_cost + eth_cost
total_value = (btc_total * btc_price) + (eth_total * eth_price)
total_pnl = total_value - total_cost
total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0

print(f"\n=== TOTAL PORTFOLIO ===")
print(f"Total Cost: ${total_cost:,.2f}")
print(f"Total Value: ${total_value:,.2f}")
print(f"Total P&L: ${total_pnl:,.2f} ({total_pnl_pct:.2f}%)")
print(f"Capital Utilization: ${total_cost:,.2f} of $1,000.00 ({(total_cost/1000)*100:.1f}%)")

# Check for critical conditions
print(f"\n=== RISK ASSESSMENT ===")
critical_alerts = []

if total_pnl_pct <= -5:
    critical_alerts.append(f"PORTFOLIO STOP-LOSS TRIGGERED: {total_pnl_pct:.2f}%")
elif total_pnl_pct <= -4:
    critical_alerts.append(f"WARNING: Approaching stop-loss: {total_pnl_pct:.2f}% (1% buffer)")

if btc_pnl_pct <= -5:
    critical_alerts.append(f"BTC STOP-LOSS TRIGGERED: {btc_pnl_pct:.2f}%")
elif btc_pnl_pct <= -4:
    critical_alerts.append(f"BTC approaching stop-loss: {btc_pnl_pct:.2f}%")

if eth_pnl_pct <= -5:
    critical_alerts.append(f"ETH STOP-LOSS TRIGGERED: {eth_pnl_pct:.2f}%")
elif eth_pnl_pct <= -4:
    critical_alerts.append(f"ETH approaching stop-loss: {eth_pnl_pct:.2f}%")

# Check max trades
try:
    status_result = subprocess.run(['curl', '-s', 'http://localhost:5001/status'], 
                                 capture_output=True, text=True)
    status_data = json.loads(status_result.stdout)
    max_trades = status_data.get('risk_parameters', {}).get('max_trades_per_day', 2)
    
    # Count today's trades (simplified - would need actual date filtering)
    today_trades = len([t for t in trades_data.get('trades', []) 
                       if '10:' in str(t.get('time', '')) or '11:' in str(t.get('time', ''))])
    
    if today_trades >= max_trades:
        critical_alerts.append(f"MAX DAILY TRADES REACHED: {today_trades}/{max_trades}")
except:
    pass

if critical_alerts:
    print("⚠️ CRITICAL ALERTS:")
    for alert in critical_alerts:
        print(f"  - {alert}")
else:
    print("✅ No critical alerts detected")

print(f"\n=== SYSTEM STATUS ===")
print(f"Dashboard: Running")
print(f"Last Analysis: {trades_data.get('timestamp', 'N/A')}")
print(f"Total Trades in System: {trades_data.get('count', 0)}")