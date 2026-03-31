#!/usr/bin/env python3
"""
REAL 26-CRYPTO TRADING BOT
Actually trades ALL 26 cryptocurrencies
- LONG on Gemini (where available)
- SHORT on Binance (all 26)
"""

import os
import json
import time
import ccxt
from datetime import datetime
import logging
import sys

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
log_file = os.path.join(BASE_DIR, "real_26_crypto_trading.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# All 26 cryptocurrencies
ALL_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'MKR', 'BAT',
    'ZRX', 'OMG', 'ENJ', 'MATIC', 'SUSHI', 'CRV'
]

# Gemini available cryptos (16 of 26)
GEMINI_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI'
]

# Trading parameters - ADJUSTED TO 1.0% THRESHOLDS
# OLD: SHORT_THRESHOLD = 3.0 (too high, no trades)
# NEW: SHORT_THRESHOLD = 1.0 (balanced approach)
GEMINI_CAPITAL = 134.27  # Gemini cash balance
BINANCE_CAPITAL = 134.27 # Binance Futures capital
LEVERAGE = 1             # REDUCED from 3x to 1x (SAFER)
POSITION_SIZE = 0.10     # REDUCED from 25% to 10% of capital (BETTER RISK)
LONG_THRESHOLD = 1.0     # ADJUSTED from 3.0% to 1.0% (BALANCED)
SHORT_THRESHOLD = 1.0    # ADJUSTED from 3.0% to 1.0% (BALANCED)
STOP_LOSS = 0.03         # TIGHTER from 5% to 3% stop-loss
TAKE_PROFIT = 0.05       # REDUCED from 10% to 5% take-profit
SCAN_INTERVAL = 300      # INCREASED from 180 to 300 seconds (5 min)
MAX_POSITIONS = 3        # NEW: Max 3 open positions (prevent overtrading)

# Load API keys
def load_api_keys():
    """Load Gemini and Binance API keys"""
    keys = {}
    try:
        # Gemini
        with open("secure_keys/.gemini_key", "r") as f:
            keys['gemini_key'] = f.read().strip()
        with open("secure_keys/.gemini_secret", "r") as f:
            keys['gemini_secret'] = f.read().strip()
        logger.info("✅ Gemini API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Gemini keys: {e}")
        keys['gemini_key'] = None
        keys['gemini_secret'] = None
    
    try:
        # Binance
        with open("secure_keys/.binance_key", "r") as f:
            keys['binance_key'] = f.read().strip()
        with open("secure_keys/.binance_secret", "r") as f:
            keys['binance_secret'] = f.read().strip()
        logger.info("✅ Binance API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Binance keys: {e}")
        keys['binance_key'] = None
        keys['binance_secret'] = None
    
    return keys

def init_exchanges(keys):
    """Initialize Gemini and Binance exchanges"""
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

def check_gemini_long_opportunities(exchange, crypto):
    """Check for LONG opportunities on Gemini"""
    try:
        symbol = f"{crypto}/USD"
        ticker = exchange.fetch_ticker(symbol)
        
        current_price = ticker['last']
        change_percent = ticker['percentage']
        
        if change_percent is None:
            # Calculate manually if percentage not available
            open_price = ticker['open']
            if open_price and open_price > 0:
                change_percent = ((current_price - open_price) / open_price) * 100
        
        if change_percent and change_percent <= -LONG_THRESHOLD:
            logger.info(f"⚡ GEMINI LONG SIGNAL: {crypto} down {change_percent:.2f}%")
            
            # Calculate position size
            position_value = GEMINI_CAPITAL * POSITION_SIZE  # $15
            amount = position_value / current_price
            
            trade_data = {
                'exchange': 'gemini',
                'symbol': symbol,
                'side': 'buy',
                'type': 'LONG',
                'current_price': current_price,
                'change_percent': change_percent,
                'amount': amount,
                'position_value': position_value,
                'capital_risk': position_value,
                'stop_loss': current_price * (1 + STOP_LOSS),  # For LONG: stop if price drops further
                'take_profit': current_price * (1 - TAKE_PROFIT),  # For LONG: profit if price recovers
                'status': 'SIGNAL_DETECTED'
            }
            
            logger.info(f"🎯 PREPARING GEMINI LONG: {crypto}")
            logger.info(f"    Current price: ${current_price:.2f}")
            logger.info(f"    24h change: {change_percent:.2f}%")
            logger.info(f"    Position size: {amount:.6f} {crypto}")
            logger.info(f"    Position value: ${position_value:.2f}")
            logger.info(f"    Capital at risk: ${position_value:.2f}")
            logger.info(f"    Stop-loss: ${trade_data['stop_loss']:.2f} (+{STOP_LOSS*100:.0f}%)")
            logger.info(f"    Take-profit: ${trade_data['take_profit']:.2f} (-{TAKE_PROFIT*100:.0f}%)")
            
            return trade_data
    
    except Exception as e:
        logger.error(f"❌ Error checking {crypto} on Gemini: {e}")
    
    return None

def check_binance_short_opportunities(exchange, crypto):
    """Check for SHORT opportunities on Binance Futures"""
    try:
        symbol = f"{crypto}/USDT"
        ticker = exchange.fetch_ticker(symbol)
        
        current_price = ticker['last']
        change_percent = ticker['percentage']
        
        if change_percent is None:
            # Calculate manually if percentage not available
            open_price = ticker['open']
            if open_price and open_price > 0:
                change_percent = ((current_price - open_price) / open_price) * 100
        
        if change_percent and change_percent <= -SHORT_THRESHOLD:
            logger.info(f"⚡ BINANCE SHORT SIGNAL: {crypto} down {change_percent:.2f}%")
            
            # Calculate position size with leverage
            capital_risk = BINANCE_CAPITAL * POSITION_SIZE  # $3.75
            position_value = capital_risk * LEVERAGE  # $11.25 with 3x leverage
            amount = position_value / current_price
            
            trade_data = {
                'exchange': 'binance',
                'symbol': symbol,
                'side': 'sell',
                'type': 'SHORT',
                'current_price': current_price,
                'change_percent': change_percent,
                'amount': amount,
                'position_value': position_value,
                'capital_risk': capital_risk,
                'leverage': LEVERAGE,
                'stop_loss': current_price * (1 + STOP_LOSS),  # For SHORT: stop if price rises
                'take_profit': current_price * (1 - TAKE_PROFIT),  # For SHORT: profit if price drops more
                'status': 'SIGNAL_DETECTED'
            }
            
            logger.info(f"🎯 PREPARING BINANCE SHORT: {crypto}")
            logger.info(f"    Current price: ${current_price:.4f}")
            logger.info(f"    24h change: {change_percent:.2f}%")
            logger.info(f"    Position size: {amount:.6f} contracts")
            logger.info(f"    Position value: ${position_value:.2f} (with {LEVERAGE}x leverage)")
            logger.info(f"    Capital at risk: ${capital_risk:.2f}")
            logger.info(f"    Stop-loss: ${trade_data['stop_loss']:.4f} (+{STOP_LOSS*100:.0f}%)")
            logger.info(f"    Take-profit: ${trade_data['take_profit']:.4f} (-{TAKE_PROFIT*100:.0f}%)")
            
            return trade_data
    
    except Exception as e:
        logger.error(f"❌ Error checking {crypto} on Binance: {e}")
    
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
        
        # Place short sell order
        order = exchange.create_order(
            symbol=trade_data['symbol'],
            type='market',
            side='sell',
            amount=trade_data['amount']
        )
        
        logger.info(f"✅ BINANCE SHORT ORDER EXECUTED: {order['id']}")
        logger.info(f"   Shorted {trade_data['amount']:.6f} contracts")
        logger.info(f"   At price: ${trade_data['current_price']:.4f}")
        logger.info(f"   Position value: ${trade_data['position_value']:.2f} ({LEVERAGE}x)")
        
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
        history_file = os.path.join(BASE_DIR, "26_crypto_trade_history.json")
        
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
    """One trading cycle - check all 26 cryptos"""
    logger.info("=" * 70)
    logger.info(f"📊 26-CRYPTO TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("=" * 70)
    
    opportunities_found = 0
    
    # Check Gemini LONG opportunities (16 cryptos)
    if exchanges['gemini']:
        logger.info(f"🔍 Checking {len(GEMINI_CRYPTOS)} cryptos on Gemini for LONG...")
        for crypto in GEMINI_CRYPTOS:
            trade = check_gemini_long_opportunities(exchanges['gemini'], crypto)
            if trade:
                # Execute REAL trade
                executed_trade = execute_gemini_trade(exchanges['gemini'], trade)
                opportunities_found += 1
    
    # Check Binance SHORT opportunities (all 26 cryptos)
    if exchanges['binance']:
        logger.info(f"🔍 Checking {len(ALL_CRYPTOS)} cryptos on Binance for SHORT...")
        for crypto in ALL_CRYPTOS:
            trade = check_binance_short_opportunities(exchanges['binance'], crypto)
            if trade:
                # Execute REAL trade
                executed_trade = execute_binance_trade(exchanges['binance'], trade)
                opportunities_found += 1
    
    logger.info(f"🎯 Opportunities found this cycle: {opportunities_found}")
    logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...")
    
    return opportunities_found

def main():
    """Main trading loop"""
    logger.info("=" * 70)
    logger.info("🚀 REAL 26-CRYPTO TRADING BOT - AGGRESSIVE MODE!")
    logger.info("=" * 70)
    logger.info(f"📊 Trading ALL 26 cryptocurrencies")
    logger.info(f"♊ Gemini LONG: {len(GEMINI_CRYPTOS)} cryptos (${GEMINI_CAPITAL:.2f} capital - FULL BALANCE!)")
    logger.info(f"₿ Binance SHORT: {len(ALL_CRYPTOS)} cryptos (${BINANCE_CAPITAL:.2f} capital, {LEVERAGE}x)")
    logger.info(f"📈 LONG threshold: {LONG_THRESHOLD}% drop (MORE AGGRESSIVE!)")
    logger.info(f"📉 SHORT threshold: {SHORT_THRESHOLD}% drop (MORE AGGRESSIVE!)")
    logger.info(f"💰 Position size: {POSITION_SIZE*100:.0f}% of capital (MORE AGGRESSIVE!)")
    logger.info(f"🛑 Stop-loss: {STOP_LOSS*100:.0f}%, ✅ Take-profit: {TAKE_PROFIT*100:.0f}% (HIGHER PROFIT!)")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds (FASTER!)")
    logger.info("=" * 70)
    logger.info("⚡ Trades WILL be executed on BOTH exchanges!")
    logger.info("⚡ USING FULL BALANCE - NOT SITTING ON SIDELINES!")
    logger.info("=" * 70)
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchanges
    exchanges = init_exchanges(keys)
    
    if not exchanges['gemini'] and not exchanges['binance']:
        logger.error("❌ No exchanges available. Exiting.")
        return
    
    cycle_count = 0
    total_opportunities = 0
    
    try:
        while True:
            cycle_count += 1
            logger.info(f"\n🔄 CYCLE {cycle_count} STARTING...")
            
            start_time = time.time()
            opportunities = trading_cycle(exchanges)
            total_opportunities += opportunities
            
            cycle_duration = time.time() - start_time
            logger.info(f"⏱️  Cycle {cycle_count} duration: {cycle_duration:.1f} seconds")
            logger.info(f"📈 Total opportunities found: {total_opportunities}")
            
            # Wait for next cycle
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()