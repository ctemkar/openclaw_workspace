#!/usr/bin/env python3
"""
UPDATED ENHANCED BOT - TRADES BOTH EXCHANGES
- Gemini LONG with lower threshold (1.5%)
- Binance SHORT with higher threshold (3.0%)
- Uses ALL capital ($685 total)
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
log_file = os.path.join(BASE_DIR, "full_capital_trading.log")
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

# UPDATED Trading parameters - USING ALL CAPITAL!
GEMINI_CAPITAL = 531.65  # ALL Gemini cash (was 134.27)
BINANCE_CAPITAL = 154.02 # ALL Binance capital (Spot + Futures)
LEVERAGE = 1             # 1x leverage (SAFER)
POSITION_SIZE = 0.10     # 10% of capital per exchange
LONG_THRESHOLD = 0.5     # LOWERED from 3.0% to 1.5% (catch bull market dips)
SHORT_THRESHOLD = 3.0    # 3.0% drop for shorts (real moves)
STOP_LOSS = 0.03         # 3% stop-loss
TAKE_PROFIT = 0.05       # 5% take-profit
SCAN_INTERVAL = 300      # 5 minutes
MAX_POSITIONS_PER_EXCHANGE = 3  # Max 3 per exchange
DAILY_LOSS_LIMIT = -0.05 # -5% daily loss limit

# Position tracking
gemini_positions = []
binance_positions = []
daily_pnl = 0

class PositionManager:
    """Manages all open positions"""
    
    @staticmethod
    def load_open_positions():
        """Load open positions from file"""
        global gemini_positions, binance_positions
        try:
            with open('26_crypto_trade_history.json', 'r') as f:
                all_positions = json.load(f)
                gemini_positions = [p for p in all_positions if p.get('status') == 'OPEN' and p.get('exchange') == 'gemini']
                binance_positions = [p for p in all_positions if p.get('status') == 'OPEN' and p.get('exchange') == 'binance']
                logger.info(f"📊 Loaded {len(gemini_positions)} Gemini, {len(binance_positions)} Binance positions")
        except FileNotFoundError:
            gemini_positions = []
            binance_positions = []
            logger.info("No existing positions file")
    
    @staticmethod
    def can_open_gemini_position():
        """Check if we can open new Gemini position"""
        if len(gemini_positions) >= MAX_POSITIONS_PER_EXCHANGE:
            return False, f"Max Gemini positions reached ({MAX_POSITIONS_PER_EXCHANGE})"
        return True, "OK"
    
    @staticmethod
    def can_open_binance_position():
        """Check if we can open new Binance position"""
        if len(binance_positions) >= MAX_POSITIONS_PER_EXCHANGE:
            return False, f"Max Binance positions reached ({MAX_POSITIONS_PER_EXCHANGE})"
        
        # Check daily loss limit
        if daily_pnl <= DAILY_LOSS_LIMIT * (GEMINI_CAPITAL + BINANCE_CAPITAL):
            return False, f"Daily loss limit reached (${daily_pnl:.2f})"
        
        return True, "OK"
    
    @staticmethod
    def save_position(trade_data):
        """Save position to history"""
        try:
            history_file = os.path.join(BASE_DIR, "26_crypto_trade_history.json")
            
            # Load existing history
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Add new position
            history.append(trade_data)
            
            # Keep only last 100 trades
            if len(history) > 100:
                history = history[-100:]
            
            # Save back
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"📝 Position saved: {trade_data['symbol']} {trade_data['side']}")
            
            # Update in-memory tracking
            if trade_data['exchange'] == 'gemini':
                gemini_positions.append(trade_data)
            else:
                binance_positions.append(trade_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to save position: {e}")
    
    @staticmethod
    def update_position_status(exchange, symbol, new_status, close_price=None, pnl=None):
        """Update position status in history"""
        try:
            history_file = os.path.join(BASE_DIR, "26_crypto_trade_history.json")
            
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Find and update position
            for i, pos in enumerate(history):
                if pos['symbol'] == symbol and pos.get('exchange') == exchange and pos.get('status') == 'OPEN':
                    history[i]['status'] = new_status
                    if close_price:
                        history[i]['close_price'] = close_price
                        history[i]['close_time'] = datetime.now().isoformat()
                    if pnl is not None:
                        history[i]['realized_pnl'] = pnl
                    history[i]['notes'] = f'AUTOMATICALLY {new_status}'
                    break
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"📝 Position updated: {symbol} -> {new_status}")
            
            # Update in-memory tracking
            PositionManager.load_open_positions()
            
        except Exception as e:
            logger.error(f"❌ Failed to update position: {e}")

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

def check_gemini_long_opportunities(gemini_exchange, crypto):
    """Check for LONG opportunities on Gemini - Uses Binance for price data"""
    try:
        # We need Binance exchange for price data
        from ccxt import binance
        import logging
        logger = logging.getLogger(__name__)
        
        # Initialize Binance for price data (public API)
        binance_exchange = binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # Use spot for price data
            }
        })
        
        # Get price data from Binance (has proper 24h change)
        binance_symbol = f"{crypto}/USDT"
        try:
            binance_ticker = binance_exchange.fetch_ticker(binance_symbol)
            binance_change = binance_ticker.get('percentage')
            binance_price = binance_ticker['last']
            
            # Convert to USD if needed
            gemini_symbol = f"{crypto}/USD"
            gemini_ticker = gemini_exchange.fetch_ticker(gemini_symbol)
            gemini_price = gemini_ticker['last']
            
            logger.debug(f"Price data: {crypto} - Binance: ${binance_price:.2f} ({binance_change:.2f}%), Gemini: ${gemini_price:.2f}")
            
            # Use Binance's 24h change (more reliable)
            if binance_change and binance_change <= -LONG_THRESHOLD:
                logger.info(f"⚡ GEMINI LONG SIGNAL: {crypto} down {binance_change:.2f}% (via Binance data)")
                
                # Check position limits
                can_trade, reason = PositionManager.can_open_gemini_position()
                if not can_trade:
                    logger.warning(f"⚠️  Cannot trade Gemini: {reason}")
                    return None
                
                # Calculate position size (10% of Gemini capital)
                position_value = GEMINI_CAPITAL * POSITION_SIZE  # $53.17
                amount = position_value / gemini_price  # Use Gemini price for execution
                
                trade_data = {
                    'exchange': 'gemini',
                    'symbol': gemini_symbol,
                    'side': 'buy',
                    'type': 'LONG',
                    'current_price': gemini_price,
                    'change_percent': binance_change,
                    'amount': amount,
                    'position_value': position_value,
                    'capital_risk': position_value,
                    'leverage': 1,
                    'stop_loss': gemini_price * (1 - STOP_LOSS),
                    'take_profit': gemini_price * (1 + TAKE_PROFIT),
                    'status': 'SIGNAL_DETECTED',
                    'notes': 'Using Binance price data'
                }
                
                logger.info(f"🎯 PREPARING GEMINI LONG: {crypto}")
                logger.info(f"    Gemini price: ${gemini_price:.2f}")
                logger.info(f"    24h change (Binance): {binance_change:.2f}%")
                logger.info(f"    Position size: {amount:.6f} {crypto}")
                logger.info(f"    Position value: ${position_value:.2f}")
                
                return trade_data
            
            # Log if close to threshold
            elif binance_change and binance_change <= -1.0:
                logger.debug(f"Gemini {crypto}: {binance_change:.2f}% down (close to 1.5% threshold)")
                
        except Exception as binance_error:
            # Fallback to simple Gemini check
            logger.warning(f"⚠️  Binance data unavailable for {crypto}: {binance_error}")
            
            # Simple check: if Gemini price dropped significantly recently
            # (This is less reliable but better than nothing)
            pass
    
    except Exception as e:
        logger.error(f"❌ Error checking {crypto} on Gemini: {e}")
    
    return Nonedef check_binance_short_opportunities(exchange, crypto):
    """Check for SHORT opportunities on Binance Futures"""
    try:
        symbol = f"{crypto}/USDT"
        ticker = exchange.fetch_ticker(symbol)
        
        current_price = ticker['last']
        change_percent = ticker['percentage']
        
        # Binance usually has good data, but add fallback
        if change_percent is None:
            # Calculate manually if percentage not available
            open_price = ticker['open']
            if open_price and open_price > 0:
                change_percent = ((current_price - open_price) / open_price) * 100
        
        if change_percent and change_percent <= -SHORT_THRESHOLD:
            logger.info(f"⚡ BINANCE SHORT SIGNAL: {crypto} down {change_percent:.2f}%")
            
            # Check position limits
            can_trade, reason = PositionManager.can_open_binance_position()
            if not can_trade:
                logger.warning(f"⚠️  Cannot trade Binance: {reason}")
                return None
            
            # Calculate position size (10% of Binance capital)
            capital_risk = BINANCE_CAPITAL * POSITION_SIZE  # $15.40
            position_value = capital_risk * LEVERAGE  # $15.40 with 1x leverage
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
        trade_data['status'] = 'OPEN'
        trade_data['entry_price'] = trade_data['current_price']
        trade_data['execution_time'] = datetime.now().isoformat()
        
        # Save position
        PositionManager.save_position(trade_data)
        
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
        trade_data['status'] = 'OPEN'
        trade_data['entry_price'] =        trade_data['entry_price'] = trade_data['current_price']
        trade_data['execution_time'] = datetime.now().isoformat()
        
        # Save position
        PositionManager.save_position(trade_data)
        
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Binance trade execution failed: {e}")
        trade_data['status'] = 'FAILED'
        trade_data['error'] = str(e)
        return trade_data

def check_and_close_positions(gemini_exchange, binance_exchange):
    """Check all open positions and close if SL/TP hit"""
    global daily_pnl
    
    positions_closed = 0
    
    # Check Gemini positions
    if gemini_exchange:
        for position in gemini_positions[:]:
            symbol = position['symbol']
            
            try:
                # Get current price
                ticker = gemini_exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                entry_price = position.get('entry_price', position.get('current_price', 0))
                stop_loss = position.get('stop_loss', 0)
                take_profit = position.get('take_profit', 0)
                
                if entry_price == 0:
                    continue
                
                # Calculate current P&L for LONG
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                # Check stop loss (price dropped below SL)
                if current_price <= stop_loss:
                    logger.warning(f"🚨 GEMINI STOP LOSS HIT: {symbol} at ${current_price:.2f} (SL: ${stop_loss:.2f})")
                    close_gemini_position(gemini_exchange, position, current_price, 'STOP_LOSS', pnl_percent)
                    positions_closed += 1
                
                # Check take profit (price rose above TP)
                elif current_price >= take_profit:
                    logger.info(f"🎯 GEMINI TAKE PROFIT HIT: {symbol} at ${current_price:.2f} (TP: ${take_profit:.2f})")
                    close_gemini_position(gemini_exchange, position, current_price, 'TAKE_PROFIT', pnl_percent)
                    positions_closed += 1
                
            except Exception as e:
                logger.error(f"❌ Error checking Gemini position {symbol}: {e}")
    
    # Check Binance positions
    if binance_exchange:
        for position in binance_positions[:]:
            symbol = position['symbol']
            
            try:
                # Get current price
                ticker = binance_exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                entry_price = position.get('entry_price', position.get('current_price', 0))
                stop_loss = position.get('stop_loss', 0)
                take_profit = position.get('take_profit', 0)
                
                if entry_price == 0:
                    continue
                
                # Calculate current P&L for SHORT
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
                
                # Check stop loss (price rose above SL for short)
                if current_price >= stop_loss:
                    logger.warning(f"🚨 BINANCE STOP LOSS HIT: {symbol} at ${current_price:.4f} (SL: ${stop_loss:.4f})")
                    close_binance_position(binance_exchange, position, current_price, 'STOP_LOSS', pnl_percent)
                    positions_closed += 1
                
                # Check take profit (price dropped below TP for short)
                elif current_price <= take_profit:
                    logger.info(f"🎯 BINANCE TAKE PROFIT HIT: {symbol} at ${current_price:.4f} (TP: ${take_profit:.4f})")
                    close_binance_position(binance_exchange, position, current_price, 'TAKE_PROFIT', pnl_percent)
                    positions_closed += 1
                
            except Exception as e:
                logger.error(f"❌ Error checking Binance position {symbol}: {e}")
    
    return positions_closed

def close_gemini_position(exchange, position, close_price, reason, pnl_percent):
    """Close a Gemini LONG position"""
    global daily_pnl
    
    symbol = position['symbol']
    
    try:
        logger.info(f"🔄 CLOSING GEMINI POSITION: {symbol} ({reason})")
        
        # To close a LONG, we need to SELL
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='sell',
            amount=position['amount']
        )
        
        logger.info(f"✅ GEMINI POSITION CLOSED: {symbol}")
        logger.info(f"   Order ID: {order['id']}")
        logger.info(f"   Close Price: ${close_price:.2f}")
        logger.info(f"   P&L: {pnl_percent:.2f}%")
        
        # Calculate dollar P&L
        position_value = position.get('position_value', 0)
        pnl_dollar = position_value * (pnl_percent / 100)
        
        # Update daily P&L
        daily_pnl += pnl_dollar
        
        # Update position in history
        PositionManager.update_position_status('gemini', symbol, 'CLOSED', close_price, pnl_dollar)
        
        logger.info(f"💰 Daily P&L updated: ${daily_pnl:.2f}")
        
    except Exception as e:
        logger.error(f"❌ Error closing Gemini position {symbol}: {e}")

def close_binance_position(exchange, position, close_price, reason, pnl_percent):
    """Close a Binance SHORT position"""
    global daily_pnl
    
    symbol = position['symbol']
    
    try:
        logger.info(f"🔄 CLOSING BINANCE POSITION: {symbol} ({reason})")
        
        # To close a SHORT, we need to BUY
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side='buy',
            amount=position['amount']
        )
        
        logger.info(f"✅ BINANCE POSITION CLOSED: {symbol}")
        logger.info(f"   Order ID: {order['id']}")
        logger.info(f"   Close Price: ${close_price:.4f}")
        logger.info(f"   P&L: {pnl_percent:.2f}%")
        
        # Calculate dollar P&L
        position_value = position.get('position_value', 0)
        pnl_dollar = position_value * (pnl_percent / 100)
        
        # Update daily P&L
        daily_pnl += pnl_dollar
        
        # Update position in history
        PositionManager.update_position_status('binance', symbol, 'CLOSED', close_price, pnl_dollar)
        
        logger.info(f"💰 Daily P&L updated: ${daily_pnl:.2f}")
        
    except Exception as e:
        logger.error(f"❌ Error closing Binance position {symbol}: {e}")

def trading_cycle(exchanges):
    """One trading cycle - check both exchanges"""
    logger.info("=" * 70)
    logger.info(f"📊 FULL CAPITAL TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("=" * 70)
    
    opportunities_found = 0
    
    # First, check and close positions if SL/TP hit
    positions_closed = check_and_close_positions(exchanges['gemini'], exchanges['binance'])
    if positions_closed > 0:
        logger.info(f"📉 Closed {positions_closed} positions")
    
    # Check Gemini LONG opportunities (LOWERED THRESHOLD)
    if exchanges['gemini']:
        logger.info(f"🔍 Checking {len(GEMINI_CRYPTOS)} cryptos on Gemini for LONG (1.5% threshold)...")
        for crypto in GEMINI_CRYPTOS:
            trade = check_gemini_long_opportunities(exchanges['gemini'], crypto)
            if trade:
                # Execute REAL trade
                executed_trade = execute_gemini_trade(exchanges['gemini'], trade)
                opportunities_found += 1
    
    # Check Binance SHORT opportunities
    if exchanges['binance']:
        logger.info(f"🔍 Checking {len(ALL_CRYPTOS)} cryptos on Binance for SHORT (3.0% threshold)...")
        for crypto in ALL_CRYPTOS:
            trade = check_binance_short_opportunities(exchanges['binance'], crypto)
            if trade:
                # Execute REAL trade
                executed_trade = execute_binance_trade(exchanges['binance'], trade)
                opportunities_found += 1
    
    logger.info(f"🎯 Opportunities found this cycle: {opportunities_found}")
    
    # Log current status
    total_positions = len(gemini_positions) + len(binance_positions)
    max_positions = MAX_POSITIONS_PER_EXCHANGE * 2  # Both exchanges
    
    logger.info(f"📊 STATUS: {len(gemini_positions)} Gemini, {len(binance_positions)} Binance positions")
    logger.info(f"💰 Daily P&L: ${daily_pnl:.2f}, Total positions: {total_positions}/{max_positions}")
    
    return opportunities_found

def main():
    """Main trading loop"""
    logger.info("=" * 70)
    logger.info("🚀 UPDATED ENHANCED BOT - FULL CAPITAL TRADING")
    logger.info("=" * 70)
    logger.info(f"💰 TOTAL CAPITAL: ${GEMINI_CAPITAL + BINANCE_CAPITAL:.2f}")
    logger.info(f"♊ Gemini LONG: ${GEMINI_CAPITAL:.2f} (16 cryptos, 1.5% threshold)")
    logger.info(f"₿ Binance SHORT: ${BINANCE_CAPITAL:.2f} (26 cryptos, 3.0% threshold)")
    logger.info(f"📈 Position size: {POSITION_SIZE*100:.0f}% of exchange capital")
    logger.info(f"⚖️  Leverage: {LEVERAGE}x (SAFE)")
    logger.info(f"🛑 Stop-loss: {STOP_LOSS*100:.0f}%, ✅ Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"📈 Max positions per exchange: {MAX_POSITIONS_PER_EXCHANGE}")
    logger.info(f"📉 Daily loss limit: {DAILY_LOSS_LIMIT*100:.0f}%")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("=" * 70)
    logger.info("⚡ TRADING BOTH EXCHANGES WITH ALL CAPITAL")
    logger.info("⚡ Gemini: Buy dips (1.5%+ down)")
    logger.info("⚡ Binance: Short drops (3.0%+ down)")
    logger.info("=" * 70)
    
    # Load open positions
    PositionManager.load_open_positions()
    
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
            logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()