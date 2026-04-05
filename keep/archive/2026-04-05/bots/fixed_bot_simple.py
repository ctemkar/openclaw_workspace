#!/usr/bin/env python3
"""
SIMPLE FIXED BOT - Uses Binance for price data, trades on Gemini
"""

import os
import json
import time
import ccxt
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
log_file = os.path.join(BASE_DIR, "fixed_bot.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Trading parameters - SIMPLIFIED
GEMINI_CAPITAL = 531.65
BINANCE_CAPITAL = 154.02
LONG_THRESHOLD = 0.5  # TEMPORARY: 0.5% instead of 1.5%
SHORT_THRESHOLD = 3.0
POSITION_SIZE = 0.10  # 10% of capital
SCAN_INTERVAL = 60    # 1 minute (for testing)

# Cryptos available on both
CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI', 'LTC']

def load_api_keys():
    """Load API keys"""
    keys = {}
    try:
        # Gemini
        with open("secure_keys/.gemini_key", "r") as f:
            keys['gemini_key'] = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            keys['gemini_secret'] = f.read().strip()
        logger.info("✅ Gemini API keys loaded")
    except:
        keys['gemini_key'] = None
        keys['gemini_secret'] = None
    
    try:
        # Binance
        with open("secure_keys/.binance_key", "r") as f:
            keys['binance_key'] = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            keys['binance_secret'] = f.read().strip()
        logger.info("✅ Binance API keys loaded")
    except:
        keys['binance_key'] = None
        keys['binance_secret'] = None
    
    return keys

def check_prices():
    """Check prices using Binance (has good 24h data)"""
    try:
        # Use Binance for price data
        binance = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        opportunities = []
        
        for crypto in CRYPTOS[:5]:  # Check first 5
            try:
                symbol = f"{crypto}/USDT"
                ticker = binance.fetch_ticker(symbol)
                
                price = ticker['last']
                change = ticker.get('percentage', 0)
                
                if change and change <= -LONG_THRESHOLD:
                    logger.info(f"🎯 {crypto}: {change:.2f}% DOWN (would buy on Gemini)")
                    opportunities.append({
                        'crypto': crypto,
                        'price': price,
                        'change': change,
                        'exchange': 'gemini'
                    })
                elif change < 0:
                    logger.debug(f"   {crypto}: {change:.2f}% down")
                else:
                    logger.debug(f"   {crypto}: +{change:.2f}% up")
                    
            except Exception as e:
                logger.debug(f"   {crypto}: Error - {str(e)[:30]}")
        
        return opportunities
        
    except Exception as e:
        logger.error(f"❌ Error checking prices: {e}")
        return []

def execute_gemini_trade(crypto, price_data):
    """Execute trade on Gemini"""
    try:
        # Load Gemini keys
        with open("secure_keys/.gemini_key", "r") as f:
            api_key = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            api_secret = f.read().strip()
        
        exchange = ccxt.gemini({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        
        symbol = f"{crypto}/USD"
        
        # Get current Gemini price
        ticker = exchange.fetch_ticker(symbol)
        gemini_price = ticker['last']
        
        # Calculate position
        position_value = GEMINI_CAPITAL * POSITION_SIZE
        amount = position_value / gemini_price
        
        logger.info(f"🚀 BUYING {crypto} on Gemini:")
        logger.info(f"   Price: ${gemini_price:.2f}")
        logger.info(f"   Amount: {amount:.6f}")
        logger.info(f"   Value: ${position_value:.2f}")
        
        # Gemini only supports limit orders
        # Place limit order slightly above current price to ensure fill
        limit_price = gemini_price * 1.001  # 0.1% above current
        
        logger.info(f"📈 Placing LIMIT order at ${limit_price:.2f} (0.1% above market)")
        
        order = exchange.create_order(
            symbol=symbol,
            type='limit',
            side='buy',
            amount=amount,
            price=limit_price
        )
        
        logger.info(f"✅ ORDER EXECUTED: {order['id']}")
        logger.info(f"   Filled at: ${order['average']:.2f}")
        
        # Save trade
        trade_data = {
            'exchange': 'gemini',
            'symbol': symbol,
            'side': 'buy',
            'price': gemini_price,
            'amount': amount,
            'value': position_value,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'notes': f"Bought on dip (Binance showed {price_data.get('change', 0):.2f}% down)"
        }
        
        save_trade(trade_data)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Trade failed: {e}")
        return False

def save_trade(trade_data):
    """Save trade to history"""
    try:
        history_file = os.path.join(BASE_DIR, "gemini_trades.json")
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(trade_data)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info("📝 Trade saved to history")
        
    except Exception as e:
        logger.error(f"❌ Error saving trade: {e}")

def main():
    """Main loop"""
    logger.info("=" * 60)
    logger.info("🚀 SIMPLE FIXED BOT - Using Binance for price data")
    logger.info("=" * 60)
    logger.info(f"💰 Gemini capital: ${GEMINI_CAPITAL:.2f}")
    logger.info(f"🎯 Buy threshold: {LONG_THRESHOLD}% dip")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("=" * 60)
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"\n🔄 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Check prices
            opportunities = check_prices()
            
            # Execute trades
            for opp in opportunities:
                logger.info(f"⚡ Executing: {opp['crypto']} ({opp['change']:.2f}% down)")
                execute_gemini_trade(opp['crypto'], opp)
            
            # Wait for next cycle
            logger.info(f"⏳ Next check in {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()