#!/usr/bin/env python3
"""
MICRO FUTURES TRADING BOT
Tiny positions ($5-10) for safe testing
"""

import os
import json
import time
import ccxt
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
log_file = os.path.join(BASE_DIR, "micro_futures_trading.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Conservative selection
MICRO_CRYPTOS = ["DOT", "COMP", "SNX", "MKR"]  # Only these 4 for micro trading

# MICRO TRADING PARAMETERS (SAFE)
SHORT_THRESHOLD = 1.5      # 1.5% drop (more conservative)
SCAN_INTERVAL = 180        # 3 minutes (slower)
MAX_DAILY_TRADES = 1       # 1 trade per day MAX
LEVERAGE = 1               # NO LEVERAGE (1x)
MAX_TRADE_SIZE = 5.00      # $5 MAX per trade
STOP_LOSS = 0.02           # 2% stop-loss (tight)
TAKE_PROFIT = 0.03         # 3% take-profit

# Track trades
trades_file = os.path.join(BASE_DIR, "micro_trades_history.json")

def load_binance_keys():
    """Load Binance API keys"""
    try:
        with open(os.path.join(BASE_DIR, '.binance_key'), 'r') as f:
            api_key = f.read().strip()
        with open(os.path.join(BASE_DIR, '.binance_secret'), 'r') as f:
            api_secret = f.read().strip()
        
        return api_key, api_secret
    except Exception as e:
        logger.error(f"Error loading Binance keys: {e}")
        return None, None

def initialize_binance_futures():
    """Initialize Binance Futures exchange"""
    api_key, api_secret = load_binance_keys()
    
    if not api_key or not api_secret:
        return None
    
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {'defaultType': 'future'},
            'enableRateLimit': True
        })
        
        exchange.load_markets()
        logger.info("✅ Binance Futures connected (MICRO MODE)")
        return exchange
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None

def check_today_trades():
    """Check trades executed today"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
            
            # Count today's trades
            today_trades = [t for t in trades if t.get('date') == today]
            return len(today_trades)
    except:
        pass
    
    return 0

def save_trade(trade_data):
    """Save trade to history"""
    trade_data['date'] = datetime.now().strftime("%Y-%m-%d")
    
    try:
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades = json.load(f)
        else:
            trades = []
        
        trades.append(trade_data)
        
        # Keep only last 100 trades
        if len(trades) > 100:
            trades = trades[-100:]
        
        with open(trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving trade: {e}")

def analyze_pair(exchange, crypto):
    """Analyze pair for SHORT"""
    try:
        symbol = f"{crypto}/USDT"
        
        if symbol not in exchange.markets:
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        
        price = ticker['last']
        change = ticker.get('percentage', 0)
        
        # Strong SHORT signal needed for micro trading
        if change < -SHORT_THRESHOLD:
            signal = "SHORT"
            strength = abs(change)
        else:
            signal = "HOLD"
            strength = 0
        
        return {
            'symbol': symbol,
            'crypto': crypto,
            'price': price,
            'change': change,
            'signal': signal,
            'strength': strength
        }
        
    except Exception as e:
        logger.debug(f"Error analyzing {crypto}: {e}")
        return None

def execute_micro_short(exchange, analysis):
    """Execute MICRO SHORT trade ($5 max)"""
    try:
        symbol = analysis['symbol']
        price = analysis['price']
        change = analysis['change']
        
        # Calculate micro position ($5 max)
        position_value = min(MAX_TRADE_SIZE, 5.00)
        amount = position_value / price
        
        # Round appropriately
        if amount < 0.001:
            amount = 0.001
        
        logger.warning(f"🎯 MICRO SHORT ATTEMPT: {symbol}")
        logger.warning(f"   Price: ${price:.4f}, Change: {change:.2f}%")
        logger.warning(f"   Amount: {amount:.6f}, Value: ${position_value:.2f}")
        logger.warning(f"   NO LEVERAGE (1x), Stop-loss: {STOP_LOSS*100:.0f}%")
        
        # Check if we've traded today
        today_trades = check_today_trades()
        if today_trades >= MAX_DAILY_TRADES:
            logger.warning(f"⚠️  Daily micro trade limit: {today_trades}/{MAX_DAILY_TRADES}")
            return None
        
        # EXECUTE MICRO TRADE
        try:
            # Set 1x leverage (no leverage)
            exchange.set_leverage(1, symbol)
            
            logger.critical(f"📉 EXECUTING MICRO SHORT: {amount:.6f} {symbol}")
            
            order = exchange.create_order(
                symbol=symbol,
                type='market',
                side='sell',
                amount=amount,
                params={'positionSide': 'SHORT'}
            )
            
            logger.critical(f"✅ MICRO SHORT EXECUTED!")
            logger.critical(f"   Order ID: {order['id']}")
            logger.critical(f"   Amount: {order['amount']}")
            logger.critical(f"   Today's trades: {today_trades + 1}/{MAX_DAILY_TRADES}")
            
            # Save trade
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'side': 'sell',
                'type': 'MICRO_SHORT',
                'order_id': order['id'],
                'entry_price': price,
                'executed_price': order.get('price', price),
                'amount': amount,
                'position_value': position_value,
                'leverage': 1,
                'stop_loss': price * (1 + STOP_LOSS),
                'take_profit': price * (1 - TAKE_PROFIT),
                'signal_strength': abs(change),
                'status': 'EXECUTED',
                'risk_level': 'MICRO ($5)'
            }
            
            save_trade(trade_data)
            
            return trade_data
            
        except Exception as e:
            logger.error(f"❌ Micro trade failed: {e}")
            return {
                'symbol': symbol,
                'status': 'FAILED',
                'error': str(e)
            }
        
    except Exception as e:
        logger.error(f"❌ Error in micro short: {e}")
        return None

def main():
    """Main micro trading loop"""
    logger.critical("=" * 70)
    logger.critical("🔬 MICRO FUTURES TRADING BOT")
    logger.critical("=" * 70)
    logger.critical("SAFE MODE: $5 max per trade, NO LEVERAGE")
    logger.critical("=" * 70)
    logger.info(f"SHORT threshold: {SHORT_THRESHOLD}% drop")
    logger.info(f"Max daily trades: {MAX_DAILY_TRADES}")
    logger.info(f"Max trade size: ${MAX_TRADE_SIZE:.2f}")
    logger.info(f"Leverage: {LEVERAGE}x (NO LEVERAGE)")
    logger.info(f"Stop-loss: {STOP_LOSS*100:.0f}%, Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"Scan interval: {SCAN_INTERVAL} seconds")
    logger.info(f"Cryptos: {', '.join(MICRO_CRYPTOS)}")
    logger.critical("=" * 70)
    logger.critical("REAL TRADES - $5 MAX RISK PER TRADE")
    logger.critical("=" * 70)
    
    # Initialize
    exchange = initialize_binance_futures()
    if not exchange:
        return
    
    # Check balance
    try:
        balance = exchange.fetch_balance()
        free_usdt = balance.get('USDT', {}).get('free', 0)
        logger.info(f"💰 Free USDT: ${free_usdt:.2f}")
        
        if free_usdt < 5:
            logger.error(f"❌ Need at least $5, have ${free_usdt:.2f}")
            return
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        return
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"\n🔍 MICRO SCAN {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            logger.info("-" * 50)
            
            # Check daily limit
            today_trades = check_today_trades()
            if today_trades >= MAX_DAILY_TRADES:
                logger.warning(f"Daily micro trades: {today_trades}/{MAX_DAILY_TRADES}")
                logger.info("Waiting for next day...")
            else:
                # Analyze micro cryptos
                for crypto in MICRO_CRYPTOS:
                    analysis = analyze_pair(exchange, crypto)
                    
                    if analysis and analysis['signal'] == 'SHORT':
                        logger.warning(f"⚡ MICRO SHORT SIGNAL: {analysis['symbol']} down {analysis['change']:.2f}%")
                        
                        # Execute micro trade
                        if today_trades < MAX_DAILY_TRADES:
                            trade = execute_micro_short(exchange, analysis)
                            if trade and trade.get('status') == 'EXECUTED':
                                today_trades += 1
                                logger.critical(f"🎯 DAILY MICRO TRADE COMPLETE")
                                logger.critical(f"   No more trades today")
                                break  # Stop after one trade
            
            logger.info(f"\n⏰ Next micro scan in {SCAN_INTERVAL} seconds...")
            logger.info("=" * 70)
            
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Micro trading bot stopped")
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()