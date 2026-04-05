#!/usr/bin/env python3
"""
CIO DECISION ENGINE - Reads BOTH scores AND comments
Detects contradictions between scores and reasoning
Makes final trading decisions
"""

import json
import re
import os
from datetime import datetime
import logging

BASE_DIR = "/Users/chetantemkar/.openclaw/workspace/app"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CIO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "cio_decisions.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Sentiment keywords
BEARISH_KEYWORDS = [
    'overextended', 'overbought', 'pullback', 'correction', 'selloff',
    'resistance', 'top', 'peak', 'decline', 'drop', 'fall', 'bearish',
    'caution', 'warning', 'risk', 'volatile', 'uncertain', 'weak',
    'downtrend', 'breakdown', 'support broken', 'loss', 'negative'
]

BULLISH_KEYWORDS = [
    'bullish', 'uptrend', 'breakout', 'support', 'bounce', 'recovery',
    'momentum', 'strength', 'rally', 'gain', 'increase', 'rise',
    'opportunity', 'buy', 'accumulate', 'strong', 'positive', 'optimistic',
    'growth', 'trending up', 'bull run', 'break above', 'resistance broken'
]

NEUTRAL_KEYWORDS = [
    'neutral', 'sideways', 'consolidation', 'range', 'flat', 'stable',
    'wait', 'observe', 'monitor', 'uncertain', 'mixed', 'balanced',
    'no clear direction', 'choppy', 'indecisive'
]

def analyze_comment_sentiment(comment):
    """Analyze comment text for bullish/bearish sentiment"""
    if not comment or comment == 'No reason' or 'Parse error' in comment:
        return 'NEUTRAL'
    
    comment_lower = comment.lower()
    
    bullish_count = sum(1 for word in BULLISH_KEYWORDS if word in comment_lower)
    bearish_count = sum(1 for word in BEARISH_KEYWORDS if word in comment_lower)
    neutral_count = sum(1 for word in NEUTRAL_KEYWORDS if word in comment_lower)
    
    # Determine sentiment
    if bullish_count > bearish_count and bullish_count > neutral_count:
        return 'BULLISH'
    elif bearish_count > bullish_count and bearish_count > neutral_count:
        return 'BEARISH'
    elif neutral_count > 0:
        return 'NEUTRAL'
    else:
        # Check for mixed signals
        if bullish_count > 0 and bearish_count > 0:
            return 'MIXED'
        elif bullish_count > 0:
            return 'BULLISH'
        elif bearish_count > 0:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

def detect_contradiction(score_signal, comment_sentiment):
    """Detect if score contradicts comment"""
    score_map = {
        'BUY': 'BULLISH',
        'STRONG_BUY': 'BULLISH',
        'SELL': 'BEARISH',
        'STRONG_SELL': 'BEARISH',
        'NEUTRAL': 'NEUTRAL'
    }
    
    score_sentiment = score_map.get(score_signal, 'NEUTRAL')
    
    # Check for contradictions
    if score_sentiment == 'BULLISH' and comment_sentiment == 'BEARISH':
        return True, f"🚨 CONTRADICTION: Score says BUY ({score_signal}) but comment is BEARISH"
    elif score_sentiment == 'BEARISH' and comment_sentiment == 'BULLISH':
        return True, f"🚨 CONTRADICTION: Score says SELL ({score_signal}) but comment is BULLISH"
    elif score_sentiment == 'NEUTRAL' and comment_sentiment in ['BULLISH', 'BEARISH']:
        return True, f"⚠️ MISMATCH: Score NEUTRAL but comment is {comment_sentiment}"
    
    return False, "OK"

def make_cio_decision(model_results, weighted_consensus):
    """
    CIO makes final decision considering BOTH scores AND comments
    Returns: {'final_signal': 'BUY/SELL/HOLD', 'confidence': 1-10, 'reason': '...'}
    """
    crypto = weighted_consensus.get('crypto', 'UNKNOWN')
    score_signal = weighted_consensus.get('signal', 'NEUTRAL')
    net_score = weighted_consensus.get('net_score', 0)
    
    logger.info(f"\n🧠 CIO ANALYSIS: {crypto}")
    logger.info(f"   Automated consensus: {score_signal} (Net: {net_score:.1f})")
    
    # Analyze each model's comment
    contradictions = []
    comment_sentiments = []
    model_decisions = []
    
    for result in model_results:
        model = result.get('model', 'unknown')
        buy_score = result.get('buy', 5)
        sell_score = result.get('sell', 5)
        comment = result.get('reason', 'No reason')
        
        # Determine score-based signal
        if buy_score - sell_score >= 3:
            model_score_signal = 'BUY'
        elif sell_score - buy_score >= 3:
            model_score_signal = 'SELL'
        else:
            model_score_signal = 'NEUTRAL'
        
        # Analyze comment sentiment
        comment_sentiment = analyze_comment_sentiment(comment)
        comment_sentiments.append(comment_sentiment)
        
        # Check for contradiction
        has_contradiction, contradiction_msg = detect_contradiction(model_score_signal, comment_sentiment)
        
        if has_contradiction:
            contradictions.append(f"{model}: {contradiction_msg}")
            logger.warning(f"   ⚠️ {model}: {contradiction_msg}")
        
        # Model's overall decision (considering both)
        if has_contradiction:
            # When contradictory, trust comment over score
            if comment_sentiment == 'BULLISH':
                model_decision = 'BUY'
            elif comment_sentiment == 'BEARISH':
                model_decision = 'SELL'
            else:
                model_decision = 'HOLD'
        else:
            # When aligned, use score signal
            model_decision = model_score_signal
        
        model_decisions.append({
            'model': model,
            'score_signal': model_score_signal,
            'comment_sentiment': comment_sentiment,
            'final_decision': model_decision,
            'contradiction': has_contradiction,
            'comment': comment[:100] + '...' if len(comment) > 100 else comment
        })
    
    # Count final decisions
    decision_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0, 'NEUTRAL': 0}
    for md in model_decisions:
        decision = md['final_decision']
        if decision in decision_counts:
            decision_counts[decision] += 1
        else:
            decision_counts['NEUTRAL'] += 1
    
    total_models = len(model_decisions)
    
    # Determine CIO final decision
    if contradictions:
        logger.warning(f"   🚨 {len(contradictions)} CONTRADICTIONS FOUND!")
        
        # When contradictions exist, be LESS conservative - trust majority consensus
        buy_percent = decision_counts['BUY'] / total_models
        sell_percent = decision_counts['SELL'] / total_models
        hold_percent = decision_counts['HOLD'] / total_models
        
        # Find the strongest signal
        max_percent = max(buy_percent, sell_percent, hold_percent)
        
        if max_percent == buy_percent and buy_percent >= 0.4:  # Lower threshold for BUY
            final_signal = 'BUY'
            confidence = 7
            reason = f"Buy consensus ({buy_percent*100:.0f}%) despite {len(contradictions)} contradictory comments"
        elif max_percent == sell_percent and sell_percent >= 0.4:  # Lower threshold for SELL
            final_signal = 'SELL'
            confidence = 7
            reason = f"Sell consensus ({sell_percent*100:.0f}%) despite {len(contradictions)} contradictory comments"
        else:
            final_signal = 'HOLD'
            confidence = 6  # Lower confidence for HOLD
            reason = f"Mixed signals with {len(contradictions)} contradictions. BUY:{buy_percent*100:.0f}%, SELL:{sell_percent*100:.0f}%, HOLD:{hold_percent*100:.0f}%"
    else:
        # No contradictions - trust the consensus
        if decision_counts['BUY'] > decision_counts['SELL'] and decision_counts['BUY'] > decision_counts['HOLD']:
            final_signal = 'BUY'
            confidence = 9
            reason = f"Clear buy consensus ({decision_counts['BUY']}/{total_models} models)"
        elif decision_counts['SELL'] > decision_counts['BUY'] and decision_counts['SELL'] > decision_counts['HOLD']:
            final_signal = 'SELL'
            confidence = 9
            reason = f"Clear sell consensus ({decision_counts['SELL']}/{total_models} models)"
        else:
            final_signal = 'HOLD'
            confidence = 8
            reason = f"No clear consensus. BUY:{decision_counts['BUY']}, SELL:{decision_counts['SELL']}, HOLD:{decision_counts['HOLD']}"
    
    # Log detailed analysis
    logger.info(f"   Comment sentiments: {', '.join(comment_sentiments)}")
    logger.info(f"   Model decisions: BUY:{decision_counts['BUY']}, SELL:{decision_counts['SELL']}, HOLD:{decision_counts['HOLD']}")
    logger.info(f"   🎯 CIO FINAL DECISION: {final_signal} (Confidence: {confidence}/10)")
    logger.info(f"   📝 Reason: {reason}")
    
    # Log individual model analysis
    for md in model_decisions:
        if md['contradiction']:
            logger.info(f"   ⚠️ {md['model'].split(':')[0]}: Score={md['score_signal']}, Comment={md['comment_sentiment']} → {md['final_decision']}")
    
    return {
        'crypto': crypto,
        'automated_signal': score_signal,
        'cio_signal': final_signal,
        'confidence': confidence,
        'reason': reason,
        'contradictions': contradictions,
        'model_decisions': model_decisions,
        'timestamp': datetime.now().isoformat()
    }

def integrate_with_llm_bot():
    """Integrate CIO with existing LLM consensus bot"""
    # This would be called from llm_consensus_bot.py
    # after getting model results but before executing trades
    
    logger.info("=" * 70)
    logger.info("🧠 CIO DECISION ENGINE ACTIVATED")
    logger.info("📊 Analyzing scores AND comments for contradictions")
    logger.info("=" * 70)
    
    # In practice, this would be called from llm_consensus_bot.py
    # with the model_results and weighted_consensus
    
    return True

if __name__ == "__main__":
    # Test with sample data
    test_results = [
        {
            'model': 'llama3.1:latest',
            'buy': 8,
            'sell': 2,
            'reason': 'Price is overextended, expect pullback soon despite recent gains',
            'weight': 1.0
        },
        {
            'model': 'llama3:latest',
            'buy': 7,
            'sell': 3,
            'reason': 'Strong momentum continuing, breakout above resistance',
            'weight': 1.0
        },
        {
            'model': 'mistral:latest',
            'buy': 6,
            'sell': 4,
            'reason': 'Neutral trend, waiting for clearer direction',
            'weight': 1.0
        }
    ]
    
    test_consensus = {
        'crypto': 'BTC',
        'signal': 'BUY',
        'net_score': 2.5
    }
    
    decision = make_cio_decision(test_results, test_consensus)
    print(f"\n✅ CIO Test Decision: {decision['cio_signal']}")
    print(f"   Reason: {decision['reason']}")