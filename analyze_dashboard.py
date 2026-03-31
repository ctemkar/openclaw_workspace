#!/usr/bin/env python3
import json
import sys
import datetime
import requests

# Fetch data from dashboard
try:
    response = requests.get('http://localhost:5007/api/data', timeout=5)
    data = response.json()
except Exception as e:
    print(f"ERROR: Failed to fetch dashboard data: {e}")
    sys.exit(1)

# Calculate totals
total_capital = data['capital']['total_capital']
deployed = data['capital']['deployed']
position_count = data['capital']['position_count']
avg_position = data['capital']['avg_position_value']
gemini_total = data['capital']['gemini_total']
binance_total = data['capital']['binance_total']
available_gemini = data['capital']['available_gemini']
available_binance = data['capital']['available_binance']

# Calculate total P&L
total_pl = sum(p['unrealized_pl'] for p in data['positions'])
total_pl_percent = (total_pl / deployed * 100) if deployed > 0 else 0

# Check for critical conditions
critical_alerts = []
warnings = []

# Check concentration risk
if position_count > 0:
    symbols = set(p['symbol'] for p in data['positions'])
    if len(symbols) == 1:
        critical_alerts.append(f"CRITICAL: 100% concentration in {list(symbols)[0]}")

# Check if any positions are at risk
for pos in data['positions']:
    pl_percent = pos['unrealized_pl_percent']
    if pl_percent < -2:  # 2% loss
        critical_alerts.append(f"STOP-LOSS TRIGGER: {pos['id']} at {pl_percent:.2f}% loss")
    elif pl_percent > 5:  # 5% profit
        warnings.append(f"TAKE-PROFIT OPPORTUNITY: {pos['id']} at {pl_percent:.2f}% profit")

# Check bot status
bot_status = data['bot_status']['status']
last_activity = data['bot_status']['last_activity']
if "found 0 opportunities" in last_activity:
    warnings.append("Bot finding 0 opportunities in recent cycles")

# Check data freshness
last_updated = data['bot_status']['last_updated']
update_time = datetime.datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
now = datetime.datetime.now(datetime.timezone.utc)
# Make both timezone aware
if update_time.tzinfo is None:
    update_time = update_time.replace(tzinfo=datetime.timezone.utc)
age_minutes = (now - update_time).total_seconds() / 60
if age_minutes > 10:
    warnings.append(f"Data stale: Last update {age_minutes:.1f} minutes ago")

# Get current time
bangkok_tz = datetime.timezone(datetime.timedelta(hours=7))
now_bangkok = datetime.datetime.now(bangkok_tz).strftime('%Y-%m-%d %H:%M:%S')

# Print analysis
print("=== TRADING DASHBOARD ANALYSIS ===")
print(f"Timestamp: {now_bangkok} (Asia/Bangkok)")
print(f"Data Source: Dashboard API (Port 5007)")
print()
print("CAPITAL SUMMARY:")
print(f"  Total Capital: ${total_capital:.2f}")
print(f"  Gemini: ${gemini_total:.2f} ({gemini_total/total_capital*100:.1f}%)")
print(f"  Binance: ${binance_total:.2f} ({binance_total/total_capital*100:.1f}%)")
print(f"  Deployed: ${deployed:.2f} ({deployed/total_capital*100:.1f}%)")
print(f"  Available: ${available_gemini + available_binance:.2f}")
print()
print("POSITION ANALYSIS:")
print(f"  Active Positions: {position_count}")
print(f"  Average Position: ${avg_position:.2f}")
print(f"  Total Unrealized P&L: ${total_pl:.2f} ({total_pl_percent:.2f}%)")
print()
print("BOT STATUS:")
print(f"  Status: {bot_status}")
print(f"  Last Activity: {last_activity}")
print(f"  Last Updated: {last_updated}")
print(f"  Data Age: {age_minutes:.1f} minutes")
print()
print("RISK ASSESSMENT:")
if critical_alerts:
    print("  CRITICAL ALERTS:")
    for alert in critical_alerts:
        print(f"    ⚠️ {alert}")
else:
    print("  ✅ No critical alerts")
print()
if warnings:
    print("  WARNINGS:")
    for warning in warnings:
        print(f"    ⚠️ {warning}")
else:
    print("  ✅ No warnings")
print()
print("RECOMMENDATIONS:")
if "CRITICAL: 100% concentration" in " ".join(critical_alerts):
    print("  1. Implement diversification strategy")
if total_pl_percent > 3:
    print("  2. Consider taking partial profits")
if age_minutes > 5:
    print("  3. Check bot process health")
if "found 0 opportunities" in last_activity:
    print("  4. Review trading parameters (1.0% dip threshold)")
print()
print("=== END ANALYSIS ===")