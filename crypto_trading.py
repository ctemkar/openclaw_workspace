#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Uses Gemini API with $1,000 capital
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Analyzes BTC/USD and ETH/USD
"""

import os
import json
import time
import requests
import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import hmac
import base64

# Configuration
CAPITAL = 1000.0  # USD
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
SYMBOLS = ["BTCUSD", "ETHUSD"]

# Gemini API Configuration (would need actual API keys in production)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_SECRET = os.getenv("GEMINI_API_SECRET", "")
GEMINI_API_URL = "https://api.gemini.com/v1"

class ConservativeCryptoTrader:
    def __init__(self):
        self.capital = CAPITAL
        self.positions = {}
        self.trades_today = 0
        self.last_trade_date = None
        self.trade_history = []
        
    def reset_daily_counter(self):
        """Reset daily trade counter if it's a new day"""
        today = datetime.date.today()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get current market data for a symbol"""
        try:
            # For BTCUSD and ETHUSD, we'll use mock data for demonstration
            # In production, this would call Gemini API
            if symbol == "BTCUSD":
                return {
                    "symbol": symbol,
                    "price": 85000.0,  # Mock price
                    "volume": 15000.0,
                    "bid": 84950.0,
                    "ask": 85050.0,
                    "change_24h": 0.02,  # +2%
                    "high_24h": 86000.0,
                    "low_24h": 84000.0
                }
            elif symbol == "ETHUSD":
                return {
                    "symbol": symbol,
                    "price": 4500.0,  # Mock price
                    "volume": 8000.0,
                    "bid": 4490.0,
                    "ask": 4510.0,
                    "change_24h": 0.015,  # +1.5%
                    "high_24h": 4600.0,
                    "low_24h": 4400.0
                }
        except Exception as e:
            print(f"Error getting market data for {symbol}: {e}")
            return None
    
    def analyze_market_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment and technical indicators"""
        market_data = self.get_market_data(symbol)
        if not market_data:
            return {"signal": "HOLD", "confidence": 0.0}
        
        price = market_data["price"]
        change_24h = market_data["change_24h"]
        high_24h = market_data["high_24h"]
        low_24h = market_data["low_24h"]
        
        # Conservative strategy rules
        signal = "HOLD"
        confidence = 0.0
        
        # Rule 1: Buy if price is near 24h low and positive momentum
        if price <= low_24h * 1.02 and change_24h > -0.01:  # Within 2% of low, not dropping too much
            signal = "BUY"
            confidence = 0.6
        
        # Rule 2: Sell if price is near 24h high and showing weakness
        elif price >= high_24h * 0.98 and change_24h < 0.01:  # Within 2% of high, not rising much
            signal = "SELL"
            confidence = 0.6
        
        # Rule 3: Strong momentum signals
        elif change_24h > 0.03:  # Strong upward momentum
            signal = "BUY"
            confidence = 0.7
        elif change_24h < -0.03:  # Strong downward momentum
            signal = "SELL"
            confidence = 0.7
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence,
            "price": price,
            "change_24h": change_24h,
            "support": low_24h,
            "resistance": high_24h
        }
    
    def calculate_position_size(self, symbol: str, price: float) -> float:
        """Calculate conservative position size (max 20% of capital per trade)"""
        max_position_value = self.capital * 0.2  # 20% of capital
        position_size = max_position_value / price
        
        # Round down to appropriate decimal places
        if symbol == "BTCUSD":
            return round(position_size, 6)  # BTC to 6 decimals
        elif symbol == "ETHUSD":
            return round(position_size, 4)  # ETH to 4 decimals
        return round(position_size, 4)
    
    def execute_trade(self, symbol: str, signal: str, price: float, confidence: float) -> Dict:
        """Execute a trade (mock for demonstration)"""
        self.reset_daily_counter()
        
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return {
                "status": "REJECTED",
                "reason": f"Maximum trades per day ({MAX_TRADES_PER_DAY}) reached"
            }
        
        if confidence < 0.5:
            return {
                "status": "REJECTED",
                "reason": f"Confidence too low: {confidence:.2f}"
            }
        
        position_size = self.calculate_position_size(symbol, price)
        trade_value = position_size * price
        
        if trade_value > self.capital * 0.25:  # Extra conservative check
            position_size = (self.capital * 0.2) / price
            if symbol == "BTCUSD":
                position_size = round(position_size, 6)
            elif symbol == "ETHUSD":
                position_size = round(position_size, 4)
            trade_value = position_size * price
        
        # Mock trade execution
        trade_id = f"TRADE_{int(time.time())}_{symbol}"
        trade = {
            "trade_id": trade_id,
            "symbol": symbol,
            "side": signal,
            "price": price,
            "quantity": position_size,
            "value": trade_value,
            "timestamp": datetime.datetime.now().isoformat(),
            "stop_loss": price * (1 - STOP_LOSS) if signal == "BUY" else price * (1 + STOP_LOSS),
            "take_profit": price * (1 + TAKE_PROFIT) if signal == "BUY" else price * (1 - TAKE_PROFIT),
            "confidence": confidence
        }
        
        self.trades_today += 1
        self.trade_history.append(trade)
        
        # Update positions
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(trade)
        
        return {
            "status": "EXECUTED",
            "trade": trade
        }
    
    def run_analysis(self) -> Dict:
        """Run full trading analysis"""
        self.reset_daily_counter()
        
        analysis_results = []
        trades_executed = []
        
        print(f"=== Conservative Crypto Trading Analysis ===")
        print(f"Time: {datetime.datetime.now()}")
        print(f"Capital: ${self.capital:.2f}")
        print(f"Daily Trade Limit: {MAX_TRADES_PER_DAY}")
        print(f"Trades Today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"Risk Parameters: {STOP_LOSS*100}% Stop-Loss, {TAKE_PROFIT*100}% Take-Profit")
        print()
        
        for symbol in SYMBOLS:
            print(f"Analyzing {symbol}...")
            
            # Get market sentiment
            sentiment = self.analyze_market_sentiment(symbol)
            analysis_results.append(sentiment)
            
            print(f"  Price: ${sentiment['price']:.2f}")
            print(f"  24h Change: {sentiment['change_24h']*100:.2f}%")
            print(f"  Support: ${sentiment['support']:.2f}")
            print(f"  Resistance: ${sentiment['resistance']:.2f}")
            print(f"  Signal: {sentiment['signal']} (Confidence: {sentiment['confidence']:.2f})")
            
            # Execute trade if signal is strong enough
            if sentiment["signal"] != "HOLD" and self.trades_today < MAX_TRADES_PER_DAY:
                trade_result = self.execute_trade(
                    symbol, 
                    sentiment["signal"], 
                    sentiment["price"], 
                    sentiment["confidence"]
                )
                
                if trade_result["status"] == "EXECUTED":
                    trades_executed.append(trade_result["trade"])
                    print(f"  ✓ Trade Executed: {sentiment['signal']} {trade_result['trade']['quantity']} {symbol} @ ${trade_result['trade']['price']:.2f}")
                else:
                    print(f"  ✗ Trade Rejected: {trade_result['reason']}")
            
            print()
        
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": analysis_results,
            "trades_executed": trades_executed,
            "trades_today": self.trades_today,
            "max_trades_per_day": MAX_TRADES_PER_DAY,
            "capital": self.capital,
            "risk_parameters": {
                "stop_loss": f"{STOP_LOSS*100}%",
                "take_profit": f"{TAKE_PROFIT*100}%"
            }
        }
    
    def generate_summary(self, results: Dict) -> str:
        """Generate plain text summary for delivery"""
        summary = []
        summary.append("CONSERVATIVE CRYPTO TRADING SUMMARY")
        summary.append("=" * 40)
        summary.append(f"Analysis Time: {results['timestamp']}")
        summary.append(f"Capital: ${results['capital']:.2f}")
        summary.append(f"Trades Executed Today: {results['trades_today']}/{results['max_trades_per_day']}")
        summary.append(f"Risk Parameters: {results['risk_parameters']['stop_loss']} Stop-Loss, {results['risk_parameters']['take_profit']} Take-Profit")
        summary.append("")
        
        if results['trades_executed']:
            summary.append("TRADES EXECUTED:")
            summary.append("-" * 40)
            for trade in results['trades_executed']:
                summary.append(f"Trade ID: {trade['trade_id']}")
                summary.append(f"Symbol: {trade['symbol']}")
                summary.append(f"Side: {trade['side']}")
                summary.append(f"Quantity: {trade['quantity']}")
                summary.append(f"Price: ${trade['price']:.2f}")
                summary.append(f"Value: ${trade['value']:.2f}")
                summary.append(f"Stop-Loss: ${trade['stop_loss']:.2f}")
                summary.append(f"Take-Profit: ${trade['take_profit']:.2f}")
                summary.append(f"Confidence: {trade['confidence']:.2f}")
                summary.append("")
        else:
            summary.append("No trades executed - conservative conditions not met")
            summary.append("")
        
        summary.append("MARKET ANALYSIS:")
        summary.append("-" * 40)
        for analysis in results['analysis']:
            summary.append(f"{analysis['symbol']}:")
            summary.append(f"  Price: ${analysis['price']:.2f}")
            summary.append(f"  24h Change: {analysis['change_24h']*100:+.2f}%")
            summary.append(f"  Support: ${analysis['support']:.2f}")
            summary.append(f"  Resistance: ${analysis['resistance']:.2f}")
            summary.append(f"  Signal: {analysis['signal']} (Confidence: {analysis['confidence']:.2f})")
            summary.append("")
        
        summary.append("RECOMMENDATION:")
        summary.append("-" * 40)
        if results['trades_today'] >= results['max_trades_per_day']:
            summary.append("Maximum daily trades reached. No further trading recommended.")
        elif not results['trades_executed']:
            summary.append("Conservative strategy suggests holding positions. Market conditions do not meet entry criteria.")
        else:
            summary.append(f"Executed {len(results['trades_executed'])} trades. Monitor positions for stop-loss/take-profit triggers.")
        
        summary.append("")
        summary.append("END OF REPORT")
        
        return "\n".join(summary)

def main():
    """Main trading function"""
    trader = ConservativeCryptoTrader()
    
    print("Starting conservative crypto trading analysis...")
    print(f"Date/Time: {datetime.datetime.now()}")
    print()
    
    # Run analysis
    results = trader.run_analysis()
    
    # Generate summary
    summary = trader.generate_summary(results)
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("TRADING SUMMARY FOR DELIVERY:")
    print("=" * 60)
    print(summary)
    
    # Also save to file for reference
    with open("trading_summary.txt", "w") as f:
        f.write(summary)
    
    return summary

if __name__ == "__main__":
    main()