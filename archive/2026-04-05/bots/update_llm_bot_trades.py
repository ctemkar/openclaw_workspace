#!/usr/bin/env python3
"""
Update LLM bot to create trades with correct structure
"""

import json

def update_bot_code():
    print("🔧 Updating LLM bot trade structure...")
    
    with open('enhanced_llm_trader.py', 'r') as f:
        content = f.read()
    
    # Update Gemini trade creation
    old_gemini = """              trade_data = {
                  'exchange': 'gemini',
                  'symbol': symbol,
                  'side': 'buy',
                  'type': f'LONG_{confidence}',
                  'current_price': current_price,
                  'change_24h': change_24h,
                  'amount': amount,
                  'position_value': position_value,
                  'stop_loss': current_price * (1 - STOP_LOSS),
                  'take_profit': current_price * (1 + TAKE_PROFIT),
                  'llm_decision': llm_decision or 'TIMEOUT',
                  'confidence': confidence,
                  'timestamp': datetime.now().isoformat()
              }"""
    
    new_gemini = """              trade_data = {
                  'exchange': 'gemini',
                  'symbol': symbol,
                  'side': 'buy',
                  'type': f'LONG_{confidence}',
                  'price': current_price,  # Entry price
                  'current_price': current_price,  # Current price (same as entry for new trade)
                  'change_24h': change_24h,
                  'amount': amount,
                  'value': position_value,  # Use 'value' instead of 'position_value'
                  'position_value': position_value,
                  'pnl': 0,  # Initialize P&L to 0
                  'pnl_percent': 0,  # Initialize P&L % to 0
                  'stop_loss': current_price * (1 - STOP_LOSS),
                  'take_profit': current_price * (1 + TAKE_PROFIT),
                  'llm_decision': llm_decision or 'TIMEOUT',
                  'confidence': confidence,
                  'timestamp': datetime.now().isoformat()
              }"""
    
    # Update Binance trade creation
    old_binance = """              trade_data = {
                  'exchange': 'binance',
                  'symbol': f"{symbol}:USDT",
                  'side': 'sell',
                  'type': f'SHORT_{confidence}',
                  'current_price': current_price,
                  'change_24h': change_24h,
                  'amount': amount,
                  'position_value': position_value,
                  'stop_loss': current_price * (1 + STOP_LOSS),
                  'take_profit': current_price * (1 - TAKE_PROFIT),
                  'llm_decision': llm_decision or 'TIMEOUT',
                  'confidence': confidence,
                  'timestamp': datetime.now().isoformat()
              }"""
    
    new_binance = """              trade_data = {
                  'exchange': 'binance',
                  'symbol': f"{symbol}:USDT",
                  'side': 'sell',
                  'type': f'SHORT_{confidence}',
                  'price': current_price,  # Entry price
                  'current_price': current_price,  # Current price (same as entry for new trade)
                  'change_24h': change_24h,
                  'amount': amount,
                  'value': position_value,  # Use 'value' instead of 'position_value'
                  'position_value': position_value,
                  'pnl': 0,  # Initialize P&L to 0
                  'pnl_percent': 0,  # Initialize P&L % to 0
                  'stop_loss': current_price * (1 + STOP_LOSS),
                  'take_profit': current_price * (1 - TAKE_PROFIT),
                  'llm_decision': llm_decision or 'TIMEOUT',
                  'confidence': confidence,
                  'timestamp': datetime.now().isoformat()
              }"""
    
    # Apply updates
    if old_gemini in content:
        content = content.replace(old_gemini, new_gemini)
        print("✅ Updated Gemini trade structure")
    else:
        print("⚠️ Could not find Gemini trade structure to update")
    
    if old_binance in content:
        content = content.replace(old_binance, new_binance)
        print("✅ Updated Binance trade structure")
    else:
        print("⚠️ Could not find Binance trade structure to update")
    
    # Save updated file
    with open('enhanced_llm_trader.py', 'w') as f:
        f.write(content)
    
    print("📄 Updated enhanced_llm_trader.py")
    
    # Also update the simple_llm_trader.py if it exists
    try:
        with open('simple_llm_trader.py', 'r') as f:
            simple_content = f.read()
        
        # Look for trade creation in simple bot
        if "'exchange': 'gemini'" in simple_content:
            # Simple pattern matching for simple bot
            lines = simple_content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if "'exchange': 'gemini'" in line:
                    # Find the trade_data dict
                    for j in range(i, min(i+20, len(lines))):
                        if '}' in lines[j] and "'exchange': 'gemini'" in '\n'.join(lines[i:j+1]):
                            # Found the dict, add missing fields
                            dict_lines = lines[i:j+1]
                            new_dict_lines = []
                            for dict_line in dict_lines:
                                new_dict_lines.append(dict_line)
                                if "'amount':" in dict_line:
                                    # Add value field after amount
                                    new_dict_lines.append("                    'value': amount * price,")
                                if "'timestamp':" in dict_line:
                                    # Add P&L fields before timestamp
                                    new_dict_lines.insert(-1, "                    'pnl': 0,")
                                    new_dict_lines.insert(-1, "                    'pnl_percent': 0,")
                                    new_dict_lines.insert(-1, "                    'current_price': price,")
                            
                            # Replace the dict
                            simple_content = simple_content.replace('\n'.join(dict_lines), '\n'.join(new_dict_lines))
                            updated = True
                            break
                    if updated:
                        break
            
            if updated:
                with open('simple_llm_trader.py', 'w') as f:
                    f.write(simple_content)
                print("✅ Updated simple_llm_trader.py")
            else:
                print("⚠️ Could not update simple_llm_trader.py")
    except FileNotFoundError:
        print("ℹ️ simple_llm_trader.py not found, skipping")
    
    print("\n🎯 LLM bots will now create trades with proper structure:")
    print("   • price (entry price)")
    print("   • current_price (same as entry for new trades)")
    print("   • value (position value)")
    print("   • pnl (initialized to 0)")
    print("   • pnl_percent (initialized to 0)")

if __name__ == "__main__":
    update_bot_code()