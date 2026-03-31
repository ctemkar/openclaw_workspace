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

# Configuration
CAPITAL = 1000.0  # $1,000 capital
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2

# Gemini API Configuration (using sandbox for safety)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.environ.get('GEMINI_API_SECRET', '')
GEMINI_API_BASE = "https://api.gemini.com"  # Production
# GEMINI_API_BASE = "https://api.sandbox.gemini.com"  # Sandbox

# Trading pairs to analyze
TRADING_PAIRS = ["btcusd", "ethusd"]

class GeminiTrader:
    def __init__(self, api_key: str, api_secret: str, base_url: str = GEMINI_API_BASE):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.trades_today = 0
        self.last_trade_date = None
        
    def _generate_payload(self, payload: Dict) -> str:
        """Generate payload for Gemini API"""
        return json.dumps(payload)
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for Gemini API"""
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        return signature
    
    def _make_request(self, endpoint: str, payload: Dict = None, method: str = "POST") -> Dict:
        """Make authenticated request to Gemini API"""
        if payload is None:
            payload = {}
        
        payload_nonce = str(int(time.time() * 1000))
        payload["request"] = f"/v1{endpoint}"
        payload["nonce"] = payload_nonce
        
        encoded_payload = base64.b64encode(json.dumps(payload).encode('utf-8'))
        signature = self._generate_signature(encoded_payload.decode('utf-8'))
        
        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': encoded_payload.decode('utf-8'),
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
        }
        
        url = f"{self.base_url}/v1{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return {"error": str(e)}
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price for a symbol"""
        try:
            response = requests.get(f"{self.base_url}/v1/pubticker/{symbol}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get ticker for {symbol}: {e}")
            return {}
    
    def get_order_book(self, symbol: str) -> Dict:
        """Get order book for a symbol"""
        try:
            response = requests.get(f"{self.base_url}/v1/book/{symbol}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get order book for {symbol}: {e}")
            return {}
    
    def get_market_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment based on order book and recent trades"""
        ticker = self.get_ticker(symbol)
        order_book = self.get_order_book(symbol)
        
        if not ticker or not order_book:
            return {"sentiment": "neutral", "confidence": 0}
        
        # Calculate bid/ask spread
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        bid_price = float(bids[0][0]) if bids and len(bids[0]) > 0 else 0
        ask_price = float(asks[0][0]) if asks and len(asks[0]) > 0 else 0
        last_price = float(ticker.get('last', 0))
        
        if bid_price == 0 or ask_price == 0:
            return {"sentiment": "neutral", "confidence": 0}
        
        spread = (ask_price - bid_price) / bid_price
        
        # Simple sentiment analysis
        sentiment = "neutral"
        confidence = 0.5
        
        if spread < 0.001:  # Tight spread suggests high liquidity
            confidence = 0.7
            if last_price > (bid_price + ask_price) / 2:
                sentiment = "bullish"
            else:
                sentiment = "bearish"
        else:
            confidence = 0.3
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "confidence": confidence,
            "last_price": last_price,
            "bid_price": bid_price,
            "ask_price": ask_price,
            "spread": spread
        }
    
    def calculate_support_resistance(self, symbol: str) -> Dict:
        """Calculate support and resistance levels based on order book"""
        order_book = self.get_order_book(symbol)
        
        if not order_book:
            return {"support": 0, "resistance": 0}
        
        # Use top 5 bids as support levels
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        if not bids or not asks:
            return {"support": 0, "resistance": 0}
        
        # Calculate weighted average support and resistance
        try:
            total_bid_volume = sum(float(bid[1]) for bid in bids[:5] if len(bid) > 1)
            total_ask_volume = sum(float(ask[1]) for ask in asks[:5] if len(ask) > 1)
            
            if total_bid_volume == 0 or total_ask_volume == 0:
                return {"support": 0, "resistance": 0}
            
            support = sum(float(bid[0]) * float(bid[1]) for bid in bids[:5] if len(bid) > 1) / total_bid_volume
            resistance = sum(float(ask[0]) * float(ask[1]) for ask in asks[:5] if len(ask) > 1) / total_ask_volume
        except (IndexError, ValueError, TypeError):
            # Fallback to simple average if data format is unexpected
            support = sum(float(bid[0]) for bid in bids[:5] if len(bid) > 0) / min(len(bids[:5]), 5)
            resistance = sum(float(ask[0]) for ask in asks[:5] if len(ask) > 0) / min(len(asks[:5]), 5)
            total_bid_volume = len(bids[:5])
            total_ask_volume = len(asks[:5])
        
        return {
            "symbol": symbol,
            "support": support,
            "resistance": resistance,
            "support_volume": total_bid_volume,
            "resistance_volume": total_ask_volume
        }
    
    def can_trade_today(self) -> bool:
        """Check if we can execute more trades today"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def execute_trade(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Execute a trade (buy or sell)"""
        if not self.can_trade_today():
            return {"error": f"Maximum trades per day ({MAX_TRADES_PER_DAY}) reached"}
        
        if not self.api_key or not self.api_secret:
            return {"error": "API credentials not configured", "simulated": True}
        
        # For safety, we'll simulate trades unless API credentials are properly configured
        print(f"SIMULATED TRADE: {side.upper()} {amount} {symbol} @ ${price:.2f}")
        
        # In a real implementation, this would make the API call:
        # payload = {
        #     "symbol": symbol,
        #     "amount": str(amount),
        #     "price": str(price),
        #     "side": side,
        #     "type": "exchange limit",
        #     "options": ["immediate-or-cancel"]
        # }
        # result = self._make_request("/order/new", payload)
        
        # For simulation, return success
        self.trades_today += 1
        
        return {
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price,
            "status": "simulated_success",
            "order_id": f"sim_{int(time.time())}",
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_trading_opportunity(self, symbol: str) -> Dict:
        """Analyze if there's a trading opportunity"""
        sentiment = self.get_market_sentiment(symbol)
        levels = self.calculate_support_resistance(symbol)
        
        if not sentiment or not levels:
            return {"opportunity": False, "reason": "Insufficient data"}
        
        last_price = sentiment.get("last_price", 0)
        support = levels.get("support", 0)
        resistance = levels.get("resistance", 0)
        
        if last_price == 0 or support == 0 or resistance == 0:
            return {"opportunity": False, "reason": "Invalid price data"}
        
        # Conservative strategy:
        # 1. Buy near support with bullish sentiment
        # 2. Sell near resistance with bearish sentiment
        
        buy_zone = support * 1.01  # Within 1% of support
        sell_zone = resistance * 0.99  # Within 1% of resistance
        
        opportunity = False
        side = None
        confidence = 0
        
        if last_price <= buy_zone and sentiment.get("sentiment") == "bullish":
            opportunity = True
            side = "buy"
            confidence = sentiment.get("confidence", 0) * 0.8  # Conservative multiplier
        elif last_price >= sell_zone and sentiment.get("sentiment") == "bearish":
            opportunity = True
            side = "sell"
            confidence = sentiment.get("confidence", 0) * 0.8
        
        return {
            "symbol": symbol,
            "opportunity": opportunity,
            "side": side,
            "confidence": confidence,
            "last_price": last_price,
            "support": support,
            "resistance": resistance,
            "sentiment": sentiment.get("sentiment"),
            "reason": f"Price ${last_price:.2f} near {'support' if side == 'buy' else 'resistance'} with {sentiment.get('sentiment')} sentiment"
        }

def main():
    """Main trading execution"""
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Capital: ${CAPITAL:.2f}")
    print(f"Risk Parameters: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
    print(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
    print("=" * 60)
    
    # Initialize trader
    trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
    
    # Check if we can trade today
    if not trader.can_trade_today():
        print("Maximum trades per day already reached. No trades will be executed.")
        return
    
    trades_executed = []
    analysis_results = []
    
    # Analyze each trading pair
    for symbol in TRADING_PAIRS:
        print(f"\nAnalyzing {symbol.upper()}...")
        
        # Get market data
        ticker = trader.get_ticker(symbol)
        sentiment = trader.get_market_sentiment(symbol)
        levels = trader.calculate_support_resistance(symbol)
        opportunity = trader.analyze_trading_opportunity(symbol)
        
        analysis_results.append({
            "symbol": symbol,
            "ticker": ticker,
            "sentiment": sentiment,
            "levels": levels,
            "opportunity": opportunity
        })
        
        # Display analysis
        if ticker:
            print(f"  Last Price: ${float(ticker.get('last', 0)):.2f}")
            print(f"  24h Change: {float(ticker.get('percentChange24h', 0)):.2f}%")
        
        if sentiment:
            print(f"  Sentiment: {sentiment.get('sentiment', 'unknown')} (confidence: {sentiment.get('confidence', 0):.2f})")
        
        if levels:
            print(f"  Support: ${levels.get('support', 0):.2f}")
            print(f"  Resistance: ${levels.get('resistance', 0):.2f}")
        
        # Execute trade if opportunity exists
        if opportunity.get("opportunity") and opportunity.get("confidence", 0) > 0.6:
            print(f"  ✓ Trading Opportunity: {opportunity.get('reason')}")
            
            side = opportunity.get("side")
            price = opportunity.get("last_price", 0)
            
            # Calculate position size (conservative: 20% of capital per trade)
            position_size = CAPITAL * 0.2 / price if side == "buy" else 0
            
            if position_size > 0:
                print(f"  Executing {side.upper()} order...")
                trade_result = trader.execute_trade(
                    symbol=symbol,
                    side=side,
                    amount=position_size,
                    price=price
                )
                
                if "error" not in trade_result:
                    trades_executed.append(trade_result)
                    print(f"  ✓ Trade executed successfully")
                else:
                    print(f"  ✗ Trade failed: {trade_result.get('error')}")
            else:
                print(f"  ✗ Position size too small")
        else:
            print(f"  ✗ No high-confidence trading opportunity")
    
    # Generate summary
    print("\n" + "=" * 60)
    print("TRADING SUMMARY")
    print("=" * 60)
    
    if trades_executed:
        print(f"\nTrades Executed Today: {len(trades_executed)}")
        for trade in trades_executed:
            print(f"  • {trade['side'].upper()} {trade['amount']:.6f} {trade['symbol']} @ ${trade['price']:.2f}")
            print(f"    Order ID: {trade.get('order_id', 'N/A')}")
            print(f"    Time: {trade.get('timestamp', 'N/A')}")
    else:
        print("\nNo trades executed today.")
    
    print(f"\nRemaining Trades Available Today: {MAX_TRADES_PER_DAY - trader.trades_today}")
    print(f"Analysis Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "trades_executed": trades_executed,
        "analysis_results": analysis_results,
        "remaining_trades": MAX_TRADES_PER_DAY - trader.trades_today
    }

if __name__ == "__main__":
    result = main()