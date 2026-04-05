#!/usr/bin/env python3
"""
Diagnose Binance API key issues
"""

import ccxt
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
            keys['api_key'] = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            keys['api_secret'] = f.read().strip()
        logger.info("✅ Binance API keys loaded")
        logger.info(f"  API Key: {keys['api_key'][:10]}...{keys['api_key'][-10:]}")
        logger.info(f"  Secret: {keys['api_secret'][:10]}...{keys['api_secret'][-10:]}")
    except Exception as e:
        logger.error(f"❌ Failed to load Binance keys: {e}")
        return None
    
    return keys

def test_spot_market(api_key, api_secret):
    """Test Binance spot market API"""
    logger.info("🔍 Testing Binance Spot Market API...")
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    try:
        # Try to fetch account balance (requires API permissions)
        logger.info("  Testing: fetch_balance()...")
        balance = exchange.fetch_balance()
        logger.info(f"  ✅ Balance fetch successful!")
        logger.info(f"  Total assets: {len(balance['total'])}")
        
        # Show available USD balance
        if 'USDT' in balance['total'] and balance['total']['USDT'] > 0:
            logger.info(f"  USDT balance: ${balance['total']['USDT']:.2f}")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ Spot market error: {e}")
        return False

def test_futures_market(api_key, api_secret):
    """Test Binance futures market API"""
    logger.info("🔍 Testing Binance Futures Market API...")
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'  # Futures market
        }
    })
    
    try:
        # Try to fetch futures account balance
        logger.info("  Testing: fetch_balance() for futures...")
        balance = exchange.fetch_balance()
        logger.info(f"  ✅ Futures balance fetch successful!")
        
        # Try to fetch positions
        logger.info("  Testing: fetch_positions()...")
        positions = exchange.fetch_positions()
        logger.info(f"  ✅ Positions fetch successful! Found {len(positions)} positions")
        
        return True
    except Exception as e:
        logger.error(f"  ❌ Futures market error: {e}")
        return False

def test_public_data():
    """Test public data access (no API keys needed)"""
    logger.info("🔍 Testing Binance Public Data Access...")
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    try:
        # Fetch ticker for BTC/USDT
        ticker = exchange.fetch_ticker('BTC/USDT')
        logger.info(f"  ✅ Public data access successful!")
        logger.info(f"  BTC price: ${ticker['last']:.2f}")
        logger.info(f"  24h change: {ticker['percentage']:.2f}%")
        return True
    except Exception as e:
        logger.error(f"  ❌ Public data error: {e}")
        return False

def main():
    """Main diagnostic function"""
    logger.info("=" * 60)
    logger.info("🔧 BINANCE API DIAGNOSTIC TOOL")
    logger.info("=" * 60)
    
    # Test 1: Public data (should always work)
    public_ok = test_public_data()
    
    # Test 2: Load API keys
    keys = load_api_keys()
    if not keys:
        logger.error("❌ Cannot proceed without API keys")
        return
    
    # Test 3: Spot market
    spot_ok = test_spot_market(keys['api_key'], keys['api_secret'])
    
    # Test 4: Futures market
    futures_ok = test_futures_market(keys['api_key'], keys['api_secret'])
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 DIAGNOSTIC SUMMARY:")
    logger.info(f"  Public Data Access: {'✅' if public_ok else '❌'}")
    logger.info(f"  Spot Market API: {'✅' if spot_ok else '❌'}")
    logger.info(f"  Futures Market API: {'✅' if futures_ok else '❌'}")
    
    if not spot_ok and not futures_ok:
        logger.info("")
        logger.info("🚨 RECOMMENDED ACTIONS:")
        logger.info("  1. Log into Binance.com")
        logger.info("  2. Go to API Management")
        logger.info("  3. Check if API key is enabled")
        logger.info("  4. Check IP whitelist (add your current IP)")
        logger.info("  5. Ensure 'Enable Futures' permission is checked")
        logger.info("  6. If issues persist, create a new API key")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()