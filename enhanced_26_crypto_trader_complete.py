#!/usr/bin/env python3
"""
ENHANCED 26-CRYPTO TRADING BOT
WITH AUTOMATIC POSITION MANAGEMENT:
- Opens positions based on improved parameters
- Automatically closes positions at stop loss/take profit
- Manages risk and frees capital when needed
- Tracks all positions in real-time
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
log_file = os.path.join(BASE_DIR, "enhanced_26_crypto_trading.log")
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

# IMPROVED Trading parameters
GEMINI_CAPITAL = 134.27
BINANCE_CAPITAL = 134.27
LEVERAGE = 1             # REDUCED from 3x to 1x (SAFER)
POSITION_SIZE = 0.10     # REDUCED from 25% to 10% of capital (BETTER RISK)
LONG_THRESHOLD = 3.0     # INCREASED from 2.0% to 3.0% (REAL DIPS)
SHORT_THRESHOLD = 3.0    # INCREASED from 0.3% to 3.0% (REAL MOVES)
STOP_LOSS = 0.03         # TIGHTER from 5% to 3% stop-loss
TAKE_PROFIT = 0.05       # REDUCED from 10% to 5% take-profit
SCAN_INTERVAL = 300      # INCREASED from 180 to 300 seconds (5 min)
MAX_POSITIONS = 3        # NEW: Max 3 open positions (prevent overtrading)
DAILY_LOSS_LIMIT = -0.05 # -5% daily loss limit

# Position tracking
open_positions = []
daily_pnl = 0
position_count = 0

class PositionManager:
    """Manages all open positions"""
    
    @staticmethod
    def load_open_positions():
        """Load open positions from file"""
        global open_positions
        try:
            with open('26_crypto_trade_history.json', 'r') as f:
                all_positions = json.load(f)
                open_positions = [p for p in all_positions if p.get('status') == 'OPEN']
                logger.info(f"📊 Loaded {len(open_positions)} open positions")
        except FileNotFoundError:
            open_positions = []
            logger.info("No existing positions file")
    
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
            
        except Exception as e:
            logger.error(f"❌ Failed to save position: {e}")
    
    @staticmethod
    def update_position_status(symbol, new_status, close_price=None, pnl=None):
        """Update position status in history"""
        try:
            history_file = os.path.join(BASE_DIR, "26_crypto_trade_history.json")
            
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Find and update position
            for i, pos in enumerate(history):
                if pos['symbol'] == symbol and pos.get('status') == 'OPEN':
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
            
            # Update open_positions list
            PositionManager.load_open_positions()
            
        except Exception as e:
            logger.error(f"❌ Failed to update position: {e}")
    
    @staticmethod
    def check_position_limits():
        """Check if we can open new positions"""
        if len(open_positions) >= MAX_POSITIONS:
            return False, f"Max positions reached ({MAX_POSITIONS})"
        
        # Check daily loss limit
        if daily_pnl <= DAILY_LOSS_LIMIT * BINANCE_CAPITAL:
            return False, f"Daily loss limit reached (${daily_pnl:.2f})"
        
        return True, "OK"
    
    @staticmethod
    def get_worst_position():
        """Get the worst performing position (for closing to free capital)"""
        if not open_positions:
            return None
        
        # Find position with largest % loss
        worst_position = min(open_positions, key=lambda x: x.get('pnl_percent', 0))
        return worst_position

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
            
            # Check position limits
            can_trade, reason = PositionManager.check_position_limits()
            if not can_trade:
                logger.warning(f"⚠️  Cannot trade: {reason}")
                return None
            
            # Calculate position size
            capital_risk = BINANCE_CAPITAL * POSITION_SIZE  # $13.43
            position_value = capital_risk * LEVERAGE  # $13.43 with 1x leverage
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
        trade_data['entry_price'] = trade_data['current_price']
        trade_data['execution_time'] = datetime.now().isoformat()
        
        # Save position
        PositionManager.save_position(trade_data)
        PositionManager.load_open_positions()
        
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Binance trade execution failed: {e}")
        trade_data['status'] = 'FAILED'
        trade_data['error'] = str(e)
        return trade_data

def check_and_close_positions(exchange):
    """Check all open positions and close if SL/TP hit"""
    global daily_pnl, open_positions
    
    if not open_positions:
        return 0
    
    logger.info(f"🔍 Checking {len(open_positions)} open positions...")
    positions_closed = 0
    
    for position in open_positions[:]:  # Copy list for safe iteration
        symbol = position['symbol']
        
        try:
            # Get current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            entry_price = position.get('entry_price', position.get('current_price', 0))
            stop_loss = position.get('stop_loss', 0)
            take_profit = position.get('take_profit', 0)
            
            if entry_price == 0:
                continue
            
            # Calculate current P&L
            if position['type'] == 'SHORT':
                pnl_percent = ((entry_price - current_price) / entry_price) * 100
            else:  # LONG
                pnl_percent = ((current_price - entry_price) / entry_price) * 100
            
            # Check stop loss
            if position['type'] == 'SHORT' and current_price >= stop_loss:
                logger.warning(f"🚨 STOP LOSS HIT: {symbol} at ${current_price:.4f} (SL: ${stop_loss:.4f})")
                close_position(exchange, position, current_price, 'STOP_LOSS', pnl_percent)
                positions_closed += 1
            
            # Check take profit
            elif position['type'] == 'SHORT' and current_price <= take_profit:
                logger.info(f"🎯 TAKE PROFIT HIT: {symbol} at ${current_price:.4f} (TP: ${take_profit:.4f})")
                close_position(exchange, position, current_price, 'TAKE_PROFIT', pnl_percent)
                positions_closed += 1
            
            # Update position P&L in memory
            position['current_price'] = current_price
            position['pnl_percent'] = pnl_percent
            position_value = position.get('position_value', 30)
            position['unrealized_pnl'] = position_value * (pnl_percent / 100)
            
        except Exception as e:
            logger.error(f"❌ Error checking position {symbol}: {e}")
    
    return positions_closed

def close_position(exchange, position, close_price, reason, pnl_percent):
    """Close a position"""
    global daily_pnl
    
    symbol = position['symbol']
    
    try:
        logger.info(f"🔄 CLOSING POSITION: {symbol} ({reason})")
        
        # To close a SHORT, we need to BUY
        if position['type'] == 'SHORT':
            close_side = 'buy'
        else:  # LONG
            close_side = 'sell'
        
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side=close_side,
            amount=position['amount']
        )
        
        logger.info(f"✅ POSITION CLOSED: {symbol}")
        logger.info(f"   Order ID: {order['id']}")
        logger.info(f"   Close Price: ${close_price:.4f}")
        logger.info(f"   P&L: {pnl_percent:.2f}%")
        
        # Calculate dollar P&L
        position_value = position.get('position_value', 30)
        pnl_dollar = position_value * (pnl_percent / 100)
        
        # Update daily P&L
        daily_pnl += pnl_dollar
        
        # Update position in history
        PositionManager.update_position_status(symbol, 'CLOSED', close_price, pnl_dollar)
        
        logger.info(f"💰 Daily P&L updated: ${daily_pnl:.2f}")
        
    except Exception as e:
        logger.error(f"❌ Error closing        position {symbol}: {e}")

def free_up_capital_if_needed(exchange):
    """Close worst position if we need capital and are at max positions"""
    if len(open_positions) < MAX_POSITIONS:
        return False
    
    # Check available balance
    try:
        balance = exchange.fetch_balance()
        free_usdt = balance['USDT']['free']
        
        # If we have less than needed for one position
        capital_needed = BINANCE_CAPITAL * POSITION_SIZE  # $13.43
        
        if free_usdt < capital_needed:
            logger.warning(f"⚠️  Low capital: ${free_usdt:.2f} available, need ${capital_needed:.2f}")
            
            # Close worst position
            worst_position = PositionManager.get_worst_position()
            if worst_position:
                logger.info(f"🔧 Freeing capital by closing worst position: {worst_position['symbol']}")
                
                # Get current price
                ticker = exchange.fetch_ticker(worst_position['symbol'])
                current_price = ticker['last']
                
                # Calculate P&L
                entry_price = worst_position.get('entry_price', worst_position.get('current_price', 0))
                if worst_position['type'] == 'SHORT':
                    pnl_percent = ((entry_price - current_price) / entry_price) * 100
                else:
                    pnl_percent = ((current_price - entry_price) / entry_price) * 100
                
                close_position(exchange, worst_position, current_price, 'CAPITAL_FREEING', pnl_percent)
                return True
    
    except Exception as e:
        logger.error(f"❌ Error checking capital: {e}")
    
    return False

def trading_cycle(exchanges):
    """One trading cycle - check opportunities and manage positions"""
    logger.info("=" * 70)
    logger.info(f"📊 ENHANCED TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("=" * 70)
    
    opportunities_found = 0
    
    # First, check and close positions if needed
    if exchanges['binance']:
        # Check SL/TP on existing positions
        positions_closed = check_and_close_positions(exchanges['binance'])
        if positions_closed > 0:
            logger.info(f"📉 Closed {positions_closed} positions")
        
        # Free up capital if needed
        if free_up_capital_if_needed(exchanges['binance']):
            logger.info("💰 Freed up capital for new trades")
    
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
    
    # Log current status
    logger.info(f"📊 STATUS: {len(open_positions)}/{MAX_POSITIONS} positions, Daily P&L: ${daily_pnl:.2f}")
    
    return opportunities_found

def main():
    """Main trading loop"""
    logger.info("=" * 70)
    logger.info("🚀 ENHANCED 26-CRYPTO TRADING BOT")
    logger.info("=" * 70)
    logger.info(f"📊 Trading ALL 26 cryptocurrencies")
    logger.info(f"₿ Binance SHORT: {len(ALL_CRYPTOS)} cryptos (${BINANCE_CAPITAL:.2f} capital)")
    logger.info(f"📉 SHORT threshold: {SHORT_THRESHOLD}% drop (REAL MOVES ONLY)")
    logger.info(f"💰 Position size: {POSITION_SIZE*100:.0f}% of capital (${BINANCE_CAPITAL * POSITION_SIZE:.2f})")
    logger.info(f"⚖️  Leverage: {LEVERAGE}x (SAFER)")
    logger.info(f"🛑 Stop-loss: {STOP_LOSS*100:.0f}%, ✅ Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"📈 Max positions: {MAX_POSITIONS}")
    logger.info(f"📉 Daily loss limit: {DAILY_LOSS_LIMIT*100:.0f}%")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info("=" * 70)
    logger.info("⚡ AUTOMATIC POSITION MANAGEMENT ENABLED")
    logger.info("⚡ Will automatically close at SL/TP")
    logger.info("⚡ Will free capital when needed")
    logger.info("=" * 70)
    
    # Load open positions
    PositionManager.load_open_positions()
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchanges
    exchanges = init_exchanges(keys)
    
    if not exchanges['binance']:
        logger.error("❌ Binance exchange not available. Exiting.")
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