#!/usr/bin/env python3
"""
SHOW TOP 10 SPREADS NOW - Direct from arbitrage bot logs
"""

import os
import re
from datetime import datetime

print("=" * 80)
print(f"📊 ACTUAL TOP 10 SPREADS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

LOG_FILE = "real_26_crypto_arbitrage.log"

if not os.path.exists(LOG_FILE):
    print("❌ Arbitrage log file not found!")
    print(f"   Expected: {LOG_FILE}")
    exit(1)

# Read the log file
with open(LOG_FILE, 'r') as f:
    content = f.read()

# Find the most recent TOP 10 SPREADS section
sections = content.split("TOP 10 CRYPTO SPREADS")
if len(sections) < 2:
    print("❌ No TOP 10 SPREADS found in log!")
    exit(1)

latest_section = sections[-1]

# Find the timestamp of this section
lines = content.split('\n')
for i in range(len(lines)-1, -1, -1):
    if "TOP 10 CRYPTO SPREADS" in lines[i]:
        # Get timestamp from previous line
        if i > 0:
            timestamp_line = lines[i-1]
            print(f"📅 Last scan: {timestamp_line.strip()}")
        break

print("\n" + "=" * 80)
print("🏆 TOP 10 CRYPTO SPREADS (Binance ↔ Gemini)")
print("=" * 80)
print("Rank | Crypto | Binance Price | Gemini Price | Spread % | Profit/$100 | Opportunity")
print("-" * 80)

# Parse and display the top 10
spreads_found = 0
lines = latest_section.split('\n')

for line in lines:
    # Match: "   1 | YFI    | $   2473.0000 | $   2456.5400 |       0.67% | $     0.67 | G→B"
    match = re.match(r'\s*(\d+)\s*\|\s*(\w+)\s*\|\s*\$\s*([\d\.]+)\s*\|\s*\$\s*([\d\.]+)\s*\|\s*([-\d\.]+)%\s*\|\s*\$\s*([\d\.]+)\s*\|\s*(\w+→\w+)', line)
    
    if match:
        rank, crypto, binance_price, gemini_price, spread_percent, profit_per_100, opportunity = match.groups()
        
        # Format for display
        spread_float = float(spread_percent)
        tradable = "✅" if abs(spread_float) >= 0.5 else "⏳"
        
        # Color code positive/negative spreads
        if spread_float > 0:
            spread_display = f"\033[92m{spread_percent:>7}%\033[0m"  # Green
        else:
            spread_display = f"\033[91m{spread_percent:>7}%\033[0m"  # Red
        
        print(f"{rank:>4} | {crypto:6} | ${binance_price:>12} | ${gemini_price:>11} | {spread_display} | ${profit_per_100:>10} | {opportunity:>10} {tradable}")
        spreads_found += 1
        
        if spreads_found >= 10:
            break

if spreads_found == 0:
    print("❌ No spread data found in the latest section!")
    
    # Show what IS in the section
    print("\n🔍 What's in the latest section:")
    for i, line in enumerate(latest_section.split('\n')[:20]):
        if line.strip():
            print(f"  {i:2}: {line}")

# Find and show summary
print("\n" + "=" * 80)
print("📈 SUMMARY")
print("=" * 80)

# Find best opportunity
for line in reversed(lines):
    if "Best opportunity:" in line:
        print(f"🎯 {line.strip()}")
    if "Action:" in line:
        print(f"🚀 {line.strip()}")
    if "TRADABLE:" in line:
        print(f"✅ {line.strip()}")
    if "Average spread:" in line:
        print(f"📊 {line.strip()}")

# Count tradable opportunities
tradable_count = 0
for line in lines:
    if "Trading opportunities found:" in line:
        print(f"📋 {line.strip()}")
        # Extract number
        match = re.search(r'(\d+)', line)
        if match:
            tradable_count = int(match.group(1))

print(f"\n🔍 Analysis:")
print(f"   • Total spreads shown: {spreads_found}")
print(f"   • Tradable opportunities (≥0.5%): {tradable_count}")
print(f"   • Data source: {LOG_FILE}")
print(f"   • Generated: {datetime.now().strftime('%H:%M:%S')}")

print("\n" + "=" * 80)
print("💡 LEGEND:")
print("   ✅ = Tradable (Spread ≥ 0.5%)")
print("   ⏳ = Monitoring (Spread < 0.5%)")
print("   \033[92mGreen\033[0m = Positive spread (Gemini > Binance)")
print("   \033[91mRed\033[0m = Negative spread (Binance > Gemini)")
print("=" * 80)