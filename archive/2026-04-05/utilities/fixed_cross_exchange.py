#!/usr/bin/env python3
"""
FIXED Cross-exchange bot with Gemini LIMIT orders
"""

import ccxt
import json
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load keys
with open('secure_keys/gemini_keys.json') as f:
    gemini_keys = json.load(f)
with open('secure_keys/binance_keys.json') as f:
    binance_keys = json.load(f)

# Initialize
gemini = ccxt.gemini({
    'apiKey': gemini_keys['api_key'],
    'secret': gemini_keys['api_secret']
})
binance = ccxt.binance({
    'apiKey': binance_keys['api_key'],
    'secret': binance_keys['api_secret']
})

GEMINI_CRYPTOS = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 'MANA', 'COMP']

def check_binance_dips():
    """Check Binance for dips to buy on Gemini"""
    logger.info("🔍 Checking for dips on Binance...")
    
    for crypto in GEMINI_CRYPTOS:
        try:
            ticker = binance.fetch_ticker(f"{crypto}/USDT")
            price = ticker['last']
            change = ticker.get('percentage', 0)
            
            if change <= -1.0:  # 1% dip
                logger.info(f"📉 {crypto} down {abs(change):.2f}% at ${price:.4f}")
                
                # Get Gemini price
                gemini_symbol = f"{crypto}/USD"
                gemini_ticker = gemini.fetch_ticker(gemini_symbol)
                gemini_price = gemini_ticker['last']
                
                # Calculate position
                position_value = 434.35 * 0.05  # 5% of Gemini capital
                amount = position_value / gemini_price
                
                logger.info(f"🚀 BUY {crypto} on Gemini at ${gemini_price:.4f}")
                logger.info(f"   Amount: {amount:.4f} (${position_value:.2f})")
                
                # Place LIMIT order (Gemini requires limit)
                # Add 0.1% buffer to ensure execution
                limit_price = gemini_price * 1.001
                
                try:
                    order = gemini.create_order(
                        symbol=gemini_symbol,
                        type='limit',
                        side='buy',
                        amount=amount,
                        price=limit_price
                    )
                    logger.info(f"✅ LIMIT order placed: {order['id']} at ${limit_price:.4f}")
                    return True
                except Exception as e:
                    logger.error(f"❌ Gemini order failed: {e}")
                    # Try with exact price
                    try:
                        order = gemini.create_order(
                            symbol=gemini_symbol,
                            type='limit',
                            side='buy',
                            amount=amount,
                            price=gemini_price
                        )
                        logger.info(f"✅ LIMIT order at exact price: {order['id']}")
                        return True
                    except Exception as e2:
                        logger.error(f"❌ Even exact price failed: {e2}")
                        
        except Exception as e:
            logger.error(f"❌ Error checking {crypto}: {e}")
    
    return False

def main():
    logger.info("🚀 FIXED Cross-exchange Bot - Gemini LIMIT orders")
    
    while True:
        if check_binance_dips():
            logger.info("✅ Trade executed!")
        else:
            logger.info("⏳ No dips found, checking again in 1 minute...")
        
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()