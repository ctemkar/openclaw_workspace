#!/usr/bin/env python3
"""
Test the new API key/secret provided
"""

import ccxt
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_api_key(api_key, api_secret):
    """Test if the provided API key/secret works"""
    logger.info(f"🔍 Testing API key: {api_key[:10]}...{api_key[-10:]}")
    logger.info(f"🔍 Testing secret: {api_secret[:10]}...{api_secret[-10:]}")
    
    # Try with the new key/secret
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    try:
        # Test public data first
        ticker = exchange.fetch_ticker('BTC/USDT')
        logger.info(f"✅ Public data works: BTC price: ${ticker['last']:.2f}")
        
        # Test private data (balance)
        logger.info("Testing balance fetch...")
        balance = exchange.fetch_balance()
        logger.info(f"✅ Balance fetch successful!")
        logger.info(f"Total assets: {len(balance['total'])}")
        
        # Show available balances
        for asset, amount in balance['total'].items():
            if amount > 0:
                logger.info(f"  {asset}: {amount}")
        
        return True
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False

def main():
    """Test the provided string as potential API key/secret"""
    provided_string = "EqD0zlJQq2D4lMFDpMdUJcVB8F6NuSufYdPdHOydGSW6zZHs9D5uUB85eYuPWIyo"
    
    logger.info("=" * 60)
    logger.info("🔧 TESTING PROVIDED API KEY/SECRET")
    logger.info("=" * 60)
    
    # The string is 64 characters - typical for Binance API secret
    logger.info(f"Provided string length: {len(provided_string)} chars")
    
    # Check if it could be an API key or secret
    if len(provided_string) == 64:
        logger.info("⚠️ This looks like a Binance API SECRET (64 chars)")
        logger.info("⚠️ Need corresponding API KEY to test")
        
        # Let me check if we have the old API key to test with this new secret
        try:
            with open("secure_keys/.binance_key", "r") as f:
                old_api_key = f.read().strip()
            
            logger.info("Testing old API key with new secret...")
            test_api_key(old_api_key, provided_string)
            
        except Exception as e:
            logger.error(f"❌ Cannot test: {e}")
            logger.info("")
            logger.info("📝 INSTRUCTIONS:")
            logger.info("1. If this is a NEW API SECRET, you also need the API KEY")
            logger.info("2. API KEY is typically shorter (e.g., 3aYW0orySV...0ouYfKhRzO)")
            logger.info("3. Update both files:")
            logger.info("   echo 'API_KEY_HERE' > secure_keys/.binance_key")
            logger.info("   echo 'EqD0zlJQq2...PWIyo' > secure_keys/.binance_secret")
    
    elif len(provided_string) < 64:
        logger.info("⚠️ This could be an API KEY (shorter than 64 chars)")
        # Try with old secret
        try:
            with open("secure_keys/.binance_secret", "r") as f:
                old_secret = f.read().strip()
            
            logger.info("Testing new API key with old secret...")
            test_api_key(provided_string, old_secret)
            
        except Exception as e:
            logger.error(f"❌ Cannot test: {e}")
    
    else:
        logger.error("❌ String length doesn't match typical API key/secret")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()