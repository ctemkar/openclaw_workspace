#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis (Simulation)
Analyzes market conditions and provides trading recommendations
without executing actual trades (for demonstration purposes)
"""

import json
import random
from datetime import datetime
from typing import Dict, List

# Configuration
CAPITAL = 1000.0
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
TRADING_PAIRS = ["BTCUSD", "ETHUSD"]

# Simulated market data (would come from API in real scenario)
SIMULATED_PRICES = {
    "BTCUSD": 65000.0,
    "ETHUSD": 3500.0
}

SIMULATED_SUPPORT_RESISTANCE = {
    "BTCUSD": {"support": 64000.0, "resistance": 66000.0},
    "ETHUSD": {"support": 3400.0, "resistance": 3600.0}
}

class MarketAnalyzer:
    def __init__(self):
        self.trades_today = 0
        self.last_analysis_time = None
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get simulated market data for analysis"""
        current_price = SIMULATED_PRICES[symbol]
        support = SIMULATED_SUPPORT_RESISTANCE[symbol]["support"]
        resistance = SIMULATED_SUPPORT_RESISTANCE[symbol]["resistance"]
        
        # Add some random variation to simulate market movement
        price_variation = random.uniform(-0.02, 0.02)  # ±2%
        current_price *= (1 + price_variation)
        
        # Calculate distances
        distance_to_support = ((current_price - support) / current_price) * 100
        distance_to_resistance = ((resistance - current_price) / current_price) * 100
        
        # Determine trend
        trend = "NEUTRAL"
        if distance_to_support < 1.5:  # Near support
            trend = "BULLISH"
        elif distance_to_resistance < 1.5:  # Near resistance
            trend = "BEARISH"
        
        # Calculate volume (simulated)
        volume = random.uniform(1000000, 5000000)  # $1M-$5M volume
        
        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "support": support,
            "resistance": resistance,
            "distance_to_support_pct": round(distance_to_support, 2),
            "distance_to_resistance_pct": round(distance_to_resistance, 2),
            "trend": trend,
            "volume": round(volume, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate conservative position size"""
        trade_capital = CAPITAL * 0.5  # Use 50% of capital per trade
        position_size = trade_capital / price
        return round(position_size, 8)
    
    def conservative_strategy(self, analysis: Dict) -> Dict:
        """Apply conservative trading strategy rules"""
        symbol = analysis["symbol"]
        
        # Rule 1: Only consider trading if we haven't reached daily limit
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return {
                "symbol": symbol,
                "action": "HOLD",
                "reason": f"Maximum daily trades ({MAX_TRADES_PER_DAY}) reached"
            }
        
        # Rule 2: Buy only when near support with bullish trend
        if analysis["trend"] == "BULLISH" and analysis["distance_to_support_pct"] < 1.0:
            position_size = self.calculate_position_size(analysis["price"])
            stop_loss = analysis["price"] * (1 - STOP_LOSS_PCT)
            take_profit = analysis["price"] * (1 + TAKE_PROFIT_PCT)
            
            self.trades_today += 1
            
            return {
                "symbol": symbol,
                "action": "BUY",
                "price": analysis["price"],
                "position_size": position_size,
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward_ratio": round(TAKE_PROFIT_PCT / STOP_LOSS_PCT, 2),
                "reason": f"Near support ({analysis['distance_to_support_pct']}%), bullish trend detected"
            }
        
        # Rule 3: Sell only when near resistance with bearish trend
        elif analysis["trend"] == "BEARISH" and analysis["distance_to_resistance_pct"] < 1.0:
            position_size = self.calculate_position_size(analysis["price"])
            stop_loss = analysis["price"] * (1 + STOP_LOSS_PCT)
            take_profit = analysis["price"] * (1 - TAKE_PROFIT_PCT)
            
            self.trades_today += 1
            
            return {
                "symbol": symbol,
                "action": "SELL",
                "price": analysis["price"],
                "position_size": position_size,
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "risk_reward_ratio": round(TAKE_PROFIT_PCT / STOP_LOSS_PCT, 2),
                "reason": f"Near resistance ({analysis['distance_to_resistance_pct']}%), bearish trend detected"
            }
        
        # Rule 4: Hold otherwise
        else:
            return {
                "symbol": symbol,
                "action": "HOLD",
                "reason": f"Market conditions not favorable. Trend: {analysis['trend']}, "
                         f"Support distance: {analysis['distance_to_support_pct']}%, "
                         f"Resistance distance: {analysis['distance_to_resistance_pct']}%"
            }
    
    def analyze_all_pairs(self) -> List[Dict]:
        """Analyze all trading pairs"""
        results = []
        
        for symbol in TRADING_PAIRS:
            # Get market analysis
            analysis = self.get_market_data(symbol)
            
            # Apply trading strategy
            trade_decision = self.conservative_strategy(analysis)
            
            # Combine analysis with decision
            result = {
                "analysis": analysis,
                "decision": trade_decision
            }
            results.append(result)
        
        return results

def generate_summary(analyzer: MarketAnalyzer, results: List[Dict]) -> str:
    """Generate plain text summary for cron delivery"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary_lines = [
        "=== CONSERVATIVE CRYPTO TRADING ANALYSIS ===",
        f"Time: {timestamp} (Asia/Bangkok)",
        f"Capital: ${CAPITAL}",
        f"Risk Parameters: {STOP_LOSS_PCT*100}% Stop Loss, {TAKE_PROFIT_PCT*100}% Take Profit",
        f"Max Trades/Day: {MAX_TRADES_PER_DAY}",
        f"Trades Executed Today: {analyzer.trades_today}/{MAX_TRADES_PER_DAY}",
        ""
    ]
    
    for result in results:
        analysis = result["analysis"]
        decision = result["decision"]
        
        summary_lines.extend([
            f"--- {analysis['symbol']} Analysis ---",
            f"Current Price: ${analysis['price']:,}",
            f"Support: ${analysis['support']:,} (Distance: {analysis['distance_to_support_pct']}%)",
            f"Resistance: ${analysis['resistance']:,} (Distance: {analysis['distance_to_resistance_pct']}%)",
            f"Trend: {analysis['trend']}",
            f"Volume: ${analysis['volume']:,.2f}",
            f"Decision: {decision['action']}",
            f"Reason: {decision['reason']}"
        ])
        
        if decision['action'] in ['BUY', 'SELL']:
            summary_lines.extend([
                f"Position Size: {decision['position_size']:.8f}",
                f"Stop Loss: ${decision['stop_loss']:,}",
                f"Take Profit: ${decision['take_profit']:,}",
                f"Risk/Reward Ratio: {decision['risk_reward_ratio']}:1"
            ])
        
        summary_lines.append("")
    
    # Add trading recommendations
    summary_lines.append("=== TRADING RECOMMENDATIONS ===")
    
    buy_signals = [r for r in results if r["decision"]["action"] == "BUY"]
    sell_signals = [r for r in results if r["decision"]["action"] == "SELL"]
    
    if buy_signals:
        summary_lines.append("BUY SIGNALS DETECTED:")
        for signal in buy_signals:
            s = signal["analysis"]["symbol"]
            p = signal["analysis"]["price"]
            summary_lines.append(f"  - {s}: ${p:,} (Near support, bullish trend)")
    
    if sell_signals:
        summary_lines.append("SELL SIGNALS DETECTED:")
        for signal in sell_signals:
            s = signal["analysis"]["symbol"]
            p = signal["analysis"]["price"]
            summary_lines.append(f"  - {s}: ${p:,} (Near resistance, bearish trend)")
    
    if not buy_signals and not sell_signals:
        summary_lines.append("No strong trading signals detected.")
        summary_lines.append("Recommendation: Maintain current positions or stay in cash.")
    
    summary_lines.extend([
        "",
        "=== RISK MANAGEMENT ===",
        f"• Maximum position size: ${CAPITAL * 0.5:,.2f} per trade",
        f"• Stop loss: {STOP_LOSS_PCT*100}% from entry",
        f"• Take profit: {TAKE_PROFIT_PCT*100}% from entry",
        f"• Daily trade limit: {MAX_TRADES_PER_DAY} trades",
        "",
        "Note: This is a simulated analysis. Actual trading requires:",
        "1. Gemini API credentials (GEMINI_API_KEY, GEMINI_API_SECRET)",
        "2. Real market data from Gemini API",
        "3. Proper risk assessment and capital allocation",
        "=" * 50
    ])
    
    return "\n".join(summary_lines)

def main():
    """Main analysis function"""
    print("Running conservative crypto trading analysis...")
    
    # Initialize analyzer
    analyzer = MarketAnalyzer()
    
    # Analyze all trading pairs
    results = analyzer.analyze_all_pairs()
    
    # Generate summary
    summary = generate_summary(analyzer, results)
    
    # Print to console
    print(summary)
    
    # Save to file
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "capital": CAPITAL,
        "trades_executed": analyzer.trades_today,
        "max_trades_per_day": MAX_TRADES_PER_DAY,
        "analysis_results": results,
        "risk_parameters": {
            "stop_loss_pct": STOP_LOSS_PCT,
            "take_profit_pct": TAKE_PROFIT_PCT
        }
    }
    
    with open("crypto_analysis_output.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    # Also save plain text summary
    with open("crypto_analysis_summary.txt", "w") as f:
        f.write(summary)
    
    print(f"\nAnalysis saved to crypto_analysis_output.json and crypto_analysis_summary.txt")
    
    return summary

if __name__ == "__main__":
    main()