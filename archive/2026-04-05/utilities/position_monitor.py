#!/usr/bin/env python3
"""
POSITION MONITOR - Checks LLM consensus on current holdings
Closes positions if LLMs turn negative or show strong sell signals
"""

import json
import os
import time
import requests
from datetime import datetime
import ccxt
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "position_monitor.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# LLM models to query - ALL 8 MODELS including new additions
OLLAMA_MODELS = [
    "glm-4.7-flash:latest",    # Large model, good reasoning
    "llama3.1:latest",         # Balanced model  
    "llama3:latest",           # Reliable model
    "qwen2.5-coder:32b",       # Large coder model
    "qwen3:latest",            # NEW addition
    "mistral:latest",          # NEW addition
    "deepseek-r1:latest",      # NEW addition (reasoning model)
    "llama3.1:8b"              # Smaller but fast
]

def load_current_positions():
    """Load current positions from trades.json"""
    trades_file = os.path.join(BASE_DIR, "trading_data/trades.json")
    if not os.path.exists(trades_file):
        return []
    
    with open(trades_file, 'r') as f:
        trades = json.load(f)
    
    # Get unique symbols from current trades
    positions = {}
    for trade in trades:
        symbol = trade.get('symbol', '')
        exchange = trade.get('exchange', '')
        if symbol and exchange:
            key = f"{exchange}:{symbol}"
            if key not in positions:
                positions[key] = {
                    'exchange': exchange,
                    'symbol': symbol,
                    'side': trade.get('side', 'buy'),
                    'entry_price': trade.get('price', 0),
                    'amount': trade.get('amount', 0),
                    'value': trade.get('value', 0),
                    'current_price': trade.get('current_price', trade.get('price', 0)),
                    'pnl': trade.get('pnl', 0),
                    'pnl_percent': trade.get('pnl_percent', 0),
                    'timestamp': trade.get('timestamp', '')
                }
    
    return list(positions.values())

def get_current_price(exchange_name, symbol):
    """Get current price from exchange"""
    try:
        # Load exchange
        if exchange_name == 'gemini':
            with open(os.path.join(BASE_DIR, 'secure_keys/gemini_keys.json')) as f:
                keys = json.load(f)
            exchange = ccxt.gemini({
                'apiKey': keys['api_key'],
                'secret': keys['api_secret']
            })
            # Convert symbol format
            if '/USDT' in symbol:
                symbol = symbol.replace('/USDT', '/USD')
        elif exchange_name == 'binance':
            with open(os.path.join(BASE_DIR, 'secure_keys/binance_keys.json')) as f:
                keys = json.load(f)
            exchange = ccxt.binance({
                'apiKey': keys['api_key'],
                'secret': keys['api_secret']
            })
            # Convert symbol format
            if '/USD' in symbol and '/USDT' not in symbol:
                symbol = symbol.replace('/USD', '/USDT')
        else:
            return None
        
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        logger.error(f"❌ Error fetching {symbol} price: {e}")
        return None

def query_llm_for_position(model, symbol, current_price, entry_price, pnl_percent):
    """Ask LLM about current position"""
    prompt = f"""
Analyze our current position in {symbol}.
We are LONG (bought) at entry price: ${entry_price:.4f}
Current price: ${current_price:.4f}
Current P&L: {pnl_percent:+.2f}%

Should we:
1. HOLD (continue holding)
2. CLOSE (take profit/cut loss)
3. ADD (buy more)

Consider: Market conditions, risk management, technical analysis.
Respond ONLY as JSON: {{"action":"HOLD|CLOSE|ADD", "confidence":1-10, "reason":"brief"}}
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
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                analysis = json.loads(result.get('response', '{}'))
                return {
                    'model': model,
                    'action': analysis.get('action', 'HOLD'),
                    'confidence': analysis.get('confidence', 5),
                    'reason': analysis.get('reason', 'No reason')
                }
            except:
                return {'model': model, 'action': 'HOLD', 'confidence': 5, 'reason': 'Parse error'}
        else:
            logger.error(f"❌ {model} failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error querying {model}: {e}")
        return None

def get_llm_consensus_for_position(symbol, current_price, entry_price, pnl_percent):
    """Get consensus from multiple LLMs about a position"""
    results = []
    
    for model in OLLAMA_MODELS:
        result = query_llm_for_position(model, symbol, current_price, entry_price, pnl_percent)
        if result:
            results.append(result)
    
    if not results:
        return None
    
    # Count votes for each action
    action_counts = {'HOLD': 0, 'CLOSE': 0, 'ADD': 0}
    total_confidence = 0
    
    for result in results:
        action = result['action']
        confidence = result['confidence']
        
        if action in action_counts:
            action_counts[action] += 1
            total_confidence += confidence
    
    # Determine consensus
    max_action = max(action_counts, key=action_counts.get)
    max_count = action_counts[max_action]
    total_votes = len(results)
    
    consensus = {
        'symbol': symbol,
        'current_price': current_price,
        'entry_price': entry_price,
        'pnl_percent': pnl_percent,
        'actions': action_counts,
        'total_votes': total_votes,
        'consensus_action': max_action,
        'consensus_strength': max_count / total_votes if total_votes > 0 else 0,
        'avg_confidence': total_confidence / total_votes if total_votes > 0 else 0,
        'details': results
    }
    
    return consensus

def should_close_position(consensus, pnl_percent):
    """Determine if position should be closed"""
    # Rule 1: Strong CLOSE consensus (≥75% votes)
    if consensus['consensus_action'] == 'CLOSE' and consensus['consensus_strength'] >= 0.75:
        logger.warning(f"🚨 STRONG CLOSE consensus for {consensus['symbol']}: {consensus['consensus_strength']*100:.0f}%")
        return True
    
    # Rule 2: Moderate CLOSE consensus AND losing position
    if (consensus['consensus_action'] == 'CLOSE' and 
        consensus['consensus_strength'] >= 0.5 and 
        pnl_percent < -2.0):  # Down more than 2%
        logger.warning(f"⚠️ CLOSE consensus + loss for {consensus['symbol']}: {pnl_percent:+.2f}%")
        return True
    
    # Rule 3: High confidence CLOSE regardless of votes
    close_votes = consensus['actions']['CLOSE']
    if close_votes > 0:
        # Check if any CLOSE vote has high confidence (≥8)
        high_confidence_close = any(
            r['action'] == 'CLOSE' and r['confidence'] >= 8 
            for r in consensus['details']
        )
        if high_confidence_close:
            logger.warning(f"⚠️ High-confidence CLOSE vote for {consensus['symbol']}")
            return True
    
    return False

def monitor_positions():
    """Main monitoring loop"""
    logger.info("=" * 70)
    logger.info("🧠 POSITION MONITOR - LLM Consensus on Current Holdings")
    logger.info("=" * 70)
    
    while True:
        try:
            # Load current positions
            positions = load_current_positions()
            
            if not positions:
                logger.info("📭 No active positions found")
                time.sleep(300)  # 5 minutes
                continue
            
            logger.info(f"📊 Monitoring {len(positions)} positions")
            
            for position in positions:
                symbol = position['symbol']
                exchange = position['exchange']
                entry_price = position['entry_price']
                pnl_percent = position['pnl_percent']
                
                # Get current price
                current_price = get_current_price(exchange, symbol)
                if not current_price:
                    current_price = position['current_price']
                
                # Update P&L
                if position['side'] == 'buy':  # LONG
                    new_pnl_percent = ((current_price - entry_price) / entry_price) * 100
                else:  # SHORT
                    new_pnl_percent = ((entry_price - current_price) / entry_price) * 100
                
                # Get LLM consensus
                logger.info(f"\n🔍 Analyzing {symbol} (Entry: ${entry_price:.4f}, Current: ${current_price:.4f}, P&L: {new_pnl_percent:+.2f}%)")
                
                consensus = get_llm_consensus_for_position(
                    symbol, current_price, entry_price, new_pnl_percent
                )
                
                if consensus:
                    logger.info(f"   LLM Consensus: {consensus['consensus_action']} ({consensus['consensus_strength']*100:.0f}%)")
                    logger.info(f"   Votes: HOLD:{consensus['actions']['HOLD']} CLOSE:{consensus['actions']['CLOSE']} ADD:{consensus['actions']['ADD']}")
                    
                    # Check if should close
                    if should_close_position(consensus, new_pnl_percent):
                        logger.warning(f"   🚨 ACTION REQUIRED: Close {symbol} position!")
                        # TODO: Implement actual closing logic
                        # For now, just log the recommendation
                    
                    # Log individual model reasons
                    for detail in consensus['details']:
                        logger.info(f"   • {detail['model'].split(':')[0]}: {detail['action']} ({detail['confidence']}/10) - {detail['reason'][:50]}...")
            
            logger.info(f"\n⏰ Next check in 5 minutes...")
            time.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error(f"❌ Error in monitor: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_positions()