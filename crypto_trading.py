#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot for Gemini API
Risk Parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Capital: $1,000
Pairs: BTC/USD and ETH/USD
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
CAPITAL = 1000.0
MAX_TRADES_PER_DAY = 2
STOP_LOSS_PCT = 5.0  # 5%
TAKE_PROFIT_PCT = 10.0  # 10%

# Gemini API endpoints
GEMINI_API_BASE = "https://api.gemini.com"
GEMINI_SANDBOX_BASE = "https://api.sandbox.gemini.com"

class GeminiTrader:
    def __init__(self, api_key: str = None, api_secret: str = None, sandbox: bool = False):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_secret = api_secret or os.getenv("GEMINI_API_SECRET")
        self.base_url = GEMINI_SANDBOX_BASE if sandbox else GEMINI_API_BASE
        self.session = requests.Session()
        self.trades_today = 0
        self.last_trade_date = None
        self.load_trade_history()
        
    def load_trade_history(self):
        """Load today's trade count from file"""
        try:
            with open("trade_history.json", "r") as f:
                history = json.load(f)
                today = datetime.now().strftime("%Y-%m-%d")
                if history.get("date") == today:
                    self.trades_today = history.get("trades", 0)
                    self.last_trade_date = today
        except FileNotFoundError:
            self.trades_today = 0
            self.last_trade_date = None
    
    def save_trade_history(self):
        """Save today's trade count to file"""
        today = datetime.now().strftime("%Y-%m-%d")
        history = {
            "date": today,
            "trades": self.trades_today
        }
        with open("trade_history.json", "w") as f:
            json.dump(history, f)
    
    def reset_daily_trades(self):
        """Reset trade count if it's a new day"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
            self.save_trade_history()
    
    def can_trade(self) -> bool:
        """Check if we can execute more trades today"""
        self.reset_daily_trades()
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def generate_signature(self, payload: str) -> str:
        """Generate Gemini API signature"""
        encoded_payload = payload.encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.api_secret.encode(), b64, hashlib.sha384).hexdigest()
        return signature
    
    def make_request(self, endpoint: str, payload: Dict = None, method: str = "POST") -> Dict:
        """Make authenticated request to Gemini API"""
        if payload is None:
            payload = {}
        
        payload["request"] = endpoint
        payload["nonce"] = int(time.time() * 1000)
        
        encoded_payload = json.dumps(payload).encode()
        b64_payload = base64.b64encode(encoded_payload)
        signature = self.generate_signature(b64_payload)
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": b64_payload,
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        if method == "POST":
            response = self.session.post(url, headers=headers)
        else:
            response = self.session.get(url, headers=headers)
        
        return response.json()
    
    def get_ticker(self, symbol: str = "btcusd") -> Dict:
        """Get current ticker price"""
        endpoint = f"/v1/pubticker/{symbol}"
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url)
        return response.json()
    
    def get_order_book(self, symbol: str = "btcusd") -> Dict:
        """Get current order book"""
        endpoint = f"/v1/book/{symbol}"
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url)
        return response.json()
    
    def get_market_sentiment(self, symbol: str = "btcusd") -> Dict:
        """Analyze market sentiment based on order book"""
        order_book = self.get_order_book(symbol)
        
        # Calculate bid/ask imbalance
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        total_bid_volume = sum(float(bid["amount"]) for bid in bids[:10]) if bids else 0
        total_ask_volume = sum(float(ask["amount"]) for ask in asks[:10]) if asks else 0
        
        sentiment = "NEUTRAL"
        if total_bid_volume > total_ask_volume * 1.2:
            sentiment = "BULLISH"
        elif total_ask_volume > total_bid_volume * 1.2:
            sentiment = "BEARISH"
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "bid_volume": total_bid_volume,
            "ask_volume": total_ask_volume,
            "bid_ask_ratio": total_bid_volume / total_ask_volume if total_ask_volume > 0 else 0
        }
    
    def calculate_support_resistance(self, symbol: str = "btcusd") -> Dict:
        """Calculate support and resistance levels from order book"""
        order_book = self.get_order_book(symbol)
        
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        # Support levels (strongest bids)
        support_levels = []
        for i, bid in enumerate(bids[:5]):
            price = float(bid["price"])
            volume = float(bid["amount"])
            support_levels.append({
                "level": price,
                "volume": volume,
                "strength": volume * (5 - i)  # Weight by position
            })
        
        # Resistance levels (strongest asks)
        resistance_levels = []
        for i, ask in enumerate(asks[:5]):
            price = float(ask["price"])
            volume = float(ask["amount"])
            resistance_levels.append({
                "level": price,
                "volume": volume,
                "strength": volume * (5 - i)  # Weight by position
            })
        
        return {
            "symbol": symbol,
            "support_levels": sorted(support_levels, key=lambda x: x["strength"], reverse=True)[:3],
            "resistance_levels": sorted(resistance_levels, key=lambda x: x["strength"], reverse=True)[:3]
        }
    
    def analyze_trading_opportunity(self, symbol: str = "btcusd") -> Dict:
        """Analyze if there's a trading opportunity"""
        ticker = self.get_ticker(symbol)
        sentiment = self.get_market_sentiment(symbol)
        levels = self.calculate_support_resistance(symbol)
        
        current_price = float(ticker["last"])
        
        # Find nearest support and resistance
        nearest_support = None
        nearest_resistance = None
        
        if levels["support_levels"]:
            nearest_support = min(levels["support_levels"], 
                                 key=lambda x: abs(x["level"] - current_price))
        
        if levels["resistance_levels"]:
            nearest_resistance = min(levels["resistance_levels"], 
                                    key=lambda x: abs(x["level"] - current_price))
        
        # Calculate distance to support/resistance as percentage
        support_distance_pct = 0
        resistance_distance_pct = 0
        
        if nearest_support:
            support_distance_pct = ((current_price - nearest_support["level"]) / current_price) * 100
        
        if nearest_resistance:
            resistance_distance_pct = ((nearest_resistance["level"] - current_price) / current_price) * 100
        
        # Determine trading signal
        signal = "HOLD"
        reason = ""
        
        # Conservative strategy:
        # 1. Buy if price is near strong support and sentiment is bullish
        # 2. Sell if price is near strong resistance and sentiment is bearish
        # 3. Otherwise hold
        
        if support_distance_pct < 2 and sentiment["sentiment"] == "BULLISH":
            signal = "BUY"
            reason = f"Price near strong support ({support_distance_pct:.2f}% away) with bullish sentiment"
        elif resistance_distance_pct < 2 and sentiment["sentiment"] == "BEARISH":
            signal = "SELL"
            reason = f"Price near strong resistance ({resistance_distance_pct:.2f}% away) with bearish sentiment"
        else:
            reason = f"No clear opportunity. Support distance: {support_distance_pct:.2f}%, Resistance distance: {resistance_distance_pct:.2f}%, Sentiment: {sentiment['sentiment']}"
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "signal": signal,
            "reason": reason,
            "sentiment": sentiment["sentiment"],
            "support_distance_pct": support_distance_pct,
            "resistance_distance_pct": resistance_distance_pct,
            "nearest_support": nearest_support["level"] if nearest_support else None,
            "nearest_resistance": nearest_resistance["level"] if nearest_resistance else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on capital and risk"""
        # Use 50% of capital per trade for conservative approach
        position_value = CAPITAL * 0.5
        position_size = position_value / price
        return position_size
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Place an order on Gemini"""
        if not self.can_trade():
            return {"error": f"Maximum daily trades ({MAX_TRADES_PER_DAY}) reached"}
        
        if not self.api_key or not self.api_secret:
            return {"error": "API credentials not configured"}
        
        payload = {
            "symbol": symbol,
            "amount": str(amount),
            "side": side,
            "type": "exchange limit"
        }
        
        if price:
            payload["price"] = str(price)
        
        # In sandbox mode, simulate order placement
        if "sandbox" in self.base_url:
            order_id = f"sim_{int(time.time())}"
            result = {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "status": "simulated"
            }
        else:
            result = self.make_request("/v1/order/new", payload)
        
        if "order_id" in result:
            self.trades_today += 1
            self.save_trade_history()
            
            # Calculate stop loss and take profit prices
            if side == "buy":
                stop_loss_price = price * (1 - STOP_LOSS_PCT / 100)
                take_profit_price = price * (1 + TAKE_PROFIT_PCT / 100)
            else:  # sell
                stop_loss_price = price * (1 + STOP_LOSS_PCT / 100)
                take_profit_price = price * (1 - TAKE_PROFIT_PCT / 100)
            
            result["stop_loss"] = stop_loss_price
            result["take_profit"] = take_profit_price
            result["risk_parameters"] = {
                "stop_loss_pct": STOP_LOSS_PCT,
                "take_profit_pct": TAKE_PROFIT_PCT
            }
        
        return result
    
    def execute_trading_strategy(self):
        """Execute the complete trading strategy"""
        print(f"\n{'='*60}")
        print(f"CRYPTO TRADING ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        print(f"\nCAPITAL: ${CAPITAL:,.2f}")
        print(f"RISK PARAMETERS: {STOP_LOSS_PCT}% stop-loss, {TAKE_PROFIT_PCT}% take-profit")
        print(f"DAILY LIMIT: {MAX_TRADES_PER_DAY} trades (used: {self.trades_today})")
        
        # Analyze both BTC and ETH
        symbols = ["btcusd", "ethusd"]
        analysis_results = []
        trading_decisions = []
        
        for symbol in symbols:
            print(f"\n{'='*40}")
            print(f"ANALYZING {symbol.upper()}")
            print(f"{'='*40}")
            
            # Get analysis
            analysis = self.analyze_trading_opportunity(symbol)
            analysis_results.append(analysis)
            
            print(f"Current Price: ${analysis['current_price']:,.2f}")
            print(f"Market Sentiment: {analysis['sentiment']}")
            print(f"Trading Signal: {analysis['signal']}")
            print(f"Reason: {analysis['reason']}")
            
            if analysis['nearest_support']:
                print(f"Nearest Support: ${analysis['nearest_support']:,.2f} ({analysis['support_distance_pct']:.2f}% away)")
            if analysis['nearest_resistance']:
                print(f"Nearest Resistance: ${analysis['nearest_resistance']:,.2f} ({analysis['resistance_distance_pct']:.2f}% away)")
            
            # Check if we should trade
            if analysis['signal'] in ['BUY', 'SELL'] and self.can_trade():
                position_size = self.calculate_position_size(analysis['current_price'])
                
                print(f"\nTRADING OPPORTUNITY DETECTED!")
                print(f"Action: {analysis['signal']}")
                print(f"Position Size: {position_size:.6f} {symbol[:3].upper()}")
                print(f"Position Value: ${position_size * analysis['current_price']:,.2f}")
                
                # Place order (simulated in sandbox)
                order_result = self.place_order(
                    symbol=symbol,
                    side="buy" if analysis['signal'] == "BUY" else "sell",
                    amount=position_size,
                    price=analysis['current_price']
                )
                
                if "order_id" in order_result:
                    trading_decisions.append({
                        "symbol": symbol,
                        "action": analysis['signal'],
                        "order_id": order_result["order_id"],
                        "price": analysis['current_price'],
                        "amount": position_size,
                        "value": position_size * analysis['current_price'],
                        "stop_loss": order_result.get("stop_loss"),
                        "take_profit": order_result.get("take_profit"),
                        "status": order_result.get("status", "executed")
                    })
                    
                    print(f"Order Placed: {order_result['order_id']}")
                    print(f"Stop Loss: ${order_result.get('stop_loss', 0):,.2f}")
                    print(f"Take Profit: ${order_result.get('take_profit', 0):,.2f}")
                else:
                    print(f"Order Failed: {order_result.get('error', 'Unknown error')}")
            else:
                if analysis['signal'] in ['BUY', 'SELL']:
                    print(f"\nSignal detected but cannot trade: Daily limit reached")
                else:
                    print(f"\nNo trading signal - Holding position")
        
        # Generate summary
        print(f"\n{'='*60}")
        print("TRADING SUMMARY")
        print(f"{'='*60}")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "capital": CAPITAL,
            "trades_today": self.trades_today,
            "max_trades_per_day": MAX_TRADES_PER_DAY,
            "risk_parameters": {
                "stop_loss_pct": STOP_LOSS_PCT,
                "take_profit_pct": TAKE_PROFIT_PCT
            },
            "market_analysis": analysis_results,
            "trades_executed": trading_decisions
        }
        
        # Save summary to file
        with open("trading_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        # Print plain text summary for cron delivery
        print("\n" + "="*60)
        print("PLAIN TEXT SUMMARY FOR DELIVERY")
        print("="*60)
        
        plain_summary = f"""
CRYPTO TRADING REPORT
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Capital: ${CAPITAL:,.2f}
Trades Today: {self.trades_today}/{MAX_TRADES_PER_DAY}
Risk Parameters: {STOP_LOSS_PCT}% stop-loss, {TAKE_PROFIT_PCT}% take-profit

MARKET ANALYSIS:
"""
        
        for analysis in analysis_results:
            plain_summary += f"""
{analysis['symbol'].upper()}:
  Price: ${analysis['current_price']:,.2f}
  Signal: {analysis['signal']}
  Sentiment: {analysis['sentiment']}
  Reason: {analysis['reason']}
"""
        
        if trading_decisions:
            plain_summary += "\nTRADES EXEC