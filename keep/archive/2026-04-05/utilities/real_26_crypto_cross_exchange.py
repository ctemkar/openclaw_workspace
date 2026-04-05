#!/usr/bin/env python3
"""
REAL 26-CRYPTO CROSS-EXCHANGE TRADING BOT
SMARTER STRATEGY: Use Binance as signal source
- Check ALL 26 cryptos on Binance
- If Binance shows dip (down 1%+) → Buy LONG on Gemini
- If Binance shows rise (up 1%+) → Sell SHORT on Binance
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
log_file = os.path.join(BASE_DIR, "cross_exchange_trading.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# All available cryptocurrencies (23 of original 26 - MATIC not available, MKR/OMG inactive)
ALL_CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI',
    'LTC', 'ATOM', 'FIL', 'XTZ', 'AAVE', 'COMP', 'YFI', 'SNX', 'ENJ', 'BAT',
    'ZEC', 'MANA', 'OXT'
]

# Gemini available cryptos (subset of ALL_CRYPTOS)
GEMINI_CRYPTOS = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 'MANA', 'COMP']

# Trading parameters
GEMINI_CAPITAL = 434.35  # Gemini cash balance
BINANCE_CAPITAL = 36.70  # Binance Futures capital
LEVERAGE = 1             # Safer 1x leverage
POSITION_SIZE = 0.05     # 5% of capital
LONG_THRESHOLD = 1.0     # Buy when down 1%+
SHORT_THRESHOLD = 1.0    # Sell when up 1%+
STOP_LOSS = 0.03         # 3% stop-loss
TAKE_PROFIT = 0.05       # 5% take-profit
SCAN_INTERVAL = 300      # 5 minute intervals

def load_api_keys():
    """Load API keys from secure storage"""
    keys = {}
    try:
        # Load Gemini keys
        with open('secure_keys/gemini_keys.json', 'r') as f:
            keys['gemini'] = json.load(f)
        logger.info("✅ Gemini API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Gemini keys: {e}")
        keys['gemini'] = None
    
    try:
        # Load Binance keys
        with open('secure_keys/binance_keys.json', 'r') as f:
            keys['binance'] = json.load(f)
        logger.info("✅ Binance API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Binance keys: {e}")
        keys['binance'] = None
    
    return keys

def initialize_exchanges(keys):
    """Initialize exchange connections"""
    exchanges = {}
    
    # Initialize Gemini
    if keys['gemini']:
        try:
            exchanges['gemini'] = ccxt.gemini({
                'apiKey': keys['gemini']['api_key'],
                'secret': keys['gemini']['api_secret'],
                'enableRateLimit': True,
            })
            logger.info("✅ Gemini exchange initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            exchanges['gemini'] = None
    else:
        exchanges['gemini'] = None
    
    # Initialize Binance Futures
    if keys['binance']:
        try:
            exchanges['binance'] = ccxt.binance({
                'apiKey': keys['binance']['api_key'],
                'secret': keys['binance']['api_secret'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                }
            })
            logger.info("✅ Binance Futures exchange initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Binance: {e}")
            exchanges['binance'] = None
    else:
        exchanges['binance'] = None
    
    return exchanges

def check_binance_price_signal(exchange, crypto):
    """
    Check Binance price for trading signal
    Returns: 'LONG', 'SHORT', or None
    """
    try:
        symbol = f"{crypto}/USDT"
        ticker = exchange.fetch_ticker(symbol)
        
        current_price = ticker['last']
        change_percent = ticker.get('percentage')
        
        if change_percent is None:
            # Calculate from 24h high/low
            high_24h = ticker.get('high')
            low_24h = ticker.get('low')
            if high_24h and low_24h and high_24h > 0:
                midpoint = (high_24h + low_24h) / 2
                change_percent = ((current_price - midpoint) / midpoint) * 100
            else:
                change_percent = 0
        
        # Determine signal based on Binance price
        if change_percent <= -LONG_THRESHOLD:
            return 'LONG', change_percent, current_price
        elif change_percent >= SHORT_THRESHOLD:
            return 'SHORT', change_percent, current_price
        else:
            return None, change_percent, current_price
            
    except Exception as e:
        logger.error(f"❌ Error checking {crypto} on Binance: {e}")
        return None, None, None

def execute_gemini_long(exchange, crypto, binance_price, change_percent):
    """Execute LONG trade on Gemini based on Binance signal"""
    try:
        # Get Gemini price for the same crypto
        gemini_symbol = f"{crypto}/USD"
        gemini_ticker = exchange.fetch_ticker(gemini_symbol)
        gemini_price = gemini_ticker['last']
        
        # Calculate position size
        position_value = GEMINI_CAPITAL * POSITION_SIZE
        amount = position_value / gemini_price
        
        logger.info(f"🚀 EXECUTING GEMINI LONG: {crypto}")
        logger.info(f"    Binance signal: down {abs(change_percent):.2f}% at ${binance_price:.4f}")
        logger.info(f"    Gemini price: ${gemini_price:.4f}")
        logger.info(f"    Position size: {amount:.6f} {crypto} (${position_value:.2f})")
        
        # Place buy order
        order = exchange.create_order(
            symbol=gemini_symbol,
            type='market',
            side='buy',
            amount=amount
        )
        
        logger.info(f"✅ Gemini LONG order executed: {order['id']}")
        
        # Save trade data
        trade_data = {
            'exchange': 'gemini',
            'symbol': gemini_symbol,
            'side': 'buy',
            'type': 'LONG_CROSS',
            'binance_price': binance_price,
            'binance_change': change_percent,
            'gemini_price': gemini_price,
            'amount': amount,
            'position_value': position_value,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'signal_source': 'BINANCE'
        }
        
        save_trade(trade_data)
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Gemini LONG execution failed: {e}")
        return None

def execute_binance_short(exchange, crypto, binance_price, change_percent):
    """Execute SHORT trade on Binance based on Binance signal"""
    try:
        # Calculate position size
        capital_risk = BINANCE_CAPITAL * POSITION_SIZE
        position_value = capital_risk * LEVERAGE
        amount = position_value / binance_price
        
        logger.info(f"🚀 EXECUTING BINANCE SHORT: {crypto}")
        logger.info(f"    Binance signal: up {change_percent:.2f}% at ${binance_price:.4f}")
        logger.info(f"    Position size: {amount:.6f} {crypto} (${position_value:.2f} with {LEVERAGE}x)")
        
        # Check minimum order size
        min_notional = 5.0  # Binance minimum
        if position_value < min_notional:
            logger.warning(f"⚠️ Position value ${position_value:.2f} < Binance minimum ${min_notional}")
            # Adjust to minimum
            amount = min_notional / binance_price
            position_value = min_notional
            logger.info(f"    Adjusted to minimum: {amount:.6f} {crypto}")
        
        symbol = f"{crypto}/USDT"
        
        # Place sell order
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='sell',
            amount=amount,
            params={'positionSide': 'SHORT'}
        )
        
        logger.info(f"✅ Binance SHORT order executed: {order['id']}")
        
        # Save trade data
        trade_data = {
            'exchange': 'binance',
            'symbol': symbol,
            'side': 'sell',
            'type': 'SHORT_CROSS',
            'binance_price': binance_price,
            'binance_change': change_percent,
            'amount': amount,
            'position_value': position_value,
            'capital_risk': capital_risk,
            'leverage': LEVERAGE,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'signal_source': 'BINANCE'
        }
        
        save_trade(trade_data)
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Binance SHORT execution failed: {e}")
        return None

def save_trade(trade_data):
    """Save trade to history"""
    try:
        history_file = os.path.join(BASE_DIR, 'trading_data', 'trades.json')
        
        # Load existing trades
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
    """One trading cycle - check Binance, trade on both exchanges"""
    logger.info("=" * 70)
    logger.info(f"📊 CROSS-EXCHANGE TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("=" * 70)
    
    opportunities_found = 0
    
    if exchanges['binance']:
        logger.info(f"🔍 Checking {len(ALL_CRYPTOS)} cryptos on Binance for signals...")
        
        for crypto in ALL_CRYPTOS:
            # Get signal from Binance
            signal, change_percent, binance_price = check_binance_price_signal(exchanges['binance'], crypto)
            
            if signal == 'LONG' and exchanges['gemini']:
                # Check if crypto is available on Gemini
                if crypto in GEMINI_CRYPTOS:
                    logger.info(f"⚡ BINANCE → GEMINI SIGNAL: {crypto} down {change_percent:.2f}%")
                    trade = execute_gemini_long(exchanges['gemini'], crypto, binance_price, change_percent)
                    if trade:
                        opportunities_found += 1
            
            elif signal == 'SHORT':
                logger.info(f"⚡ BINANCE SHORT SIGNAL: {crypto} up {change_percent:.2f}%")
                trade = execute_binance_short(exchanges['binance'], crypto, binance_price, change_percent)
                if trade:
                    opportunities_found += 1
    
    logger.info(f"🎯 Opportunities found this cycle: {opportunities_found}")
    logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...")
    
    return opportunities_found

def main():
    """Main trading loop"""
    logger.info("=" * 70)
    logger.info("🚀 REAL 26-CRYPTO CROSS-EXCHANGE TRADING BOT")
    logger.info("📈 STRATEGY: Binance signals → Gemini LONG / Binance SHORT")
    logger.info("=" * 70)
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchanges
    exchanges = initialize_exchanges(keys)
    
    if not exchanges['binance']:
        logger.error("❌ Binance exchange not available - cannot generate signals")
        return
    
    logger.info(f"♊ Gemini LONG: {len(GEMINI_CRYPTOS)} available cryptos (${GEMINI_CAPITAL:.2f} capital)")
    logger.info(f"₿ Binance SHORT: {len(ALL_CRYPTOS)} cryptos (${BINANCE_CAPITAL:.2f} capital, {LEVERAGE}x)")
    logger.info(f"💰 Position size: {POSITION_SIZE*100:.0f}% of capital")
    logger.info(f"🎯 Thresholds: ±{LONG_THRESHOLD}% price change")
    logger.info("⚡ USING BINANCE AS UNIFIED SIGNAL SOURCE!")
    
    cycle_count = 0
    total_opportunities = 0
    
    while True:
        cycle_count += 1
        logger.info(f"\n🔄 CYCLE {cycle_count} STARTING...")
        
        opportunities = trading_cycle(exchanges)
        total_opportunities += opportunities
        
        logger.info(f"⏱️  Cycle {cycle_count} duration: {SCAN_INTERVAL} seconds")
        logger.info(f"📈 Total opportunities found: {total_opportunities}")
        
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()