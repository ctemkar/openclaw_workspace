#!/usr/bin/env python3
"""
Test and fix Gemini data collection
"""

import ccxt
import time

def test_gemini_data():
    """Test Gemini API data quality"""
    
    print("🔧 TESTING GEMINI API DATA QUALITY")
    print("=" * 60)
    
    # Initialize Gemini
    exchange = ccxt.gemini({
        'enableRateLimit': True,
    })
    
    cryptos = ['BTC', 'ETH', 'SOL', 'XRP']
    
    for crypto in cryptos:
        try:
            symbol = f"{crypto}/USD"
            ticker = exchange.fetch_ticker(symbol)
            
            print(f"\n📊 {crypto}/USD:")
            print(f"   Last: ${ticker['last']:.2f}")
            print(f"   Open: ${ticker.get('open', 'N/A')}")
            print(f"   High: ${ticker.get('high', 'N/A')}")
            print(f"   Low: ${ticker.get('low', 'N/A')}")
            print(f"   Close: ${ticker.get('close', 'N/A')}")
            print(f"   Percentage (API): {ticker.get('percentage', 'N/A')}")
            
            # Calculate manually
            if ticker.get('open') and ticker['open'] > 0:
                manual_change = ((ticker['last'] - ticker['open']) / ticker['open']) * 100
                print(f"   Manual calc: {manual_change:.2f}%")
            
            # Check all available fields
            print(f"   Available keys: {list(ticker.keys())[:10]}...")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")

def create_fixed_gemini_check():
    """Create fixed version of Gemini check function"""
    
    fixed_code = '''
def check_gemini_long_opportunities_fixed(exchange, crypto):
    """FIXED: Check for LONG opportunities on Gemini"""
    try:
        symbol = f"{crypto}/USD"
        ticker = exchange.fetch_ticker(symbol)
        
        current_price = ticker[\'last\']
        
        # ALWAYS calculate manually - Gemini API percentage is unreliable
        open_price = ticker.get(\'open\')
        if not open_price or open_price <= 0:
            # Try alternative: use 24h average of high/low
            high = ticker.get(\'high\')
            low = ticker.get(\'low\')
            if high and low and high > 0 and low > 0:
                open_price = (high + low) / 2
            else:
                # Last resort: use current price (no change)
                open_price = current_price
        
        # Calculate 24h change manually
        change_percent = ((current_price - open_price) / open_price) * 100
        
        # DEBUG logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Gemini {crypto}: Open=${open_price:.2f}, Current=${current_price:.2f}, Change={change_percent:.2f}%")
        
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
                \'exchange\': \'gemini\',
                \'symbol\': symbol,
                \'side\': \'buy\',
                \'type\': \'LONG\',
                \'current_price\': current_price,
                \'change_percent\': change_percent,
                \'amount\': amount,
                \'position_value\': position_value,
                \'capital_risk\': position_value,
                \'leverage\': 1,
                \'stop_loss\': current_price * (1 - STOP_LOSS),  # For LONG: stop if price drops further
                \'take_profit\': current_price * (1 + TAKE_PROFIT),  # For LONG: profit if price recovers
                \'status\': \'SIGNAL_DETECTED\'
            }
            
            logger.info(f"🎯 PREPARING GEMINI LONG: {crypto}")
            logger.info(f"    Current price: ${current_price:.2f}")
            logger.info(f"    24h change: {change_percent:.2f}%")
            logger.info(f"    Position size: {amount:.6f} {crypto}")
            logger.info(f"    Position value: ${position_value:.2f}")
            logger.info(f"    Capital at risk: ${position_value:.2f}")
            logger.info(f"    Stop-loss: ${trade_data[\'stop_loss\']:.2f} (-{STOP_LOSS*100:.0f}%)")
            logger.info(f"    Take-profit: ${trade_data[\'take_profit\']:.2f} (+{TAKE_PROFIT*100:.0f}%)")
            
            return trade_data
        
        # Log if close to threshold
        elif change_percent <= -1.0:  # Close but not enough
            logger.debug(f"Gemini {crypto}: {change_percent:.2f}% down (close to 1.5% threshold)")
    
    except Exception as e:
        logger.error(f"❌ Error checking {crypto} on Gemini: {e}")
    
    return None
'''
    
    print("\n" + "=" * 60)
    print("✅ FIXED GEMINI CHECK FUNCTION")
    print("=" * 60)
    print("Changes made:")
    print("1. ALWAYS calculates 24h change manually")
    print("2. Uses open price, or high/low average as fallback")
    print("3. Added debug logging for troubleshooting")
    print("4. Logs when close to threshold (1.0% down)")
    
    return fixed_code

if __name__ == "__main__":
    test_gemini_data()
    fixed_code = create_fixed_gemini_check()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED ACTION:")
    print("=" * 60)
    print("1. Stop current bot")
    print("2. Update check_gemini_long_opportunities() function")
    print("3. Add debug logging to see actual price changes")
    print("4. Restart bot")
    print("\nOr use TEMPORARY FIX:")
    print("• Lower LONG_THRESHOLD to 0.5% temporarily")
    print("• Force manual calculation of 24h change")