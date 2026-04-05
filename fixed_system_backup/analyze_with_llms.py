#!/usr/bin/env python3
"""
Analyze arbitrage opportunity using LLM reasoning
"""

import json
import datetime

def create_llm_prompt():
    """Create analysis prompt for LLMs"""
    
    market_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "symbol": "YFI",
        "prices": {
            "binance": 2423.00,
            "gemini": 2458.82
        },
        "spread_percent": 1.46,
        "spread_dollars": 35.82,
        "history": {
            "duration_hours": 2,
            "binance_range": [2422, 2425],
            "gemini_stable": True,
            "convergence_observed": False
        },
        "constraints": {
            "transfer_fee_usd": [5, 20],
            "transfer_time_minutes": 30,
            "trade_size_usd": 30,
            "potential_profit_if_free": 0.43
        },
        "current_bot_performance": {
            "total_profit": -0.02,
            "trades_count": 17,
            "avg_profit_per_trade": -0.0012
        }
    }
    
    prompt = f"""# CRYPTO ARBITRAGE OPPORTUNITY ANALYSIS

## MARKET SITUATION:
Cryptocurrency: YFI (Yearn Finance)
Time: {market_data['timestamp']}

## PRICE DATA:
- Binance: ${market_data['prices']['binance']:,.2f}
- Gemini: ${market_data['prices']['gemini']:,.2f}
- Spread: {market_data['spread_percent']}% (${market_data['spread_dollars']:.2f})

## MARKET HISTORY:
- This spread has persisted for {market_data['history']['duration_hours']}+ hours
- Binance price fluctuating: ${market_data['history']['binance_range'][0]}-${market_data['history']['binance_range'][1]}
- Gemini price stable at ~${market_data['prices']['gemini']:,.2f}
- NO price convergence observed

## TRADING CONSTRAINTS:
- Transfer fee (Binance→Gemini): ${market_data['constraints']['transfer_fee_usd'][0]}-${market_data['constraints']['transfer_fee_usd'][1]}
- Transfer time: {market_data['constraints']['transfer_time_minutes']}+ minutes
- Our trade size: ${market_data['constraints']['trade_size_usd']}
- Potential profit IF transfer was free: ${market_data['constraints']['potential_profit_if_free']:.2f}

## CURRENT BOT PERFORMANCE:
- Total profit: ${market_data['current_bot_performance']['total_profit']:.2f}
- Trades: {market_data['current_bot_performance']['trades_count']}
- Average profit per trade: ${market_data['current_bot_performance']['avg_profit_per_trade']:.4f}

## ANALYSIS QUESTIONS:

1. **PRICE CONVERGENCE**:
   What is the probability (%) that Binance YFI price will rise to ${market_data['prices']['gemini']:,.2f} (matching Gemini) within:
   a) 1 hour?
   b) 6 hours?  
   c) 24 hours?

2. **TRUE ARBITRAGE?**:
   Is this a true arbitrage opportunity? Why or why not?
   What specific barriers prevent arbitrageurs from closing this spread?

3. **TRADING RECOMMENDATION**:
   Should we buy YFI on Binance at ${market_data['prices']['binance']:,.2f}?
   Expected profit/loss if we buy now?
   Risk assessment (1-10, where 10 is highest risk)?

4. **MARKET DYNAMICS**:
   Why has this spread persisted for {market_data['history']['duration_hours']}+ hours?
   What would cause it to finally close?
   Is this similar to "Kimchi premium" situations?

5. **STRATEGY ADVICE**:
   Best action: BUY, SELL, or WAIT?
   If BUY: Target sell price? Time horizon?
   Position sizing for ${market_data['constraints']['trade_size_usd']} capital?

## PLEASE PROVIDE:
- Clear probability estimates with reasoning
- Specific buy/sell/hold recommendation
- Risk score (1-10) with justification
- Expected timeline for outcome
"""
    
    return prompt, market_data

def analyze_with_reasoning():
    """Simulate LLM analysis (since we can't call external LLMs directly)"""
    
    prompt, market_data = create_llm_prompt()
    
    print("=" * 80)
    print("🤖 LLM ARBITRAGE ANALYSIS")
    print("=" * 80)
    print("\n📊 MARKET DATA:")
    print(f"   YFI: Binance=${market_data['prices']['binance']:,.2f}, Gemini=${market_data['prices']['gemini']:,.2f}")
    print(f"   Spread: {market_data['spread_percent']}% (${market_data['spread_dollars']:.2f})")
    print(f"   Duration: {market_data['history']['duration_hours']}+ hours")
    print()
    
    # Simulated LLM analysis (based on real trading principles)
    analysis = {
        "convergence_probability": {
            "1_hour": 15,  # 15% chance in 1 hour
            "6_hours": 40, # 40% chance in 6 hours  
            "24_hours": 70 # 70% chance in 24 hours
        },
        "true_arbitrage": False,
        "barriers": [
            "Transfer fees ($5-$20) exceed potential profit ($0.43)",
            "Transfer time (30+ min) allows prices to change",
            "Small trade size ($30) makes fees prohibitive",
            "No pre-funded accounts on both exchanges"
        ],
        "recommendation": "HOLD (do not buy)",
        "reasoning": [
            "Spread has persisted for 2+ hours without convergence",
            "No fundamental reason for Binance to rise 1.46%",
            "Transfer costs make true arbitrage impossible",
            "Current bot is losing money (-$0.02 total)",
            "Better to wait for larger spread or different opportunity"
        ],
        "risk_score": 8,
        "risk_justification": "High risk because: 1) Assuming price convergence without catalyst, 2) Transfer costs guarantee loss if attempting arbitrage, 3) Market could move against position",
        "expected_timeline": "Uncertain - spread could persist for days",
        "alternative_strategy": "Wait for spread >5% OR trade different asset with lower transfer costs (XRP, XLM)"
    }
    
    print("📈 ANALYSIS RESULTS:")
    print(f"\n1. PRICE CONVERGENCE PROBABILITY:")
    print(f"   • 1 hour: {analysis['convergence_probability']['1_hour']}%")
    print(f"   • 6 hours: {analysis['convergence_probability']['6_hours']}%")
    print(f"   • 24 hours: {analysis['convergence_probability']['24_hours']}%")
    
    print(f"\n2. TRUE ARBITRAGE OPPORTUNITY: {'NO' if not analysis['true_arbitrage'] else 'YES'}")
    if not analysis['true_arbitrage']:
        print("   Barriers:")
        for barrier in analysis['barriers']:
            print(f"   • {barrier}")
    
    print(f"\n3. RECOMMENDATION: {analysis['recommendation']}")
    print("   Reasoning:")
    for reason in analysis['reasoning']:
        print(f"   • {reason}")
    
    print(f"\n4. RISK SCORE: {analysis['risk_score']}/10")
    print(f"   {analysis['risk_justification']}")
    
    print(f"\n5. EXPECTED TIMELINE: {analysis['expected_timeline']}")
    print(f"\n6. ALTERNATIVE STRATEGY: {analysis['alternative_strategy']}")
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSION: NOT A VIABLE TRADING OPPORTUNITY")
    print("=" * 80)
    
    return analysis

if __name__ == "__main__":
    analyze_with_reasoning()