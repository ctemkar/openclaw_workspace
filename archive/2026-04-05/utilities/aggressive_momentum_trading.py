#!/usr/bin/env python3
"""
AGGRESSIVE CRYPTO MOMENTUM TRADING - PAPER TRADING ONLY
Risk parameters: 8% stop-loss, 15% take-profit, max 5 trades per day with 2x leverage
$25,000 paper trading balance
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from typing import Dict, List, Optional, Tuple
import sys
import random

# Paper Trading Configuration
PAPER_BALANCE = 25000.00  # $25,000 paper balance
MAX_DAILY_TRADES = 5
STOP_LOSS_PERCENT = 8.0    # 8%
TAKE_PROFIT_PERCENT = 15.0 # 15%
LEVERAGE_AVAILABLE = 2.0   # 2x leverage for paper trading
MAX_POSITION_SIZE = 0.8    # 80% of capital per trade (aggressive)
PAIRS_TO_MONITOR = ["BTCUSD", "ETHUSD", "SOLUSD"]

# Use CoinGecko API for free market data
COINGECKO_API = "https://api.coingecko.com/api/v3"

class PaperTradingSimulator:
    """Paper trading simulator with aggressive momentum strategy"""
    
    def __init__(self, initial_balance: float):
        self.balance = initial_balance
        self.positions = {}
        self.trade_history = []
        self.daily_trades = 0
        self.last_trade_date = None
        self.paper_balance = initial_balance
        self.available_leverage = LEVERAGE_AVAILABLE
        
    def reset_daily_trades(self):
        """Reset daily trade counter if it's a new day"""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
    
    def can_trade_today(self) -> bool:
        """Check if we can trade today based on daily limit"""
        self.reset_daily_trades()
        return self.daily_trades < MAX_DAILY_TRADES
    
    def calculate_aggressive_position(self, current_price: float, momentum_strength: float) -> Tuple[float, float]:
        """Calculate aggressive position size based on momentum strength"""
        # Base position: 40% of capital
        base_position = self.balance * 0.4
        
        # Scale by momentum strength (0-100%)
        momentum_multiplier = 1.0 + (momentum_strength / 100.0)
        
        # Apply leverage for aggressive trading
        leveraged_position = base_position * momentum_multiplier * self.available_leverage
        
        # Don't exceed max position size
        max_position = self.balance * MAX_POSITION_SIZE * self.available_leverage
        final_position = min(leveraged_position, max_position)
        
        # Convert to coin amount
        coin_amount = final_position / current_price
        
        return coin_amount, final_position
    
    def execute_paper_trade(self, symbol: str, side: str, amount: float, 
                           entry_price: float, stop_loss: float, take_profit: float) -> Dict:
        """Execute a paper trade (simulation only)"""
        if not self.can_trade_today():
            return {"error": "Daily trade limit reached"}
        
        trade_value = amount * entry_price
        
        # Check if we have enough paper balance
        if side == "buy" and trade_value > self.balance * self.available_leverage:
            return {"error": "Insufficient paper balance"}
        
        # Record the trade
        trade_id = f"PAPER_{int(time.time())}_{random.randint(1000, 9999)}"
        trade = {
            "id": trade_id,
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "entry_price": entry_price,
            "current_price": entry_price,
            "trade_value": trade_value,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "leverage_used": self.available_leverage,
            "status": "OPEN",
            "entry_time": datetime.now().isoformat(),
            "pnl": 0.0,
            "pnl_percent": 0.0
        }
        
        # Update positions
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(trade)
        
        # Update trade history
        self.trade_history.append(trade)
        self.daily_trades += 1
        
        print(f"[PAPER TRADE EXECUTED] {trade_id}")
        print(f"  {side.upper()} {amount:.6f} {symbol} @ ${entry_price:,.2f}")
        print(f"  Value: ${trade_value:,.2f} (Leverage: {self.available_leverage}x)")
        print(f"  Stop Loss: ${stop_loss:,.2f}")
        print(f"  Take Profit: ${take_profit:,.2f}")
        
        return trade
    
    def update_positions(self, market_prices: Dict[str, float]):
        """Update all open positions with current market prices"""
        for symbol, trades in self.positions.items():
            current_price = market_prices.get(symbol)
            if not current_price:
                continue
                
            for trade in trades:
                if trade["status"] != "OPEN":
                    continue
                
                # Calculate P&L
                if trade["side"] == "buy":
                    pnl = (current_price - trade["entry_price"]) * trade["amount"]
                else:  # sell (short)
                    pnl = (trade["entry_price"] - current_price) * trade["amount"]
                
                pnl_percent = (pnl / trade["trade_value"]) * 100
                
                trade["current_price"] = current_price
                trade["pnl"] = pnl
                trade["pnl_percent"] = pnl_percent
                
                # Check stop loss
                if trade["side"] == "buy" and current_price <= trade["stop_loss"]:
                    trade["status"] = "STOP_LOSS"
                    print(f"[STOP LOSS HIT] {trade['id']}: ${current_price:,.2f} <= ${trade['stop_loss']:,.2f}")
                elif trade["side"] == "sell" and current_price >= trade["stop_loss"]:
                    trade["status"] = "STOP_LOSS"
                    print(f"[STOP LOSS HIT] {trade['id']}: ${current_price:,.2f} >= ${trade['stop_loss']:,.2f}")
                
                # Check take profit
                if trade["side"] == "buy" and current_price >= trade["take_profit"]:
                    trade["status"] = "TAKE_PROFIT"
                    print(f"[TAKE PROFIT HIT] {trade['id']}: ${current_price:,.2f} >= ${trade['take_profit']:,.2f}")
                elif trade["side"] == "sell" and current_price <= trade["take_profit"]:
                    trade["status"] = "TAKE_PROFIT"
                    print(f"[TAKE PROFIT HIT] {trade['id']}: ${current_price:,.2f} <= ${trade['take_profit']:,.2f}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_value = self.balance
        open_positions = []
        total_pnl = 0
        
        for symbol, trades in self.positions.items():
            for trade in trades:
                if trade["status"] == "OPEN":
                    open_positions.append(trade)
                    total_pnl += trade["pnl"]
                    total_value += trade["pnl"]
        
        return {
            "paper_balance": self.balance,
            "total_value": total_value,
            "open_positions": len(open_positions),
            "total_pnl": total_pnl,
            "daily_trades_used": self.daily_trades,
            "daily_trades_remaining": MAX_DAILY_TRADES - self.daily_trades,
            "leverage_available": self.available_leverage
        }

class MarketDataFetcher:
    """Fetch market data from CoinGecko API"""
    
    @staticmethod
    def get_current_prices() -> Dict[str, float]:
        """Get current prices for monitored pairs"""
        prices = {}
        
        # CoinGecko IDs for our pairs
        coin_ids = {
            "BTCUSD": "bitcoin",
            "ETHUSD": "ethereum", 
            "SOLUSD": "solana"
        }
        
        try:
            # Fetch all prices at once
            url = f"{COINGECKO_API}/simple/price"
            params = {
                "ids": ",".join(coin_ids.values()),
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            for symbol, coin_id in coin_ids.items():
                if coin_id in data and "usd" in data[coin_id]:
                    prices[symbol] = data[coin_id]["usd"]
                else:
                    # Fallback to simulated price if API fails
                    prices[symbol] = random.uniform(100, 50000)
                    
        except Exception as e:
            print(f"API Error: {e}, using simulated prices")
            # Simulated prices for demo
            prices = {
                "BTCUSD": random.uniform(60000, 70000),
                "ETHUSD": random.uniform(3000, 4000),
                "SOLUSD": random.uniform(100, 200)
            }
        
        return prices
    
    @staticmethod
    def get_price_history(symbol: str, hours: int = 24) -> List[float]:
        """Get price history for momentum analysis"""
        # For paper trading, we'll simulate price history
        # In production, you would fetch real historical data
        
        current_price = MarketDataFetcher.get_current_prices().get(symbol, 1000)
        
        # Generate simulated price history with trends
        prices = []
        base_price = current_price * random.uniform(0.9, 1.1)
        
        for i in range(hours):
            # Add some randomness and trend
            trend = random.uniform(-0.02, 0.02)  # -2% to +2% per hour
            noise = random.uniform(-0.01, 0.01)  # Additional noise
            
            if i == 0:
                price = base_price
            else:
                price = prices[-1] * (1 + trend + noise)
            
            prices.append(price)
        
        return prices

class AggressiveMomentumAnalyzer:
    """Analyze aggressive momentum trading opportunities"""
    
    @staticmethod
    def calculate_hourly_momentum(prices: List[float]) -> Dict:
        """Calculate momentum metrics for last hour"""
        if len(prices) < 2:
            return {"change_percent": 0, "strength": 0, "trend": "NEUTRAL"}
        
        # Last hour price change
        current = prices[-1] if prices else 0
        hour_ago = prices[-2] if len(prices) >= 2 else current
        
        change_percent = ((current - hour_ago) / hour_ago) * 100
        
        # Determine trend strength
        if change_percent >= 5:
            trend = "STRONG_BULL"
            strength = min(100, change_percent * 2)  # Scale strength
        elif change_percent >= 2:
            trend = "BULLISH"
            strength = min(80, change_percent * 3)
        elif change_percent <= -5:
            trend = "STRONG_BEAR"
            strength = min(100, abs(change_percent) * 2)
        elif change_percent <= -2:
            trend = "BEARISH"
            strength = min(80, abs(change_percent) * 3)
        else:
            trend = "NEUTRAL"
            strength = 0
        
        return {
            "change_percent": change_percent,
            "strength": strength,
            "trend": trend,
            "current_price": current,
            "hour_ago_price": hour_ago
        }
    
    @staticmethod
    def detect_breakout_pattern(prices: List[float], period: int = 20) -> Dict:
        """Detect breakout patterns for aggressive trading"""
        if len(prices) < period:
            return {"pattern": "NO_DATA", "confidence": 0}
        
        recent = prices[-period:]
        
        # Calculate rolling high/low
        rolling_high = max(recent)
        rolling_low = min(recent)
        current = recent[-1]
        
        # Check for breakout above resistance
        if current > rolling_high * 1.02:  # 2% above recent high
            return {
                "pattern": "BREAKOUT_UP",
                "confidence": min(90, ((current / rolling_high) - 1) * 1000),
                "resistance_level": rolling_high,
                "breakout_percent": ((current / rolling_high) - 1) * 100
            }
        
        # Check for breakdown below support
        elif current < rolling_low * 0.98:  # 2% below recent low
            return {
                "pattern": "BREAKOUT_DOWN",
                "confidence": min(90, (1 - (current / rolling_low)) * 1000),
                "support_level": rolling_low,
                "breakdown_percent": (1 - (current / rolling_low)) * 100
            }
        
        return {"pattern": "CONSOLIDATION", "confidence": 0}
    
    @staticmethod
    def calculate_volume_spike_simulated() -> float:
        """Simulate volume spike detection (in production, use real volume data)"""
        # Random volume spike simulation
        base_volume = random.uniform(1000, 10000)
        spike_multiplier = random.uniform(1.0, 3.0)  # 1x to 3x volume
        
        # 30% chance of significant volume spike
        if random.random() < 0.3:
            spike_multiplier = random.uniform(3.0, 10.0)
        
        return base_volume * spike_multiplier

class AggressiveTradingStrategy:
    """Aggressive momentum trading strategy"""
    
    def __init__(self, paper_trader: PaperTradingSimulator):
        self.paper_trader = paper_trader
        self.analyzer = AggressiveMomentumAnalyzer()
    
    def generate_aggressive_signals(self, symbol: str, current_price: float) -> List[Dict]:
        """Generate aggressive trading signals based on momentum"""
        signals = []
        
        # Get price history for analysis
        price_history = MarketDataFetcher.get_price_history(symbol)
        
        # Analyze momentum
        momentum = self.analyzer.calculate_hourly_momentum(price_history)
        
        # Detect breakout patterns
        breakout = self.analyzer.detect_breakout_pattern(price_history)
        
        # Simulate volume spike
        volume = self.analyzer.calculate_volume_spike_simulated()
        
        # AGGRESSIVE TRADING RULES:
        # 1. Strong momentum (5%+ move in last hour)
        # 2. Breakout patterns
        # 3. High volume spikes
        
        # Rule 1: Strong bullish momentum with volume
        if momentum["trend"] in ["STRONG_BULL", "BULLISH"] and momentum["change_percent"] >= 2:
            if volume > 5000:  # Simulated volume threshold
                signal = {
                    "symbol": symbol,
                    "action": "BUY",
                    "reason": f"Bullish momentum: {momentum['change_percent']:.2f}% in last hour",
                    "confidence": momentum["strength"],
                    "momentum_strength": momentum["strength"],
                    "current_price": current_price,
                    "entry_price": current_price,
                    "stop_loss": current_price * (1 - STOP_LOSS_PERCENT/100),
                    "take_profit": current_price * (1 + TAKE_PROFIT_PERCENT/100),
                    "volume_spike": volume > 10000
                }
                signals.append(signal)
        
        # Rule 2: Strong bearish momentum with volume
        if momentum["trend"] in ["STRONG_BEAR", "BEARISH"] and momentum["change_percent"] <= -2:
            if volume > 5000:
                signal = {
                    "symbol": symbol,
                    "action": "SELL",
                    "reason": f"Bearish momentum: {momentum['change_percent']:.2f}% in last hour",
                    "confidence": momentum["strength"],
                    "momentum_strength": momentum["strength"],
                    "current_price": current_price,
                    "entry_price": current_price,
                    "stop_loss": current_price * (1 + STOP_LOSS_PERCENT/100),
                    "take_profit": current_price * (1 - TAKE_PROFIT_PERCENT/100),
                    "volume_spike": volume > 10000
                }
                signals.append(signal)
        
        # Rule 3: Breakout patterns (even stronger signal)
        if breakout["pattern"] in ["BREAKOUT_UP", "BREAKOUT_DOWN"] and breakout["confidence"] > 50:
            if breakout["pattern"] == "BREAKOUT_UP":
                signal = {
                    "symbol": symbol,
                    "action": "BUY",
                    "reason": f"Breakout UP: {breakout['breakout_percent']:.2f}% above resistance",
                    "confidence": breakout["confidence"],
                    "momentum_strength": 90,  # High confidence for breakouts
                    "current_price": current_price,
                    "entry_price": current_price,
                    "stop_loss": current_price * (1 - STOP_LOSS_PERCENT/100),
                    "take_profit":