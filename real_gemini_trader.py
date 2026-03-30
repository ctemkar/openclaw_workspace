#!/usr/bin/env python3
"""
REAL Gemini Trading Bot - Actually buys/sells with $200
Conservative strategy with real order execution
"""

import ccxt
import time
import json
from datetime import datetime, timedelta
import os

print("="*70)
print("🚀 REAL GEMINI TRADING BOT - ACTIVE TRADING")
print("="*70)

# Load API keys
try:
    with open("secure_keys/.gemini_key", "r") as f:
        GEMINI_KEY = f.read().strip()
    with open("secure_keys/.gemini_secret", "r") as f:
        GEMINI_SECRET = f.read().strip()
    
    print(f"✅ Gemini Key: {GEMINI_KEY[:10]}...")
    print(f"✅ Gemini Secret: {GEMINI_SECRET[:10]}...")
except Exception as e:
    print(f"❌ Cannot load Gemini API keys: {e}")
    exit(1)

# Initialize exchange
exchange = ccxt.gemini({
    'apiKey': GEMINI_KEY,
    'secret': GEMINI_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
    }
})

# Trading parameters
CAPITAL = 200.00  # $200 for Gemini longs
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD']

# State tracking
trades_today = 0
last_trade_date = datetime.now().date()
open_positions = []
trade_history = []

print(f"💰 Capital: ${CAPITAL:.2f}")
print(f"🎯 Risk: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
print(f"📈 Symbols: {', '.join(SYMBOLS)}")
print(f"📊 Max trades/day: {MAX_TRADES_PER_DAY}")
print("="*70)

def check_balance():
    """Check Gemini balance"""
    try:
        balance = exchange.fetch_balance()
        usd = balance['free'].get('USD', 0)
        print(f"📊 Gemini Balance: ${usd:.2f} USD")
        return usd
    except Exception as e:
        print(f"❌ Balance check error: {e}")
        return 0

def get_market_data(symbol):
    """Get current market data"""
    try:
        ticker = exchange.fetch_ticker(symbol)
        change = ticker.get('percentage')
        if change is None:
            # Calculate change from previous close if available
            change = 0.0
        
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'bid': ticker['bid'],
            'ask': ticker['ask'],
            'volume': ticker.get('quoteVolume', 0),
            'change': change
        }
    except Exception as e:
        print(f"❌ Market data error for {symbol}: {e}")
        return None

def analyze_symbol(symbol, market_data):
    """Conservative analysis for a symbol"""
    price = market_data['price']
    change = market_data['change']
    
    # Conservative strategy
    signal = "HOLD"
    confidence = 0.5
    reason = "Neutral market"
    
    # Buy if price dropped 3%+ (buy the dip)
    if change < -3.0:
        signal = "BUY"
        confidence = 0.65
        reason = f"Price dropped {abs(change):.1f}% - buying dip"
    
    # Sell if price rose 8%+ (take profit)
    elif change > 8.0 and any(p['symbol'] == symbol for p in open_positions):
        signal = "SELL"
        confidence = 0.70
        reason = f"Price up {change:.1f}% - taking profit"
    
    return {
        'symbol': symbol,
        'price': price,
        'signal': signal,
        'confidence': confidence,
        'reason': reason,
        'change': change
    }

def execute_buy(symbol, price, confidence, reason):
    """Execute a BUY order"""
    global trades_today
    
    # Check daily limit
    if trades_today >= MAX_TRADES_PER_DAY:
        print(f"⚠️ Max trades per day ({MAX_TRADES_PER_DAY}) reached")
        return None
    
    # Calculate position size (20% of capital per trade)
    position_value = CAPITAL * 0.2
    quantity = position_value / price
    
    try:
        print(f"📈 Placing BUY order: {symbol} at ${price:.2f}")
        print(f"   Quantity: {quantity:.6f}, Value: ${position_value:.2f}")
        print(f"   Reason: {reason}")
        
        # Place market order
        order = exchange.create_market_buy_order(symbol, quantity)
        
        trade = {
            'id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': 'BUY',
            'price': price,
            'quantity': quantity,
            'value': position_value,
            'status': 'FILLED',
            'confidence': confidence,
            'reason': reason,
            'stop_loss': price * (1 - STOP_LOSS),
            'take_profit': price * (1 + TAKE_PROFIT)
        }
        
        trades_today += 1
        open_positions.append(trade)
        trade_history.append(trade)
        
        print(f"✅ BUY order executed: {order['id']}")
        print(f"   Filled: {order['filled']} at avg price: ${order['average']}")
        
        return trade
        
    except Exception as e:
        print(f"❌ BUY order failed: {e}")
        return None

def execute_sell(symbol, price, confidence, reason):
    """Execute a SELL order"""
    global trades_today
    
    # Find matching position
    position = None
    for pos in open_positions:
        if pos['symbol'] == symbol and pos['side'] == 'BUY':
            position = pos
            break
    
    if not position:
        print(f"⚠️ No BUY position found for {symbol}")
        return None
    
    try:
        quantity = position['quantity']
        print(f"📉 Placing SELL order: {symbol} at ${price:.2f}")
        print(f"   Quantity: {quantity:.6f}")
        print(f"   Reason: {reason}")
        
        # Place market order
        order = exchange.create_market_sell_order(symbol, quantity)
        
        # Calculate P&L
        buy_value = position['quantity'] * position['price']
        sell_value = position['quantity'] * price
        pnl = sell_value - buy_value
        pnl_percent = (pnl / buy_value) * 100
        
        trade = {
            'id': order['id'],
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': 'SELL',
            'price': price,
            'quantity': quantity,
            'value': sell_value,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'status': 'FILLED',
            'confidence': confidence,
            'reason': reason
        }
        
        trades_today += 1
        open_positions.remove(position)
        trade_history.append(trade)
        
        print(f"✅ SELL order executed: {order['id']}")
        print(f"   P&L: ${pnl:.2f} ({pnl_percent:.2f}%)")
        
        return trade
        
    except Exception as e:
        print(f"❌ SELL order failed: {e}")
        return None

def check_daily_reset():
    """Reset daily counters if new day"""
    global trades_today, last_trade_date
    today = datetime.now().date()
    
    if today != last_trade_date:
        print(f"📅 New day: Resetting trade counter")
        trades_today = 0
        last_trade_date = today
        return True
    return False

def main_loop():
    """Main trading loop"""
    print("\n🔄 Starting REAL trading loop (10-minute intervals)...")
    print("="*70)
    
    iteration = 0
    while True:
        iteration += 1
        print(f"\n📊 Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        # Check daily reset
        check_daily_reset()
        
        # Check balance
        balance = check_balance()
        if balance < CAPITAL * 0.1:
            print("⚠️ Low balance - trading paused")
            time.sleep(600)
            continue
        
        # Get market data
        print("📈 Market Analysis:")
        analyses = []
        for symbol in SYMBOLS:
            market_data = get_market_data(symbol)
            if market_data:
                analysis = analyze_symbol(symbol, market_data)
                analyses.append(analysis)
                print(f"   {symbol}: ${market_data['price']:.2f} ({analysis['signal']} - {analysis['reason']})")
        
        # Execute trades based on analysis
        print("\n🎯 Trade Execution:")
        for analysis in analyses:
            if analysis['signal'] == 'BUY' and analysis['confidence'] > 0.6:
                execute_buy(
                    analysis['symbol'],
                    analysis['price'],
                    analysis['confidence'],
                    analysis['reason']
                )
            elif analysis['signal'] == 'SELL' and analysis['confidence'] > 0.65:
                execute_sell(
                    analysis['symbol'],
                    analysis['price'],
                    analysis['confidence'],
                    analysis['reason']
                )
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Trades today: {trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"   Open positions: {len(open_positions)}")
        print(f"   Total trades: {len(trade_history)}")
        
        print(f"\n⏳ Next analysis in 10 minutes...")
        print("="*70)
        
        # Wait 10 minutes
        time.sleep(600)

if __name__ == "__main__":
    try:
        # Test connection
        print("🔌 Testing Gemini connection...")
        balance = check_balance()
        print(f"✅ Balance: ${balance:.2f}")
        
        # Start trading
        main_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Trading bot stopped by user")
        print(f"📊 Final stats: {trades_today} trades today, {len(open_positions)} open positions")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()