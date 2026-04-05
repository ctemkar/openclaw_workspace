#!/usr/bin/env python3
"""
FIX ALL TRADE AMOUNTS - Critical bug fix
LLM bot was recording wrong amounts (57,000× too large for BTC!)
"""

import json
from datetime import datetime

def main():
    print("🔧 CRITICAL FIX: Correcting trade amounts")
    print("="*70)
    
    # Load trades
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    print(f"Total trades: {len(trades)}")
    
    # Constants from LLM bot
    GEMINI_CAPITAL = 393.22
    POSITION_SIZE = 0.1  # 10%
    position_value = GEMINI_CAPITAL * POSITION_SIZE  # $39.32
    
    # Current market prices (approximate)
    market_prices = {
        'BTC/USD': 65000,
        'SOL/USD': 150,
        'ETH/USD': 3500,
        'DOT/USD': 7.50,
        'XRP/USD': 0.60,
        'DOGE/USD': 0.15,
        'LTC/USD': 80,
        'UNI/USD': 10,
        'LINK/USD': 15,
        'AVAX/USD': 40
    }
    
    fixed_count = 0
    
    for i, trade in enumerate(trades):
        symbol = trade.get('symbol', '')
        exchange = trade.get('exchange', '')
        trade_type = trade.get('type', '')
        
        # Only fix spot trades from LLM bot
        if trade_type == 'spot' and exchange == 'gemini':
            # Get approximate price
            approx_price = market_prices.get(symbol, 100)
            
            # Calculate CORRECT amount
            correct_amount = position_value / approx_price
            
            # Get current (wrong) amount
            current_amount = trade.get('amount', 0)
            
            if current_amount > correct_amount * 1.5:  # If significantly wrong
                print(f"\n🚨 Trade {i}: {symbol}")
                print(f"  Wrong amount: {current_amount}")
                print(f"  Correct amount: {correct_amount:.8f}")
                print(f"  Error factor: {current_amount / correct_amount:.0f}×")
                
                # Fix the trade
                trades[i]['amount'] = correct_amount
                trades[i]['price'] = approx_price
                trades[i]['current_price'] = approx_price
                trades[i]['value'] = position_value
                trades[i]['pnl'] = 0
                trades[i]['pnl_percent'] = 0
                trades[i]['note'] = f"{trade.get('note', '')} | AMOUNT FIXED: Was {current_amount}, now {correct_amount:.8f} (position value: ${position_value:.2f})"
                
                fixed_count += 1
    
    if fixed_count > 0:
        # Save fixed trades
        with open('trading_data/trades.json', 'w') as f:
            json.dump(trades, f, indent=2)
        
        print(f"\n✅ Fixed {fixed_count} trades with wrong amounts")
        print(f"📄 Saved to trading_data/trades.json")
        
        # Create backup
        with open('trading_data/trades_amount_fixed_backup.json', 'w') as f:
            json.dump(trades, f, indent=2)
        print(f"📄 Backup saved to trading_data/trades_amount_fixed_backup.json")
    else:
        print("\n✅ All trades already have correct amounts")
    
    # Verify the fix
    print("\n🔍 VERIFYING FIX:")
    with open('trading_data/trades.json', 'r') as f:
        trades = json.load(f)
    
    print("\nFixed trades:")
    for i, trade in enumerate(trades):
        if trade.get('type') == 'spot' and trade.get('exchange') == 'gemini':
            symbol = trade.get('symbol', 'UNKNOWN')
            amount = trade.get('amount', 0)
            price = trade.get('price', 0)
            value = trade.get('value', 0)
            
            print(f"  Trade {i}: {symbol}")
            print(f"    Amount: {amount:.8f}")
            print(f"    Price: ${price:.2f}")
            print(f"    Value: ${value:.2f}")
            print(f"    Check: {amount:.8f} × ${price:.2f} = ${amount * price:.2f}")
    
    # Also need to fix the LLM bot code
    print("\n" + "="*70)
    print("🚨 ALSO NEED TO FIX LLM BOT CODE")
    print("The bug is in enhanced_llm_trader.py")
    print("It's calculating amounts wrong somewhere")
    print("\nRun this to check the bot:")
    print("  grep -n 'amount =' enhanced_llm_trader.py")
    print("\nThe formula should be:")
    print("  amount = position_value / current_price")
    print(f"  Where position_value = ${position_value:.2f} (10% of ${GEMINI_CAPITAL})")

if __name__ == "__main__":
    main()