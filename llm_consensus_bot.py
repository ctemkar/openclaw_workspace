#!/usr/bin/env python3
"""
LLM CONSENSUS TRADING BOT - SIMPLIFIED VERSION
DeepSeek coordinates, queries 4 Ollama models, makes consensus trades
"""

import os
import json
import time
import ccxt
import requests
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "llm_consensus.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration - ALL AVAILABLE MODELS
OLLAMA_MODELS = [
    "glm-4.7-flash:latest",    # Large model, good reasoning
    "llama3.1:latest",         # Balanced model  
    "llama3:latest",           # Reliable model
    "qwen2.5-coder:32b",       # Large coder model
    "qwen3:latest",            # New addition
    "mistral:latest",          # New addition
    "deepseek-r1:latest",      # New addition
    "llama3.1:8b"              # Smaller but fast
]

# Model weights based on performance (will be updated based on accuracy tracking)
MODEL_WEIGHTS = {
    "glm-4.7-flash:latest": 1.2,      # Higher weight for large model
    "llama3.1:latest": 1.0,
    "llama3:latest": 1.0,
    "qwen2.5-coder:32b": 1.1,         # Higher for coder model
    "qwen3:latest": 1.0,              # New - start with neutral
    "mistral:latest": 1.0,            # New - start with neutral
    "deepseek-r1:latest": 1.1,        # Higher for reasoning model
    "llama3.1:8b": 0.9                # Lower for smaller model
}

CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI']
GEMINI_CRYPTOS = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 'MANA', 'COMP']

# UPDATED WITH REAL BALANCES
GEMINI_CAPITAL = 319.04      # Real balance
BINANCE_CAPITAL = 0.00       # Disabled - no balance
POSITION_SIZE = 0.10         # 10% of capital
SCAN_INTERVAL = 600          # 10 minutes

def query_ollama_sync(model, crypto, price, change):
    """Synchronous query to Ollama"""
    prompt = f"""
Analyze {crypto} trading opportunity.
Current: ${price:.2f}, 24h: {change:+.2f}%
Give scores 1-10 for BUY and SELL.
Respond ONLY as JSON: {{"buy":1-10, "sell":1-10, "reason":"brief"}}
"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                analysis = json.loads(result.get('response', '{}'))
                return {
                    'model': model,
                    'buy': analysis.get('buy', 5),
                    'sell': analysis.get('sell', 5),
                    'reason': analysis.get('reason', 'No reason')
                }
            except:
                return {'model': model, 'buy': 5, 'sell': 5, 'reason': 'Parse error'}
        else:
            logger.error(f"❌ {model} failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error querying {model}: {e}")
        return None

def get_llm_consensus(crypto, price, change):
    """Get consensus from all LLMs with weighted voting"""
    logger.info(f"🔍 Getting weighted LLM consensus for {crypto}...")
    
    results = []
    for model in OLLAMA_MODELS:
        result = query_ollama_sync(model, crypto, price, change)
        if result:
            weight = MODEL_WEIGHTS.get(model, 1.0)
            result['weight'] = weight
            results.append(result)
            reason = result.get('reason', 'No reason')
            logger.info(f"  {model.split(':')[0]}: BUY={result['buy']}, SELL={result['sell']} - {reason[:60]}... (weight: {weight})")
    
    if not results:
        return None
    
    # Calculate WEIGHTED averages
    total_weight = sum(r['weight'] for r in results)
    weighted_buy = sum(r['buy'] * r['weight'] for r in results) / total_weight
    weighted_sell = sum(r['sell'] * r['weight'] for r in results) / total_weight
    
    # Track individual model predictions for accuracy analysis
    model_predictions = []
    for r in results:
        model_predictions.append({
            'model': r['model'].split(':')[0],
            'buy': r['buy'],
            'sell': r['sell'],
            'weight': r['weight'],
            'net_score': r['buy'] - r['sell']
        })
    
    consensus = {
        'crypto': crypto,
        'buy_score': round(weighted_buy, 2),
        'sell_score': round(weighted_sell, 2),
        'model_count': len(results),
        'signal': 'NEUTRAL',
        'model_predictions': model_predictions,
        'timestamp': datetime.now().isoformat()
    }
    
    # Determine signal with weighted scores
    net_score = weighted_buy - weighted_sell
    if net_score >= 3.0:
        consensus['signal'] = 'STRONG_BUY'
    elif net_score >= 1.5:
        consensus['signal'] = 'BUY'
    elif net_score <= -3.0:
        consensus['signal'] = 'STRONG_SELL'
    elif net_score <= -1.5:
        consensus['signal'] = 'SELL'
    
    logger.info(f"📊 {crypto} weighted consensus: BUY={weighted_buy:.1f}, SELL={weighted_sell:.1f}, Net={net_score:.1f}, Signal={consensus['signal']}")
    
    # Log top reasons from models
    if results:
        top_buy_reason = max(results, key=lambda x: x['buy']).get('reason', 'No reason')
        top_sell_reason = max(results, key=lambda x: x['sell']).get('reason', 'No reason')
        logger.info(f"   🟢 Top BUY reason: {top_buy_reason[:80]}...")
        logger.info(f"   🔴 Top SELL reason: {top_sell_reason[:80]}...")
    
    # 🧠 CIO DECISION ENGINE - Analyze scores AND comments for contradictions
    try:
        from cio_decision_engine import make_cio_decision
        cio_decision = make_cio_decision(results, consensus)
        consensus['cio_signal'] = cio_decision['cio_signal']
        consensus['cio_confidence'] = cio_decision['confidence']
        consensus['cio_reason'] = cio_decision['reason']
        consensus['contradictions'] = cio_decision['contradictions']
        
        # Use CIO signal if different from automated signal
        if cio_decision['cio_signal'] != consensus['signal']:
            logger.warning(f"   🚨 CIO OVERRIDE: Changing from {consensus['signal']} to {cio_decision['cio_signal']}")
            logger.warning(f"   📝 Reason: {cio_decision['reason']}")
            consensus['signal'] = cio_decision['cio_signal']
    except Exception as e:
        logger.error(f"❌ CIO engine failed: {e}")
        consensus['cio_signal'] = consensus['signal']
        consensus['cio_confidence'] = 5
        consensus['cio_reason'] = f"CIO engine error: {e}"
    
    # Save prediction for accuracy tracking
    save_prediction_for_analysis(consensus, price)
    
    return consensus

def save_prediction_for_analysis(consensus, current_price):
    """Save prediction to track accuracy over time"""
    try:
        prediction_file = os.path.join(BASE_DIR, "llm_predictions_history.json")
        
        # Load existing predictions
        if os.path.exists(prediction_file):
            with open(prediction_file, 'r') as f:
                predictions = json.load(f)
        else:
            predictions = []
        
        # Add new prediction
        prediction_record = {
            'crypto': consensus['crypto'],
            'timestamp': consensus['timestamp'],
            'buy_score': consensus['buy_score'],
            'sell_score': consensus['sell_score'],
            'signal': consensus['signal'],
            'current_price': current_price,
            'model_predictions': consensus['model_predictions']
        }
        
        predictions.append(prediction_record)
        
        # Keep only last 1000 predictions
        if len(predictions) > 1000:
            predictions = predictions[-1000:]
        
        with open(prediction_file, 'w') as f:
            json.dump(predictions, f, indent=2)
            
    except Exception as e:
        logger.error(f"❌ Error saving prediction: {e}")

def analyze_model_accuracy():
    """Analyze which models are most accurate and update weights"""
    try:
        prediction_file = os.path.join(BASE_DIR, "llm_predictions_history.json")
        if not os.path.exists(prediction_file):
            logger.info("📊 No prediction history yet. Will analyze after collecting data.")
            return
        
        with open(prediction_file, 'r') as f:
            predictions = json.load(f)
        
        if len(predictions) < 10:
            logger.info(f"📊 Only {len(predictions)} predictions. Need more data for analysis.")
            return
        
        # TODO: Implement accuracy analysis
        # For now, just log that we have data
        logger.info(f"📊 Have {len(predictions)} predictions for accuracy analysis")
        
    except Exception as e:
        logger.error(f"❌ Error analyzing model accuracy: {e}")

def main():
    """Main loop - DeepSeek coordinates everything"""
    logger.info("=" * 70)
    logger.info("🧠 LLM CONSENSUS TRADING BOT")
    logger.info("🤖 DeepSeek (main) + 4 Ollama models")
    logger.info("=" * 70)
    
    # Load exchanges
    try:
        with open('secure_keys/gemini_keys.json') as f:
            gemini_keys = json.load(f)
        gemini = ccxt.gemini({
            'apiKey': gemini_keys['api_key'],
            'secret': gemini_keys['api_secret']
        })
        logger.info("✅ Gemini loaded")
    except:
        logger.warning("⚠️ Gemini not available")
        gemini = None
    
    try:
        with open('secure_keys/binance_keys.json') as f:
            binance_keys = json.load(f)
        binance = ccxt.binance({
            'apiKey': binance_keys['api_key'],
            'secret': binance_keys['api_secret']
        })
        logger.info("✅ Binance loaded")
    except:
        logger.warning("⚠️ Binance not available")
        binance = None
    
    cycle = 0
    while True:
        cycle += 1
        logger.info(f"\n🔄 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
        
        if not binance:
            logger.error("❌ Need Binance for prices")
            time.sleep(SCAN_INTERVAL)
            continue
        
        # Get prices
        prices = {}
        for crypto in CRYPTOS:
            try:
                ticker = binance.fetch_ticker(f"{crypto}/USDT")
                prices[crypto] = {
                    'price': ticker['last'],
                    'change': ticker.get('percentage', 0)
                }
            except:
                prices[crypto] = None
        
        # Get LLM consensus for each crypto
        consensus_list = []
        for crypto in CRYPTOS:
            if prices.get(crypto):
                consensus = get_llm_consensus(
                    crypto, 
                    prices[crypto]['price'],
                    prices[crypto]['change']
                )
                if consensus:
                    consensus_list.append(consensus)
        
        # Execute trades with LLM trade executor
        logger.info("\n🎯 TRADE DECISIONS:")
        
        # Import trade executor
        try:
            from llm_trade_executor import LLMTradeExecutor
            executor = LLMTradeExecutor()
            logger.info("✅ Trade executor loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load trade executor: {e}")
            executor = None
        
        executed_trades = 0
        for consensus in consensus_list:
            crypto = consensus['crypto']
            signal = consensus['signal']
            
            # Only execute STRONG_BUY and STRONG_SELL signals
            if signal in ["STRONG_BUY", "STRONG_SELL"] and executor:
                price = prices[crypto]['price']
                confidence = abs(consensus['buy_score'] - consensus['sell_score'])
                
                logger.info(f"  {crypto}: {signal} (confidence: {confidence:.1f})")
                
                # Execute trade
                trade = executor.execute_trade(crypto, signal, price, confidence)
                if trade:
                    executed_trades += 1
                    logger.info(f"    ✅ Trade executed: {trade['side'].upper()} {trade['amount']:.4f} {crypto}")
                else:
                    logger.info(f"    ⚠️ Trade not executed (insufficient capital or other issue)")
            else:
                logger.info(f"  {crypto}: {signal} (no trade - signal not strong enough)")
        
        logger.info(f"\n📊 CYCLE SUMMARY: {executed_trades} trades executed")
        
        # Save consensus decisions
        decisions_file = os.path.join(BASE_DIR, "llm_consensus_decisions.json")
        try:
            decisions = []
            if os.path.exists(decisions_file):
                with open(decisions_file, 'r') as f:
                    decisions = json.load(f)
            
            for consensus in consensus_list:
                decision = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': consensus['crypto'],
                    'action': consensus['signal'],
                    'buy_score': consensus['buy_score'],
                    'sell_score': consensus['sell_score'],
                    'executed': consensus['signal'] in ["STRONG_BUY", "STRONG_SELL"]
                }
                decisions.append(decision)
            
            # Keep only last 100 decisions
            decisions = decisions[-100:]
            
            with open(decisions_file, 'w') as f:
                json.dump(decisions, f, indent=2)
                
            logger.info(f"✅ Decisions saved to {decisions_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving decisions: {e}")
            buy_score = consensus['buy_score']
            sell_score = consensus['sell_score']
            
            # Get current price
            if prices.get(crypto):
                price = prices[crypto]['price']
                
                if signal in ['STRONG_BUY', 'BUY']:
                    logger.info(f"  📈 {crypto}: BUY signal ({signal})")
                    if executor:
                        if executor.process_consensus_signal(crypto, signal, price, buy_score, sell_score):
                            executed_trades += 1
                
                elif signal in ['STRONG_SELL', 'SELL']:
                    logger.info(f"  📉 {crypto}: SELL signal ({signal})")
                    if executor:
                        if executor.process_consensus_signal(crypto, signal, price, buy_score, sell_score):
                            executed_trades += 1
        
        if executed_trades > 0:
            logger.info(f"✅ Executed {executed_trades} trades this cycle")
        else:
            logger.info("⏭️ No trades executed (waiting for stronger signals)")
        
        logger.info(f"⏰ Next analysis in {SCAN_INTERVAL//60} minutes...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()