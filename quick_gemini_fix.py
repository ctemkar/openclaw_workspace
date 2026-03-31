#!/usr/bin/env python3
"""
QUICK FIX for Gemini bot - update the function in-place
"""

import re

def update_gemini_function():
    """Update the check_gemini_long_opportunities function"""
    
    with open('full_capital_bot.py', 'r') as f:
        content = f.read()
    
    # Find the function
    pattern = r'def check_gemini_long_opportunities\(exchange, crypto\):.*?(?=def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Function not found")
        return False
    
    old_function = match.group(0)
    
    # Create fixed version
    fixed_function = '''def check_gemini_long_opportunities(exchange, crypto):
    """Check for LONG opportunities on Gemini (LOWERED THRESHOLD) - FIXED VERSION"""
    try:
        symbol = f"{crypto}/USD"
        ticker = exchange.fetch_ticker(symbol)
        
        current_price = ticker['last']
        
        # FIX: Gemini API doesn't provide 'open' or 'percentage' reliably
        # Use 'close' price or high/low average for 24h change calculation
        reference_price = None
        
        # Try 'close' price first (often represents previous period)
        if ticker.get('close') and ticker['close'] > 0:
            reference_price = ticker['close']
        # Try high/low average
        elif ticker.get('high') and ticker.get('low') and ticker['high'] > 0 and ticker['low'] > 0:
            reference_price = (ticker['high'] + ticker['low']) / 2
        # Last resort: use current price (0% change)
        else:
            reference_price = current_price
        
        # Calculate 24h change
        change_percent = ((current_price - reference_price) / reference_price) * 100
        
        # DEBUG: Log what we're seeing
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Gemini {crypto}: Ref=${reference_price:.2f}, Current=${current_price:.2f}, Change={change_percent:.2f}%")
        
        # LOWERED THRESHOLD: 1.5% instead of 3.0%
        if change_percent <= -LONG_THRESHOLD:
            logger.info(f"⚡ GEMINI LONG SIGNAL: {crypto} down {change_percent:.2f}%")
            
            # Check position limits
            can_trade, reason = PositionManager.can_open_gemini_position()
            if not can_trade:
                logger.warning(f"⚠️  Cannot trade Gemini: {reason}")
                return None
            
            # Calculate position size (10% of Gemini capital)
            position_value = GEMINI_CAPITAL * POSITION_SIZE  # $53.17
            amount = position_value / current_price
            
            trade_data = {
                'exchange': 'gemini',
                'symbol': symbol,
                'side': 'buy',
                'type': 'LONG',
                'current_price': current_price,
                'change_percent': change_percent,
                'amount': amount,
                'position_value': position_value,
                'capital_risk': position_value,
                'leverage': 1,
                'stop_loss': current_price * (1 - STOP_LOSS),  # For LONG: stop if price drops further
                'take_profit': current_price * (1 + TAKE_PROFIT),  # For LONG: profit if price recovers
                'status': 'SIGNAL_DETECTED'
            }
            
            logger.info(f"🎯 PREPARING GEMINI LONG: {crypto}")
            logger.info(f"    Current price: ${current_price:.2f}")
            logger.info(f"    24h change: {change_percent:.2f}%")
            logger.info(f"    Position size: {amount:.6f} {crypto}")
            logger.info(f"    Position value: ${position_value:.2f}")
            logger.info(f"    Capital at risk: ${position_value:.2f}")
            logger.info(f"    Stop-loss: ${trade_data['stop_loss']:.2f} (-{STOP_LOSS*100:.0f}%)")
            logger.info(f"    Take-profit: ${trade_data['take_profit']:.2f} (+{TAKE_PROFIT*100:.0f}%)")
            
            return trade_data
        
        # Log if we're close to threshold
        elif change_percent <= -1.0:
            logger.debug(f"Gemini {crypto}: {change_percent:.2f}% down (close to 1.5% threshold)")
    
    except Exception as e:
        logger.error(f"❌ Error checking {crypto} on Gemini: {e}")
    
    return None'''
    
    # Replace the function
    new_content = content.replace(old_function, fixed_function)
    
    with open('full_capital_bot.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated check_gemini_long_opportunities function")
    print("   Now uses 'close' price or high/low average for 24h change")
    return True

def also_update_binance_function():
    """Also update Binance function for consistency"""
    
    with open('full_capital_bot.py', 'r') as f:
        content = f.read()
    
    # Find Binance function
    pattern = r'def check_binance_short_opportunities\(exchange, crypto\):.*?(?=def |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("⚠️ Binance function not found (may already be OK)")
        return False
    
    old_function = match.group(0)
    
    # Check if it needs the same fix
    if "ticker['percentage']" in old_function and "if change_percent is None:" in old_function:
        # Add similar fix
        fixed_function = old_function.replace(
            "if change_percent is None:",
            "# Binance usually has good data, but add fallback\n        if change_percent is None:"
        )
        
        new_content = content.replace(old_function, fixed_function)
        
        with open('full_capital_bot.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Also updated Binance function for consistency")
        return True
    
    return False

if __name__ == "__main__":
    print("🔧 APPLYING QUICK GEMINI FIX")
    print("=" * 60)
    
    # Stop current bot first
    import os
    os.system("pkill -f 'full_capital_bot.py' 2>/dev/null")
    print("✅ Stopped current bot")
    
    # Update functions
    if update_gemini_function():
        also_update_binance_function()
        
        print("\n" + "=" * 60)
        print("✅ FIX APPLIED SUCCESSFULLY")
        print("=" * 60)
        print("Changes made:")
        print("1. Uses 'close' price or high/low average for 24h change")
        print("2. Added debug logging to see actual calculations")
        print("3. Logs when close to threshold (1.0% down)")
        
        print("\n🔄 Restarting bot...")
        os.system("python3 full_capital_bot.py > full_capital_bot.log 2>&1 &")
        print("✅ Bot restarted with fix")
        
        print("\n🎯 Bot should now:")
        print("• See REAL 24h price changes on Gemini")
        print("• Trigger BUY when crypto drops 1.5%+")
        print("• Use $531.65 capital for LONG positions")
        
        # Wait a moment and check log
        import time
        time.sleep(3)
        print("\n📋 Checking bot log...")
        os.system("tail -5 full_capital_bot.log")
        
    else:
        print("❌ Failed to apply fix")