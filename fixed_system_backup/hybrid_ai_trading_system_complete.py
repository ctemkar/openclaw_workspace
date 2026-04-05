#!/usr/bin/env python3
"""
HYBRID AI TRADING SYSTEM
Combines: Quantitative analysis + LLM qualitative analysis + CIO AI decision maker
Implements: Short selling on Binance + Long on Gemini arbitrage
"""

import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import statistics
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hybrid_ai_trading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuantitativeAnalyzer:
    """Quantitative analysis module - numbers, spreads, statistics"""
    
    def __init__(self):
        self.min_spread_for_trade = 0.5  # 0.5% minimum spread
        self.min_profit_after_fees = 0.1  # $0.10 minimum profit after fees
        self.transfer_fee = 5.0  # $5 transfer fee (ERC-20)
    
    def analyze_opportunity(self, symbol: str, binance_price: float, 
                          gemini_price: float, duration_hours: float) -> Dict:
        """Quantitative analysis of arbitrage opportunity"""
        
        spread = gemini_price - binance_price
        spread_percent = (spread / binance_price) * 100
        
        # Calculate profit metrics
        trade_size = 30.0  # $30 trade
        profit_if_free = abs(spread) * (trade_size / binance_price)
        net_profit = profit_if_free - self.transfer_fee
        
        # Probability calculations (based on spread duration)
        if duration_hours < 1:
            convergence_prob_1h = 70  # 70% chance to converge in 1h if new
            convergence_prob_24h = 90  # 90% chance in 24h
        elif duration_hours < 3:
            convergence_prob_1h = 40  # 40% chance if persisted 1-3h
            convergence_prob_24h = 80  # 80% chance in 24h
        else:
            convergence_prob_1h = 20  # 20% chance if persisted >3h
            convergence_prob_24h = 60  # 60% chance in 24h
        
        # Risk score (0-10, 10 = highest risk)
        risk_score = 0
        risk_score += 3 if abs(spread_percent) < 1 else 0  # Small spread = higher risk
        risk_score += 4 if duration_hours > 3 else 0  # Persistent = higher risk
        risk_score += 3 if net_profit <= 0 else 0  # Negative profit = higher risk
        risk_score = min(risk_score, 10)
        
        # Quantitative recommendation
        if net_profit > self.min_profit_after_fees and abs(spread_percent) > self.min_spread_for_trade:
            quant_recommendation = "TRADE"
            confidence = min(80 + (abs(spread_percent) * 10), 95)  # Higher spread = higher confidence
        elif net_profit <= 0:
            quant_recommendation = "AVOID"
            confidence = 90  # High confidence to avoid losing trades
        else:
            quant_recommendation = "MONITOR"
            confidence = 50
        
        return {
            "symbol": symbol,
            "spread_percent": round(spread_percent, 2),
            "spread_dollars": round(spread, 4),
            "profit_if_free": round(profit_if_free, 4),
            "net_profit": round(net_profit, 2),
            "convergence_prob_1h": convergence_prob_1h,
            "convergence_prob_24h": convergence_prob_24h,
            "risk_score": risk_score,
            "recommendation": quant_recommendation,
            "confidence": confidence,
            "reason": f"Quantitative: Spread {abs(spread_percent):.2f}%, Net profit ${net_profit:.2f}, Risk {risk_score}/10"
        }

class QualitativeAnalyzer:
    """Qualitative analysis module - LLM text reasoning"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.1:latest"
    
    def analyze_with_llm(self, symbol: str, quant_analysis: Dict) -> Dict:
        """LLM qualitative analysis of opportunity"""
        
        prompt = self.create_prompt(symbol, quant_analysis)
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.4, "num_predict": 200}
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                # Parse LLM response
                analysis = self.parse_llm_response(response_text)
                return analysis
            else:
                logger.error(f"❌ LLM HTTP error: {response.status_code}")
                return self.default_analysis(symbol, quant_analysis)
                
        except Exception as e:
            logger.error(f"❌ LLM error: {e}")
            return self.default_analysis(symbol, quant_analysis)
    
    def create_prompt(self, symbol: str, quant: Dict) -> str:
        """Create prompt for LLM analysis"""
        
        direction = "Gemini is HIGHER" if quant["spread_dollars"] > 0 else "Binance is HIGHER"
        
        prompt = f"""As a crypto trading analyst, analyze this arbitrage opportunity:

SYMBOL: {symbol}
QUANTITATIVE ANALYSIS:
- Spread: {quant['spread_percent']:.2f}% ({direction})
- Duration: Provided as context (market has conditions)
- Net profit after $5 transfer fee: ${quant['net_profit']:.2f}
- Convergence probability (1h): {quant['convergence_prob_1h']}%
- Risk score: {quant['risk_score']}/10
- Quantitative recommendation: {quant['recommendation']} ({quant['confidence']}% confidence)

YOUR TASK: Provide QUALITATIVE analysis considering:
1. Market sentiment around {symbol}
2. Likelihood this spread is "real arbitrage" vs "persistent difference"
3. Transfer fee impact on profitability
4. Market conditions that might affect convergence
5. Your gut feeling about this trade

Respond in this exact JSON format:
{{
  "qualitative_recommendation": "TRADE/AVOID/MONITOR",
  "confidence": 0-100,
  "risk_assessment": "low/medium/high",
  "key_insights": "2-3 key insights from your analysis",
  "reasoning": "Your detailed reasoning (2-3 sentences)",
  "trust_numbers": true/false  # Should we trust the quantitative analysis?
}}"""
        
        return prompt
    
    def parse_llm_response(self, response_text: str) -> Dict:
        """Parse LLM response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
        
        # Default if parsing fails
        return {
            "qualitative_recommendation": "MONITOR",
            "confidence": 50,
            "risk_assessment": "medium",
            "key_insights": "LLM analysis unavailable",
            "reasoning": "Failed to parse LLM response",
            "trust_numbers": True
        }
    
    def default_analysis(self, symbol: str, quant: Dict) -> Dict:
        """Default analysis if LLM fails"""
        return {
            "qualitative_recommendation": "MONITOR",
            "confidence": 50,
            "risk_assessment": "medium",
            "key_insights": "Using quantitative analysis as fallback",
            "reasoning": "LLM analysis failed, relying on numbers",
            "trust_numbers": True
        }

class CIOAIDecisionMaker:
    """CIO AI - Decides whether to trust numbers or comments"""
    
    def __init__(self):
        # Decision weights (can be learned over time)
        self.quant_weight = 0.6  # Default: trust numbers 60%
        self.qual_weight = 0.4  # Default: trust LLM 40%
        
        # Decision history for learning
        self.decision_history = []
    
    def make_decision(self, symbol: str, quant_analysis: Dict, 
                     qual_analysis: Dict) -> Dict:
        """CIO AI makes final trading decision"""
        
        # Extract recommendations and confidences
        quant_rec = quant_analysis["recommendation"]
        quant_conf = quant_analysis["confidence"] / 100.0  # Convert to 0-1
        
        qual_rec = qual_analysis["qualitative_recommendation"]
        qual_conf = qual_analysis["confidence"] / 100.0
        
        # Convert recommendations to scores
        quant_score = self.recommendation_to_score(quant_rec) * quant_conf
        qual_score = self.recommendation_to_score(qual_rec) * qual_conf
        
        # Apply weights
        weighted_quant = quant_score * self.quant_weight
        weighted_qual = qual_score * self.qual_weight
        
        total_score = weighted_quant + weighted_qual
        
        # Determine final recommendation
        if total_score >= 0.7:
            final_recommendation = "TRADE"
            action = "EXECUTE"
        elif total_score >= 0.4:
            final_recommendation = "MONITOR"
            action = "WAIT"
        else:
            final_recommendation = "AVOID"
            action = "SKIP"
        
        # Determine trust decision
        trust_numbers = qual_analysis.get("trust_numbers", True)
        if trust_numbers:
            trust_decision = "TRUST NUMBERS"
            trust_reason = "LLM agrees with quantitative analysis"
        else:
            trust_decision = "TRUST COMMENTS"
            trust_reason = "LLM suggests qualitative factors override numbers"
        
        # Calculate decision confidence
        decision_confidence = (quant_conf * self.quant_weight + 
                             qual_conf * self.qual_weight) * 100
        
        return {
            "symbol": symbol,
            "final_recommendation": final_recommendation,
            "action": action,
            "decision_confidence": round(decision_confidence, 1),
            "trust_decision": trust_decision,
            "trust_reason": trust_reason,
            "quant_score": round(quant_score, 3),
            "qual_score": round(qual_score, 3),
            "weighted_quant": round(weighted_quant, 3),
            "weighted_qual": round(weighted_qual, 3),
            "total_score": round(total_score, 3),
            "quant_recommendation": quant_rec,
            "qual_recommendation": qual_rec,
            "quant_analysis": quant_analysis,
            "qual_analysis": qual_analysis
        }
    
    def recommendation_to_score(self, recommendation: str) -> float:
        """Convert recommendation to numerical score"""
        rec_map = {
            "TRADE": 1.0,
            "EXECUTE": 1.0,
            "BUY": 1.0,
            "SELL": 1.0,
            "MONITOR": 0.5,
            "WAIT": 0.5,
            "HOLD": 0.5,
            "AVOID": 0.0,
            "SKIP": 0.0
        }
        return rec_map.get(recommendation.upper(), 0.5)
    
    def learn_from_outcome(self, symbol: str, decision: Dict, 
                          actual_outcome: str, profit: float):
        """Learn from trade outcomes to improve weights"""
        # Record outcome
        self.decision_history.append({
            "symbol": symbol,
            "decision": decision,
            "outcome": actual_outcome,
            "profit": profit,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simple learning: adjust weights based on profit
        if profit > 0:
            # Successful trade - reinforce whatever was trusted more
            if decision["trust_decision"] == "TRUST NUMBERS":
                self.quant_weight = min(self.quant_weight + 0.05, 0.9)
                self.qual_weight = max(self.qual_weight - 0.05, 0.1)
            else:
                self.qual_weight = min(self.qual_weight + 0.05, 0.9)
                self.quant_weight = max(self.quant_weight - 0.05, 0.1)
        elif profit < 0:
            # Losing trade - reduce weight of whatever was trusted
            if decision["trust_decision"] == "TRUST NUMBERS":
                self.quant_weight = max(self.quant_weight - 0.05, 0.1)
                self.qual_weight = min(self.qual_weight + 0.05, 0.9)
            else:
                self.qual_weight = max(self.qual_weight - 0.05, 0.1)
                self.quant_weight = min(self.quant_weight + 0.05, 0.9)

class HybridAITradingSystem:
    """Main hybrid AI trading system"""
    
    def __init__(self):
        self.quant_analyzer = QuantitativeAnalyzer()
        self.qual_analyzer = QualitativeAnalyzer()
        self.cio_ai = CIOAIDecisionMaker()
        
        # Sample market data
        self.market_data = [
            {
                "symbol": "XTZ",
                "binance_price": 0.3409,
                "gemini_price": 0.3542,
                "duration_hours": 2.5,
                "description": "Tezos - Best current opportunity"
            },
            {
                "symbol": "YFI",
                "binance_price": 2423.00,
                "gemini_price": 2458.82,
                "duration_hours": 4.0,
                "description": "Yearn Finance - Persistent spread"
            },
            {
                "symbol": "FIL",
                "binance_price": 0.8230,
                "gemini_price": 0.8179,
                "duration_hours": 1.5,
                "description": "Filecoin - Reverse spread (Gemini cheaper)"
            },
            {
                "symbol": "MANA",
                "binance_price": 0.0853,
                "gemini_price": 0.0849,
                "duration_hours": 3.0,
                "description": "Decentraland - Small spread"
            }
        ]
    
    def analyze_opportunity(self, market: Dict) -> Dict:
        """Full analysis pipeline for one opportunity"""
        symbol = market["symbol"]
        
        print(f"\n🔍 Analyzing {symbol}: {market['description']}")
        print(f"   Prices: Binance=${market['binance_price']:,.4f}, Gemini=${market['gemini_price']:,.4f}")
        print(f"   Duration: {market['duration_hours']:.1f} hours")
        
        # Step 1: Quantitative analysis
        print("   1️⃣ Quantitative analysis...")
        quant = self.quant_analyzer.analyze_opportunity(
            symbol, market["binance_price"], market["gemini_price"], 
            market["duration_hours"]
        )
        print(f"      → Recommendation: {quant['recommendation']} ({quant['confidence']}% confidence)")
        print(f"      → Net profit: ${quant['net_profit']:.2f}, Risk: {quant['risk_score']}/10")
        
        # Step 2: Qualitative analysis (LLM)
        print("   2️⃣ Qualitative analysis (LLM)...")
        qual = self.qual_analyzer.analyze_with_llm(symbol, quant)
        print(f"      → Recommendation: {qual['qualitative_recommendation']} ({qual['confidence']}% confidence)")
        print(f"      → Risk: {qual['risk_assessment']}, Trust numbers: {qual['trust_numbers']}")
        
        # Step 3: CIO AI decision
        print("   3️⃣ CIO AI decision...")
        decision = self.cio_ai.make_decision(symbol, quant, qual)
        print(f"      → Final: {decision['final_recommendation']} ({decision['decision_confidence']}% confidence)")
        print(f"      → Action: {decision['action']}, Trust: {decision['trust_decision']}")
        
        return {
            "symbol": symbol,
            "market_data": market,
            "quantitative_analysis": quant,
            "qualitative_analysis": qual,
            "cio_decision": decision
        }
    
    def generate_trade_plan(self, analysis: Dict) -> Dict:
        """Generate detailed trade plan for execution"""
        symbol = analysis["symbol"]
        decision = analysis["cio_decision"]
        quant = analysis["quantitative_analysis"]
        
        if decision["action"] != "EXECUTE":
            return {
                "symbol": symbol,
                "action": "NO_TRADE",
                "reason": f"CIO AI recommends {decision['action']}",
                "details": decision
            }
        
        # Determine trade direction
        if quant["spread_dollars"] > 0:
            # Gemini price > Binance price
            direction = "SHORT Binance, LONG Gemini"
            binance_action = "SHORT"
            gemini_action = "LONG"
            explanation = f"Gemini price (${analysis['market_data']['gemini_price']:,.4f}) > Binance price (${analysis['market_data']['binance_price']:,.4f})"
        else:
            # Binance price > Gemini price
            direction = "LONG Binance, SHORT Gemini"
            binance_action = "