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

# Configuration
OLLAMA_MODELS = ["glm-4.7-flash:latest", "llama3.1:latest", "llama3:latest", "qwen2.5-coder:32b"]
CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI']
GEMINI_CRYPTOS = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 'MANA', 'COMP']

GEMINI_CAPITAL = 434.35
BINANCE_CAPITAL = 36.70
POSITION_SIZE = 0.05
SCAN_INTERVAL = 600  # 10 minutes

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
    """Get consensus from all LLMs"""
    logger.info(f"🔍 Getting LLM consensus for {crypto}...")
    
    results = []
    for model in OLLAMA_MODELS:
        result = query_ollama_sync(model, crypto, price, change)
        if result:
            results.append(result)
            logger.info(f"  {model.split(':')[0]}: BUY={result['buy']}, SELL={result['sell']}")
    
    if not results:
        return None
    
    # Calculate averages
    avg_buy = sum(r['buy'] for r in results) / len(results)
    avg_sell = sum(r['sell'] for r in results) / len(results)
    
    consensus = {
        'crypto': crypto,
        'buy_score': round(avg_buy, 2),
        'sell_score': round(avg_sell, 2),
        'model_count': len(results),
        'signal': 'NEUTRAL'
    }
    
    # Determine signal
    if avg_buy - avg_sell >= 3.0:
        consensus['signal'] = 'STRONG_BUY'
    elif avg_buy - avg_sell >= 1.5:
        consensus['signal'] = 'BUY'
    elif avg_sell - avg_buy >= 3.0:
        consensus['signal'] = 'STRONG_SELL'
    elif avg_sell - avg_buy >= 1.5:
        consensus['signal'] = 'SELL'
    
    logger.info(f"📊 {crypto} consensus: BUY={avg_buy:.1f}, SELL={avg_sell:.1f}, Signal={consensus['signal']}")
    return consensus

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
        
        # Execute trades (simplified - just log for now)
        logger.info("\n🎯 TRADE DECISIONS:")
        for consensus in consensus_list:
            crypto = consensus['crypto']
            signal = consensus['signal']
            
            if signal in ['STRONG_BUY', 'BUY']:
                logger.info(f"  📈 {crypto}: BUY signal ({signal})")
                # Would execute Gemini LONG here
                
            elif signal in ['STRONG_SELL', 'SELL']:
                logger.info(f"  📉 {crypto}: SELL signal ({signal})")
                # Would execute Binance SHORT here
        
        logger.info(f"⏰ Next analysis in {SCAN_INTERVAL//60} minutes...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()