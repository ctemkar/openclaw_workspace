#!/usr/bin/env python3
"""
Fix new trades structure - add missing fields to trades added by LLM bot
"""

import json
from datetime import datetime

def main():
    print("🔧 Fixing new trades structure...")
    
    # Load trades
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    print(f"Total trades: {len(trades)}")
    
    # Find trades missing required fields
    fixed_count = 0
    for i, trade in enumerate(trades):
        # Check if it's a spot trade missing fields
        if trade.get('type') == 'spot':
            required_fields = ['current_price', 'pnl', 'pnl_percent', 'value']
            missing_fields = [field for field in required_fields if field not in trade]
            
            if missing_fields:
                print(f"\nTrade {i} ({trade.get('symbol', 'UNKNOWN')}) missing fields: {missing_fields}")
                
                # Add missing fields with default values
                if 'current_price' not in trade:
                    trade['current_price'] = trade.get('price', 0)
                
                if 'pnl' not in trade:
                    trade['pnl'] = 0
                
                if 'pnl_percent' not in trade:
                    trade['pnl_percent'] = 0
                
                if 'value' not in trade:
                    # Calculate value = price * amount
                    price = trade.get('price', 0)
                    amount = trade.get('amount', 0)
                    trade['value'] = price * amount
                
                fixed_count += 1
                print(f"  Added: current_price={trade['current_price']}, pnl={trade['pnl']}, value={trade['value']}")
    
    if fixed_count > 0:
        # Save fixed trades
        with open('trading_data/trades.json', 'w') as f:
            json.dump(trades, f, indent=2)
        
        print(f"\n✅ Fixed {fixed_count} trades")
        print(f"📄 Saved to trading_data/trades.json")
        
        # Also create a backup
        with open('trading_data/trades_fixed_backup.json', 'w') as f:
            json.dump(trades, f, indent=2)
        print(f"📄 Backup saved to trading_data/trades_fixed_backup.json")
    else:
        print("\n✅ All trades already have required fields")
    
    # Verify the fix
    print("\n🔍 Verifying fix...")
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    all_good = True
    for i, trade in enumerate(trades):
        if trade.get('type') == 'spot':
            required_fields = ['current_price', 'pnl', 'pnl_percent', 'value']
            missing = [field for field in required_fields if field not in trade]
            if missing:
                print(f"❌ Trade {i} still missing: {missing}")
                all_good = False
    
    if all_good:
        print("✅ All trades now have required fields")
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)