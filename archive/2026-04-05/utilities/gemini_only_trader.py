#!/usr/bin/env python3
"""
GEMINI-ONLY TRADING BOT
Trades only on Gemini (LONG positions) to avoid exchange discrepancies
"""

import ccxt
import json
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_only_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCAN_INTERVAL = 300  # 5 minutes
POSITION_SIZE_PERCENT = 0.10  # 10% of capital per trade (increased since no margin)

# Cryptocurrencies available on Gemini
GEMINI_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'ATOM', 'FIL'
]

# Capital allocation (100% to Gemini since Binance is paused)
GEMINI_CAPITAL = 655.36  # Total portfolio value

def load_api_keys():
    """Load API keys from environment"""
    return {
        'gemini_key': os.getenv('GEMINI_API_KEY'),
        'gemini_secret': os.getenv('GEMINI_API_SECRET'),
    }

def initialize_exchange(keys):
    """Initialize Gemini exchange connection"""
    if keys['gemini_key'] and keys['gemini_secret']:
        exchange = ccxt.gemini({
            'apiKey': keys['gemini_key'],
            'secret': keys['gemini_secret'],
            'enableRateLimit': True,
        })
        logger.info("✅ Gemini exchange initialized")
        return exchange
    else:
        logger.error("❌ Gemini API keys not found")
        return None

def load_open_positions():
    """Load current open positions from trades.json"""
    try:
        trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            
            # Extract open positions
            open_positions = {}
            for trade in trades:
                symbol = trade.get('symbol', '')
                if '/' in symbol:
                    asset = symbol.split('/')[0]
                else:
                    asset = symbol.replace('USD', '')
                
                exchange = trade.get('exchange', '')
                side = trade.get('side', '')
                
                if exchange == 'gemini' and side == 'buy':
                    key = f"{asset}_gemini"
                    open_positions[key] = {
                        'asset': asset,
                        'exchange': exchange,
                        'side': side,
                        'price': trade.get('price', 0),
                        'amount': trade.get('amount', 0)
                    }
            
            logger.info(f"📊 Loaded {len(open_positions)} Gemini LONG positions")
            return open_positions
        else:
            logger.warning("⚠️ No trades.json found, starting with empty positions")
            return {}
    except Exception as e:
        logger.error(f"❌ Error loading open positions: {e}")
        return {}

def check_gemini_long_opportunities(exchange, crypto, open_positions):
    """Check for LONG opportunities on Gemini"""
    try:
        symbol = f"{crypto}/USD"
        
        # Check if we already have a position
        if f"{crypto}_gemini" in open_positions:
            logger.info(f"⏭️ Skipping {crypto}: Already have LONG position")
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Check 24h price change
        if ticker['open'] and ticker['open'] > 0:
            price_change_24h = ((current_price - ticker['open']) / ticker['open']) * 100
        else:
            # Fallback to using previous close
            price_change_24h = ((current_price - ticker['previousClose']) / ticker['previousClose']) * 100 if ticker.get('previousClose') else 0
        
        # LONG opportunity: Price dropped significantly
        if price_change_24h < -1.5:  # 1.5% drop threshold (more conservative)
            logger.info(f"🎯 GEMINI LONG OPPORTUNITY: {symbol}")
            logger.info(f"   Current: ${current_price:.2f}")
            logger.info(f"   24h Change: {price_change_24h:.2f}%")
            
            # Calculate position size
            position_value = GEMINI_CAPITAL * POSITION_SIZE_PERCENT
            amount = position_value / current_price
            
            return {
                'exchange': 'gemini',
                'symbol': symbol,
                'side': 'buy',
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'position_value': position_value,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error checking Gemini {crypto}: {e}")
        return None

def execute_gemini_trade(exchange, trade_data):
    """Execute REAL Gemini LONG trade"""
    try:
        logger.info(f"🚀 EXECUTING GEMINI LONG: {trade_data['symbol']}")
        
        # Place buy order
        order = exchange.create_order(
            symbol=trade_data['symbol'],
            type='market',
            side='buy',
            amount=trade_data['amount']
        )
        
        logger.info(f"✅ GEMINI LONG ORDER EXECUTED: {order['id']}")
        logger.info(f"   Bought {trade_data['amount']:.6f} {trade_data['symbol'].split('/')[0]}")
        logger.info(f"   At price: ${trade_data['current_price']:.2f}")
        logger.info(f"   Cost: ${trade_data['position_value']:.2f}")
        
        trade_data['order_id'] = order['id']
        trade_data['status'] = 'EXECUTED'
        trade_data['execution_time'] = datetime.now().isoformat()
        
        # Save trade to history
        save_trade_history(trade_data)
        
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Gemini trade execution failed: {e}")
        trade_data['status'] = 'FAILED'
        trade_data['error'] = str(e)
        return trade_data

def save_trade_history(trade_data):
    """Save trade to trades.json"""
    try:
        trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
        
        # Load existing trades
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
        else:
            trades = []
        
        # Add new trade
        trades.append(trade_data)
        
        # Save back
        with open(trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
        
        logger.info(f"💾 Trade saved to history (total: {len(trades)})")
        
    except Exception as e:
        logger.error(f"❌ Error saving trade history: {e}")

def trading_cycle(exchange):
    """Single trading cycle"""
    logger.info("🔄 Starting trading cycle...")
    
    # Load current positions
    open_positions = load_open_positions()
    
    opportunities_found = 0
    
    # Check Gemini LONG opportunities
    if exchange:
        logger.info(f"🔍 Checking {len(GEMINI_CRYPTOS)} cryptos on Gemini for LONG...")
        for crypto in GEMINI_CRYPTOS:
            trade = check_gemini_long_opportunities(exchange, crypto, open_positions)
            if trade:
                # Execute REAL trade
                executed_trade = execute_gemini_trade(exchange, trade)
                opportunities_found += 1
                break  # Only take one trade per cycle to be conservative
    
    logger.info(f"🎯 Opportunities found this cycle: {opportunities_found}")
    logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...")

def main():
    """Main trading bot loop"""
    logger.info("=" * 70)
    logger.info("🤖 GEMINI-ONLY TRADING BOT STARTING")
    logger.info("=" * 70)
    logger.info(f"💰 Capital: ${GEMINI_CAPITAL:.2f} (100% Gemini)")
    logger.info(f"📊 Position size: {POSITION_SIZE_PERCENT*100}% of capital")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("🛑 Binance SHORT strategy: PAUSED (due to price discrepancies)")
    logger.info("=" * 70)
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchange
    exchange = initialize_exchange(keys)
    if not exchange:
        logger.error("❌ Cannot start bot - exchange not available")
        return
    
    cycle_count = 0
    
    # Main loop
    while True:
        try:
            cycle_count += 1
            logger.info(f"\n📈 CYCLE {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Run trading cycle
            trading_cycle(exchange)
            
            # Wait for next cycle
            logger.info(f"⏳ Waiting {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
            logger.info("⏳ Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()