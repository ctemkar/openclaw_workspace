#!/usr/bin/env python3
"""
UPDATED BOT - Uses common data layer
"""

import os
import time
import ccxt
from datetime import datetime
import logging

# Import common data layer
import trading_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Setup logging
log_file = os.path.join(BASE_DIR, "bot_common.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Trading parameters - ADJUSTED TO 1.0% THRESHOLDS
GEMINI_CAPITAL = 531.65
LONG_THRESHOLD = 1.0  # ADJUSTED from 0.5% to 1.0% (BALANCED)
POSITION_SIZE = 0.10  # 10% of capital
SCAN_INTERVAL = 60    # 1 minute

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
    """Execute trade on Gemini using COMMON DATA LAYER"""
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
        
        # Save trade using COMMON DATA LAYER
        trade_data = {
            'exchange': 'gemini',
            'symbol': symbol,
            'side': 'buy',
            'price': order['average'],
            'amount': amount,
            'value': position_value,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'notes': f"Bought on {price_data.get('change', 0):.2f}% dip (Binance data)",
            'status': 'open'  # Mark as open position
        }
        
        # Use common data layer
        trading_data.TradingData.save_trade(trade_data)
        
        # Update bot status
        trading_data.TradingData.update_bot_status({
            'status': 'running',
            'strategy': f'Gemini LONG at {LONG_THRESHOLD}% dips',
            'scan_interval': SCAN_INTERVAL,
            'last_activity': f'Bought {crypto} at ${order["average"]:.2f}',
            'last_trade': trade_data['timestamp']
        })
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Trade failed: {e}")
        return False

def main():
    """Main loop"""
    logger.info("=" * 60)
    logger.info("🚀 UPDATED BOT - USING COMMON DATA LAYER")
    logger.info("=" * 60)
    logger.info(f"💰 Gemini capital: ${GEMINI_CAPITAL:.2f}")
    logger.info(f"🎯 Buy threshold: {LONG_THRESHOLD}% dip")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("=" * 60)
    
    # Update bot status
    trading_data.TradingData.update_bot_status({
        'status': 'starting',
        'strategy': f'Gemini LONG at {LONG_THRESHOLD}% dips',
        'scan_interval': SCAN_INTERVAL,
        'last_activity': 'Bot starting up',
        'started_at': datetime.now().isoformat()
    })
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"\n🔄 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Update bot status
            trading_data.TradingData.update_bot_status({
                'status': 'scanning',
                'last_scan': datetime.now().isoformat(),
                'cycle_count': cycle
            })
            
            # Check prices
            opportunities = check_prices()
            
            # Execute trades
            for opp in opportunities:
                logger.info(f"⚡ Executing: {opp['crypto']} ({opp['change']:.2f}% down)")
                execute_gemini_trade(opp['crypto'], opp)
            
            # Update bot status
            trading_data.TradingData.update_bot_status({
                'status': 'waiting',
                'last_activity': f'Completed cycle {cycle}, found {len(opportunities)} opportunities',
                'next_scan': datetime.now().isoformat()
            })
            
            # Wait for next cycle
            logger.info(f"⏳ Next check in {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        trading_data.TradingData.update_bot_status({
            'status': 'stopped',
            'last_activity': 'Stopped by user',
            'stopped_at': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        trading_data.TradingData.update_bot_status({
            'status': 'error',
            'last_activity': f'Error: {str(e)[:100]}',
            'error_at': datetime.now().isoformat()
        })

if __name__ == "__main__":
    main()