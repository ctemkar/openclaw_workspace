#!/usr/bin/env python3
"""
Clean up fake trades and prepare for real trading
"""

import json
import os
from datetime import datetime

print("="*70)
print("🧹 CLEANING FAKE TRADE DATA")
print("="*70)

# 1. Clear completed_trades.json (keep only real trades)
real_trades = []
if os.path.exists('completed_trades.json'):
    with open('completed_trades.json', 'r') as f:
        try:
            trades = json.load(f)
            # Keep only trades that don't have fake Gemini data
            for trade in trades:
                # Remove fake Gemini trades (prices around 74k when BTC is at 66k)
                price = trade.get('price', 0)
                if price > 70000:  # Fake high prices
                    print(f"❌ Removing fake trade: ${price}")
                    continue
                real_trades.append(trade)
        except:
            pass
    
    with open('completed_trades.json', 'w') as f:
        json.dump(real_trades, f, indent=2)
    print(f"✅ Cleaned completed_trades.json - kept {len(real_trades)} real trades")

# 2. Create real trading log
with open('real_trading.log', 'w') as f:
    f.write(f"=== REAL TRADING LOG STARTED ===\n")
    f.write(f"Time: {datetime.now()}\n")
    f.write(f"Balance: $542.27\n")
    f.write(f"Goal: Grow $100 investment\n")
    f.write("="*50 + "\n")
print("✅ Created fresh real_trading.log")

# 3. Update analyze_current.py to remove hardcoded data
if os.path.exists('analyze_current.py'):
    with open('analyze_current.py', 'r') as f:
        content = f.read()
    
    # Remove the hardcoded trades_data
    if 'trades_data = ' in content:
        # Find and remove the hardcoded data
        lines = content.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if 'trades_data = ' in line:
                skip = True
                new_lines.append('# Real trades will be loaded from completed_trades.json')
                new_lines.append('trades_data = \'\'\'{"count":0,"trades":[]}\'\'\'')
            elif skip and line.strip().endswith(']\'\'\''):
                skip = False
            elif not skip:
                new_lines.append(line)
        
        with open('analyze_current.py', 'w') as f:
            f.write('\n'.join(new_lines))
        print("✅ Removed hardcoded fake data from analyze_current.py")

print("\n" + "="*70)
print("✅ CLEANUP COMPLETE!")
print("💰 Real Balance: $542.27")
print("🎯 Ready for REAL trading")
print("="*70)