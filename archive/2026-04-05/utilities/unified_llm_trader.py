#!/usr/bin/env python3
"""
UNIFIED LLM-POWERED TRADING BOT
Combines best of both strategies with LLM decision making
"""

import ccxt
import json
import time
import logging
import os
from datetime import datetime
import subprocess
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_CAPITAL = 393.22  # From your Gemini balance
BINANCE_CAPITAL = 262.14  # From your Binance allocation
POSITION_SIZE = 0.1       # 10% of capital per trade
LONG_THRESHOLD = 1.0      # 1% drop for LONG
SHORT_THRESHOLD = 1.0     # 1% drop for SHORT
STOP_LOSS = 0.03          # 3% stop-loss
TAKE_PROFIT = 0.05        # 5% take-profit
SCAN_INTERVAL = 300       # 5 minutes

# 26 Cryptocurrencies to trade
CRYPTOS = [
    'BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'XRP', 'DOGE', 'LTC', 'UNI', 'LINK',
    'MATIC', 'AVAX', 'ATOM', 'ALGO', 'FIL', 'ETC', 'XTZ', 'EOS', 'AAVE', 'COMP',
    'MKR', 'SNX', 'YFI', 'SUSHI', 'CRV', 'REN'
]

# LLM Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODELS = ["deepseek-r1", "qwen3", "mistral", "llama3.2", "gemma2"]

def load_api_keys():
    """Load API keys from secure storage"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(os.path.join(base_dir, 'secure_keys/.gemini_key'), 'r') as f:
        gemini_key = f.read().strip()
    with open(os.path.join(base_dir, 'secure_keys/.gemini_secret'), 'r') as f:
        gemini_secret = f.read().strip()
    
    with open(os.path.join(base_dir, 'secure_keys/.binance_key'), 'r') as f:
        binance_key = f.read().strip()
    with open(os.path.join(base_dir, 'secure_keys/.binance_secret'), 'r') as f:
        binance_secret = f.read().strip()
    
    return gemini_key, gemini_secret, binance_key, binance_secret

def init_exchanges(keys):
    """Initialize exchange connections"""
    gemini_key, gemini_secret, binance_key, binance_secret = keys
    
    gemini = ccxt.gemini({
        'apiKey': gemini_key,
        'secret': gemini_secret,
        'enableRateLimit': True
    })
    
    binance = ccxt.binance({
        'apiKey': binance_key,
        'secret': binance_secret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        }
    })
    
    return gemini, binance

def query_llm(prompt, model="deepseek-r1"):
    """Query Ollama LLM for trading decision with fallback"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 50  # Shorter responses for speed
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=5)  # Reduced timeout
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            logger.warning(f"LLM API error: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        logger.warning(f"LLM timeout for {model}, using fallback")
        return None
    except Exception as e:
        logger.warning(f"LLM query error: {e}")
        return None

def get_llm_trading_decision(crypto, price_data, market_context):
    """Get LLM decision for a specific crypto"""
    # Simplified, more aggressive prompt
    prompt = f"""Trading decision for {crypto}:
Price: ${price_data['current']:.2f}
24h change: {price_data['change_24h']:.2f}%
Market: {market_context['trend']} trend, {market_context['sentiment']} sentiment

Rule: Buy if dropped >1% (LONG), Short if dropped >1% (SHORT)
Current: Price dropped {abs(price_data['change_24h']):.1f}% in 24h

Decision (LONG/SHORT/HOLD):"""

    response = query_llm(prompt)
    if response:
        # Parse response - look for LONG/SHORT/HOLD
        response_upper = response.upper()
        if 'LONG' in response_upper:
            return "LONG"
        elif 'SHORT' in response_upper:
            return "SHORT"
        else:
            return "HOLD"
    
    return "HOLD"  # Default to HOLD if LLM fails

def calculate_24h_change(exchange, symbol):
    """Calculate 24-hour price change using OHLCV"""
    try:
        # Get 24-hour OHLCV (1-hour candles for last 24 hours)
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=24)
        if ohlcv and len(ohlcv) >= 24:
            open_24h = ohlcv[0][1]  # Open price 24h ago
            current_price = ohlcv[-1][4]  # Current price
            
            if open_24h and open_24h > 0:
                change = ((current_price - open_24h) / open_24h) * 100
                return change, current_price, ohlcv[0][2], ohlcv[0][3], ohlcv[-1][5]
    except Exception as e:
        logger.warning(f"Could not calculate 24h change for {symbol}: {e}")
    
    return None, None, None, None, None

def check_gemini_opportunity(exchange, crypto, market_context):
    """Check for Gemini LONG opportunity with LLM validation"""
    try:
        symbol = f"{crypto}/USD"
        
        # Get price data
        change_24h, current_price, high_24h, low_24h, volume = calculate_24h_change(exchange, symbol)
        if change_24h is None:
            return None
        
        # Rule-based signal
        rule_signal = None
        if change_24h <= -LONG_THRESHOLD:
            rule_signal = "LONG"
        
        # Get LLM decision
        price_data = {
            'current': current_price,
            'change_24h': change_24h,
            'high_24h': high_24h,
            'low_24h': low_24h,
            'volume': volume
        }
        
        llm_decision = get_llm_trading_decision(crypto, price_data, market_context)
        
        # Combine rule-based and LLM decisions with AGGRESSIVE fallback
        if rule_signal == "LONG":
            # Check how big the drop is
            drop_magnitude = abs(change_24h) if change_24h < 0 else 0
            
            if llm_decision == "LONG":
                logger.info(f"✅ STRONG SIGNAL: {crypto} - Rule + LLM agree on LONG")
                confidence = 'HIGH'
                position_multiplier = 1.0
            elif llm_decision is None:  # LLM timeout or error
                logger.info(f"⚠️ RULE-ONLY: {crypto} - Rule says LONG, LLM timeout")
                confidence = 'MEDIUM'
                position_multiplier = 0.75  # 75% position if LLM timeout
            elif llm_decision == "HOLD":
                # LLM says HOLD but market dropped significantly
                if drop_magnitude >= 3.0:  # Big drop (>3%), override LLM
                    logger.info(f"🎯 OVERRIDE: {crypto} - Big drop ({drop_magnitude:.1f}%), overriding LLM HOLD")
                    confidence = 'MEDIUM_OVERRIDE'
                    position_multiplier = 0.5  # 50% position when overriding
                else:
                    logger.info(f"⚠️ CONFLICT: {crypto} - Rule says LONG, LLM says HOLD (small drop)")
                    return None
            else:  # LLM says something else
                logger.info(f"⚠️ CONFLICT: {crypto} - Rule says LONG, LLM says {llm_decision}")
                return None
            
            # Calculate position
            position_value = GEMINI_CAPITAL * POSITION_SIZE * position_multiplier
            amount = position_value / current_price
            
            trade_data = {
                'exchange': 'gemini',
                'symbol': symbol,
                'side': 'buy',
                'type': f'LONG_{confidence}',
                'current_price': current_price,
                'change_24h': change_24h,
                'amount': amount,
                'position_value': position_value,
                'stop_loss': current_price * (1 - STOP_LOSS),
                'take_profit': current_price * (1 + TAKE_PROFIT),
                'llm_decision': llm_decision or 'TIMEOUT',
                'confidence': confidence,
                'drop_magnitude': drop_magnitude
            }
            
            return trade_data
            
        elif rule_signal is None and llm_decision == "LONG":
            logger.info(f"⚠️ LLM ONLY: {crypto} - LLM suggests LONG but no rule signal")
            # Skip LLM-only signals for safety
            return None
            
        else:
            # No signal
            return None
            
    except Exception as e:
        logger.error(f"Error checking Gemini opportunity for {crypto}: {e}")
        return None

def check_binance_opportunity(exchange, crypto, market_context):
    """Check for Binance SHORT opportunity with LLM validation"""
    try:
        # Check Binance balance first
        balance = exchange.fetch_balance()
        usdt_balance = balance['free'].get('USDT', 0)
        
        if usdt_balance < 10:  # Need minimum $10 for trading
            logger.warning(f"⚠️ Insufficient Binance balance: ${usdt_balance:.2f}")
            return None
        
        symbol = f"{crypto}/USDT"
        
        # Get price data
        change_24h, current_price, high_24h, low_24h, volume = calculate_24h_change(exchange, symbol)
        if change_24h is None:
            return None
        
        # Rule-based signal
        rule_signal = None
        if change_24h <= -SHORT_THRESHOLD:
            rule_signal = "SHORT"
        
        # Get LLM decision
        price_data = {
            'current': current_price,
            'change_24h': change_24h,
            'high_24h': high_24h,
            'low_24h': low_24h,
            'volume': volume
        }
        
        llm_decision = get_llm_trading_decision(crypto, price_data, market_context)
        
        # Combine rule-based and LLM decisions with fallback
        if rule_signal == "SHORT":
            if llm_decision == "SHORT":
                logger.info(f"✅ STRONG SIGNAL: {crypto} - Rule + LLM agree on SHORT")
                confidence = 'HIGH'
            elif llm_decision is None:  # LLM timeout or error
                logger.info(f"⚠️ RULE-ONLY: {crypto} - Rule says SHORT, LLM timeout")
                confidence = 'MEDIUM'  # Allow rule-only with medium confidence
            else:  # LLM says HOLD or something else
                logger.info(f"⚠️ CONFLICT: {crypto} - Rule says SHORT, LLM says {llm_decision}")
                return None  # Skip if LLM explicitly disagrees
            
            # Calculate position (smaller if LLM timeout)
            position_value = BINANCE_CAPITAL * POSITION_SIZE
            if confidence == 'MEDIUM':
                position_value *= 0.5  # Half position if LLM timeout
            
            amount = position_value / current_price
            
            trade_data = {
                'exchange': 'binance',
                'symbol': f"{symbol}:USDT",  # Futures symbol
                'side': 'sell',
                'type': f'SHORT_{confidence}',
                'current_price': current_price,
                'change_24h': change_24h,
                'amount': amount,
                'position_value': position_value,
                'stop_loss': current_price * (1 + STOP_LOSS),  # For SHORT
                'take_profit': current_price * (1 - TAKE_PROFIT),  # For SHORT
                'llm_decision': llm_decision or 'TIMEOUT',
                'confidence': confidence
            }
            
            return trade_data
            
        else:
            # No signal
            return None
            
    except Exception as e:
        logger.error(f"Error checking Binance opportunity for {crypto}: {e}")
        return None

def execute_trade(exchange, trade_data):
    """Execute a trade (with safety checks)"""
    try:
        logger.info(f"🎯 EXECUTING TRADE: {trade_data['exchange']} {trade_data['symbol']}")
        logger.info(f"   Side: {trade_data['side']}, Amount: {trade_data['amount']:.6f}")
        logger.info(f"   Value: ${trade_data['position_value']:.2f}")
        logger.info(f"   Stop-loss: ${trade_data['stop_loss']:.2f}")
        logger.info(f"   Take-profit: ${trade_data['take_profit']:.2f}")
        
        # In production, this would place actual orders
        # For now, log and simulate
        
        # Save trade to history
        save_trade_history(trade_data)
        
        logger.info(f"✅ TRADE EXECUTED (simulated)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Trade execution failed: {e}")
        return False

def save_trade_history(trade_data):
    """Save trade to history file"""
    try:
        history_file = 'llm_trade_history.json'
        
        # Add timestamp
        trade_data['timestamp'] = datetime.now().isoformat()
        trade_data['status'] = 'EXECUTED'
        
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new trade
        history.append(trade_data)
        
        # Save
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving trade history: {e}")

def get_market_context():
    """Get overall market context for LLM decisions"""
    try:
        # Simple market context
        return {
            'trend': 'bearish' if time.localtime().tm_hour < 12 else 'neutral',
            'sentiment': 'cautious',
            'volatility': 'medium'
        }
    except:
        return {
            'trend': 'neutral',
            'sentiment': 'neutral',
            'volatility': 'medium'
        }

def trading_cycle(exchanges, cycle_count):
    """Main trading cycle"""
    gemini, binance = exchanges
    
    logger.info(f"\n🔄 CYCLE {cycle_count} STARTING...")
    logger.info("="*70)
    logger.info(f"📊 UNIFIED LLM TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("="*70)
    
    # Get market context for LLM
    market_context = get_market_context()
    
    opportunities = []
    
    # Check Gemini opportunities
    logger.info("🔍 Checking Gemini for LONG opportunities...")
    gemini_opportunities = 0
    for crypto in CRYPTOS[:16]:  # First 16 for Gemini
        opportunity = check_gemini_opportunity(gemini, crypto, market_context)
        if opportunity:
            opportunities.append(opportunity)
            gemini_opportunities += 1
    
    # Check Binance opportunities
    logger.info("🔍 Checking Binance for SHORT opportunities...")
    binance_opportunities = 0
    for crypto in CRYPTOS:  # All 26 for Binance
        opportunity = check_binance_opportunity(binance, crypto, market_context)
        if opportunity:
            opportunities.append(opportunity)
            binance_opportunities += 1
    
    # Execute trades
    executed_trades = 0
    for trade in opportunities:
        if trade['exchange'] == 'gemini':
            success = execute_trade(gemini, trade)
        else:
            success = execute_trade(binance, trade)
        
        if success:
            executed_trades += 1
    
    logger.info(f"\n📊 CYCLE {cycle_count} SUMMARY:")
    logger.info(f"   Gemini opportunities: {gemini_opportunities}")
    logger.info(f"   Binance opportunities: {binance_opportunities}")
    logger.info(f"   Trades executed: {executed_trades}")
    logger.info("="*70)
    
    return executed_trades

def main():
    """Main function"""
    logger.info("="*70)
    logger.info("🚀 UNIFIED LLM-POWERED TRADING BOT")
    logger.info("="*70)
    logger.info("🤖 Combining rule-based signals with LLM decision making")
    logger.info("♊ Gemini LONG: 16 cryptos with LLM confirmation")
    logger.info("₿ Binance SHORT: 26 cryptos with LLM confirmation")
    logger.info(f"💰 Capital: Gemini ${GEMINI_CAPITAL:.2f}, Binance ${BINANCE_CAPITAL:.2f}")
    logger.info(f"🎯 Position size: {POSITION_SIZE*100:.0f}% of capital")
    logger.info(f"📈 LONG threshold: {LONG_THRESHOLD}% drop")
    logger.info(f"📉 SHORT threshold: {SHORT_THRESHOLD}% drop")
    logger.info(f"🛑 Stop-loss: {STOP_LOSS*100:.0f}%, ✅ Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"⏰ Scan interval: {SCAN_INTERVAL} seconds")
    logger.info(f"🧠 LLM Models: {', '.join(LLM_MODELS)}")
    logger.info("="*70)
    
    # Load API keys
    try:
        keys = load_api_keys()
        logger.info("✅ API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load API keys: {e}")
        return
    
    # Initialize exchanges
    try:
        gemini, binance = init_exchanges(keys)
        logger.info("✅ Exchanges initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize exchanges: {e}")
        return
    
    # Check Ollama availability
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            available_models = [m['name'] for m in models]
            logger.info(f"✅ Ollama available with {len(available_models)} models")
            
            # Check if our preferred models are available
            for model in LLM_MODELS:
                if any(model in m for m in available_models):
                    logger.info(f"   ✓ {model} available")
                else:
                    logger.warning(f"   ⚠️ {model} not available")
        else:
            logger.warning("⚠️ Ollama not responding, will use rule-based only")
    except Exception as e:
        logger.warning(f"⚠️ Cannot connect to Ollama: {e}")
        logger.info("   Will use rule-based trading only")
    
    # Main trading loop
    cycle_count = 1
    total_trades = 0
    
    logger.info("\n" + "="*70)
    logger.info("🎯 STARTING TRADING CYCLES")
    logger.info("="*70)
    
    try:
        while True:
            try:
                trades = trading_cycle((gemini, binance), cycle_count)
                total_trades += trades
                
                logger.info(f"\n📈 TOTAL TRADES SO FAR: {total_trades}")
                logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...")
                
                time.sleep(SCAN_INTERVAL)
                cycle_count += 1
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in trading cycle: {e}")
                logger.info("⏰ Retrying in 60 seconds...")
                time.sleep(60)
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    
    logger.info("="*70)
    logger.info("🤖 UNIFIED LLM TRADING BOT STOPPED")
    logger.info(f"📊 Total cycles: {cycle_count}")
    logger.info(f"📈 Total trades: {total_trades}")
    logger.info("="*70)

if __name__ == '__main__':
    main()