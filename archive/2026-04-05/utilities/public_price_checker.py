#!/usr/bin/env python3
"""
Public price checker - no API keys needed
"""

import ccxt
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Check Binance prices without API keys (public data)"""
    logger.info("🔍 Starting public price checker...")
    
    # Initialize Binance without API keys
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    logger.info("✅ Binance exchange initialized (public access)")
    
    # Check all 26 cryptos
    cryptos = [
        'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
        'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'BAT', 'ZRX',
        'ENJ', 'SUSHI', 'CRV'
    ]
    
    prices = {}
    
    for crypto in cryptos:
        try:
            symbol = f"{crypto}/USDT"
            ticker = exchange.fetch_ticker(symbol)
            
            current_price = ticker['last']
            change_percent = ticker['percentage']
            
            prices[crypto] = current_price
            logger.info(f"  {crypto}: ${current_price:.4f} ({change_percent:.2f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error checking {crypto}: {e}")
    
    # Show top 10 by price
    logger.info("\n🏆 TOP 10 CRYPTOS BY PRICE:")
    sorted_prices = sorted(prices.items(), key=lambda x: x[1], reverse=True)
    for i, (crypto, price) in enumerate(sorted_prices[:10], 1):
        logger.info(f"  {i:2d}. {crypto}: ${price:.2f}")
    
    logger.info("✅ Public price check complete")

if __name__ == "__main__":
    main()