#!/usr/bin/env python3
"""
Fix position data format for enhanced bot
"""

import json

def fix_position_data():
    """Fix position data format"""
    
    # Load current positions
    with open('26_crypto_trade_history.json', 'r') as f:
        positions = json.load(f)
    
    # Fix each position
    for pos in positions:
        if pos.get('status') == 'OPEN':
            # Ensure 'amount' field exists
            if 'amount' not in pos:
                # Calculate amount from position size and entry price
                position_size = abs(pos.get('position_size', 30))
                entry_price = pos.get('entry_price', pos.get('current_price', 1))
                if entry_price > 0:
                    pos['amount'] = position_size / entry_price
                else:
                    pos['amount'] = 0
            
            # Ensure stop loss and take profit are calculated
            if 'stop_loss' not in pos or pos['stop_loss'] == 0:
                entry_price = pos.get('entry_price', pos.get('current_price', 0))
                if entry_price > 0:
                    # For SHORT: stop if price rises 3%
                    pos['stop_loss'] = entry_price * 1.03
                    pos['take_profit'] = entry_price * 0.95
    
    # Save fixed positions
    with open('26_crypto_trade_history.json', 'w') as f:
        json.dump(positions, f, indent=2)
    
    print(f"✅ Fixed {len(positions)} positions")
    
    # Also update system status
    with open('system_status.json', 'r') as f:
        status = json.load(f)
    
    # Update position count (DOT closed, 4 remain)
    status['positions']['open'] = 4
    status['positions']['closed'] = 3  # DOT + 2 BTC
    
    with open('system_status.json', 'w') as f:
        json.dump(status, f, indent=2)
    
    print("✅ Updated system status")

if __name__ == "__main__":
    fix_position_data()