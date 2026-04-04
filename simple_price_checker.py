#!/usr/bin/env python3
"""
Simple price checker for Binance to debug API issues
"""

import ccxt
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_api_keys():
    """Load API keys from secure_keys directory"""
    keys = {}
    
    try:
        with open("secure_keys/.binance_key", "r") as f:
            keys['binance_key'] = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            keys['binance_secret'] = f.read().strip()
        logger.info("✅ Binance API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Binance keys: {e}")
        return None
    
    return keys

def main():
    """Check Binance prices for a few cryptos"""
    logger.info("🔍 Starting Binance price checker...")
    
    keys = load_api_keys()
    if not keys:
        return
    
    # Initialize Binance (spot market, not futures)
    exchange = ccxt.binance({
        'apiKey': keys['binance_key'],
        'secret': keys['binance_secret'],
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'  # Use spot market, not futures
        }
    })
    
    logger.info("✅ Binance exchange initialized (spot market)")
    
    # Check a few cryptos
    cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA']
    
    for crypto in cryptos:
        try:
            symbol = f"{crypto}/USDT"
            ticker = exchange.fetch_ticker(symbol)
            
            current_price = ticker['last']
            change_percent = ticker['percentage']
            
            logger.info(f"  {crypto}: ${current_price:.4f} ({change_percent:.2f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error checking {crypto}: {e}")
    
    logger.info("✅ Price check complete")

if __name__ == "__main__":
    main()