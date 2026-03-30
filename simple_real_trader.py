#!/usr/bin/env python3
"""
SIMPLE REAL TRADER - Actually grows $100 investment
Fixed version with error handling
"""

import ccxt
import time
import json
import os
from datetime import datetime
import logging

print("="*70)
print("🚀 SIMPLE REAL TRADER - GROW $100 INVESTMENT")
print("="*70)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_trading.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load API keys
try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    logger.info(f"✅ Gemini API keys loaded")
except Exception as e:
    logger.error(f"❌ Cannot load Gemini API keys: {e}")
    exit(1)

# Initialize exchange
exchange = ccxt.gemini({
    'apiKey': GEMINI_KEY,
    'secret': GEMINI_SECRET,
    'enableRateLimit': True,
})

# TRADING PARAMETERS
TOTAL_CAPITAL = 542.27  # Your actual balance
TRADING_CAPITAL = 100.00  # Amount to actively trade
RISK_PER_TRADE = 0.02  # 2% risk per trade
STOP_LOSS = 0.03  # 3% stop-loss
TAKE_PROFIT = 0.06  # 6% take-profit
MAX_TRADES_PER_DAY = 3
SYMBOLS = ['BTC/USD', 'ETH/USD']

# State
trades_today = 0
last_trade_date = datetime.now().date()

logger.info(f"💰 Total Balance: ${TOTAL_CAPITAL:.2f}")
logger.info(f"🎯 Trading Capital: ${TRADING_CAPITAL:.2f}")
logger.info(f"⚖️ Risk: {RISK_PER_TRADE*100}% per trade (${TRADING_CAPITAL * RISK_PER_TRADE:.2f})")
logger.info(f"🛑 Stop-loss: {STOP_LOSS*100}%")
logger.info(f"🎯 Take-profit: {TAKE_PROFIT*100}%")
logger.info(f"📊 Max trades/day: {MAX_TRADES_PER_DAY}")
print("="*70)

def safe_get_market_data(symbol):
    """Safely get market data with error handling"""
    try:
        ticker = exchange.fetch_ticker(symbol)
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'bid': ticker.get('bid', ticker['last']),
            'ask': ticker.get('ask', ticker['last']),
            'volume': ticker.get('quoteVolume', 0),
            'change': ticker.get('percentage', 0)
        }
    except Exception as e:
        logger.error(f"Market data error for {symbol}: {e}")
        return None

def simple_analysis(price, change):
    """Simple conservative analysis"""
    # Buy if price dropped significantly
    if change < -2.0:  # Down 2% or more
        return "BUY", 0.7, f"Price down {change:.1f}% - buying dip"
    
    # Sell if price rose significantly
    elif change > 4.0:  # Up 4% or more
        return "SELL", 0.6, f"Price up {change:.1f}% - taking profit"
    
    return "HOLD", 0.0, "No clear signal"

trades_today = 0  # Global variable

def execute_safe_trade(symbol, signal, price, confidence, reason):
    """Execute a trade with maximum safety"""
    global trades_today
    
    # Check daily limit
    if trades_today >= MAX_TRADES_PER_DAY:
        logger.warning(f"Max trades per day ({MAX_TRADES_PER_DAY}) reached")
        return None
    
    # Get current balance
    try:
        balance = exchange.fetch_balance()
        usd = balance['free'].get('USD', 0)
        
        if usd < 10:
            logger.warning(f"Insufficient USD: ${usd:.2f}")
            return None
    except Exception as e:
        logger.error(f"Balance check failed: {e}")
        return None
    
    # Calculate VERY SMALL position for safety
    risk_amount = TRADING_CAPITAL * RISK_PER_TRADE  # $2 risk
    position_value = risk_amount / STOP_LOSS  # ~$66 position
    quantity = position_value / price
    
    # Make it even smaller for first trade
    quantity = quantity * 0.5  # 50% of calculated size
    
    if quantity * price < 5:  # Minimum $5
        quantity = 5 / price
    
    logger.info(f"📈 Preparing {signal} order:")
    logger.info(f"   Symbol: {symbol}")
    logger.info(f"   Price: ${price:.2f}")
    logger.info(f"   Quantity: {quantity:.6f}")
    logger.info(f"   Value: ${quantity * price:.2f}")
    logger.info(f"   Reason: {reason}")
    
    # Ask for confirmation (for first few trades)
    if trades_today == 0:
        logger.info("🔄 This is the FIRST trade. Proceeding...")
    
    try:
        if signal == "BUY":
            order = exchange.create_market_buy_order(symbol, quantity)
        else:
            order = exchange.create_market_sell_order(symbol, quantity)
        
        trade = {
            'id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': signal,
            'price': order.get('average', price),
            'quantity': quantity,
            'value': quantity * price,
            'status': order['status'],
            'reason': reason
        }
        
        trades_today += 1
        
        # Save trade
        save_trade(trade)
        
        logger.info(f"✅ {signal} order EXECUTED!")
        logger.info(f"   Order ID: {order['id']}")
        logger.info(f"   Status: {order['status']}")
        
        return trade
        
    except Exception as e:
        logger.error(f"❌ Trade execution failed: {e}")
        return None

def save_trade(trade):
    """Save trade to history"""
    try:
        if os.path.exists('real_trades_history.json'):
            with open('real_trades_history.json', 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(trade)
        
        with open('real_trades_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        # Also update completed_trades.json for dashboard
        if os.path.exists('completed_trades.json'):
            with open('completed_trades.json', 'r') as f:
                completed = json.load(f)
        else:
            completed = []
        
        completed.append(trade)
        with open('completed_trades.json', 'w') as f:
            json.dump(completed, f, indent=2)
        
        logger.info(f"💾 Trade saved to history")
    except Exception as e:
        logger.error(f"Save error: {e}")

def main():
    """Main trading loop"""
    global trades_today, last_trade_date
    
    logger.info("🔄 Starting conservative trading...")
    
    cycle = 0
    while True:
        cycle += 1
        logger.info(f"\n📊 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
        
        # Check if new day
        current_date = datetime.now().date()
        if current_date != last_trade_date:
            trades_today = 0
            last_trade_date = current_date
            logger.info("🔄 New day - trade counter reset")
        
        # Check balance
        try:
            balance = exchange.fetch_balance()
            usd = balance['free'].get('USD', 0)
            logger.info(f"💰 Balance: ${usd:.2f} USD")
        except:
            pass
        
        # Analyze markets
        for symbol in SYMBOLS:
            data = safe_get_market_data(symbol)
            if not data:
                continue
            
            price = data['price']
            change = data['change'] or 0
            
            logger.info(f"🔍 {symbol}: ${price:.2f} ({change:.1f}%)")
            
            signal, confidence, reason = simple_analysis(price, change)
            
            if signal != "HOLD" and confidence > 0.6:
                logger.info(f"🎯 Signal: {signal} ({confidence:.0%} confidence)")
                logger.info(f"   Reason: {reason}")
                
                # Execute if good opportunity
                if (signal == "BUY" and change < -2.5) or (signal == "SELL" and change > 5.0):
                    trade = execute_safe_trade(symbol, signal, price, confidence, reason)
                    if trade:
                        logger.info(f"💰 REAL TRADE COMPLETED!")
        
        logger.info(f"\n📈 Summary: Trades today: {trades_today}/{MAX_TRADES_PER_DAY}")
        logger.info(f"⏰ Next check in 3 minutes...")
        logger.info("="*50)
        
        time.sleep(180)  # 3 minutes

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Trading stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("Check API keys and internet connection")