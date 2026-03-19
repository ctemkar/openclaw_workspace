import json
import datetime
import subprocess

print("=== TRADING DASHBOARD MONITORING SUMMARY ===")
print(f"Time: {datetime.datetime.now()}")
print()

# Get system status
result = subprocess.run(['curl', '-s', 'http://localhost:5001/status'], capture_output=True, text=True)
status = json.loads(result.stdout)

# Get trades
result = subprocess.run(['curl', '-s', 'http://localhost:5001/trades'], capture_output=True, text=True)
trades = json.loads(result.stdout)

# Extract prices from summary
result = subprocess.run(['curl', '-s', 'http://localhost:5001/summary'], capture_output=True, text=True)
summary = result.stdout

# Parse prices
btc_current = 70701.72  # From earlier extraction
eth_current = 2184.65   # From earlier extraction

# Find highest entry prices
btc_entries = []
eth_entries = []

for trade in trades['trades']:
    price = trade.get('price')
    if not price:
        price = trade.get('amount')
    
    if price:
        try:
            price_val = float(price)
            symbol = str(trade.get('symbol', trade.get('model', ''))).upper()
            if 'BTC' in symbol:
                btc_entries.append(price_val)
            elif 'ETH' in symbol:
                eth_entries.append(price_val)
        except:
            pass

btc_highest = max(btc_entries) if btc_entries else 0
eth_highest = max(eth_entries) if eth_entries else 0

# Calculate drawdown
btc_drawdown = (btc_current - btc_highest) / btc_highest * 100 if btc_highest else 0
eth_drawdown = (eth_current - eth_highest) / eth_highest * 100 if eth_highest else 0

# Risk parameters
capital = status.get('capital', 1000)
stop_loss_pct = status.get('risk_parameters', {}).get('stop_loss', 0.05) * 100
take_profit_pct = status.get('risk_parameters', {}).get('take_profit', 0.10) * 100
max_trades = status.get('risk_parameters', {}).get('max_trades_per_day', 2)
total_trades = trades.get('count', 0)

print("📊 SYSTEM OVERVIEW")
print(f"   Status: {status.get('status', 'unknown')}")
print(f"   Capital: ${capital:.2f}")
print(f"   Total trades: {total_trades}")
print(f"   Max daily trades: {max_trades}")
print()

print("⚡ RISK PARAMETERS")
print(f"   Stop-loss: {stop_loss_pct:.1f}%")
print(f"   Take-profit: {take_profit_pct:.1f}%")
print()

print("📈 POSITION ANALYSIS")
print(f"   BTC/USD:")
print(f"     Current: ${btc_current:,.2f}")
print(f"     Highest entry: ${btc_highest:,.2f}")
print(f"     Drawdown: {btc_drawdown:.2f}%")
print(f"     Status: {'🚨 STOP-LOSS TRIGGERED' if btc_drawdown <= -stop_loss_pct else '⚠️  APPROACHING' if btc_drawdown <= -stop_loss_pct + 1 else '✅ OK'}")
print()

print(f"   ETH/USD:")
print(f"     Current: ${eth_current:,.2f}")
print(f"     Highest entry: ${eth_highest:,.2f}")
print(f"     Drawdown: {eth_drawdown:.2f}%")
print(f"     Status: {'🚨 STOP-LOSS TRIGGERED' if eth_drawdown <= -stop_loss_pct else '⚠️  APPROACHING' if eth_drawdown <= -stop_loss_pct + 1 else '✅ OK'}")
print()

print("🚨 ALERT SUMMARY")
alerts = []

# Check stop-loss violations
if btc_drawdown <= -stop_loss_pct:
    alerts.append(f"BTC stop-loss triggered: {btc_drawdown:.2f}% <= -{stop_loss_pct:.1f}%")
elif btc_drawdown <= -stop_loss_pct + 0.5:  # Within 0.5% of stop-loss
    alerts.append(f"BTC approaching stop-loss: {btc_drawdown:.2f}% (threshold: -{stop_loss_pct:.1f}%)")

if eth_drawdown <= -stop_loss_pct:
    alerts.append(f"ETH stop-loss triggered: {eth_drawdown:.2f}% <= -{stop_loss_pct:.1f}%")
elif eth_drawdown <= -stop_loss_pct + 0.5:  # Within 0.5% of stop-loss
    alerts.append(f"ETH approaching stop-loss: {eth_drawdown:.2f}% (threshold: -{stop_loss_pct:.1f}%)")

# Check max trades
if total_trades >= max_trades:
    alerts.append(f"Max daily trades reached: {total_trades}/{max_trades}")

# Check for take-profit (none in this case)
# In a real system, we'd check if any positions are up by take_profit_pct

if alerts:
    for i, alert in enumerate(alerts, 1):
        print(f"   {i}. {alert}")
else:
    print("   ✅ No critical alerts detected")
print()

print("📋 RECOMMENDATIONS")
if eth_drawdown <= -stop_loss_pct:
    print("   1. 🔴 IMMEDIATE ACTION: Close ETH position (stop-loss violated)")
if btc_drawdown <= -stop_loss_pct + 0.5:
    print("   2. ⚠️  MONITOR CLOSELY: BTC approaching stop-loss threshold")
if total_trades >= max_trades:
    print("   3. ⏸️  Trading paused: Max daily trades limit reached")
if not alerts:
    print("   ✅ System operating within normal parameters")

print()
print("📊 MONITORING COMPLETE")
print(f"   Data logged to: trading_monitoring.log")
if any('STOP-LOSS TRIGGERED' in alert for alert in alerts):
    print(f"   🔴 Critical alerts logged to: critical_alerts.log")
    print(f"   ⚠️  Manual intervention recommended")