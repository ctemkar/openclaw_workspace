#!/usr/bin/env python3
"""
ENHANCED LLM TRADER - Option B optimized
Real market data + LLM decisions + override logic
"""

import ccxt
import json
import time
import logging
import os
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_llm_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_CAPITAL = 393.22
BINANCE_CAPITAL = 262.14
POSITION_SIZE = 0.1  # 10%
LONG_THRESHOLD = 1.0  # 1% drop for LONG
SHORT_THRESHOLD = 1.0  # 1% drop for SHORT
STOP_LOSS = 0.03  # 3%
TAKE_PROFIT = 0.05  # 5%
SCAN_INTERVAL = 300  # 5 minutes

# LLM Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODELS = ["deepseek-r1", "qwen3", "mistral"]

# Cryptocurrencies to trade
CRYPTOS = ['BTC', 'ETH', 'SOL', 'DOT', 'XRP', 'DOGE', 'LTC', 'UNI', 'LINK', 'AVAX', 'ATOM', 'FIL']

def load_api_keys():
    """Load API keys"""
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
    """Initialize exchanges"""
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

def query_llm_optimized(prompt, model="deepseek-r1"):
    """Optimized LLM query with shorter timeout"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,  # Slightly higher for less conservatism
                "top_p": 0.9,
                "num_predict": 30  # Very short responses
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=3)  # Very short timeout
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '').strip()
            
            # Parse for trading decision
            response_upper = response_text.upper()
            if 'LONG' in response_upper or 'BUY' in response_upper:
                return "LONG"
            elif 'SHORT' in response_upper or 'SELL' in response_upper:
                return "SHORT"
            else:
                return "HOLD"
                
        return "HOLD"
    except:
        return None  # Timeout or error

def calculate_24h_change(exchange, symbol):
    """Calculate 24h price change"""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=24)
        if ohlcv and len(ohlcv) >= 24:
            open_24h = ohlcv[0][1]
            current = ohlcv[-1][4]
            
            if open_24h > 0:
                change = ((current - open_24h) / open_24h) * 100
                return change, current, ohlcv[0][2], ohlcv[0][3], ohlcv[-1][5]
    except Exception as e:
        logger.debug(f"Could not calculate 24h change for {symbol}: {e}")
    
    return None, None, None, None, None

def get_llm_decision_aggressive(crypto, price_data):
    """Get LLM decision with aggressive prompt"""
    prompt = f"""Trading {crypto}:
Price dropped {abs(price_data['change']):.1f}% in 24h.
Current: ${price_data['current']:.2f}
Market is down significantly.
Should we buy the dip? Answer: LONG or HOLD"""
    
    return query_llm_optimized(prompt)

def check_gemini_opportunity(exchange, crypto):
    """Check Gemini opportunity with LLM"""
    try:
        symbol = f"{crypto}/USD"
        
        # Get price data
        change_24h, current_price, high_24h, low_24h, volume = calculate_24h_change(exchange, symbol)
        if change_24h is None:
            return None
        
        # Rule-based signal
        rule_signal = "LONG" if change_24h <= -LONG_THRESHOLD else None
        
        if rule_signal:
            # Get LLM decision
            price_data = {
                'current': current_price,
                'change': change_24h,
                'high': high_24h,
                'low': low_24h,
                'volume': volume
            }
            
            llm_decision = get_llm_decision_aggressive(crypto, price_data)
            drop_magnitude = abs(change_24h)
            
            # Decision logic with overrides
            if llm_decision == "LONG":
                logger.info(f"✅ LLM CONFIRMED: {crypto} - Rule + LLM agree on LONG")
                confidence = "HIGH"
                position_multiplier = 1.0
            elif llm_decision is None:  # LLM timeout
                logger.info(f"⚠️ LLM TIMEOUT: {crypto} - Rule says LONG, LLM timeout")
                confidence = "MEDIUM"
                position_multiplier = 0.75
            elif llm_decision == "HOLD":
                # Check if drop is big enough to override
                if drop_magnitude >= 2.5:  # Override for >2.5% drops
                    logger.info(f"🎯 OVERRIDE: {crypto} - Big drop ({drop_magnitude:.1f}%), overriding LLM HOLD")
                    confidence = "OVERRIDE"
                    position_multiplier = 0.5
                else:
                    logger.info(f"⚠️ LLM REJECTED: {crypto} - LLM says HOLD (small drop)")
                    return None
            else:
                logger.info(f"⚠️ UNKNOWN: {crypto} - LLM says {llm_decision}")
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
                'timestamp': datetime.now().isoformat()
            }
            
            return trade_data
            
    except Exception as e:
        logger.error(f"Error checking {crypto}: {e}")
    
    return None

def check_binance_opportunity(exchange, crypto):
    """Check Binance opportunity with LLM"""
    try:
        # Check balance
        balance = exchange.fetch_balance()
        usdt_balance = balance['free'].get('USDT', 0)
        
        if usdt_balance < 10:
            logger.debug(f"Low Binance balance: ${usdt_balance:.2f}")
            return None
        
        symbol = f"{crypto}/USDT"
        
        # Get price data
        change_24h, current_price, high_24h, low_24h, volume = calculate_24h_change(exchange, symbol)
        if change_24h is None:
            return None
        
        # Rule-based signal
        rule_signal = "SHORT" if change_24h <= -SHORT_THRESHOLD else None
        
        if rule_signal:
            # Get LLM decision
            price_data = {
                'current': current_price,
                'change': change_24h,
                'high': high_24h,
                'low': low_24h,
                'volume': volume
            }
            
            llm_decision = get_llm_decision_aggressive(crypto, price_data)
            drop_magnitude = abs(change_24h)
            
            # Similar logic as Gemini
            if llm_decision == "SHORT":
                confidence = "HIGH"
                position_multiplier = 1.0
            elif llm_decision is None:
                confidence = "MEDIUM"
                position_multiplier = 0.75
            elif llm_decision == "HOLD" and drop_magnitude >= 2.5:
                confidence = "OVERRIDE"
                position_multiplier = 0.5
            else:
                return None
            
            # Calculate position
            position_value = BINANCE_CAPITAL * POSITION_SIZE * position_multiplier
            amount = position_value / current_price
            
            trade_data = {
                'exchange': 'binance',
                'symbol': f"{symbol}:USDT",
                'side': 'sell',
                'type': f'SHORT_{confidence}',
                'current_price': current_price,
                'change_24h': change_24h,
                'amount': amount,
                'position_value': position_value,
                'stop_loss': current_price * (1 + STOP_LOSS),
                'take_profit': current_price * (1 - TAKE_PROFIT),
                'llm_decision': llm_decision or 'TIMEOUT',
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
            return trade_data
            
    except Exception as e:
        logger.error(f"Error checking Binance {crypto}: {e}")
    
    return None

def execute_trade_simulated(trade_data):
    """Execute trade (simulated for safety)"""
    logger.info(f"🎯 SIMULATED TRADE: {trade_data['exchange']} {trade_data['symbol']}")
    logger.info(f"   Side: {trade_data['side']}, Amount: {trade_data['amount']:.6f}")
    logger.info(f"   Value: ${trade_data['position_value']:.2f}")
    logger.info(f"   Confidence: {trade_data['confidence']}")
    logger.info(f"   LLM: {trade_data['llm_decision']}")
    
    # Save to history
    save_trade_history(trade_data)
    
    return True

def save_trade_history(trade_data):
    """Save trade to history"""
    try:
        history_file = 'enhanced_llm_trades.json'
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(trade_data)
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving trade history: {e}")

def trading_cycle(exchanges, cycle_count):
    """Main trading cycle"""
    gemini, binance = exchanges
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🔄 ENHANCED LLM TRADING CYCLE #{cycle_count}")
    logger.info(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    logger.info(f"{'='*70}")
    
    opportunities = []
    
    # Check Gemini
    logger.info("🔍 Checking Gemini opportunities...")
    for crypto in CRYPTOS:
        opportunity = check_gemini_opportunity(gemini, crypto)
        if opportunity:
            opportunities.append(opportunity)
    
    # Check Binance
    logger.info("🔍 Checking Binance opportunities...")
    for crypto in CRYPTOS:
        opportunity = check_binance_opportunity(binance, crypto)
        if opportunity:
            opportunities.append(opportunity)
    
    # Execute trades
    executed = 0
    for trade in opportunities:
        if execute_trade_simulated(trade):
            executed += 1
    
    logger.info(f"\n📊 CYCLE SUMMARY:")
    logger.info(f"   Opportunities found: {len(opportunities)}")
    logger.info(f"   Trades executed: {executed}")
    logger.info(f"{'='*70}")
    
    return executed

def main():
    """Main function"""
    logger.info("="*70)
    logger.info("🚀 ENHANCED LLM TRADER - OPTION B OPTIMIZED")
    logger.info("="*70)
    logger.info("🤖 Real market data + LLM decisions + override logic")
    logger.info(f"💰 Capital: Gemini ${GEMINI_CAPITAL:.2f}, Binance ${BINANCE_CAPITAL:.2f}")
    logger.info(f"🎯 Position: {POSITION_SIZE*100:.0f}%, Threshold: {LONG_THRESHOLD}% drop")
    logger.info(f"🛑 Stop-loss: {STOP_LOSS*100:.0f}%, ✅ Take-profit: {TAKE_PROFIT*100:.0f}%")
    logger.info(f"🧠 LLM Models: {', '.join(LLM_MODELS)}")
    logger.info(f"⏰ Interval: {SCAN_INTERVAL} seconds")
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
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            available = [m['name'] for m in models]
            logger.info(f"✅ Ollama available ({len(available)} models)")
        else:
            logger.warning("⚠️ Ollama not responding")
    except:
        logger.warning("⚠️ Cannot connect to Ollama")
    
    # Main loop
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
                
                logger.info(f"📈 TOTAL TRADES: {total_trades}")
                logger.info(f"⏰ Next cycle in {SCAN_INTERVAL} seconds...\n")
                
                time.sleep(SCAN_INTERVAL)
                cycle_count += 1
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                time.sleep(60)
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    
    logger.info("="*70)
    logger.info("🤖 ENHANCED LLM TRADER STOPPED")
    logger.info(f"📊 Cycles: {cycle_count}, Trades: {total_trades}")
    logger.info("="*70)

if __name__ == '__main__':
    main()