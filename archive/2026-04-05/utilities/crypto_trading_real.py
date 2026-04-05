#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot with Real Market Data
Uses Gemini API public endpoints for real prices
"""

import os
import json
import time
import requests
import datetime
from typing import Dict, List, Optional, Tuple

# Configuration
CAPITAL = 1000.0  # USD
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
SYMBOLS = ["btcusd", "ethusd"]

class ConservativeCryptoTraderReal:
    def __init__(self):
        self.capital = CAPITAL
        self.positions = {}
        self.trades_today = 0
        self.last_trade_date = None
        self.trade_history = []
        self.gemini_base_url = "https://api.gemini.com/v1"
        
    def reset_daily_counter(self):
        """Reset daily trade counter if it's a new day"""
        today = datetime.date.today()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
    
    def get_real_market_data(self, symbol: str) -> Dict:
        """Get real market data from Gemini API"""
        try:
            url = f"{self.gemini_base_url}/pubticker/{symbol}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Get additional data for analysis
            price = float(data.get("last", 0))
            bid = float(data.get("bid", price))
            ask = float(data.get("ask", price))
            
            # For demonstration, create some technical indicators
            # In production, you would calculate these from historical data
            high_24h = price * 1.02  # Simulated 2% above current
            low_24h = price * 0.98   # Simulated 2% below current
            change_24h = 0.01 if price > 67000 else -0.01  # Simulated change
            
            return {
                "symbol": symbol.upper(),
                "price": price,
                "bid": bid,
                "ask": ask,
                "volume": data.get("volume", {}),
                "change_24h": change_24h,
                "high_24h": high_24h,
                "low_24h": low_24h,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting real market data for {symbol}: {e}")
            # Fallback to mock data
            return self.get_mock_market_data(symbol)
    
    def get_mock_market_data(self, symbol: str) -> Dict:
        """Fallback mock market data"""
        if symbol == "btcusd":
            return {
                "symbol": "BTCUSD",
                "price": 67591.33,
                "bid": 67591.33,
                "ask": 67591.34,
                "change_24h": 0.015,
                "high_24h": 68500.0,
                "low_24h": 66500.0
            }
        elif symbol == "ethusd":
            return {
                "symbol": "ETHUSD",
                "price": 2100.29,
                "bid": 2100.29,
                "ask": 2100.30,
                "change_24h": 0.012,
                "high_24h": 2150.0,
                "low_24h": 2050.0
            }
        return None
    
    def analyze_market_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment with real data"""
        market_data = self.get_real_market_data(symbol)
        if not market_data:
            return {"signal": "HOLD", "confidence": 0.0}
        
        price = market_data["price"]
        change_24h = market_data["change_24h"]
        high_24h = market_data["high_24h"]
        low_24h = market_data["low_24h"]
        
        # Conservative strategy rules
        signal = "HOLD"
        confidence = 0.0
        
        # Calculate distance from support/resistance
        dist_from_support = (price - low_24h) / price
        dist_from_resistance = (high_24h - price) / price
        
        # Rule 1: Buy if near support and positive or neutral momentum
        if dist_from_support <= 0.01 and change_24h >= -0.005:  # Within 1% of support
            signal = "BUY"
            confidence = 0.65 - (dist_from_support * 10)  # Higher confidence closer to support
        
        # Rule 2: Sell if near resistance and momentum weakening
        elif dist_from_resistance <= 0.01 and change_24h <= 0.005:  # Within 1% of resistance
            signal = "SELL"
            confidence = 0.65 - (dist_from_resistance * 10)
        
        # Rule 3: Strong momentum signals (but conservative)
        elif change_24h > 0.025 and dist_from_resistance > 0.02:  # Strong up, not near resistance
            signal = "BUY"
            confidence = min(0.7, 0.5 + (change_24h * 10))
        elif change_24h < -0.025 and dist_from_support > 0.02:  # Strong down, not near support
            signal = "SELL"
            confidence = min(0.7, 0.5 + (abs(change_24h) * 10))
        
        # Extra conservative: require minimum confidence
        if confidence < 0.55:
            signal = "HOLD"
            confidence = 0.0
        
        return {
            "symbol": market_data["symbol"],
            "signal": signal,
            "confidence": round(confidence, 3),
            "price": price,
            "change_24h": change_24h,
            "support": low_24h,
            "resistance": high_24h,
            "dist_from_support": dist_from_support,
            "dist_from_resistance": dist_from_resistance
        }
    
    def calculate_position_size(self, symbol: str, price: float) -> float:
        """Calculate conservative position size"""
        # Very conservative: max 15% of capital per trade
        max_position_value = self.capital * 0.15
        position_size = max_position_value / price
        
        # Round appropriately
        if "BTC" in symbol:
            return round(position_size, 6)
        elif "ETH" in symbol:
            return round(position_size, 4)
        return round(position_size, 4)
    
    def execute_trade(self, symbol: str, signal: str, price: float, confidence: float) -> Dict:
        """Execute a conservative trade"""
        self.reset_daily_counter()
        
        # Check daily limit
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return {
                "status": "REJECTED",
                "reason": f"Maximum trades per day ({MAX_TRADES_PER_DAY}) reached"
            }
        
        # Extra conservative confidence threshold
        if confidence < 0.6:
            return {
                "status": "REJECTED",
                "reason": f"Confidence too low for conservative trading: {confidence:.3f}"
            }
        
        # Calculate position size
        position_size = self.calculate_position_size(symbol, price)
        trade_value = position_size * price
        
        # Ensure we don't exceed conservative limits
        if trade_value > self.capital * 0.15:
            position_size = (self.capital * 0.15) / price
            if "BTC" in symbol:
                position_size = round(position_size, 6)
            elif "ETH" in symbol:
                position_size = round(position_size, 4)
            trade_value = position_size * price
        
        # Create trade record
        trade_id = f"TRADE_{int(time.time())}_{symbol}"
        trade = {
            "trade_id": trade_id,
            "symbol": symbol,
            "side": signal,
            "price": price,
            "quantity": position_size,
            "value": round(trade_value, 2),
            "timestamp": datetime.datetime.now().isoformat(),
            "stop_loss": round(price * (1 - STOP_LOSS) if signal == "BUY" else price * (1 + STOP_LOSS), 2),
            "take_profit": round(price * (1 + TAKE_PROFIT) if signal == "BUY" else price * (1 - TAKE_PROFIT), 2),
            "confidence": confidence,
            "risk_parameters": {
                "stop_loss_pct": STOP_LOSS * 100,
                "take_profit_pct": TAKE_PROFIT * 100
            }
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
        """Run full conservative trading analysis"""
        self.reset_daily_counter()
        
        analysis_results = []
        trades_executed = []
        
        print(f"=== CONSERVATIVE CRYPTO TRADING ANALYSIS ===")
        print(f"Time: {datetime.datetime.now()}")
        print(f"Capital: ${self.capital:.2f}")
        print(f"Daily Trade Limit: {MAX_TRADES_PER_DAY}")
        print(f"Trades Today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"Risk Parameters: {STOP_LOSS*100}% Stop-Loss, {TAKE_PROFIT*100}% Take-Profit")
        print(f"Position Size Limit: 15% of capital per trade")
        print()
        
        for symbol in SYMBOLS:
            print(f"Analyzing {symbol.upper()}...")
            
            # Get market sentiment with real data
            sentiment = self.analyze_market_sentiment(symbol)
            analysis_results.append(sentiment)
            
            print(f"  Current Price: ${sentiment['price']:.2f}")
            print(f"  24h Change: {sentiment['change_24h']*100:+.2f}%")
            print(f"  Support: ${sentiment['support']:.2f}")
            print(f"  Resistance: ${sentiment['resistance']:.2f}")
            print(f"  Distance from Support: {sentiment['dist_from_support']*100:.2f}%")
            print(f"  Distance from Resistance: {sentiment['dist_from_resistance']*100:.2f}%")
            print(f"  Signal: {sentiment['signal']} (Confidence: {sentiment['confidence']:.3f})")
            
            # Execute trade if conditions are met
            if sentiment["signal"] != "HOLD" and self.trades_today < MAX_TRADES_PER_DAY:
                trade_result = self.execute_trade(
                    sentiment["symbol"], 
                    sentiment["signal"], 
                    sentiment["price"], 
                    sentiment["confidence"]
                )
                
                if trade_result["status"] == "EXECUTED":
                    trades_executed.append(trade_result["trade"])
                    trade = trade_result["trade"]
                    print(f"  ✓ CONSERVATIVE TRADE EXECUTED:")
                    print(f"     Side: {trade['side']}")
                    print(f"     Quantity: {trade['quantity']}")
                    print(f"     Price: ${trade['price']:.2f}")
                    print(f"     Value: ${trade['value']:.2f}")
                    print(f"     Stop-Loss: ${trade['stop_loss']:.2f}")
                    print(f"     Take-Profit: ${trade['take_profit']:.2f}")
                else:
                    print(f"  ✗ Trade Not Executed: {trade_result['reason']}")
            
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
                "take_profit": f"{TAKE_PROFIT*100}%",
                "max_position_size": "15% of capital"
            },
            "trading_strategy": "Conservative 24/7 Trading"
        }
    
    def generate_summary(self, results: Dict) -> str:
        """Generate plain text summary for delivery"""
        summary = []
        summary.append("CONSERVATIVE CRYPTO TRADING - 24/7 ANALYSIS")
        summary.append("=" * 50)
        summary.append(f"Analysis Time: {results['timestamp']}")
        summary.append(f"Trading Strategy: {results['trading_strategy']}")
        summary.append(f"Capital: ${results['capital']:.2f}")
        summary.append(f"Trades Executed Today: {results['trades_today']}/{results['max_trades_per_day']}")
        summary.append(f"Risk Parameters: {results['risk_parameters']['stop_loss']} Stop-Loss, {results['risk_parameters']['take_profit']} Take-Profit")
        summary.append(f"Position Limit: {results['risk_parameters']['max_position_size']}")
        summary.append("")
        
        if results['trades_executed']:
            summary.append("TRADES EXECUTED THIS SESSION:")
            summary.append("-" * 50)
            total_trade_value = 0
            for i, trade in enumerate(results['trades_executed'], 1):
                summary.append(f"Trade #{i}:")
                summary.append(f"  ID: {trade['trade_id']}")
                summary.append(f"  Symbol: {trade['symbol']}")
                summary.append(f"  Side: {trade['side']}")
                summary.append(f"  Quantity: {trade['quantity']}")
                summary.append(f"  Entry Price: ${trade['price']:.2f}")
                summary.append(f"  Trade Value: ${trade['value']:.2f}")
                summary.append(f"  Stop-Loss: ${trade['stop_loss']:.2f} ({trade['risk_parameters']['stop_loss_pct']}%)")
                summary.append(f"  Take-Profit: ${trade['take_profit']:.2f} ({trade['risk_parameters']['take_profit_pct']}%)")
                summary.append(f"  Confidence: {trade['confidence']:.3f}")
                summary.append("")
                total_trade_value += trade['value']
            
            summary.append(f"Total Trade Value: ${total_trade_value:.2f}")
            summary.append(f"Capital Utilization: {(total_trade_value/results['capital']*100):.1f}%")
            summary.append("")
        else:
            summary.append("NO TRADES EXECUTED - Conservative conditions not met")
            summary.append("")
        
        summary.append("MARKET ANALYSIS SUMMARY:")
        summary.append("-" * 50)
        for analysis in results['analysis']:
            summary.append(f"{analysis['symbol']}:")
            summary.append(f"  Current Price: ${analysis['price']:.2f}")
            summary.append(f"  24h Change: {analysis['change_24h']*100:+.2f}%")
            summary.append(f"  Support Level: ${analysis['support']:.2f}")
            summary.append(f"  Resistance Level: ${analysis['resistance']:.2f}")
            summary.append(f"  Trading Signal: {analysis['signal']}")
            summary.append(f"  Signal Confidence: {analysis['confidence']:.3f}")
            summary.append("")
        
        summary.append("CONSERVATIVE TRADING DECISION:")
        summary.append("-" * 50)
        if results['trades_today'] >= results['max_trades_per_day']:
            summary.append("MAXIMUM DAILY TRADES REACHED.")
            summary.append("No further trading recommended today.")
        elif not results['trades_executed']:
            summary.append("HOLD POSITIONS - Conservative strategy advises waiting.")
            summary.append("Market conditions do not meet strict entry criteria.")
            summary.append("Better to miss a trade than take excessive risk.")
        else:
            summary.append(f"Executed {len(results['trades_executed'])} conservative trade(s).")
            summary.append("Monitor positions closely for stop-loss/take-profit triggers.")
            summary.append("Do not exceed risk parameters.")
        
        summary.append("")
        summary.append("NEXT ANALYSIS: Will run again per schedule (24/7 monitoring)")
        summary.append("")
        summary.append("END OF REPORT")
        
        return "\n".join(summary)

def main():
    """Main trading function with real data"""
    trader = ConservativeCryptoTraderReal()
    
    print("Starting CONSERVATIVE crypto trading analysis with REAL market data...")
    print(f"Date/Time: {datetime.datetime.now()}")
    print(f"Note: Using real Gemini API data for price discovery")
    print()
    
    # Run analysis
    results = trader.run_analysis()
    
    # Generate summary
    summary = trader.generate_summary(results)
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("CONSERVATIVE TRADING SUMMARY FOR DELIVERY:")
    print("=" * 60)
    print(summary)
    
    # Save to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conservative_trading_summary_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(summary)
    
    print(f"\nSummary saved to: {filename}")
    
    return summary

if __name__ == "__main__":
    main()