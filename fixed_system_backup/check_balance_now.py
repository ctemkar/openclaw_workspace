#!/usr/bin/env python3
"""Check Binance balance right now"""

import ccxt
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_binance_balance():
    """Check actual Binance balance"""
    try:
        # Load API keys
        key_file = os.path.expanduser("~/.openclaw/keys/binance.key")
        secret_file = os.path.expanduser("~/.openclaw/keys/binance.secret")
        
        if not os.path.exists(key_file) or not os.path.exists(secret_file):
            logger.error("❌ Binance API keys not found")
            return None
        
        with open(key_file, 'r') as f:
            api_key = f.read().strip()
        with open(secret_file, 'r') as f:
            api_secret = f.read().strip()
        
        # Initialize Binance
        binance = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Fetch balance
        logger.info("🔍 Fetching Binance balance...")
        balance = binance.fetch_balance()
        
        # Extract USDT balance
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        total_balance = balance.get('USDT', {}).get('total', 0)
        
        logger.info(f"💰 Binance Balance:")
        logger.info(f"   Free USDT: ${usdt_balance:.2f}")
        logger.info(f"   Total USDT: ${total_balance:.2f}")
        
        # Check other currencies
        logger.info(f"📊 Other balances:")
        for currency, data in balance.items():
            if isinstance(data, dict) and data.get('free', 0) > 0:
                if currency != 'USDT' and currency != 'info':
                    logger.info(f"   {currency}: {data.get('free', 0):.8f}")
        
        return {
            'free_usdt': usdt_balance,
            'total_usdt': total_balance,
            'full_balance': balance
        }
        
    except Exception as e:
        logger.error(f"❌ Error checking balance: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("🔍 REAL-TIME BINANCE BALANCE CHECK")
    print("="*60)
    result = check_binance_balance()
    if result:
        print(f"\n✅ Balance check completed")
        print(f"💰 Free USDT: ${result['free_usdt']:.2f}")
        print(f"📈 Total USDT: ${result['total_usdt']:.2f}")
    else:
        print("\n❌ Failed to check balance")
    print("="*60)