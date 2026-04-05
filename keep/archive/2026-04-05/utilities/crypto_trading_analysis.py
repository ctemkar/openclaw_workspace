#!/usr/bin/env python3
"""
Conservative Crypto Trading Analysis for Gemini API
Risk Parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Capital: $1,000
Pairs: BTC/USD, ETH/USD
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Tuple
import math

class ConservativeCryptoTrader:
    def __init__(self, capital: float = 1000.0):
        self.capital = capital
        self.risk_per_trade = 0.05  # 5% stop-loss
        self.take_profit = 0.10     # 10% take-profit
        self.max_trades_per_day = 2
        self.trades_today = 0
        self.last_trade_date = None
        
        # Gemini API endpoints (public for price data)
        self.gemini_base_url = "https://api.gemini.com/v1"
        
        # Trading pairs
        self.pairs = ["btcusd", "ethusd"]
        
        # Support/Resistance levels (will be calculated dynamically)
        self.support_resistance = {}
        
        # Market sentiment indicators
        self.sentiment_data = {}
        
    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for BTC/USD and ETH/USD"""
        prices = {}
        
        for pair in self.pairs:
            try:
                url = f"{self.gemini_base_url}/pubticker/{pair}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    prices[pair] = float(data['last'])
                else:
                    print(f"Error fetching {pair}: {response.status_code}")
                    prices[pair] = 0.0
            except Exception as e:
                print(f"Exception fetching {pair}: {e}")
                prices[pair] = 0.0
                
        return prices
    
    def calculate_support_resistance(self, pair: str, price_history: List[float]) -> Dict[str, float]:
        """Calculate support and resistance levels based on price history"""
        if not price_history:
            return {"support": 0, "resistance": 0}
            
        current_price = price_history[-1]
        sorted_prices = sorted(price_history)
        
        # Simple support/resistance calculation
        # Support: 5% below current price
        # Resistance: 5% above current price
        support = current_price * 0.95
        resistance = current_price * 1.05
        
        # Adjust based on historical levels
        if len(sorted_prices) >= 20:
            # Use recent lows and highs
            recent_lows = sorted_prices[:10]
            recent_highs = sorted_prices[-10:]
            
            avg_low = sum(recent_lows) / len(recent_lows)
            avg_high = sum(recent_highs) / len(recent_highs)
            
            support = max(support, avg_low * 0.98)
            resistance = min(resistance, avg_high * 1.02)
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "current": round(current_price, 2)
        }
    
    def analyze_market_sentiment(self, pair: str) -> Dict[str, str]:
        """Analyze market sentiment for a trading pair"""
        try:
            url = f"{self.gemini_base_url}/pubticker/{pair}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Get volume and price change data
                volume = float(data.get('volume', {}).get('USD', 0))
                bid = float(data.get('bid', 0))
                ask = float(data.get('ask', 0))
                last = float(data.get('last', 0))
                
                # Calculate spread
                spread = ((ask - bid) / bid) * 100 if bid > 0 else 0
                
                # Determine sentiment
                sentiment = "NEUTRAL"
                if spread < 0.1 and volume > 1000000:  # High volume, low spread
                    sentiment = "BULLISH"
                elif spread > 0.5:  # High spread indicates uncertainty
                    sentiment = "BEARISH"
                
                return {
                    "sentiment": sentiment,
                    "volume_usd": f"${volume:,.0f}",
                    "spread_percent": f"{spread:.2f}%",
                    "bid": f"${bid:,.2f}",
                    "ask": f"${ask:,.2f}"
                }
        except Exception as e:
            print(f"Error analyzing sentiment for {pair}: {e}")
        
        return {
            "sentiment": "UNKNOWN",
            "volume_usd": "$0",
            "spread_percent": "0%",
            "bid": "$0",
            "ask": "$0"
        }
    
    def get_price_history(self, pair: str, hours: int = 24) -> List[float]:
        """Get price history for the last N hours"""
        # For demo purposes, we'll simulate price history
        # In production, you would use Gemini's candle API
        current_price = self.get_current_prices().get(pair, 0)
        
        if current_price == 0:
            return []
            
        # Simulate some price movement
        import random
        history = []
        base_price = current_price * 0.95  # Start 5% lower
        
        for i in range(hours):
            # Random walk with slight upward bias
            change = random.uniform(-0.005, 0.01)
            base_price *= (1 + change)
            history.append(base_price)
            
        # Ensure last price matches current
        history[-1] = current_price
        
        return history
    
    def should_trade(self, pair: str, price: float, sentiment: Dict[str, str]) -> Tuple[bool, str, float]:
        """Determine if we should trade based on conservative strategy"""
        
        # Check if we've reached daily trade limit
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
            
        if self.trades_today >= self.max_trades_per_day:
            return False, "Daily trade limit reached", 0.0
        
        # Get price history and calculate support/resistance
        price_history = self.get_price_history(pair, 6)  # Last 6 hours
        if not price_history:
            return False, "No price history available", 0.0
            
        sr_levels = self.calculate_support_resistance(pair, price_history)
        
        # Conservative trading rules:
        # 1. Only trade if sentiment is BULLISH
        # 2. Only buy near support levels
        # 3. Use small position size (10% of capital max)
        
        support = sr_levels["support"]
        resistance = sr_levels["resistance"]
        
        # Calculate distance from support/resistance
        distance_to_support = abs(price - support) / price * 100
        distance_to_resistance = abs(price - resistance) / price * 100
        
        position_size = 0.0
        trade_signal = ""
        
        if sentiment["sentiment"] == "BULLISH":
            # Conservative buy: only if price is within 2% of support
            if distance_to_support <= 2.0:
                trade_signal = "BUY"
                # Position size: 10% of capital, but ensure we don't exceed risk
                position_size = min(self.capital * 0.1, self.capital * self.risk_per_trade * 2)
            elif distance_to_resistance <= 2.0:
                # Near resistance, consider taking profits if we had a position
                trade_signal = "HOLD/TAKE PROFITS"
                position_size = 0.0
            else:
                trade_signal = "HOLD"
                position_size = 0.0
        else:
            trade_signal = "HOLD (sentiment not bullish)"
            position_size = 0.0
        
        should_execute = trade_signal == "BUY" and position_size > 0
        
        if should_execute:
            self.trades_today += 1
            
        return should_execute, trade_signal, position_size
    
    def calculate_trade_parameters(self, pair: str, price: float, position_size: float) -> Dict:
        """Calculate stop-loss and take-profit levels for a trade"""
        entry_price = price
        
        # Conservative: 5% stop-loss, 10% take-profit
        stop_loss_price = entry_price * (1 - self.risk_per_trade)
        take_profit_price = entry_price * (1 + self.take_profit)
        
        # Calculate position size in crypto units
        crypto_amount = position_size / entry_price
        
        return {
            "pair": pair,
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss_price, 2),
            "take_profit": round(take_profit_price, 2),
            "position_size_usd": round(position_size, 2),
            "crypto_amount": round(crypto_amount, 6),
            "risk_reward_ratio": round(self.take_profit / self.risk_per_trade, 2)
        }
    
    def execute_trade(self, trade_params: Dict) -> Dict:
        """Execute a trade (simulated for this example)"""
        # In production, this would call Gemini's private API with authentication
        # For this example, we'll simulate execution
        
        trade_result = {
            **trade_params,
            "status": "SIMULATED_EXECUTION",
            "order_id": f"SIM_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "executed": True,
            "message": "Trade would be executed with real Gemini API credentials"
        }
        
        return trade_result
    
    def run_analysis(self) -> Dict:
        """Run complete trading analysis"""
        print(f"\n{'='*60}")
        print(f"CONSERVATIVE CRYPTO TRADING ANALYSIS")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Capital: ${self.capital:,.2f}")
        print(f"Risk Parameters: {self.risk_per_trade*100}% SL, {self.take_profit*100}% TP")
        print(f"Max Trades/Day: {self.max_trades_per_day}")
        print(f"{'='*60}\n")
        
        # Get current prices
        prices = self.get_current_prices()
        
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "capital": self.capital,
            "prices": {},
            "sentiment": {},
            "support_resistance": {},
            "trading_signals": [],
            "executed_trades": []
        }
        
        for pair in self.pairs:
            price = prices.get(pair, 0)
            if price == 0:
                print(f"⚠️  Could not fetch price for {pair}")
                continue
                
            print(f"\n📊 {pair.upper()} Analysis:")
            print(f"   Current Price: ${price:,.2f}")
            
            # Analyze sentiment
            sentiment = self.analyze_market_sentiment(pair)
            analysis_results["sentiment"][pair] = sentiment
            print(f"   Market Sentiment: {sentiment['sentiment']}")
            print(f"   24h Volume: {sentiment['volume_usd']}")
            print(f"   Bid/Ask Spread: {sentiment['spread_percent']}")
            
            # Calculate support/resistance
            price_history = self.get_price_history(pair, 12)
            sr_levels = self.calculate_support_resistance(pair, price_history)
            analysis_results["support_resistance"][pair] = sr_levels
            print(f"   Support: ${sr_levels['support']:,.2f}")
            print(f"   Resistance: ${sr_levels['resistance']:,.2f}")
            print(f"   Current: ${sr_levels['current']:,.2f}")
            
            # Determine trading signal
            should_trade, signal, position_size = self.should_trade(pair, price, sentiment)
            
            signal_info = {
                "pair": pair,
                "price": price,
                "signal": signal,
                "should_trade": should_trade,
                "position_size": position_size,
                "sentiment": sentiment["sentiment"]
            }
            analysis_results["trading_signals"].append(signal_info)
            
            print(f"   Trading Signal: {signal}")
            
            if should_trade and position_size > 0:
                print(f"   ✅ TRADE RECOMMENDED")
                print(f"   Position Size: ${position_size:,.2f}")
                
                # Calculate trade parameters
                trade_params = self.calculate_trade_parameters(pair, price, position_size)
                
                print(f"   Entry: ${trade_params['entry_price']:,.2f}")
                print(f"   Stop Loss: ${trade_params['stop_loss']:,.2f} (-{self.risk_per_trade*100}%)")
                print(f"   Take Profit: ${trade_params['take_profit']:,.2f} (+{self.take_profit*100}%)")
                print(f"   Risk/Reward: 1:{trade_params['risk_reward_ratio']}")
                
                # Execute trade (simulated)
                trade_result = self.execute_trade(trade_params)
                analysis_results["executed_trades"].append(trade_result)
                
                print(f"   📝 Trade Executed (Simulated)")
            else:
                print(f"   ⏸️  No trade at this time")
            
            print(f"{'-'*40}")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY:")
        print(f"Trades Today: {self.trades_today}/{self.max_trades_per_day}")
        print(f"Recommended Trades: {len([t for t in analysis_results['trading_signals'] if t['should_trade']])}")
        print(f"Executed Trades: {len(analysis_results['executed_trades'])}")
        print(f"{'='*60}")
        
        return analysis_results

def main():
    """Main function"""
    trader = ConservativeCryptoTrader(capital=1000.0)
    
    try:
        results = trader.run_analysis()
        
        # Generate plain text summary for cron delivery
        summary = generate_plain_text_summary(results)
        
        # Save results to file
        with open("trading_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Results saved to trading_results.json")
        
        return summary
        
    except Exception as e:
        error_msg = f"Error in trading analysis: {str(e)}"
        print(error_msg)
        return error_msg

def generate_plain_text_summary(results: Dict) -> str:
    """Generate plain text summary for cron delivery"""
    summary_lines = []
    
    summary_lines.append("=" * 60)
    summary_lines.append("CONSERVATIVE CRYPTO TRADING SUMMARY")
    summary_lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    summary_lines.append(f"Capital: ${results.get('capital', 0):,.2f}")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    
    # Market Overview
    summary_lines.append("MARKET OVERVIEW:")
    for pair in results.get('prices', {}):
        price = results['prices'].get(pair, 0)
        sentiment = results['sentiment'].get(pair, {}).get('sentiment', 'UNKNOWN')
        summary_lines.append(f"  {pair.upper()}: ${price:,.2f} ({sentiment})")
    
    summary_lines.append("")
    
    # Trading Signals
    summary_lines.append("TRADING SIGNALS:")
    signals = results.get('trading_signals', [])
    if not signals:
        summary_lines.append("  No trading signals generated")
    else:
        for signal in signals:
            pair = signal['pair'].upper()
            price = signal['price']
            action = signal['signal']
            should_trade = signal['should_trade']
            
            if should_trade:
                summary_lines.append(f"  ✅ {pair}: {action} at ${price:,.2f}")
            else:
                summary_lines.append(f"  ⏸️  {pair}: {action}")
    
    summary_lines.append("")
    
    # Executed Trades
    executed_trades = results.get('executed_trades', [])
    if executed_trades:
        summary_lines.append("EXECUTED TRADES:")
        for trade in executed_trades:
            pair = trade['pair'].upper()
            entry = trade['entry_price']
            sl = trade['stop_loss']
            tp = trade['take_profit']
            size = trade['position_size_usd']
            
            summary_lines.append(f"  📈 {pair}:")
            summary_lines.append(f"     Entry: ${entry:,.2f}")
            summary_lines.append(f"     Stop Loss: ${sl:,.2f} (-5%)")
            summary_lines.append(f"     Take Profit: ${tp:,.2f} (+10%)")
            summary_lines.append(f"     Size: ${size:,.2f}")
            summary_lines.append(f"     Status: {trade.get('status', 'EXECUTED')}")
            summary_lines.append("")
    else:
        summary_lines.append("EXECUTED TRADES: None")
        summary_lines.append("")
    
    # Risk Summary
    summary_lines.append("RISK SUMMARY:")
    summary_lines.append(f"  Max Trades Today: {2 - len(executed_trades)} remaining")
    summary_lines.append(f"  Stop Loss: 5%")
    summary_lines.append(f"  Take Profit: 10%")
    summary_lines.append(f"  Risk/Reward Ratio: 1:2")
    summary_lines.append(f"  Capital at Risk per Trade: 5%")
    
    summary_lines.append("")
    summary_lines.append("=" * 60)
    summary_lines.append("END OF TRADING SUMMARY")
    summary_lines.append("=" * 60)
    
    return "\n".join(summary_lines)