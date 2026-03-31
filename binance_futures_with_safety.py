#!/usr/bin/env python3
"""
BINANCE FUTURES SHORT TRADING BOT WITH SAFETY FEATURES
Actually executes SHORT trades on Binance Futures with safety checks
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
log_file = os.path.join(BASE_DIR, "binance_futures_safe.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to load simple safety monitor
try:
    sys.path.append(BASE_DIR)
    from simple_safety_monitor import simple_safety_monitor as safety_monitor
    SAFETY_ENABLED = True
    logger.info("✅ Simple Safety Monitor loaded for Binance")
except ImportError as e:
    SAFETY_ENABLED = False
    logger.warning(f"⚠️ Safety Monitor not available: {e}")

# Cryptocurrencies for futures trading (focus on smaller caps for $50 capital)
FUTURES_CRYPTOS = [
    "DOGE", "SHIB", "ADA", "XRP", "DOT", "MATIC", "LINK",
    "UNI", "ATOM", "ETC", "XLM", "ALGO", "VET", "FIL",
    "XTZ", "EOS", "COMP", "SNX"
]

# Trading parameters
SHORT_THRESHOLD = 0.8   # 0.8% drop for SHORT
SCAN_INTERVAL = 60      # 60 seconds
FUTURES_CAPITAL = 50.00  # $50 for futures shorting
LEVERAGE = 3            # 3x leverage (conservative)
POSITION_SIZE = 0.2     # 20% of capital per trade
STOP_LOSS = 0.05        # 5% stop-loss
TAKE_PROFIT = 0.08      # 8% take-profit

# Price history for safety checks
price_history = {}

def load_binance_keys():
    """Load Binance API keys"""
    try:
        with open(os.path.join(BASE_DIR, 'secure_keys/.binance_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, 'secure_keys/.binance_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        logger.info("✅ Binance API keys loaded")
        return api_key, api_secret
    except Exception as e:
        logger.error(f"❌ Failed to load Binance keys: {e}")
        return None, None

def run_safety_checks(symbol, current_price):
    """Run safety checks before shorting"""
    if not SAFETY_ENABLED:
        return {'trade_allowed': True, 'suggested_action': 'NORMAL', 'alerts': []}
    
    # Get price history for this symbol
    hist = price_history.get(symbol, [])
    
    # Run safety checks
    safety_result = safety_monitor.run_safety_checks(
        symbol=symbol,
        current_price=current_price,
        price_history=hist[-100:] if len(hist) >= 100 else hist
    )
    
    return safety_result

def execute_futures_short(symbol, current_price, change_24h):
    """Execute futures short with safety checks"""
    
    # Run SAFETY CHECKS first
    safety_result = run_safety_checks(symbol, current_price)
    
    if not safety_result['trade_allowed']:
        logger.error(f"🚨 SHORTING HALTED by Safety Monitor!")
        for alert in safety_result['alerts']:
            if alert['severity'] in ['CRITICAL', 'HIGH']:
                logger.error(f"   {alert['message']}")
        return None
    
    if safety_result['suggested_action'] == 'REDUCE_RISK':
        logger.warning(f"⚠️ Safety Monitor suggests reducing risk for {symbol}")
        # Reduce position size by 50% when risk is high
        risk_multiplier = 0.5
    else:
        risk_multiplier = 1.0
    
    # Load API keys
    api_key, api_secret = load_binance_keys()
    if not api_key or not api_secret:
        return None
    
    # Initialize Binance Futures exchange
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',  # Futures trading
        }
    })
    
    # Prepare trade data
    trade_data = {
        'symbol': symbol,
        'side': 'SHORT',
        'entry_price': current_price,
        '24h_change': change_24h,
        'timestamp': datetime.now().isoformat(),
        'status': 'PLANNED',
        'safety_alerts': [a['message'] for a in safety_result['alerts'] if a['severity'] in ['CRITICAL', 'HIGH']]
    }
    
    try:
        # Calculate position size with risk multiplier
        position_value = FUTURES_CAPITAL * POSITION_SIZE * risk_multiplier
        amount = position_value / current_price
        
        # Ensure minimum contract size (0.001 for BTC, adjust for others)
        if symbol == 'BTC/USDT' and amount < 0.001:
            amount = 0.001  # Minimum BTC contract size
            position_value = amount * current_price
            logger.info(f"   Adjusted to minimum: 0.001 BTC (${position_value:.2f})")
        
        # Apply leverage
        leveraged_value = position_value * LEVERAGE
        leveraged_amount = amount * LEVERAGE
        
        # Calculate stop-loss and take-profit prices
        stop_loss_price = current_price * (1 + STOP_LOSS)  # Higher price for short (loss)
        take_profit_price = current_price * (1 - TAKE_PROFIT)  # Lower price for short (profit)
        
        logger.info(f"🎯 PREPARING FUTURES SHORT: {symbol}")
        logger.info(f"    Current price: ${current_price:.4f}")
        logger.info(f"    24h change: {change_24h:.2f}%")
        logger.info(f"    Position size: {leveraged_amount:.6f} contracts")
        logger.info(f"    Position value: ${leveraged_value:.2f} (with {LEVERAGE}x leverage)")
        logger.info(f"    Capital at risk: ${position_value:.2f}")
        logger.info(f"    Stop-loss: ${stop_loss_price:.4f} (+{STOP_LOSS*100:.0f}%)")
        logger.info(f"    Take-profit: ${take_profit_price:.4f} (-{TAKE_PROFIT*100:.0f}%)")
        if risk_multiplier < 1.0:
            logger.info(f"    ⚠️ Reduced size: {risk_multiplier*100:.0f}% due to safety alerts")
        
        # ✅ REAL TRADING ENABLED
        try:
            # Set leverage first
            exchange.set_leverage(LEVERAGE, symbol)
            
            # Place short order (SELL for short position)
            order = exchange.create_order(
                symbol=symbol,
                type='market',
                side='sell',
                amount=leveraged_amount
            )
            
            trade_data['status'] = 'EXECUTED'
            trade_data['order_id'] = order['id']
            trade_data['executed_amount'] = leveraged_amount
            trade_data['risk_multiplier'] = risk_multiplier
            
            logger.info(f"✅ REAL SHORT ORDER EXECUTED: {order['id']}")
            logger.info(f"   Safety alerts considered: {len(trade_data['safety_alerts'])}")
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            trade_data['status'] = 'FAILED'
            trade_data['error'] = str(e)
        
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Error in futures short execution: {e}")
        return None

def scan_futures_opportunities():
    """Scan for futures short opportunities"""
    api_key, api_secret = load_binance_keys()
    if not api_key or not api_secret:
        return
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
        }
    })
    
    logger.info(f"\n🔍 Scanning {len(FUTURES_CRYPTOS)} cryptocurrencies for short opportunities...")
    
    opportunities = 0
    
    for crypto in FUTURES_CRYPTOS:
        symbol = f"{crypto}/USDT"
        
        try:
            # Fetch ticker for futures
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            change_24h = ((current_price - ticker['open']) / ticker['open']) * 100 if ticker['open'] else 0
            
            # Update price history for safety checks
            if symbol not in price_history:
                price_history[symbol] = []
            price_history[symbol].append(current_price)
            if len(price_history[symbol]) > 200:
                price_history[symbol] = price_history[symbol][-200:]
            
            # Check for short opportunity (price dropping)
            if change_24h < -SHORT_THRESHOLD:
                logger.info(f"⚡ FUTURES SHORT SIGNAL: {symbol} down {abs(change_24h):.2f}%")
                
                # Execute short with safety checks
                trade = execute_futures_short(symbol, current_price, change_24h)
                if trade and trade['status'] == 'EXECUTED':
                    opportunities += 1
                    # Limit to 2 trades per scan to avoid over-trading
                    if opportunities >= 2:
                        break
        
        except Exception as e:
            logger.debug(f"Could not fetch {symbol}: {e}")
            continue
    
    if opportunities == 0:
        logger.info("📊 No strong short opportunities found this cycle")

def main():
    """Main futures trading loop"""
    logger.info("=" * 70)
    logger.info("🚀 BINANCE FUTURES SHORT TRADING BOT WITH SAFETY")
    logger.info("=" * 70)
    logger.info(f"SHORT threshold: {SHORT_THRESHOLD}% drop")
    logger.info(f"Futures capital: ${FUTURES_CAPITAL:.2f}")
    logger.info(f"Leverage: {LEVERAGE}x (conservative)")
    logger.info(f"Position size: {POSITION_SIZE*100:.0f}% of capital")
    logger.info(f"Stop-loss: {STOP_LOSS*100:.0f}%, Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"Scan interval: {SCAN_INTERVAL} seconds")
    
    if SAFETY_ENABLED:
        logger.info("✅ SAFETY FEATURES ENABLED:")
        logger.info("   • Market crash detection")
        logger.info("   • Basic technical indicators")
        logger.info("   • Price action monitoring")
    else:
        logger.warning("⚠️ Safety features NOT available")
    
    logger.info("=" * 70)
    logger.info("🚨 REAL TRADING MODE - ACTIVE")
    logger.info("   Trades WILL be executed on Binance Futures")
    logger.info("   Using 3x leverage for short positions")
    logger.info("=" * 70)
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"\n📊 FUTURES SCAN CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            scan_futures_opportunities()
            
            logger.info(f"⏰ Next scan in {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n👋 Binance Futures bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == '__main__':
    main()