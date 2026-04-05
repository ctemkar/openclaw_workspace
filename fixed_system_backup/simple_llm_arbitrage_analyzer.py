#!/usr/bin/env python3
"""
SIMPLE LLM ARBITRAGE ANALYZER
Uses llama3.1 (fastest) to analyze arbitrage opportunities
"""

import json
import time
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simple_llm_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleLLMAnalyzer:
    """Simple LLM arbitrage analyzer using llama3.1"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.1:latest"  # Fast, reliable model
        
        # Current market data
        self.markets = {
            "YFI": {
                "binance": 2423.00,
                "gemini": 2458.82,
                "spread_percent": 1.46,
                "duration_hours": 2.5,
                "transfer_fee": 8.0
            },
            "FIL": {
                "binance": 0.8230,
                "gemini": 0.8179,
                "spread_percent": -0.62,
                "duration_hours": 1.2,
                "transfer_fee": 5.0
            }
        }
    
    def create_prompt(self, symbol: str, data: dict) -> str:
        """Create analysis prompt"""
        
        direction = "Gemini is CHEAPER" if data["spread_percent"] < 0 else "Binance is CHEAPER"
        abs_spread = abs(data["spread_percent"])
        
        prompt = f"""You are a crypto trading analyst. Analyze this arbitrage opportunity:

SYMBOL: {symbol}
Binance: ${data['binance']:,.4f}
Gemini: ${data['gemini']:,.4f}
Spread: {abs_spread:.2f}% ({direction})
Duration: {data['duration_hours']:.1f} hours
Transfer fee: ${data['transfer_fee']:.2f}
Trade size: $30

Key issue: Transfer fee (${data['transfer_fee']:.2f}) may exceed potential profit.

Question: Should we attempt this arbitrage trade?

Provide analysis in this exact JSON format:
{{
  "analysis": "Brief analysis of the opportunity",
  "profit_potential": "high/medium/low",
  "risk": "high/medium/low", 
  "transfer_issue": "yes/no",
  "recommendation": "trade/avoid/monitor",
  "reason": "1-2 sentence explanation"
}}"""
        
        return prompt
    
    def query_llm(self, prompt: str) -> dict:
        """Query the LLM"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 200}
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                # Try to extract JSON
                try:
                    # Look for JSON block
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        return json.loads(json_str)
                    else:
                        # Fallback: create simple analysis
                        return {
                            "analysis": "Could not parse full analysis",
                            "profit_potential": "unknown",
                            "risk": "unknown",
                            "transfer_issue": "yes",
                            "recommendation": "avoid",
                            "reason": "LLM response parsing failed"
                        }
                except json.JSONDecodeError:
                    logger.error("❌ Failed to parse JSON from LLM")
                    return None
            else:
                logger.error(f"❌ HTTP error {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    def analyze_market(self, symbol: str, data: dict) -> dict:
        """Analyze a single market"""
        print(f"\n🔍 Analyzing {symbol} arbitrage...")
        print(f"   Spread: {abs(data['spread_percent']):.2f}% for {data['duration_hours']:.1f}h")
        print(f"   Binance: ${data['binance']:,.4f}, Gemini: ${data['gemini']:,.4f}")
        
        prompt = self.create_prompt(symbol, data)
        result = self.query_llm(prompt)
        
        if result:
            print(f"   🤖 LLM Analysis:")
            print(f"      • Analysis: {result.get('analysis', 'N/A')}")
            print(f"      • Profit Potential: {result.get('profit_potential', 'N/A')}")
            print(f"      • Risk: {result.get('risk', 'N/A')}")
            print(f"      • Transfer Issue: {result.get('transfer_issue', 'N/A')}")
            print(f"      • Recommendation: {result.get('recommendation', 'N/A')}")
            print(f"      • Reason: {result.get('reason', 'N/A')}")
            
            # Calculate actual numbers
            spread_value = abs(data['binance'] - data['gemini'])
            profit_if_free = (spread_value / data['binance']) * 30  # For $30 trade
            net_profit = profit_if_free - data['transfer_fee']
            
            print(f"\n   📊 Reality Check:")
            print(f"      • Spread value: ${spread_value:.4f}")
            print(f"      • Profit if free transfer: ${profit_if_free:.4f}")
            print(f"      • Transfer fee: ${data['transfer_fee']:.2f}")
            print(f"      • Net profit: ${net_profit:.2f}")
            
            if net_profit <= 0:
                print(f"      ❌ VERDICT: DO NOT TRADE (fees > profit)")
            elif result.get('recommendation') == 'trade' and result.get('risk') == 'low':
                print(f"      ✅ VERDICT: CONSIDER TRADING")
            else:
                print(f"      ⚠️ VERDICT: {result.get('recommendation', 'avoid').upper()} (caution advised)")
            
            return result
        else:
            print(f"   ❌ Failed to get LLM analysis")
            return None
    
    def run_analysis(self):
        """Run analysis on all markets"""
        print("\n" + "="*80)
        print("🤖 LLM ARBITRAGE OPPORTUNITY ANALYSIS")
        print("="*80)
        print(f"Using model: {self.model}")
        print()
        
        results = {}
        
        for symbol, data in self.markets.items():
            result = self.analyze_market(symbol, data)
            if result:
                results[symbol] = result
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 SUMMARY")
        print("="*80)
        
        for symbol, result in results.items():
            data = self.markets[symbol]
            spread = abs(data['spread_percent'])
            rec = result.get('recommendation', 'avoid')
            risk = result.get('risk', 'high')
            
            if rec == 'trade' and risk == 'low':
                print(f"✅ {symbol}: {spread:.2f}% - GOOD opportunity")
            elif rec == 'trade' and risk == 'medium':
                print(f"⚠️  {symbol}: {spread:.2f}% - MODERATE opportunity")
            elif rec == 'avoid':
                print(f"❌ {symbol}: {spread:.2f}% - AVOID")
            else:
                print(f"⏸️  {symbol}: {spread:.2f}% - MONITOR")
        
        print("\n" + "="*80)
        print("💡 KEY TAKEAWAYS")
        print("="*80)
        print("1. Transfer fees ($5-$20) kill most small arbitrage")
        print("2. LLM helps identify when spreads are 'real' vs 'persistent'")
        print("3. Best opportunities: Large spreads (>3%) + Low fees")
        print("4. Current reality: Most opportunities not profitable")
        print("="*80)
        
        # Save results
        with open("llm_analysis_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Results saved to 'llm_analysis_results.json'")

def main():
    """Main function"""
    analyzer = SimpleLLMAnalyzer()
    
    print("🚀 Starting LLM Arbitrage Analyzer...")
    print("Analyzing YFI and FIL arbitrage opportunities")
    print("Using llama3.1 for fast analysis")
    print()
    
    try:
        analyzer.run_analysis()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()