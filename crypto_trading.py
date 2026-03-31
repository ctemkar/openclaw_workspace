#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Using Gemini API with $1,000 capital
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Analyzes BTC/USD and ETH/USD
"""

import os
import time
import json
import requests
import datetime
from typing import Dict, List, Optional, Tuple
import math

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_SECRET = os.environ.get("GEMINI_API_SECRET", "")
GEMINI_API_URL = "https://api.gemini.com"

# Trading parameters
CAPITAL = 1000.0  # $1,000
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
SYMBOLS = ["BTCUSD", "ETHUSD"]

class ConservativeCryptoTrader:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_secret = GEMINI_API_SECRET
        self.capital = CAPITAL
        self.trades_today = 0
        self.trade_history = []
        self.last_trade_date = None
        
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            url = f"{GEMINI_API_URL}/v1/pubticker/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return float(data['last'])
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
        return None
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get comprehensive market data including bid/ask, volume, etc."""
        try:
            url = f"{GEMINI_API_URL}/v1/pubticker/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': float(data['last']),
                    'bid': float(data['bid']),
                    'ask': float(data['ask']),
                    'volume': float(data['volume']['USD']),
                    'change': float(data.get('percentChange24h', 0))
                }
        except Exception as e:
            print(f"Error getting market data for {symbol}: {e}")
        return {}
    
    def calculate_support_resistance(self, symbol: str) -> Dict:
        """Calculate simple support and resistance levels based on recent price action"""
        price = self.get_current_price(symbol)
        if not price:
            return {}
        
        # Simplified calculation - in production would use more sophisticated methods
        support = price * 0.97  # 3% below current
        resistance = price * 1.03  # 3% above current
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current': round(price, 2)
        }
    
    def analyze_market_sentiment(self) -> str:
        """Analyze basic market sentiment based on price changes"""
        sentiments = []
        
        for symbol in SYMBOLS:
            data = self.get_market_data(symbol)
            if data:
                change = data.get('change', 0)
                if change > 2:
                    sentiments.append(f"{symbol}: Bullish (+{change:.2f}%)")
                elif change < -2:
                    sentiments.append(f"{symbol}: Bearish ({change:.2f}%)")
                else:
                    sentiments.append(f"{symbol}: Neutral ({change:.2f}%)")
        
        return " | ".join(sentiments) if sentiments else "No data available"
    
    def check_trade_limits(self) -> bool:
        """Check if we've reached daily trade limits"""
        today = datetime.date.today()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate conservative position size (10% of capital per trade)"""
        position_value = self.capital * 0.10  # 10% of capital
        position_size = position_value / price
        return round(position_size, 6)  # Round to 6 decimal places for crypto
    
    def simulate_trade(self, symbol: str, action: str, price: float) -> Dict:
        """Simulate a trade (since we don't have real API credentials)"""
        if not self.check_trade_limits():
            return {"error": "Daily trade limit reached"}
        
        position_size = self.calculate_position_size(price)
        trade_value = position_size * price
        
        # Calculate stop loss and take profit levels
        if action == "BUY":
            stop_loss = price * (1 - STOP_LOSS_PCT)
            take_profit = price * (1 + TAKE_PROFIT_PCT)
        else:  # SELL (for short positions)
            stop_loss = price * (1 + STOP_LOSS_PCT)
            take_profit = price * (1 - TAKE_PROFIT_PCT)
        
        trade = {
            'timestamp': datetime.datetime.now().isoformat(),
            'symbol': symbol,
            'action': action,
            'price': round(price, 2),
            'size': position_size,
            'value': round(trade_value, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'status': 'SIMULATED',
            'risk_reward_ratio': round(TAKE_PROFIT_PCT / STOP_LOSS_PCT, 2)
        }
        
        self.trades_today += 1
        self.trade_history.append(trade)
        
        return trade
    
    def conservative_trading_strategy(self) -> List[Dict]:
        """Execute conservative trading strategy"""
        trades = []
        
        for symbol in SYMBOLS:
            # Get market data
            market_data = self.get_market_data(symbol)
            if not market_data:
                continue
            
            price = market_data['price']
            change = market_data.get('change', 0)
            volume = market_data.get('volume', 0)
            
            # Calculate support/resistance
            sr_levels = self.calculate_support_resistance(symbol)
            
            # Conservative strategy rules:
            # 1. Only trade if volume > $10M (liquidity check)
            # 2. Buy if price near support and market neutral/bullish
            # 3. Sell if price near resistance and market bearish
            # 4. Avoid trading during extreme volatility
            
            if volume > 10000000:  # $10M volume threshold
                current_to_support = abs(price - sr_levels.get('support', price)) / price
                current_to_resistance = abs(price - sr_levels.get('resistance', price)) / price
                
                # Check if we can trade today
                if not self.check_trade_limits():
                    print(f"Daily trade limit reached for {symbol}")
                    continue
                
                # Conservative buy signal: price near support, small negative or neutral change
                if current_to_support < 0.01 and -1 < change < 1:  # Within 1% of support
                    print(f"Conservative BUY signal for {symbol} near support")
                    trade = self.simulate_trade(symbol, "BUY", price)
                    if 'error' not in trade:
                        trades.append(trade)
                
                # Conservative sell signal: price near resistance, small positive change
                elif current_to_resistance < 0.01 and 0 < change < 2:  # Within 1% of resistance
                    print(f"Conservative SELL signal for {symbol} near resistance")
                    trade = self.simulate_trade(symbol, "SELL", price)
                    if 'error' not in trade:
                        trades.append(trade)
                else:
                    print(f"No clear conservative signal for {symbol}")
        
        return trades
    
    def generate_summary(self) -> str:
        """Generate plain text summary of trading activity"""
        summary_lines = []
        
        # Current time
        now = datetime.datetime.now()
        summary_lines.append(f"CRYPTO TRADING SUMMARY - {now.strftime('%Y-%m-%d %H:%M:%S')}")
        summary_lines.append("=" * 50)
        
        # Market conditions
        summary_lines.append("\nMARKET CONDITIONS:")
        summary_lines.append(f"Sentiment: {self.analyze_market_sentiment()}")
        
        for symbol in SYMBOLS:
            price = self.get_current_price(symbol)
            if price:
                sr = self.calculate_support_resistance(symbol)
                summary_lines.append(f"\n{symbol}:")
                summary_lines.append(f"  Current: ${price:,.2f}")
                summary_lines.append(f"  Support: ${sr.get('support', 0):,.2f}")
                summary_lines.append(f"  Resistance: ${sr.get('resistance', 0):,.2f}")
        
        # Trading parameters
        summary_lines.append("\nTRADING PARAMETERS:")
        summary_lines.append(f"Capital: ${self.capital:,.2f}")
        summary_lines.append(f"Stop Loss: {STOP_LOSS_PCT*100}%")
        summary_lines.append(f"Take Profit: {TAKE_PROFIT_PCT*100}%")
        summary_lines.append(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
        summary_lines.append(f"Trades Today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        
        # Trade history
        if self.trade_history:
            summary_lines.append("\nTRADES EXECUTED:")
            for i, trade in enumerate(self.trade_history[-5:], 1):  # Last 5 trades
                summary_lines.append(f"\nTrade #{i}:")
                summary_lines.append(f"  Symbol: {trade['symbol']}")
                summary_lines.append(f"  Action: {trade['action']}")
                summary_lines.append(f"  Price: ${trade['price']:,.2f}")
                summary_lines.append(f"  Size: {trade['size']}")
                summary_lines.append(f"  Value: ${trade['value']:,.2f}")
                summary_lines.append(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
                summary_lines.append(f"  Take Profit: ${trade['take_profit']:,.2f}")
                summary_lines.append(f"  Risk/Reward: {trade['risk_reward_ratio']}:1")
                summary_lines.append(f"  Status: {trade['status']}")
        else:
            summary_lines.append("\nTRADES EXECUTED: None")
        
        # Recommendations
        summary_lines.append("\nRECOMMENDATIONS:")
        if self.trades_today >= MAX_TRADES_PER_DAY:
            summary_lines.append("✓ Daily trade limit reached - no further trades today")
        else:
            summary_lines.append(f"✓ {MAX_TRADES_PER_DAY - self.trades_today} trades available today")
        
        summary_lines.append("✓ Maintain conservative position sizing (10% of capital)")
        summary_lines.append("✓ Adhere to 5% stop-loss and 10% take-profit levels")
        
        return "\n".join(summary_lines)

def main():
    """Main trading execution"""
    print("Starting Conservative Crypto Trading Analysis...")
    
    # Check for API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("WARNING: Gemini API credentials not found. Running in simulation mode.")
        print("Set GEMINI_API_KEY and GEMINI_API_SECRET environment variables for real trading.")
    
    trader = ConservativeCryptoTrader()
    
    # Execute trading strategy
    trades = trader.conservative_trading_strategy()
    
    # Generate summary
    summary = trader.generate_summary()
    
    print("\n" + summary)
    
    # Save summary to file
    with open("trading_summary.txt", "w") as f:
        f.write(summary)
    
    return summary

if __name__ == "__main__":
    main()