#!/usr/bin/env python3
"""
REAL BINANCE FUTURES SHORT TRADING BOT
Actually executes SHORT trades on Binance Futures
"""

import os
import json
import time
import ccxt
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
log_file = os.path.join(BASE_DIR, "real_futures_trading.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cryptocurrencies for futures trading (filtered to avoid errors)
FUTURES_CRYPTOS = [
    "BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE",
    "AVAX", "MATIC", "LINK", "UNI", "LTC", "ATOM", "ETC",
    "XLM", "ALGO", "VET", "FIL", "ICP", "XTZ", 
    "AAVE", "MKR", "COMP", "SNX", "YFI"
]

# Trading parameters - CONSERVATIVE
SHORT_THRESHOLD = 1.0   # 1.0% drop for SHORT (more conservative)
SCAN_INTERVAL = 120      # 120 seconds (2 minutes - slower)
MAX_DAILY_TRADES = 2     # Max 2 trades per day
LEVERAGE = 2             # 2x leverage (VERY conservative)
POSITION_SIZE = 0.15     # 15% of capital per trade
STOP_LOSS = 0.03         # 3% stop-loss (tight)
TAKE_PROFIT = 0.05       # 5% take-profit

# Track daily trades
daily_trades_file = os.path.join(BASE_DIR, "daily_trades_counter.json")

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
        
        # Test connection
        exchange.load_markets()
        logger.info("✅ Binance Futures exchange connected")
        return exchange
    except Exception as e:
        logger.error(f"❌ Binance Futures connection failed: {e}")
        return None

def check_futures_balance(exchange):
    """Check Binance Futures USDT balance"""
    try:
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        total_balance = balance.get('USDT', {}).get('total', 0)
        
        logger.info(f"💰 Binance Futures balance:")
        logger.info(f"   Free USDT: ${usdt_balance:.2f}")
        logger.info(f"   Total USDT: ${total_balance:.2f}")
        
        return usdt_balance, total_balance
    except Exception as e:
        logger.error(f"Error checking futures balance: {e}")
        return 0, 0

def check_daily_trades():
    """Check how many trades we've done today"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        if os.path.exists(daily_trades_file):
            with open(daily_trades_file, 'r') as f:
                data = json.load(f)
            
            if data.get('date') == today:
                return data.get('count', 0)
    except:
        pass
    
    return 0

def update_daily_trades(count):
    """Update daily trades counter"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    data = {
        'date': today,
        'count': count,
        'last_update': datetime.now().isoformat()
    }
    
    try:
        with open(daily_trades_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error updating daily trades: {e}")

def analyze_futures_pair(exchange, crypto):
    """Analyze a futures pair for SHORT opportunities"""
    try:
        # Futures symbol format
        symbol = f"{crypto}/USDT"
        
        # Check if symbol exists
        if symbol not in exchange.markets:
            logger.debug(f"Symbol not found: {symbol}")
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        
        price = ticker['last']
        change = ticker.get('percentage', 0)
        
        # SHORT signal (price dropping significantly)
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
            'strength': strength,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.debug(f"Error analyzing {crypto} futures: {e}")
        return None

def calculate_futures_position(price, usdt_balance, leverage=LEVERAGE):
    """Calculate futures position size"""
    # Position value with leverage
    position_value = usdt_balance * POSITION_SIZE * leverage
    
    # Contract amount
    amount = position_value / price
    
    # Round to appropriate decimal places
    # Different cryptos have different min amounts
    if amount < 0.001:
        amount = 0.001
    
    return amount, position_value

def execute_real_futures_short(exchange, analysis, usdt_balance):
    """Execute a REAL SHORT trade on Binance Futures"""
    try:
        symbol = analysis['symbol']
        crypto = analysis['crypto']
        current_price = analysis['price']
        change = analysis['change']
        
        logger.warning(f"🎯 ATTEMPTING REAL FUTURES SHORT: {symbol}")
        logger.warning(f"   Current price: ${current_price:.4f}")
        logger.warning(f"   24h change: {change:.2f}%")
        
        # Check daily trade limit
        daily_trades = check_daily_trades()
        if daily_trades >= MAX_DAILY_TRADES:
            logger.warning(f"⚠️  Daily trade limit reached: {daily_trades}/{MAX_DAILY_TRADES}")
            return None
        
        # Calculate position
        amount, position_value = calculate_futures_position(current_price, usdt_balance)
        
        logger.warning(f"   Position size: {amount:.6f} contracts")
        logger.warning(f"   Position value: ${position_value:.2f} (with {LEVERAGE}x leverage)")
        logger.warning(f"   Capital at risk: ${position_value/LEVERAGE:.2f}")
        
        # Calculate stop-loss and take-profit
        stop_loss_price = current_price * (1 + STOP_LOSS)
        take_profit_price = current_price * (1 - TAKE_PROFIT)
        
        logger.warning(f"   Stop-loss: ${stop_loss_price:.4f} (+{STOP_LOSS*100:.1f}%)")
        logger.warning(f"   Take-profit: ${take_profit_price:.4f} (-{TAKE_PROFIT*100:.1f}%)")
        
        # TRADE EXECUTION
        try:
            # Set leverage
            logger.info(f"Setting {LEVERAGE}x leverage for {symbol}...")
            exchange.set_leverage(LEVERAGE, symbol)
            
            # Place SHORT market order
            logger.warning(f"📉 PLACING REAL SHORT ORDER: {amount:.6f} {symbol} @ market")
            
            order = exchange.create_order(
                symbol=symbol,
                type='market',
                side='sell',
                amount=amount,
                params={'positionSide': 'SHORT'}  # Explicitly short
            )
            
            logger.critical(f"✅ REAL SHORT ORDER EXECUTED!")
            logger.critical(f"   Order ID: {order['id']}")
            logger.critical(f"   Symbol: {order['symbol']}")
            logger.critical(f"   Side: {order['side']}")
            logger.critical(f"   Amount: {order['amount']}")
            logger.critical(f"   Price: ${order['price'] if order['price'] else 'market'}")
            
            # Update daily trades counter
            daily_trades += 1
            update_daily_trades(daily_trades)
            
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'exchange': 'binance_futures',
                'symbol': symbol,
                'side': 'sell',
                'type': 'SHORT',
                'order_id': order['id'],
                'entry_price': current_price,
                'executed_price': order['price'] if order['price'] else current_price,
                'amount': amount,
                'position_value': position_value,
                'leverage': LEVERAGE,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'signal_strength': abs(change),
                'status': 'EXECUTED',
                'daily_trade_count': daily_trades,
                'risk_notes': f"Capital at risk: ${position_value/LEVERAGE:.2f}"
            }
            
            # Save executed trade
            trades_file = os.path.join(BASE_DIR, "executed_futures_trades.json")
            try:
                if os.path.exists(trades_file):
                    with open(trades_file, 'r') as f:
                        trades = json.load(f)
                else:
                    trades = []
                
                trades.append(trade_data)
                
                with open(trades_file, 'w') as f:
                    json.dump(trades, f, indent=2)
                    
            except Exception as e:
                logger.error(f"Error saving executed trade: {e}")
            
            return trade_data
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            return {
                'symbol': symbol,
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"❌ Error in futures short execution: {e}")
        return None

def main():
    """Main futures trading loop - REAL EXECUTION"""
    logger.critical("=" * 70)
    logger.critical("🚀 REAL BINANCE FUTURES SHORT TRADING BOT")
    logger.critical("=" * 70)
    logger.critical("⚠️  WARNING: REAL TRADE EXECUTION ENABLED")
    logger.critical("=" * 70)
    logger.info(f"SHORT threshold: {SHORT_THRESHOLD}% drop")
    logger.info(f"Max daily trades: {MAX_DAILY_TRADES}")
    logger.info(f"Leverage: {LEVERAGE}x (conservative)")
    logger.info(f"Position size: {POSITION_SIZE*100:.0f}% of capital")
    logger.info(f"Stop-loss: {STOP_LOSS*100:.0f}%, Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"Scan interval: {SCAN_INTERVAL} seconds")
    logger.critical("=" * 70)
    logger.critical("REAL MONEY AT RISK - TRADES WILL BE EXECUTED")
    logger.critical("=" * 70)
    
    # Initialize Binance Futures
    exchange = initialize_binance_futures()
    if not exchange:
        logger.error("❌ Failed to initialize Binance Futures")
        return
    
    # Check futures balance
    free_balance, total_balance = check_futures_balance(exchange)
    
    if total_balance < 10:
        logger.error(f"❌ Insufficient Futures balance: ${total_balance:.2f}")
        logger.info("💡 Need at least $10 for trading")
        return
    
    logger.info(f"✅ Sufficient balance: ${total_balance:.2f}")
    
    # Check daily trades
    daily_trades = check_daily_trades()
    logger.info(f"Daily trades today: {daily_trades}/{MAX_DAILY_TRADES}")
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            cycle_start = datetime.now()
            
            logger.info(f"\n📊 REAL TRADING CYCLE {cycle} - {cycle_start.strftime('%H:%M:%S')}")
            logger.info("-" * 50)
            
            trades_executed = 0
            
            # Check if we've reached daily limit
            if daily_trades >= MAX_DAILY_TRADES:
                logger.warning(f"⚠️  Daily trade limit reached: {daily_trades}/{MAX_DAILY_TRADES}")
                logger.info("   Waiting for next day...")
            else:
                # Check futures pairs
                logger.info(f"🔍 Analyzing futures pairs for SHORT opportunities...")
                
                for crypto in FUTURES_CRYPTOS:
                    analysis = analyze_futures_pair(exchange, crypto)
                    
                    if analysis and analysis['signal'] == 'SHORT':
                        logger.warning(f"⚡ STRONG SHORT SIGNAL: {analysis['symbol']} down {analysis['change']:.2f}%")
                        
                        # Check balance and daily limit
                        if free_balance >= 10 and daily_trades < MAX_DAILY_TRADES:
                            # EXECUTE REAL TRADE
                            trade_result = execute_real_futures_short(exchange, analysis, free_balance)
                            if trade_result and trade_result.get('status') == 'EXECUTED':
                                trades_executed += 1
                                daily_trades += 1
                        else:
                            logger.warning(f"⚠️  Cannot trade: Balance=${free_balance:.2f}, Daily={daily_trades}/{MAX_DAILY_TRADES}")
            
            cycle_end = datetime.now()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            logger.info(f"\n📈 CYCLE {cycle} SUMMARY:")
            logger.info(f"   Trades executed: {trades_executed}")
            logger.info(f"   Daily trades: {daily_trades}/{MAX_DAILY_TRADES}")
            logger.info(f"   Cycle duration: {cycle_duration:.1f} seconds")
            logger.info(f"   Free balance: ${free_balance:.2f}")
            
            if trades_executed > 0:
                logger.critical(f"   🎯 REAL TRADES EXECUTED THIS CYCLE!")
                logger.critical(f"   Check executed_futures_trades.json")
            else:
                logger.info(f"   ⏳ No trades this cycle")
            
            logger.info(f"\n⏰ Next scan in {SCAN_INTERVAL} seconds...")
            logger.info("=" * 70)
            
            # Update balance
            free_balance, total_balance = check_futures_balance(exchange)
            
            # Wait for next cycle
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Real futures trading bot stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Error in real futures bot: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()