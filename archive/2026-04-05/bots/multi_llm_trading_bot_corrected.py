#!/usr/bin/env python3
"""
MULTI-LLM VOTING TRADING SYSTEM
DeepSeek (main) + 4 Ollama LLMs consensus trading
"""

import os
import json
import time
import ccxt
import requests
import asyncio
import aiohttp
from datetime import datetime
import logging
import sys
from typing import List, Dict, Tuple

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
log_file = os.path.join(BASE_DIR, "multi_llm_trading.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Trading parameters
GEMINI_CAPITAL = 434.35  # Gemini cash balance
BINANCE_CAPITAL = 36.70  # Binance Futures capital
POSITION_SIZE = 0.05     # 5% of capital
SCAN_INTERVAL = 600      # 10 minute intervals (LLMs need time)

# Ollama models to query (4 different perspectives)
OLLAMA_MODELS = [
    "glm-4.7-flash:latest",    # Chinese model, good at analysis
    "llama3.1:latest",         # Meta's latest, balanced
    "llama3:latest",           # Previous version, conservative
    "qwen2.5-coder:32b"        # Coding/technical focus
]

# Cryptos to analyze (top 10 by market cap + some alts)
CRYPTOS_TO_ANALYZE = [
    'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 
    'DOT', 'DOGE', 'AVAX', 'LINK', 'UNI'
]

# Gemini available cryptos
GEMINI_CRYPTOS = ['BTC', 'ETH', 'LTC', 'BCH', 'ZEC', 'FIL', 'BAT', 'LINK', 'MANA', 'COMP']

def load_api_keys():
    """Load exchange API keys"""
    keys = {}
    try:
        with open('secure_keys/gemini_keys.json', 'r') as f:
            keys['gemini'] = json.load(f)
        logger.info("✅ Gemini API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Gemini keys: {e}")
        keys['gemini'] = None
    
    try:
        with open('secure_keys/binance_keys.json', 'r') as f:
            keys['binance'] = json.load(f)
        logger.info("✅ Binance API keys loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load Binance keys: {e}")
        keys['binance'] = None
    
    return keys

def initialize_exchanges(keys):
    """Initialize exchange connections"""
    exchanges = {}
    
    if keys['gemini']:
        try:
            exchanges['gemini'] = ccxt.gemini({
                'apiKey': keys['gemini']['api_key'],
                'secret': keys['gemini']['api_secret'],
                'enableRateLimit': True,
            })
            logger.info("✅ Gemini exchange initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            exchanges['gemini'] = None
    
    if keys['binance']:
        try:
            exchanges['binance'] = ccxt.binance({
                'apiKey': keys['binance']['api_key'],
                'secret': keys['binance']['api_secret'],
                'enableRateLimit': True,
            })
            logger.info("✅ Binance exchange initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Binance: {e}")
            exchanges['binance'] = None
    
    return exchanges

async def query_ollama_model(model: str, crypto: str, current_price: float, change_24h: float) -> Dict:
    """
    Query a single Ollama model for crypto analysis
    Returns: {'buy_score': 1-10, 'sell_score': 1-10, 'reason': str, 'confidence': 1-10}
    """
    prompt = f"""
Analyze {crypto} (current price: ${current_price:.2f}, 24h change: {change_24h:+.2f}%).
Provide your trading recommendation with scores:

1. BUY score (1-10): How strongly do you recommend BUYING? (1=avoid, 10=strong buy)
2. SELL score (1-10): How strongly do you recommend SELLING/SHORTING? (1=avoid, 10=strong sell)
3. Reason: Brief explanation of your analysis
4. Confidence (1-10): How confident are you in this analysis?

Respond in JSON format only:
{{
    "buy_score": <number>,
    "sell_score": <number>, 
    "reason": "<explanation>",
    "confidence": <number>
}}
"""
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            async with session.post('http://localhost:11434/api/generate', 
                                   json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get('response', '{}')
                    
                    # Parse JSON response
                    try:
                        analysis = json.loads(response_text)
                        return {
                            'model': model,
                            'crypto': crypto,
                            'buy_score': analysis.get('buy_score', 5),
                            'sell_score': analysis.get('sell_score', 5),
                            'reason': analysis.get('reason', 'No reason provided'),
                            'confidence': analysis.get('confidence', 5)
                        }
                    except json.JSONDecodeError:
                        logger.warning(f"❌ {model} returned invalid JSON for {crypto}")
                        return {
                            'model': model,
                            'crypto': crypto,
                            'buy_score': 5,
                            'sell_score': 5,
                            'reason': 'Invalid response format',
                            'confidence': 3
                        }
                else:
                    logger.error(f"❌ {model} query failed: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"❌ Error querying {model} for {crypto}: {e}")
        return None

async def get_llm_consensus(crypto: str, current_price: float, change_24h: float) -> Dict:
    """
    Get consensus from all Ollama models for a crypto
    """
    logger.info(f"🔍 Getting LLM consensus for {crypto}...")
    
    tasks = []
    for model in OLLAMA_MODELS:
        task = query_ollama_model(model, crypto, current_price, change_24h)
        tasks.append(task)
    
    # Run all queries concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter valid results
    valid_results = []
    for result in results:
        if isinstance(result, dict) and result:
            valid_results.append(result)
        elif isinstance(result, Exception):
            logger.error(f"❌ Query error: {result}")
    
    if not valid_results:
        logger.warning(f"⚠️ No valid LLM responses for {crypto}")
        return None
    
    # Calculate consensus
    total_buy = 0
    total_sell = 0
    total_confidence = 0
    reasons = []
    
    for result in valid_results:
        # Weight by confidence
        weight = result['confidence'] / 10.0
        total_buy += result['buy_score'] * weight
        total_sell += result['sell_score'] * weight
        total_confidence += result['confidence']
        reasons.append(f"{result['model'].split(':')[0]}: {result['reason']}")
    
    avg_buy = total_buy / len(valid_results)
    avg_sell = total_sell / len(valid_results)
    avg_confidence = total_confidence / len(valid_results)
    
    consensus = {
        'crypto': crypto,
        'buy_score': round(avg_buy, 2),
        'sell_score': round(avg_sell, 2),
        'confidence': round(avg_confidence, 2),
        'model_count': len(valid_results),
        'reasons': reasons,
        'signal': 'NEUTRAL'
    }
    
    # Determine signal
    if avg_buy - avg_sell >= 3.0:  # Strong buy signal
        consensus['signal'] = 'STRONG_BUY'
    elif avg_buy - avg_sell >= 1.5:  # Moderate buy
        consensus['signal'] = 'BUY'
    elif avg_sell - avg_buy >= 3.0:  # Strong sell
        consensus['signal'] = 'STRONG_SELL'
    elif avg_sell - avg_buy >= 1.5:  # Moderate sell
        consensus['signal'] = 'SELL'
    
    logger.info(f"📊 {crypto} consensus: BUY={avg_buy:.2f}, SELL={avg_sell:.2f}, Signal={consensus['signal']}")
    
    return consensus

def get_current_prices(exchange, cryptos: List[str]) -> Dict:
    """Get current prices for multiple cryptos"""
    prices = {}
    
    for crypto in cryptos:
        try:
            symbol = f"{crypto}/USDT" if exchange.id == 'binance' else f"{crypto}/USD"
            ticker = exchange.fetch_ticker(symbol)
            
            prices[crypto] = {
                'price': ticker['last'],
                'change_24h': ticker.get('percentage', 0),
                'high_24h': ticker.get('high'),
                'low_24h': ticker.get('low')
            }
        except Exception as e:
            logger.error(f"❌ Error getting price for {crypto}: {e}")
            prices[crypto] = None
    
    return prices

def execute_gemini_trade(exchange, crypto: str, consensus: Dict):
    """Execute Gemini LONG trade based on LLM consensus"""
    try:
        symbol = f"{crypto}/USD"
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Calculate position size based on confidence
        confidence_factor = consensus['confidence'] / 10.0  # 0.3 to 1.0
        position_value = GEMINI_CAPITAL * POSITION_SIZE * confidence_factor
        amount = position_value / current_price
        
        logger.info(f"🚀 EXECUTING GEMINI LONG: {crypto}")
        logger.info(f"    LLM Consensus: BUY={consensus['buy_score']}, Signal={consensus['signal']}")
        logger.info(f"    Confidence: {consensus['confidence']}/10")
        logger.info(f"    Position: {amount:.6f} {crypto} (${position_value:.2f})")
        
        # Place buy order
        order = exchange.create_order(
            symbol=symbol,
            type='limit', price=trade_data['price'],
            side='buy',
            amount=amount
        )
        
        logger.info(f"✅ Gemini LONG order executed: {order['id']}")
        
        # Save trade with LLM consensus data
        trade_data = {
            'exchange': 'gemini',
            'symbol': symbol,
            'side': 'buy',
            'type': 'LONG_LLM',
            'price': current_price,
            'amount': amount,
            'position_value': position_value,
            'llm_consensus': consensus,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat()
        }
        
        save_trade(trade_data)
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Gemini LONG execution failed: {e}")
        return None

def execute_binance_trade(exchange, crypto: str, consensus: Dict):
    """Execute Binance trade based on LLM consensus (spot for now)"""
    try:
        symbol = f"{crypto}/USDT"
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Determine side based on signal
        if consensus['signal'] in ['SELL', 'STRONG_SELL']:
            side = 'sell'
            trade_type = 'SHORT_LLM'
        else:
            side = 'buy'
            trade_type = 'LONG_LLM'
        
        # Calculate position size
        confidence_factor = consensus['confidence'] / 10.0
        position_value = BINANCE_CAPITAL * POSITION_SIZE * confidence_factor
        amount = position_value / current_price
        
        logger.info(f"🚀 EXECUTING BINANCE {side.upper()}: {crypto}")
        logger.info(f"    LLM Consensus: BUY={consensus['buy_score']}, SELL={consensus['sell_score']}")
        logger.info(f"    Signal: {consensus['signal']}, Confidence: {consensus['confidence']}/10")
        logger.info(f"    Position: {amount:.6f} {crypto} (${position_value:.2f})")
        
        # Check minimum order size
        min_notional = 10.0  # Binance spot minimum
        if position_value < min_notional:
            logger.warning(f"⚠️ Position ${position_value:.2f} < minimum ${min_notional}")
            amount = min_notional / current_price
            position_value = min_notional
        
        # Place order
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side=side,
            amount=amount
        )
        
        logger.info(f"✅ Binance {side.upper()} order executed: {order['id']}")
        
        trade_data = {
            'exchange': 'binance',
            'symbol': symbol,
            'side': side,
            'type': trade_type,
            'price': current_price,
            'amount': amount,
            'position_value': position_value,
            'llm_consensus': consensus,
            'order_id': order['id'],
            'timestamp': datetime.now().isoformat()
        }
        
        save_trade(trade_data)
        return trade_data
        
    except Exception as e:
        logger.error(f"❌ Binance trade execution failed: {e}")
        return None

def save_trade(trade_data):
    """Save trade to history"""
    try:
        history_file = os.path.join(BASE_DIR, 'trading_data', 'llm_trades.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(trade_data)
        
        if len(history) > 100:
            history = history[-100:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"📝 LLM trade saved: {trade_data['symbol']} {trade_data['side']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save trade: {e}")

async def trading_cycle(exchanges):
    """One trading cycle - get LLM consensus and trade"""
    logger.info("=" * 70)
    logger.info(f"🧠 MULTI-LLM TRADING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
    logger.info("=" * 70)
    
    if not exchanges.get('binance'):
        logger.error("❌ Binance not available for price data")
        return 0
    
    # Get current prices
    logger.info(f"📈 Getting current prices for {len(CRYPTOS_TO_ANALYZE)} cryptos...")
    prices = get_current_prices(exchanges['binance'], CRYPTOS_TO_ANALYZE)
    
    # Get LLM consensus for each crypto
    consensus_results = []
    for crypto in CRYPTOS_TO_ANALYZE:
        price_data = prices.get(crypto)
        if price_data:
            consensus = await get_llm_consensus(
                crypto, 
                price_data['price'], 
                price_data.get('change_24h', 0)
            )
            if consensus:
                consensus_results.append(consensus)
    
    # Execute trades based on consensus
    trades_executed = 0
    for consensus in consensus_results:
        crypto = consensus['crypto']
        
        # Gemini LONG for strong buy signals
        if consensus['signal'] in ['STRONG_BUY', 'BUY'] and exchanges.get('gemini'):
            if crypto in GEMINI_CRYPTOS:
                trade = execute_gemini_trade(exchanges['gemini'], crypto, consensus)
                if trade:
                    trades_executed += 1
        
        # Binance trades (both buy and sell)
        if exchanges.get('binance') and consensus['confidence'] >= 6.0:
            trade = execute_binance_trade(exchanges['binance'], crypto, consensus)
            if trade:
                trades_executed += 1
    
    logger.info(f"🎯 LLM consensus trades executed: {trades_executed}")
    
    # Log consensus summary
    logger.info("\n📊 LLM CONSENSUS SUMMARY:")
    for consensus in consensus_results:
        logger.info(f"  {consensus['crypto']}: BUY={consensus['buy_score']:.1f}, "
                   f"SELL={consensus['sell_score']:.1f}, Signal={consensus['signal']}")
    
    return trades_executed

async def main():
    """Main trading loop"""
    logger.info("=" * 70)
    logger.info("🧠 MULTI-LLM VOTING TRADING SYSTEM")
    logger.info("🤖 DeepSeek (main) + 4 Ollama LLMs consensus")
    logger.info("=" * 70)
    
    # Load API keys
    keys = load_api_keys()
    
    # Initialize exchanges
    exchanges = initialize_exchanges(keys)
    
    logger.info("✅ Exchanges initialized")
    logger.info(f"💰 Gemini capital: ${GEMINI_CAPITAL:.2f}")
    logger.info(f"💰 Binance capital: ${BINANCE_CAPITAL:.2f}")
    
    cycle = 0
    while True:
        cycle += 1
        logger.info(f"\n🔄 TRADING CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Run one trading cycle
            await trading_cycle(exchanges)
            
            logger.info(f"✅ Cycle {cycle} completed")
            logger.info(f"💤 Sleeping for {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
        except Exception as e:
            logger.error(f"❌ Error in cycle {cycle}: {e}")
            logger.info("💤 Sleeping for 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
