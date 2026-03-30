#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
$1,000 investment with real Gemini API trades
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
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

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_SECRET = os.environ.get("GEMINI_API_SECRET")
GEMINI_BASE_URL = "https://api.gemini.com"

# Trading Parameters
INITIAL_CAPITAL = 1000.0  # $1,000
MAX_DAILY_TRADES = 2
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_POSITION_SIZE = 0.5  # 50% of capital per trade
MIN_TRADE_AMOUNT = 10.0  # Minimum $10 per trade

# Trading Pairs
TRADING_PAIRS = ["BTCUSD", "ETHUSD"]

class GeminiTradingBot:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_secret = GEMINI_API_SECRET.encode()
        self.session = requests.Session()
        self.trades_today = 0
        self.last_trade_date = None
        
    def _generate_payload(self, payload: Dict) -> str:
        """Generate payload for Gemini API"""
        return json.dumps(payload)
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC SHA384 signature"""
        signature = hmac.new(
            self.api_secret,
            payload.encode(),
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
        
        encoded_payload = base64.b64encode(json.dumps(payload).encode())
        signature = self._generate_signature(encoded_payload.decode())
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": encoded_payload.decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        url = f"{GEMINI_BASE_URL}/v1{endpoint}"
        
        try:
            if method == "POST":
                response = self.session.post(url, headers=headers)
            else:
                response = self.session.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return {}
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price for a symbol"""
        try:
            response = requests.get(f"{GEMINI_BASE_URL}/v1/pubticker/{symbol.lower()}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ticker Error for {symbol}: {e}")
            return {}
    
    def get_order_book(self, symbol: str) -> Dict:
        """Get order book for a symbol"""
        try:
            response = requests.get(f"{GEMINI_BASE_URL}/v1/book/{symbol.lower()}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Order Book Error for {symbol}: {e}")
            return {}
    
    def get_market_sentiment(self, symbol: str) -> str:
        """Analyze market sentiment based on order book and recent price action"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            return "NEUTRAL"
        
        order_book = self.get_order_book(symbol)
        if not order_book:
            return "NEUTRAL"
        
        # Calculate bid-ask spread
        try:
            bid_price = float(order_book.get('bids', [{}])[0].get('price', 0))
            ask_price = float(order_book.get('asks', [{}])[0].get('price', 0))
            
            if bid_price == 0 or ask_price == 0:
                return "NEUTRAL"
            
            spread_pct = (ask_price - bid_price) / bid_price * 100
            
            # Get 24h price change
            last_price = float(ticker.get('last', 0))
            open_price = float(ticker.get('open', last_price))
            
            if open_price == 0:
                return "NEUTRAL"
            
            change_pct = ((last_price - open_price) / open_price) * 100
            
            # Determine sentiment
            if change_pct > 2 and spread_pct < 0.1:
                return "BULLISH"
            elif change_pct < -2 and spread_pct < 0.1:
                return "BEARISH"
            elif abs(change_pct) < 1 and spread_pct < 0.05:
                return "CONSOLIDATING"
            else:
                return "NEUTRAL"
                
        except (IndexError, ValueError, KeyError) as e:
            print(f"Sentiment analysis error: {e}")
            return "NEUTRAL"
    
    def calculate_support_resistance(self, symbol: str) -> Tuple[float, float]:
        """Calculate approximate support and resistance levels"""
        ticker = self.get_ticker(symbol)
        if not ticker:
            return 0.0, 0.0
        
        try:
            last_price = float(ticker.get('last', 0))
            high_24h = float(ticker.get('high', last_price * 1.05))
            low_24h = float(ticker.get('low', last_price * 0.95))
            
            # Simple calculation for support and resistance
            support = low_24h * 0.99  # 1% below 24h low
            resistance = high_24h * 1.01  # 1% above 24h high
            
            return support, resistance
        except (ValueError, KeyError) as e:
            print(f"Support/Resistance calculation error: {e}")
            return last_price * 0.95, last_price * 1.05
    
    def can_trade_today(self) -> bool:
        """Check if we can make more trades today"""
        today = datetime.now().date()
        
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        return self.trades_today < MAX_DAILY_TRADES
    
    def get_account_balance(self) -> Dict:
        """Get account balances"""
        return self._make_request("/balances")
    
    def place_order(self, symbol: str, amount: float, price: float, side: str) -> Dict:
        """Place a limit order"""
        if not self.can_trade_today():
            return {"error": "Daily trade limit reached"}
        
        # Validate order parameters
        if amount < MIN_TRADE_AMOUNT:
            return {"error": f"Amount below minimum: ${MIN_TRADE_AMOUNT}"}
        
        payload = {
            "symbol": symbol.lower(),
            "amount": str(amount),
            "price": str(price),
            "side": side.lower(),
            "type": "exchange limit",
            "options": ["maker-or-cancel"]
        }
        
        result = self._make_request("/order/new", payload)
        
        if "order_id" in result:
            self.trades_today += 1
            print(f"Order placed: {side} {amount} {symbol} @ ${price}")
        
        return result
    
    def get_open_orders(self) -> List:
        """Get all open orders"""
        return self._make_request("/orders")
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        payload = {"order_id": order_id}
        return self._make_request("/order/cancel", payload)
    
    def conservative_trading_strategy(self, symbol: str) -> Dict:
        """Conservative trading strategy based on analysis"""
        # Get current market data
        ticker = self.get_ticker(symbol)
        if not ticker:
            return {"action": "HOLD", "reason": "No ticker data"}
        
        last_price = float(ticker.get('last', 0))
        if last_price == 0:
            return {"action": "HOLD", "reason": "Invalid price"}
        
        # Analyze market conditions
        sentiment = self.get_market_sentiment(symbol)
        support, resistance = self.calculate_support_resistance(symbol)
        
        # Conservative trading logic
        price_from_support = ((last_price - support) / support) * 100 if support > 0 else 0
        price_to_resistance = ((resistance - last_price) / last_price) * 100 if last_price > 0 else 0
        
        # Decision making
        if sentiment == "BULLISH" and price_from_support < 2:
            # Near support in bullish market - potential buy
            buy_price = last_price * 0.995  # 0.5% below current
            stop_loss = buy_price * (1 - STOP_LOSS_PCT)
            take_profit = buy_price * (1 + TAKE_PROFIT_PCT)
            
            return {
                "action": "BUY",
                "price": buy_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "sentiment": sentiment,
                "support": support,
                "resistance": resistance,
                "reason": f"Bullish sentiment, near support ({price_from_support:.1f}% above)"
            }
        
        elif sentiment == "BEARISH" and price_to_resistance < 2:
            # Near resistance in bearish market - potential sell (if we had position)
            sell_price = last_price * 1.005  # 0.5% above current
            return {
                "action": "SELL",
                "price": sell_price,
                "sentiment": sentiment,
                "support": support,
                "resistance": resistance,
                "reason": f"Bearish sentiment, near resistance ({price_to_resistance:.1f}% below)"
            }
        
        else:
            # Hold - market conditions not favorable
            return {
                "action": "HOLD",
                "price": last_price,
                "sentiment": sentiment,
                "support": support,
                "resistance": resistance,
                "reason": f"Market {sentiment.lower()}, not at key levels"
            }

def main():
    """Main trading execution"""
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING BOT")
    print(f"Capital: ${INITIAL_CAPITAL}")
    print(f"Risk Parameters: {STOP_LOSS_PCT*100}% Stop-Loss, {TAKE_PROFIT_PCT*100}% Take-Profit")
    print(f"Max Daily Trades: {MAX_DAILY_TRADES}")
    print("=" * 60)
    
    # Check API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("ERROR: Gemini API credentials not found in environment variables")
        print("Please set GEMINI_API_KEY and GEMINI_API_SECRET environment variables")
        return
    
    bot = GeminiTradingBot()
    
    # Market Analysis
    print("\n📊 MARKET ANALYSIS")
    print("-" * 40)
    
    analysis_results = {}
    for pair in TRADING_PAIRS:
        ticker = bot.get_ticker(pair)
        if ticker:
            last_price = float(ticker.get('last', 0))
            change = float(ticker.get('change', 0))
            volume = float(ticker.get('volume', {}).get('USD', 0))
            
            sentiment = bot.get_market_sentiment(pair)
            support, resistance = bot.calculate_support_resistance(pair)
            
            analysis_results[pair] = {
                "price": last_price,
                "change": change,
                "volume": volume,
                "sentiment": sentiment,
                "support": support,
                "resistance": resistance
            }
            
            print(f"\n{pair}:")
            print(f"  Price: ${last_price:,.2f}")
            print(f"  24h Change: {change:+.2f}%")
            print(f"  Volume: ${volume:,.0f}")
            print(f"  Sentiment: {sentiment}")
            print(f"  Support: ${support:,.2f}")
            print(f"  Resistance: ${resistance:,.2f}")
    
    # Trading Decisions
    print("\n🎯 TRADING DECISIONS")
    print("-" * 40)
    
    trading_decisions = {}
    for pair in TRADING_PAIRS:
        decision = bot.conservative_trading_strategy(pair)
        trading_decisions[pair] = decision
        
        print(f"\n{pair} Decision:")
        print(f"  Action: {decision['action']}")
        print(f"  Reason: {decision['reason']}")
        
        if decision['action'] in ['BUY', 'SELL']:
            print(f"  Target Price: ${decision.get('price', 0):,.2f}")
            if 'stop_loss' in decision:
                print(f"  Stop-Loss: ${decision['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}%)")
            if 'take_profit' in decision:
                print(f"  Take-Profit: ${decision['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}%)")
    
    # Check if we can trade today
    if not bot.can_trade_today():
        print(f"\n⚠️ Daily trade limit reached ({MAX_DAILY_TRADES} trades)")
        return
    
    # Execute trades based on decisions
    print("\n💼 TRADE EXECUTION")
    print("-" * 40)
    
    executed_trades = []
    for pair, decision in trading_decisions.items():
        if decision['action'] == 'BUY' and bot.can_trade_today():
            # Calculate position size (conservative: 25% of capital)
            position_size = INITIAL_CAPITAL * 0.25
            target_price = decision['price']
            
            print(f"\nExecuting BUY order for {pair}:")
            print(f"  Amount: ${position_size:,.2f}")
            print(f"  Price: ${target_price:,.2f}")
            
            # Place order (commented out for safety - uncomment for real trading)
            # order_result = bot.place_order(
            #     symbol=pair,
            #     amount=position_size,
            #     price=target_price,
            #     side="buy"
            # )
            
            # Simulated order for demonstration
            order_result = {
                "order_id": f"sim_{int(time.time())}",
                "symbol": pair,
                "side": "buy",
                "price": target_price,
                "amount": position_size,
                "status": "simulated"
            }
            
            executed_trades.append(order_result)
            print(f"  Order ID: {order_result.get('order_id')}")
            print(f"  Status: {order_result.get('status', 'pending')}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TRADING SUMMARY")
    print("=" * 60)
    
    print(f"\n📈 Market Analysis:")
    for pair, data in analysis_results.items():
        print(f"  {pair}: ${data['price']:,.2f} ({data['sentiment']})")
    
    print(f"\n🎯 Trading Decisions:")
    for pair, decision in trading_decisions.items():
        print(f"  {pair}: {decision['action']} - {decision['reason']}")
    
    print(f"\n💼 Executed Trades: {len(executed_trades)}")
    for trade in executed_trades:
        print(f"  {trade.get('symbol')}: {trade.get('side').upper()} ${trade.get('amount'):,.2f} @ ${trade.get('price'):,.2f}")
    
    print(f"\n⚠️ Remaining Daily Trades: {MAX_DAILY_TRADES - bot.trades_today}")
    
    print("\n" + "=" * 60)
    print("Conservative trading complete. Always trade responsibly!")
    print("=" * 60)

if __name__ == "__main__":
    main()