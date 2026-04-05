#!/usr/bin/env python3
"""
MULTI-LLM ARBITRAGE ANALYZER
Uses local Ollama LLMs to analyze arbitrage opportunities
"""

import json
import time
import requests
import logging
from datetime import datetime
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("llm_arbitrage_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiLLMArbitrageAnalyzer:
    """Multi-LLM arbitrage opportunity analyzer"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Available Ollama models
        self.models = [
            "llama3.1:latest",      # Balanced, general purpose
            "glm-4.7-flash:latest", # Chinese model, good at analysis
            "qwen2.5-coder:32b",    # Technical/coding focus
        ]
        
        # Current market data (from progress monitor)
        self.market_data = {
            "YFI": {
                "binance": 2423.00,
                "gemini": 2458.82,
                "spread_percent": 1.46,
                "spread_dollars": 35.82,
                "duration_hours": 2.5,
                "transfer_fee": 8.0
            },
            "FIL": {
                "binance": 0.8230,
                "gemini": 0.8179,
                "spread_percent": -0.62,  # Negative = Gemini cheaper
                "spread_dollars": -0.0051,
                "duration_hours": 1.2,
                "transfer_fee": 5.0
            },
            "MANA": {
                "binance": 0.0853,
                "gemini": 0.0849,
                "spread_percent": -0.47,
                "spread_dollars": -0.0004,
                "duration_hours": 3.0,
                "transfer_fee": 5.0
            }
        }
    
    def create_prompt(self, symbol: str, data: Dict) -> str:
        """Create analysis prompt for LLM"""
        
        direction = "Gemini is CHEAPER" if data["spread_percent"] < 0 else "Binance is CHEAPER"
        abs_spread = abs(data["spread_percent"])
        
        prompt = f"""Analyze this crypto arbitrage opportunity:

SYMBOL: {symbol}
BINANCE PRICE: ${data['binance']:,.4f}
GEMINI PRICE: ${data['gemini']:,.4f}
SPREAD: {abs_spread:.2f}% (${abs(data['spread_dollars']):.4f})
DIRECTION: {direction}
DURATION: {data['duration_hours']:.1f} hours
TRANSFER FEE: ${data['transfer_fee']:.2f}
TRADE SIZE: $30

Key facts:
1. Spread has persisted for {data['duration_hours']:.1f} hours
2. Transfer takes 30+ minutes and costs ${data['transfer_fee']:.2f}
3. Potential profit if free transfer: ${abs(data['spread_dollars'] * 30 / data['binance']):.4f}
4. Net profit after fees: ${abs(data['spread_dollars'] * 30 / data['binance']) - data['transfer_fee']:.2f}

Please provide analysis in this JSON format:
{{
  "buy_score": 0-10,  // How strongly to BUY on cheaper exchange
  "sell_score": 0-10, // How strongly to SELL on expensive exchange  
  "confidence": 0-10, // Your confidence in this analysis
  "convergence_1h": 0-100, // % chance prices converge in 1 hour
  "convergence_24h": 0-100, // % chance prices converge in 24 hours
  "risk_score": 0-10, // Risk level (10 = highest)
  "recommendation": "BUY/SELL/HOLD",
  "reason": "Brief explanation"
}}

Consider: Transfer fees kill small profits, persistent spreads may not converge, true arbitrage requires pre-funded accounts."""
        
        return prompt
    
    def query_llm(self, model: str, prompt: str) -> Dict:
        """Query a single LLM"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Try to extract JSON
                try:
                    # Look for JSON block
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        return json.loads(json_str)
                    else:
                        # Try to parse whole response
                        return json.loads(response_text)
                except json.JSONDecodeError:
                    logger.error(f"❌ {model}: Failed to parse JSON")
                    return None
            else:
                logger.error(f"❌ {model}: HTTP error {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ {model}: Error: {e}")
            return None
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """Analyze a single symbol with all LLMs"""
        data = self.market_data[symbol]
        prompt = self.create_prompt(symbol, data)
        
        logger.info(f"🔍 Analyzing {symbol} with {len(self.models)} LLMs...")
        
        analyses = []
        for model in self.models:
            logger.info(f"  Querying {model}...")
            result = self.query_llm(model, prompt)
            
            if result:
                analyses.append({
                    "model": model,
                    "analysis": result
                })
                logger.info(f"    ✅ Got analysis from {model}")
            else:
                logger.warning(f"    ⚠️ No analysis from {model}")
        
        # Calculate consensus
        if analyses:
            consensus = self.calculate_consensus(symbol, data, analyses)
            return consensus
        else:
            logger.error(f"❌ No LLM analyses for {symbol}")
            return None
    
    def calculate_consensus(self, symbol: str, data: Dict, analyses: List[Dict]) -> Dict:
        """Calculate consensus from all LLM analyses"""
        
        # Extract scores
        buy_scores = []
        sell_scores = []
        confidences = []
        conv_1h = []
        conv_24h = []
        risks = []
        recommendations = []
        reasons = []
        
        for analysis in analyses:
            a = analysis["analysis"]
            buy_scores.append(a.get("buy_score", 5))
            sell_scores.append(a.get("sell_score", 5))
            confidences.append(a.get("confidence", 5))
            conv_1h.append(a.get("convergence_1h", 50))
            conv_24h.append(a.get("convergence_24h", 50))
            risks.append(a.get("risk_score", 5))
            recommendations.append(a.get("recommendation", "HOLD"))
            reasons.append(a.get("reason", "No reason"))
        
        # Calculate averages
        avg_buy = sum(buy_scores) / len(buy_scores)
        avg_sell = sum(sell_scores) / len(sell_scores)
        avg_conf = sum(confidences) / len(confidences)
        avg_conv_1h = sum(conv_1h) / len(conv_1h)
        avg_conv_24h = sum(conv_24h) / len(conv_24h)
        avg_risk = sum(risks) / len(risks)
        
        # Most common recommendation
        from collections import Counter
        rec_counter = Counter(recommendations)
        final_rec = rec_counter.most_common(1)[0][0]
        rec_confidence = rec_counter[final_rec] / len(recommendations)
        
        # Generate trade advice
        trade_advice = self.generate_trade_advice(symbol, data, final_rec, rec_confidence, avg_risk, avg_conv_1h)
        
        return {
            "symbol": symbol,
            "llm_count": len(analyses),
            "avg_buy_score": round(avg_buy, 2),
            "avg_sell_score": round(avg_sell, 2),
            "avg_confidence": round(avg_conf, 2),
            "avg_convergence_1h": round(avg_conv_1h, 1),
            "avg_convergence_24h": round(avg_conv_24h, 1),
            "avg_risk_score": round(avg_risk, 2),
            "final_recommendation": final_rec,
            "recommendation_confidence": round(rec_confidence, 2),
            "trade_advice": trade_advice,
            "individual_analyses": analyses
        }
    
    def generate_trade_advice(self, symbol: str, data: Dict, recommendation: str, 
                            confidence: float, risk: float, convergence_1h: float) -> str:
        """Generate trade advice based on analysis"""
        
        direction = "Buy Binance, Sell Gemini" if data["spread_percent"] > 0 else "Buy Gemini, Sell Binance"
        profit_if_free = abs(data["spread_dollars"] * 30 / data["binance"])
        net_profit = profit_if_free - data["transfer_fee"]
        
        advice = []
        advice.append(f"📊 {symbol}: {abs(data['spread_percent']):.2f}% spread for {data['duration_hours']:.1f}h")
        advice.append(f"💰 Direction: {direction}")
        advice.append(f"💵 Profit if free: ${profit_if_free:.4f}, Fee: ${data['transfer_fee']:.2f}, Net: ${net_profit:.2f}")
        advice.append(f"🤖 LLM Consensus: {recommendation} ({confidence:.0%} confidence)")
        advice.append(f"⚠️ Risk: {risk:.1f}/10, Convergence (1h): {convergence_1h:.0f}%")
        
        if net_profit <= 0:
            advice.append("❌ DO NOT TRADE: Transfer fees > potential profit")
        elif confidence > 0.7 and risk < 6 and convergence_1h > 60:
            advice.append("✅ CONSIDER TRADING: Good opportunity (if pre-funded)")
        elif confidence < 0.5:
            advice.append("⏸️ WAIT: Low LLM confidence")
        else:
            advice.append("⚠️ CAUTION: Mixed signals, monitor closely")
        
        return "\n".join(advice)
    
    def run_analysis(self):
        """Run analysis on all symbols"""
        print("\n" + "="*80)
        print("🤖 MULTI-LLM ARBITRAGE OPPORTUNITY ANALYSIS")
        print("="*80)
        print(f"Using {len(self.models)} LLMs: {', '.join(self.models)}")
        print()
        
        all_results = []
        
        for symbol in self.market_data.keys():
            print(f"\n🔍 ANALYZING {symbol}:")
            print("-" * 40)
            
            result = self.analyze_symbol(symbol)
            
            if result:
                all_results.append(result)
                
                # Print results
                print(result["trade_advice"])
                print()
                
                # Show individual LLM analyses
                print("🧠 Individual LLM Analyses:")
                for analysis in result["individual_analyses"]:
                    model = analysis["model"].split(":")[0]
                    a = analysis["analysis"]
                    print(f"  • {model}: {a.get('recommendation', 'HOLD')} ", end="")
                    print(f"(Buy:{a.get('buy_score', 5)}, Sell:{a.get('sell_score', 5)})")
                    reason = a.get('reason', 'No reason')
                    if len(reason) > 80:
                        print(f"    Reason: {reason[:80]}...")
                    else:
                        print(f"    Reason: {reason}")
                print()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 SUMMARY RECOMMENDATIONS")
        print("="*80)
        
        for result in all_results:
            symbol = result["symbol"]
            rec = result["final_recommendation"]
            conf = result["recommendation_confidence"]
            risk = result["avg_risk_score"]
            
            if rec == "BUY" and conf > 0.7 and risk < 6:
                print(f"✅ {symbol}: STRONG BUY ({conf:.0%} confidence, risk: {risk:.1f}/10)")
            elif rec == "SELL" and conf > 0.7 and risk < 6:
                print(f"🔻 {symbol}: STRONG SELL ({conf:.0%} confidence, risk: {risk:.1f}/10)")
            elif rec == "HOLD" or conf < 0.5:
                print(f"⏸️  {symbol}: HOLD (confidence: {conf:.0%}, risk: {risk:.1f}/10)")
            else:
                print(f"⚠️  {symbol}: {rec} with caution ({conf:.0%} confidence, risk: {risk:.1f}/10)")
        
        print("\n" + "="*80)
        print("💡 KEY INSIGHTS")
        print("="*80)
        print("1. Transfer fees make small arbitrage unprofitable")
        print("2. LLM consensus helps avoid emotional trading")
        print("3. Persistent spreads (>2h) unlikely to converge quickly")
        print("4. Best opportunities: Large spreads (>3%) + Low fees")
        print("5. Consider pre-funded accounts or different assets")
        print("="*80)
        
        # Save results
        with open("llm_arbitrage_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        print("\n💾 Results saved to 'llm_arbitrage_results.json'")

def main():
    """Main function"""
    analyzer = MultiLLMArbitrageAnalyzer()
    
    print("🚀 Starting Multi-LLM Arbitrage Analyzer...")
    print("This will analyze YFI, FIL, and MANA arbitrage opportunities")
    print("Using local Ollama LLMs for consensus analysis")
    print()
    
    try:
        analyzer.run_analysis()
    except Exception as e:
        logger.error(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()