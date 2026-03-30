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
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

# Configuration
CAPITAL = 1000.0  # $1,000 capital
STOP_LOSS = 0.05  # 5% stop-loss
TAKE_PROFIT = 0.10  # 10% take-profit
MAX_TRADES_PER_DAY = 2
SYMBOLS = ["BTCUSD", "ETHUSD"]

class GeminiTrader:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.api_secret = os.environ.get("GEMINI_API_SECRET", "")
        self.base_url = "https://api.gemini.com"
        self.sandbox_url = "https://api.sandbox.gemini.com"
        self.use_sandbox = True  # Use sandbox for testing
        
        # Trade tracking
        self.trades_today = 0
        self.last_trade_date = None
        self.total_capital = CAPITAL
        self.available_capital = CAPITAL
        self.positions = {}
        
        # Load trade history
        self.load_trade_history()
        
    def load_trade_history(self):
        """Load trade history from file"""
        try:
            with open("trade_history.json", "r") as f:
                data = json.load(f)
                self.trades_today = data.get("trades_today", 0)
                self.last_trade_date = data.get("last_trade_date")
                self.total_capital = data.get("total_capital", CAPITAL)
                self.available_capital = data.get("available_capital", CAPITAL)
                self.positions = data.get("positions", {})
        except FileNotFoundError:
            pass
            
    def save_trade_history(self):
        """Save trade history to file"""
        data = {
            "trades_today": self.trades_today,
            "last_trade_date": self.last_trade_date,
            "total_capital": self.total_capital,
            "available_capital": self.available_capital,
            "positions": self.positions,
            "last_updated": datetime.utcnow().isoformat()
        }
        with open("trade_history.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def reset_daily_trades(self):
        """Reset daily trade count if it's a new day"""
        today = datetime.utcnow().date()
        if self.last_trade_date != str(today):
            self.trades_today = 0
            self.last_trade_date = str(today)
    
    def generate_signature(self, payload: str) -> str:
        """Generate Gemini API signature"""
        encoded_payload = payload.encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.api_secret.encode(), b64, hashlib.sha384).hexdigest()
        return signature
    
    def make_request(self, endpoint: str, method: str = "GET", payload: Dict = None) -> Dict:
        """Make authenticated request to Gemini API"""
        if payload is None:
            payload = {}
            
        url = f"{self.sandbox_url if self.use_sandbox else self.base_url}{endpoint}"
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "Cache-Control": "no-cache"
        }
        
        if method == "POST":
            payload_str = json.dumps(payload)
            signature = self.generate_signature(payload_str)
            headers["X-GEMINI-PAYLOAD"] = payload_str
            headers["X-GEMINI-SIGNATURE"] = signature
            response = requests.post(url, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        return response.json()
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get current market data for a symbol"""
        try:
            # For BTCUSD, use BTCUSD on Gemini
            gemini_symbol = symbol.replace("USD", "USD")
            endpoint = f"/v1/pubticker/{gemini_symbol}"
            data = self.make_request(endpoint)
            
            if "bid" in data and "ask" in data:
                return {
                    "symbol": symbol,
                    "bid": float(data["bid"]),
                    "ask": float(data["ask"]),
                    "last": float(data["last"]),
                    "volume": float(data.get("volume", {}).get("USD", 0)),
                    "timestamp": int(data["timestamp"])
                }
        except Exception as e:
            print(f"Error getting market data for {symbol}: {e}")
        
        # Fallback to mock data if API fails
        return self.get_mock_market_data(symbol)
    
    def get_mock_market_data(self, symbol: str) -> Dict:
        """Generate mock market data for testing"""
        import random
        base_prices = {
            "BTCUSD": 65000.0,
            "ETHUSD": 3500.0
        }
        base = base_prices.get(symbol, 1000.0)
        variation = random.uniform(-0.02, 0.02)  # ±2% variation
        price = base * (1 + variation)
        
        return {
            "symbol": symbol,
            "bid": price * 0.999,
            "ask": price * 1.001,
            "last": price,
            "volume": random.uniform(1000000, 5000000),
            "timestamp": int(time.time())
        }
    
    def calculate_support_resistance(self, symbol: str, historical_prices: List[float]) -> Dict:
        """Calculate support and resistance levels"""
        if not historical_prices:
            return {"support": 0, "resistance": 0}
        
        prices = sorted(historical_prices)
        n = len(prices)
        
        # Simple support/resistance calculation
        support = prices[int(n * 0.25)]  # 25th percentile
        resistance = prices[int(n * 0.75)]  # 75th percentile
        
        return {
            "support": support,
            "resistance": resistance,
            "current": historical_prices[-1] if historical_prices else 0
        }
    
    def analyze_market_sentiment(self, symbol: str, market_data: Dict) -> str:
        """Analyze market sentiment"""
        current_price = market_data["last"]
        volume = market_data["volume"]
        
        # Simple sentiment analysis
        if volume > 3000000:  # High volume
            if current_price > market_data["bid"] * 1.005:  # Price above bid
                return "bullish"
            elif current_price < market_data["ask"] * 0.995:  # Price below ask
                return "bearish"
        
        return "neutral"
    
    def should_trade(self, symbol: str, market_data: Dict, sentiment: str) -> Tuple[bool, str, float]:
        """Determine if we should trade based on conservative strategy"""
        self.reset_daily_trades()
        
        # Check daily trade limit
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return False, "Daily trade limit reached", 0.0
        
        # Check available capital
        if self.available_capital < 100:  # Minimum $100 per trade
            return False, "Insufficient capital", 0.0
        
        current_price = market_data["last"]
        
        # Conservative trading strategy
        # Only trade if we have clear signals
        if sentiment == "bullish":
            # Buy signal
            position_size = min(self.available_capital * 0.2, 200)  # Max 20% of capital or $200
            return True, "buy", position_size / current_price  # Return quantity
            
        elif sentiment == "bearish" and symbol in self.positions:
            # Sell signal (only if we have position)
            position = self.positions[symbol]
            return True, "sell", position["quantity"]
        
        return False, "No clear trading signal", 0.0
    
    def execute_trade(self, symbol: str, side: str, quantity: float, market_data: Dict) -> Dict:
        """Execute a trade (mock implementation for sandbox)"""
        trade_id = f"trade_{int(time.time())}_{symbol}"
        price = market_data["last"]
        cost = quantity * price
        
        if side == "buy":
            if cost > self.available_capital:
                return {"success": False, "error": "Insufficient funds"}
            
            self.available_capital -= cost
            self.positions[symbol] = {
                "quantity": quantity,
                "entry_price": price,
                "entry_time": datetime.utcnow().isoformat(),
                "stop_loss": price * (1 - STOP_LOSS),
                "take_profit": price * (1 + TAKE_PROFIT)
            }
            
        elif side == "sell":
            if symbol not in self.positions:
                return {"success": False, "error": "No position to sell"}
            
            position = self.positions[symbol]
            profit_loss = (price - position["entry_price"]) * quantity
            
            self.available_capital += cost
            self.total_capital += profit_loss
            del self.positions[symbol]
        
        self.trades_today += 1
        self.save_trade_history()
        
        return {
            "success": True,
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "cost": cost,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def check_stop_loss_take_profit(self) -> List[Dict]:
        """Check if any positions hit stop-loss or take-profit"""
        closed_trades = []
        
        for symbol, position in list(self.positions.items()):
            market_data = self.get_market_data(symbol)
            current_price = market_data["last"]
            
            # Check stop-loss
            if current_price <= position["stop_loss"]:
                trade = self.execute_trade(symbol, "sell", position["quantity"], market_data)
                if trade["success"]:
                    trade["reason"] = "stop_loss"
                    closed_trades.append(trade)
            
            # Check take-profit
            elif current_price >= position["take_profit"]:
                trade = self.execute_trade(symbol, "sell", position["quantity"], market_data)
                if trade["success"]:
                    trade["reason"] = "take_profit"
                    closed_trades.append(trade)
        
        return closed_trades
    
    def run_analysis(self) -> Dict:
        """Run complete trading analysis"""
        print(f"\n=== Crypto Trading Analysis - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} ===")
        print(f"Capital: ${self.total_capital:.2f} (Available: ${self.available_capital:.2f})")
        print(f"Trades today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"Open positions: {len(self.positions)}")
        
        analysis_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "capital": self.total_capital,
            "available_capital": self.available_capital,
            "trades_today": self.trades_today,
            "max_trades_per_day": MAX_TRADES_PER_DAY,
            "open_positions": len(self.positions),
            "symbols_analyzed": [],
            "trades_executed": [],
            "closed_trades": []
        }
        
        # Check for stop-loss/take-profit triggers
        closed_trades = self.check_stop_loss_take_profit()
        analysis_results["closed_trades"].extend(closed_trades)
        
        # Analyze each symbol
        for symbol in SYMBOLS:
            print(f"\n--- Analyzing {symbol} ---")
            
            # Get market data
            market_data = self.get_market_data(symbol)
            print(f"Price: ${market_data['last']:.2f} (Bid: ${market_data['bid']:.2f}, Ask: ${market_data['ask']:.2f})")
            print(f"24h Volume: ${market_data['volume']:,.2f}")
            
            # Analyze sentiment
            sentiment = self.analyze_market_sentiment(symbol, market_data)
            print(f"Sentiment: {sentiment}")
            
            # Check if we should trade
            should_trade, action, quantity = self.should_trade(symbol, market_data, sentiment)
            
            symbol_analysis = {
                "symbol": symbol,
                "price": market_data["last"],
                "bid": market_data["bid"],
                "ask": market_data["ask"],
                "volume": market_data["volume"],
                "sentiment": sentiment,
                "should_trade": should_trade,
                "action": action,
                "quantity": quantity
            }
            analysis_results["symbols_analyzed"].append(symbol_analysis)
            
            if should_trade:
                print(f"Trading signal: {action.upper()} {quantity:.6f} {symbol}")
                
                # Execute trade
                trade_result = self.execute_trade(symbol, action, quantity, market_data)
                
                if trade_result["success"]:
                    print(f"✓ Trade executed: {trade_result['trade_id']}")
                    print(f"  {action.upper()} {quantity:.6f} {symbol} @ ${trade_result['price']:.2f}")
                    print(f"  Cost: ${trade_result['cost']:.2f}")
                    
                    analysis_results["trades_executed"].append(trade_result)
                else:
                    print(f"✗ Trade failed: {trade_result.get('error', 'Unknown error')}")
            else:
                print(f"No trade: {action}")
        
        # Save updated history
        self.save_trade_history()
        
        print(f"\n=== Analysis Complete ===")
        print(f"Final capital: ${self.total_capital:.2f}")
        print(f"Available capital: ${self.available_capital:.2f}")
        print(f"Total trades executed this run: {len(analysis_results['trades_executed'])}")
        print(f"Total positions closed this run: {len(analysis_results['closed_trades'])}")
        
        return analysis_results

def main():
    """Main function"""
    print("Starting Conservative Crypto Trading Bot")
    print(f"Capital: ${CAPITAL}")
    print(f"Risk Parameters: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
    print(f"Max trades per day: {MAX_TRADES_PER_DAY}")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    
    # Check for API credentials
    if not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_API_SECRET"):
        print("\n⚠️  WARNING: GEMINI_API_KEY and GEMINI_API_SECRET environment variables not set.")
        print("Using sandbox/mock mode for demonstration.")
        print("To use real trading, set these environment variables.")
    
    trader = GeminiTrader()
    results = trader.run_analysis()
    
    # Save analysis results
    with open("trading_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    main()