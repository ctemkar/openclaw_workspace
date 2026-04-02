#!/usr/bin/env python3
"""
26-CRYPTO TRADING BOT - FIXED VERSION
FIXED: Prevents simultaneous LONG/SHORT on same asset
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
        logging.FileHandler('26_crypto_trader_fixed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCAN_INTERVAL = 300  # 5 minutes
LEVERAGE = 3
POSITION_SIZE_PERCENT = 0.05  # 5% of capital per trade (REDUCED from 10% due to margin issues)

# Cryptocurrencies to trade
ALL_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'MATIC', 'ATOM', 'FIL', 'NEAR', 'ALGO', 'VET', 'XTZ', 'EOS', 'AAVE', 'COMP',
    'MKR', 'SNX', 'YFI', 'SUSHI', 'CRV', '1INCH'
]

# Only include symbols that actually exist on Gemini
GEMINI_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'ATOM', 'FIL'
]

# Capital allocation (FIXED: 60% Gemini LONG, 40% Binance SHORT)
GEMINI_CAPITAL = 393.22  # 60% of portfolio
BINANCE_CAPITAL = 262.14  # 40% of portfolio

def load_api_keys():
    """Load API keys from environment"""
    return {
        'gemini_key': os.getenv('GEMINI_API_KEY'),
        'gemini_secret': os.getenv('GEMINI_API_SECRET'),
        'binance_key': os.getenv('BINANCE_API_KEY'),
        'binance_secret': os.getenv('BINANCE_API_SECRET'),
    }

def initialize_exchanges(keys):
    """Initialize exchange connections"""
    exchanges = {}
    
    # Initialize Gemini
    if keys['gemini_key'] and keys['gemini_secret']:
        exchanges['gemini'] = ccxt.gemini({
            'apiKey': keys['gemini_key'],
            'secret': keys['gemini_secret'],
            'enableRateLimit': True,
        })
        logger.info("✅ Gemini exchange initialized")
    else:
        exchanges['gemini'] = None
        logger.warning("⚠️ Gemini exchange not available")
    
    # Initialize Binance Futures
    if keys['binance_key'] and keys['binance_secret']:
        exchanges['binance'] = ccxt.binance({
            'apiKey': keys['binance_key'],
            'secret': keys['binance_secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        logger.info("✅ Binance Futures exchange initialized")
    else:
        exchanges['binance'] = None
        logger.warning("⚠️ Binance exchange not available")
    
    return exchanges

def load_open_positions():
    """Load current open positions from trades.json"""
    try:
        trades_file = os.path.join(BASE_DIR, "trading_data", "trades.json")
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            
            # Extract open positions (assuming all trades in file are open)
            open_positions = {}
            for trade in trades:
                symbol = trade.get('symbol', '').replace('/USD', '').replace('/USDT', '').replace(':USDT', '')
                exchange = trade.get('exchange', '')
                side = trade.get('side', '')
                
                if symbol and exchange and side:
                    key = f"{symbol}_{exchange}"
                    open_positions[key] = {
                        'symbol': symbol,
                        'exchange': exchange,
                        'side': side,
                        'price': trade.get('price', 0),
                        'amount': trade.get('amount', 0)
                    }
            
            logger.info(f"📊 Loaded {len(open_positions)} open positions")
            return open_positions
        else:
            logger.warning("⚠️ No trades.json found, starting with empty positions")
            return {}
    except Exception as e:
        logger.error(f"❌ Error loading open positions: {e}")
        return {}

def has_opposite_position(symbol, target_exchange, target_side, open_positions):
    """
    Check if we already have an opposite position on the other exchange
    Returns True if we should NOT trade (to avoid hedging)
    """
    other_exchange = 'binance' if target_exchange == 'gemini' else 'gemini'
    opposite_side = 'sell' if target_side == 'buy' else 'buy'
    
    key = f"{symbol}_{other_exchange}"
    
    if key in open_positions:
        existing_side = open_positions[key].get('side', '')
        if existing_side == opposite_side:
            logger.warning(f"⚠️ SKIPPING {symbol}: Already have {existing_side.upper()} on {other_exchange}, would conflict with {target_side.upper()} on {target_exchange}")
            return True
    
    return False

def check_gemini_long_opportunities(exchange, crypto, open_positions):
    """Check for LONG opportunities on Gemini"""
    try:
        symbol = f"{crypto}/USD"
        
        # Check if we already have opposite position on Binance
        if has_opposite_position(crypto, 'gemini', 'buy', open_positions):
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Check 24h price change (handle missing open price)
        if ticker['open'] and ticker['open'] > 0:
            price_change_24h = ((current_price - ticker['open']) / ticker['open']) * 100
        else:
            # Fallback to using previous close
            price_change_24h = ((current_price - ticker['previousClose']) / ticker['previousClose']) * 100 if ticker.get('previousClose') else 0
        
        # LONG opportunity: Price dropped significantly
        if price_change_24h < -1.0:  # 1% drop threshold
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

def check_binance_short_opportunities(exchange, crypto, open_positions):
    """Check for SHORT opportunities on Binance Futures"""
    try:
        symbol = f"{crypto}/USDT"
        
        # Check if we already have opposite position on Gemini
        if has_opposite_position(crypto, 'binance', 'sell', open_positions):
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Check 24h price change
        price_change_24h = ((current_price - ticker['open']) / ticker['open']) * 100
        
        # SHORT opportunity: Price increased significantly
        if price_change_24h > 1.0:  # 1% increase threshold
            logger.info(f"🎯 BINANCE SHORT OPPORTUNITY: {symbol}")
            logger.info(f"   Current: ${current_price:.2f}")
            logger.info(f"   24h Change: {price_change_24h:.2f}%")
            
            # Calculate position size
            position_value = BINANCE_CAPITAL * POSITION_SIZE_PERCENT
            amount = (position_value * LEVERAGE) / current_price
            
            return {
                'exchange': 'binance',
                'symbol': symbol,
                'side': 'sell',
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'position_value': position_value,
                'amount': amount,
                'leverage': LEVERAGE,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error checking Binance {crypto}: {e}")
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

def execute_binance_trade(exchange, trade_data):
    """Execute REAL Binance Futures SHORT trade"""
    try:
        logger.info(f"🚀 EXECUTING BINANCE SHORT: {trade_data['symbol']}")
        
        # Set leverage first
        exchange.set_leverage(LEVERAGE, trade_data['symbol'])
        
        # Place sell order (SHORT)
        order = exchange.create_order(
            symbol=trade_data['symbol'],
            type='market',
            side='sell',
            amount=trade_data['amount']
        )
        
        logger.info(f"✅ BINANCE SHORT ORDER EXECUTED: {order['id']}")
        logger.info(f"   Sold {trade_data['amount']:.6f} {trade_data['symbol'].split('/')[0]}")
        logger.info(f"   At price: ${trade_data['current_price']:.2f}")
        logger.info(f"   Position value: ${trade_data['position_value']:.2f}")
        logger.info(f"   Leverage: {LEVERAGE}x")
        
        trade_data['order_id'] = order['id']
        trade_data['status'] = 'EXECUTED'
        trade_data['execution_time'] = datetime.now().isoformat()
        
        # Save trade to history
        save_trade_history(trade_data)
        
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Binance trade execution failed: {e}")
        trade_data['status'] = 'FAILED'
        trade_data['error'] = str(e)
        return trade_data

def save_trade_history(trade_data):
    """Save trade to history file"""
    try:
        history_file = os.path.join(BASE_DIR, "26_crypto_trade_history_fixed.json")
        
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new trade
        history.append(trade_data)
        
        # Keep only last 100 trades
        if len(history) > 100:
            history = history[-100:]
        
        # Save back
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"📝 Trade saved to history: {trade_data['symbol']} {trade_data['side']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save trade history: {e}")

def trading_cycle(exchanges):
    """One trading cycle - check all 26 cryptos with position checking"""
    logger.info("=" * 70)
    logger.info(f"📊 26-CRYPTO TRADING CYCLE (FIXED) - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("=" * 70)
    
    # Load current open positions
    open_positions = load_open_positions()
    
    opportunities_found = 0
    skipped_hedges = 0
    
    # Check Gemini LONG opportunities (16 cryptos)
    if exchanges['gemini']:
        logger.info(f"🔍 Checking {len(GEMINI_CRYPTOS)} cryptos on Gemini for LONG...")
        for crypto in GEMINI_CRYPTOS:
            trade = check_gemini_long_opportunities(exchanges['gemini'], crypto, open_positions)
            if trade:
                # Execute REAL trade
                executed_trade = execute_gemini_trade(exchanges['gemini'], trade)
                opportunities_found += 1
            elif trade is None:
                # Check if it was skipped due to hedge
                # (has_opposite_position would have logged warning)
                pass
    
    # Check Binance SHORT opportunities (all 26 cryptos)
    if exchanges['binance']:
        logger.info(f"🔍 Checking {len(ALL_CRYPTOS)} cryptos on Binance for SHORT...")
        for crypto in ALL_CRYPTOS:
            trade = check_binance_short_opportunities(exchanges['binance'], crypto, open_positions)
            if trade:
                # Execute REAL trade
                executed_trade = execute_binance_trade(exchanges['binance'], trade)
                opportunities_found += 1
            elif trade is None:
                # Check if it was skipped due to hedge
                pass
    
    logger.info(f"🎯 Opportunities found this cycle: {opportunities_found}")
    logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...")

def main():
    """Main trading bot loop"""
    logger.info("=" * 70)
    logger.info("🤖 26-CRYPTO TRADING BOT STARTING (FIXED VERSION)")
    logger.info("=" * 70)
    logger.info(f"💰 Capital: ${GEMINI_CAPITAL:.2f} Gemini (LONG), ${BINANCE_CAPITAL:.2f} Binance (SHORT)")
    logger.info(f"📊 Position size: {POSITION_SIZE_PERCENT*100}% of capital")
    logger.info(f"⚡ Leverage: {LEVERAGE}x (Binance only)")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("🛡️  FIX: Position checking enabled - prevents simultaneous LONG/SHORT")
    logger.info("=" * 70)
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchanges
    exchanges = initialize_exchanges(keys)
    
    if not exchanges['gemini'] and not exchanges['binance']:
        logger.error("❌ No exchanges available. Check API keys.")
        return
    
    cycle_count = 0
    
    # Main trading loop
    while True:
        try:
            cycle_count += 1
            logger.info(f"🔄 CYCLE #{cycle_count}")
            
            # Run trading cycle
            trading_cycle(exchanges)
            
            # Wait for next cycle
            logger.info(f"⏳ Waiting {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
            logger.info("⏳ Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()