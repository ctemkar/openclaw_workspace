#!/usr/bin/env python3
"""
ENHANCED MULTI-LLM ARBITRAGE ANALYZER
Combines: Claude Haiku, GPT-3.5-turbo, Gemini Flash + Local Ollama LLMs
Analyzes arbitrage opportunities with AI consensus
"""

import os
import json
import time
import requests
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import asyncio
import aiohttp
from dataclasses import dataclass
import statistics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enhanced_llm_arbitrage.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Market data for arbitrage analysis"""
    symbol: str
    binance_price: float
    gemini_price: float
    spread_percent: float
    spread_dollars: float
    duration_hours: float
    binance_volume: float = 0
    gemini_volume: float = 0
    transfer_fee: float = 5.0  # Default ERC-20 transfer fee

@dataclass
class LLMAnalysis:
    """LLM analysis result"""
    model: str
    buy_score: float  # 0-10
    sell_score: float  # 0-10
    confidence: float  # 0-10
    reason: str
    convergence_probability_1h: float  # 0-100%
    convergence_probability_24h: float  # 0-100%
    risk_score: float  # 0-10
    recommendation: str  # BUY, SELL, HOLD

@dataclass
class ConsensusResult:
    """Consensus from all LLMs"""
    symbol: str
    avg_buy_score: float
    avg_sell_score: float
    avg_confidence: float
    avg_convergence_1h: float
    avg_convergence_24h: float
    avg_risk_score: float
    final_recommendation: str
    recommendation_confidence: float
    llm_analyses: List[LLMAnalysis]
    trade_advice: str

class EnhancedMultiLLMAnalyzer:
    """Enhanced multi-LLM arbitrage analyzer"""
    
    def __init__(self):
        # API endpoints (configure with your API keys)
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Available LLMs with weights (higher = more trusted)
        self.llms = [
            # Local Ollama models (free)
            {"name": "llama3.1:latest", "type": "ollama", "weight": 0.8},
            {"name": "glm-4.7-flash:latest", "type": "ollama", "weight": 0.9},
            {"name": "qwen2.5-coder:32b", "type": "ollama", "weight": 0.7},
            
            # Cloud models (need API keys - uncomment and add your keys)
            # {"name": "claude-3-haiku", "type": "anthropic", "weight": 1.0, "api_key": ""},
            # {"name": "gpt-3.5-turbo", "type": "openai", "weight": 1.0, "api_key": ""},
            # {"name": "gemini-flash", "type": "google", "weight": 1.0, "api_key": ""},
        ]
        
        # Sample market data (would come from real API)
        self.sample_markets = [
            MarketData(
                symbol="YFI",
                binance_price=2423.00,
                gemini_price=2458.82,
                spread_percent=1.46,
                spread_dollars=35.82,
                duration_hours=2.5,
                transfer_fee=8.0
            ),
            MarketData(
                symbol="FIL",
                binance_price=0.8230,
                gemini_price=0.8179,
                spread_percent=-0.62,  # Negative = Gemini cheaper
                spread_dollars=-0.0051,
                duration_hours=1.2,
                transfer_fee=5.0
            ),
            MarketData(
                symbol="MANA",
                binance_price=0.0853,
                gemini_price=0.0849,
                spread_percent=-0.47,
                spread_dollars=-0.0004,
                duration_hours=3.0,
                transfer_fee=5.0
            )
        ]
    
    def create_analysis_prompt(self, market: MarketData) -> str:
        """Create prompt for LLM analysis"""
        
        direction = "Gemini is CHEAPER" if market.spread_percent < 0 else "Binance is CHEAPER"
        abs_spread = abs(market.spread_percent)
        
        prompt = f"""# CRYPTO ARBITRAGE OPPORTUNITY ANALYSIS

## MARKET SITUATION:
Cryptocurrency: {market.symbol}
Time: {datetime.now().isoformat()}

## PRICE DATA:
- Binance: ${market.binance_price:,.4f}
- Gemini: ${market.gemini_price:,.4f}
- Spread: {abs_spread:.2f}% (${abs(market.spread_dollars):.4f})
- Direction: {direction}

## MARKET HISTORY:
- This spread has persisted for {market.duration_hours:.1f} hours
- {direction} by {abs_spread:.2f}%
- NO significant price convergence observed

## TRADING CONSTRAINTS:
- Transfer fee (between exchanges): ${market.transfer_fee:.2f}
- Transfer time: 30+ minutes (blockchain confirmation)
- Typical trade size: $30
- Potential profit IF transfer was free: ${abs(market.spread_dollars * 30 / market.binance_price):.4f}

## ANALYSIS REQUESTED:

Please analyze this arbitrage opportunity and provide:

1. **BUY/SELL SCORES** (0-10 scale):
   - BUY score: How strongly should we BUY {market.symbol} on the cheaper exchange?
   - SELL score: How strongly should we SELL {market.symbol} on the more expensive exchange?

2. **CONFIDENCE** (0-10): How confident are you in this analysis?

3. **PRICE CONVERGENCE PROBABILITY** (0-100%):
   - Probability prices will converge (spread close to 0%) within:
     a) 1 hour: __%
     b) 24 hours: __%

4. **RISK SCORE** (0-10): 0=no risk, 10=extremely risky

5. **RECOMMENDATION**: BUY, SELL, or HOLD

6. **REASONING**: Brief explanation of your analysis

## RESPONSE FORMAT (JSON):
{{
  "buy_score": 0-10,
  "sell_score": 0-10,
  "confidence": 0-10,
  "convergence_probability_1h": 0-100,
  "convergence_probability_24h": 0-100,
  "risk_score": 0-10,
  "recommendation": "BUY/SELL/HOLD",
  "reason": "Your reasoning here"
}}

## IMPORTANT CONTEXT:
- Transfer fees make true arbitrage difficult
- Spread has persisted for hours
- Prices on different exchanges can stay different indefinitely
- Consider if this is a true arbitrage or just persistent spread"""
        
        return prompt
    
    async def query_ollama(self, model: str, prompt: str) -> Optional[Dict]:
        """Query Ollama model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response", "")
                        
                        # Try to extract JSON from response
                        try:
                            # Look for JSON in the response
                            import re
                            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                            if json_match:
                                json_str = json_match.group()
                                analysis = json.loads(json_str)
                                return analysis
                            else:
                                # Try to parse the whole response as JSON
                                analysis = json.loads(response_text)
                                return analysis
                        except json.JSONDecodeError:
                            logger.error(f"❌ Failed to parse JSON from {model}")
                            return None
                    else:
                        logger.error(f"❌ Ollama error for {model}: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Error querying Ollama {model}: {e}")
            return None
    
    async def analyze_with_llm(self, llm_config: Dict, market: MarketData) -> Optional[LLMAnalysis]:
        """Analyze market with specific LLM"""
        prompt = self.create_analysis_prompt(market)
        
        if llm_config["type"] == "ollama":
            result = await self.query_ollama(llm_config["name"], prompt)
            
            if result:
                try:
                    return LLMAnalysis(
                        model=llm_config["name"],
                        buy_score=float(result.get("buy_score", 5)),
                        sell_score=float(result.get("sell_score", 5)),
                        confidence=float(result.get("confidence", 5)),
                        reason=result.get("reason", "No reason provided"),
                        convergence_probability_1h=float(result.get("convergence_probability_1h", 50)),
                        convergence_probability_24h=float(result.get("convergence_probability_24h", 50)),
                        risk_score=float(result.get("risk_score", 5)),
                        recommendation=result.get("recommendation", "HOLD")
                    )
                except Exception as e:
                    logger.error(f"❌ Error parsing {llm_config['name']} response: {e}")
                    return None
        
        # Add implementations for other LLM types here
        # elif llm_config["type"] == "anthropic":
        #     # Implement Claude Haiku
        #     pass
        # elif llm_config["type"] == "openai":
        #     # Implement GPT-3.5-turbo
        #     pass
        # elif llm_config["type"] == "google":
        #     # Implement Gemini Flash
        #     pass
        
        return None
    
    def calculate_consensus(self, market: MarketData, analyses: List[LLMAnalysis]) -> ConsensusResult:
        """Calculate consensus from all LLM analyses"""
        
        if not analyses:
            return ConsensusResult(
                symbol=market.symbol,
                avg_buy_score=5.0,
                avg_sell_score=5.0,
                avg_confidence=5.0,
                avg_convergence_1h=50.0,
                avg_convergence_24h=50.0,
                avg_risk_score=5.0,
                final_recommendation="HOLD",
                recommendation_confidence=0.0,
                llm_analyses=[],
                trade_advice="No LLM analyses available"
            )
        
        # Calculate weighted averages
        buy_scores = [a.buy_score for a in analyses]
        sell_scores = [a.sell_score for a in analyses]
        confidences = [a.confidence for a in analyses]
        conv_1h = [a.convergence_probability_1h for a in analyses]
        conv_24h = [a.convergence_probability_24h for a in analyses]
        risks = [a.risk_score for a in analyses]
        
        # Count recommendations
        recommendations = {}
        for analysis in analyses:
            rec = analysis.recommendation.upper()
            recommendations[rec] = recommendations.get(rec, 0) + 1
        
        # Determine final recommendation
        if recommendations:
            final_rec = max(recommendations, key=recommendations.get)
            rec_confidence = recommendations[final_rec] / len(analyses)
        else:
            final_rec = "HOLD"
            rec_confidence = 0.0
        
        # Generate trade advice
        trade_advice = self.generate_trade_advice(market, analyses, final_rec, rec_confidence)
        
        return ConsensusResult(
            symbol=market.symbol,
            avg_buy_score=statistics.mean(buy_scores),
            avg_sell_score=statistics.mean(sell_scores),
            avg_confidence=statistics.mean(confidences),
            avg_convergence_1h=statistics.mean(conv_1h),
            avg_convergence_24h=statistics.mean(conv_24h),
            avg_risk_score=statistics.mean(risks),
            final_recommendation=final_rec,
            recommendation_confidence=rec_confidence,
            llm_analyses=analyses,
            trade_advice=trade_advice
        )
    
    def generate_trade_advice(self, market: MarketData, analyses: List[LLMAnalysis], 
                            recommendation: str, confidence: float) -> str:
        """Generate detailed trade advice"""
        
        if market.spread_percent > 0:
            direction = f"Buy on Binance (${market.binance_price:,.4f}), Sell on Gemini (${market.gemini_price:,.4f})"
        else:
            direction = f"Buy on Gemini (${market.gemini_price:,.4f}), Sell on Binance (${market.binance_price:,.4f})"
        
        profit_if_free = abs(market.spread_dollars * 30 / market.binance_price)
        net_profit = profit_if_free - market.transfer_fee
        
        advice_parts = []
        
        # Basic info
        advice_parts.append(f"📊 {market.symbol}: {abs(market.spread_percent):.2f}% spread for {market.duration_hours:.1f}h")
        advice_parts.append(f"💰 Direction: {direction}")
        
        # Profit analysis
        advice_parts.append(f"💵 Profit if free transfer: ${profit_if_free:.4f}")
        advice_parts.append(f"🚫 Transfer fee: ${market.transfer_fee:.2f}")
        advice_parts.append(f"📉 Net profit: ${net_profit:.2f} (LOSS due to fees)")
        
        # LLM consensus
        advice_parts.append(f"🤖 LLM Consensus: {recommendation} ({confidence:.0%} confidence)")
        advice_parts.append(f"⚠️ Risk score: {statistics.mean([a.risk_score for a in analyses]):.1f}/10")
        
        # Convergence probability
        conv_1h = statistics.mean([a.convergence_probability_1h for a in analyses])
        conv_24h = statistics.mean([a.convergence_probability_24h for a in analyses])
        advice_parts.append(f"🎯 Convergence probability: {conv_1h:.0f}% (1h), {conv_24h:.0f}% (24h)")
        
        # Final recommendation
        if net_profit > 0 and confidence > 0.7 and conv_1h > 60:
            advice_parts.append("✅ RECOMMENDATION: CONSIDER TRADING (if pre-funded accounts)")
        elif net_profit <= 0:
            advice_parts.append("❌ RECOMMENDATION: DO NOT TRADE (transfer fees > profit)")
        elif confidence < 0.5:
            advice_parts.append("⚠️ RECOMMENDATION: WAIT (low LLM confidence)")
        else:
            advice_parts.append("⏸️ RECOMMENDATION: HOLD (monitor for changes)")
        
        return "\n".join(advice_parts)
    
    async def analyze_all_markets(self) -> List[ConsensusResult]:
        """Analyze all markets with all LLMs"""
        results = []
        
        for market in self.sample_markets:
            logger.info(f"🔍 Analyzing {market.symbol} with {len(self.llms)} LLMs...")
            
            # Query all LLMs in parallel
            tasks = []
            for llm in self.llms:
                task = self.analyze_with_llm(llm, market)
                tasks.append(task)
            
            analyses = await asyncio.gather(*tasks)
            analyses = [a for a in analyses if a is not None]  # Remove failed analyses
            
            logger.info(f"✅ {market.symbol}: Got {len(analyses)}/{len(self.llms)} LLM analyses")
            
            # Calculate consensus
            consensus = self.calculate_consensus(market, analyses)
            results.append(consensus)
            
            # Log results
            logger.info(f"📊 {market.symbol} Consensus:")
            logger.info(f"   Recommendation: {consensus.final_recommendation} ({consensus.recommendation_confidence:.0%})")
            logger.info(f"   Buy Score: {consensus.avg_buy_score:.2f}, Sell Score: {consensus.avg_sell_score:.2f}")
            logger.info(f"   Risk: {consensus.avg_risk_score:.2f}/10")
            logger.info(f"   Convergence: {consensus.avg_convergence_1h:.0f}% (1h), {consensus.avg_convergence_24h:.0f}% (24h)")
        
        return results
    
    def print_detailed_report(self, results: List[ConsensusResult]):
        """Print detailed analysis report"""
        print("\n" + "="*80)
        print("🤖 ENHANCED MULTI-LLM ARBITRAGE ANALYSIS REPORT")
        print("="*80)
        
        for result