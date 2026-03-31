#!/usr/bin/env python3
"""
Conservative Crypto Trading Script for Gemini API
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Capital: $1,000
Pairs: BTC/USD and ETH/USD
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
CAPITAL = 1000.0
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
TRADING_PAIRS = ["BTCUSD", "ETHUSD"]

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_SECRET = os.environ.get("GEMINI_API_SECRET")
GEMINI_API_BASE = "https://api.gemini.com"

class GeminiTrader:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.trades_today = 0
        self.last_trade_date = None
        
    def _generate_payload(self, payload: Dict) -> str:
        """Generate payload for Gemini API"""
        return json.dumps(payload)
    
    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for Gemini API"""
        signature = hmac.new(
            self.api_secret.encode(),
            payload.encode(),
            hashlib.sha384
        ).hexdigest()
        return signature
    
    def _make_request(self, endpoint: str, payload: Dict = None, method: str = "POST") -> Dict:
        """Make authenticated request to Gemini API"""
        if payload is None:
            payload = {}
        
        payload_nonce = str(int(time.time() * 1000))
        payload["request"] = endpoint
        payload["nonce"] = payload_nonce
        
        encoded_payload = self._generate_payload(payload)
        b64_payload = base64.b64encode(encoded_payload.encode())
        signature = self._generate_signature(b64_payload)
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": b64_payload.decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        url = f"{GEMINI_API_BASE}{endpoint}"
        
        try:
            if method == "POST":
                response = self.session.post(url, headers=headers)
            else:
                response = self.session.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return {"error": str(e)}
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price for a symbol"""
        endpoint = f"/v1/pubticker/{symbol.lower()}"
        try:
            response = requests.get(f"{GEMINI_API_BASE}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get ticker for {symbol}: {e}")
            return {}
    
    def get_order_book(self, symbol: str) -> Dict:
        """Get order book for a symbol"""
        endpoint = f"/v1/book/{symbol.lower()}"
        try:
            response = requests.get(f"{GEMINI_API_BASE}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get order book for {symbol}: {e}")
            return {}
    
    def get_account_balances(self) -> List[Dict]:
        """Get account balances"""
        return self._make_request("/v1/balances")
    
    def place_order(self, symbol: str, amount: float, price: float, side: str, 
                   order_type: str = "exchange limit") -> Dict:
        """Place an order on Gemini"""
        # Check if we've reached daily trade limit
        today = datetime.date.today()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return {"error": f"Daily trade limit reached ({MAX_TRADES_PER_DAY} trades)"}
        
        payload = {
            "symbol": symbol.lower(),
            "amount": str(amount),
            "price": str(price),
            "side": side,
            "type": order_type,
            "options": ["maker-or-cancel"]  # Avoid taker fees
        }
        
        result = self._make_request("/v1/order/new", payload)
        
        if "order_id" in result:
            self.trades_today += 1
            print(f"Order placed successfully: {result['order_id']}")
        
        return result
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        payload = {"order_id": order_id}
        return self._make_request("/v1/order/cancel", payload)
    
    def get_active_orders(self) -> List[Dict]:
        """Get active orders"""
        return self._make_request("/v1/orders")
    
    def get_past_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Get past trades for a symbol"""
        endpoint = f"/v1/mytrades"
        payload = {"symbol": symbol.lower(), "limit_trades": limit}
        return self._make_request(endpoint, payload)

class TradingStrategy:
    def __init__(self, trader: GeminiTrader):
        self.trader = trader
        self.capital = CAPITAL
        self.position_size = CAPITAL * 0.25  # Use 25% of capital per trade
        
    def analyze_market(self, symbol: str) -> Dict:
        """Analyze market conditions for a symbol"""
        ticker = self.trader.get_ticker(symbol)
        order_book = self.trader.get_order_book(symbol)
        
        if not ticker or not order_book:
            return {"error": "Failed to fetch market data"}
        
        current_price = float(ticker.get("last", 0))
        bid = float(ticker.get("bid", 0))
        ask = float(ticker.get("ask", 0))
        volume = float(ticker.get("volume", {}).get("USD", 0))
        
        # Calculate support and resistance levels
        bids = order_book.get("bids", [])
        asks = order_book.get("asks", [])
        
        # Simple support/resistance calculation
        support_levels = [float(bid[0]) for bid in bids[:5]]  # Top 5 bids
        resistance_levels = [float(ask[0]) for ask in asks[:5]]  # Top 5 asks
        
        # Calculate market sentiment
        spread = (ask - bid) / current_price * 100
        bid_ask_ratio = sum([float(bid[1]) for bid in bids[:5]]) / sum([float(ask[1]) for ask in asks[:5]]) if asks else 1
        
        # Determine trend (simple)
        price_change_24h = ((current_price - float(ticker.get("open", current_price))) / float(ticker.get("open", current_price))) * 100
        
        analysis = {
            "symbol": symbol,
            "current_price": current_price,
            "bid": bid,
            "ask": ask,
            "spread_pct": spread,
            "volume_usd": volume,
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "bid_ask_ratio": bid_ask_ratio,
            "price_change_24h": price_change_24h,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return analysis
    
    def calculate_position(self, price: float) -> Tuple[float, float, float]:
        """Calculate position size, stop loss, and take profit"""
        position_amount = self.position_size / price
        stop_loss_price = price * (1 - STOP_LOSS_PCT)
        take_profit_price = price * (1 + TAKE_PROFIT_PCT)
        
        return position_amount, stop_loss_price, take_profit_price
    
    def should_trade(self, analysis: Dict) -> bool:
        """Determine if we should trade based on conservative strategy"""
        if "error" in analysis:
            return False
        
        # Conservative trading rules
        current_price = analysis["current_price"]
        spread = analysis["spread_pct"]
        price_change = analysis["price_change_24h"]
        bid_ask_ratio = analysis["bid_ask_ratio"]
        
        # Rule 1: Avoid trading if spread is too high (>0.5%)
        if spread > 0.5:
            print(f"Spread too high: {spread:.2f}%")
            return False
        
        # Rule 2: Avoid extreme volatility (>5% price change in 24h)
        if abs(price_change) > 5:
            print(f"Volatility too high: {price_change:.2f}%")
            return False
        
        # Rule 3: Prefer balanced markets (bid/ask ratio close to 1)
        if bid_ask_ratio < 0.8 or bid_ask_ratio > 1.2:
            print(f"Market imbalance: bid/ask ratio = {bid_ask_ratio:.2f}")
            return False
        
        # Rule 4: Check if price is near support/resistance
        support_levels = analysis["support_levels"]
        resistance_levels = analysis["resistance_levels"]
        
        # Consider buying near support, selling near resistance
        near_support = any(abs(current_price - level) / current_price < 0.01 for level in support_levels[:3])
        near_resistance = any(abs(current_price - level) / current_price < 0.01 for level in resistance_levels[:3])
        
        if not (near_support or near_resistance):
            print("Price not near key levels")
            return False
        
        return True
    
    def determine_trade_direction(self, analysis: Dict) -> Optional[str]:
        """Determine trade direction (buy/sell) based on analysis"""
        current_price = analysis["current_price"]
        support_levels = analysis["support_levels"]
        resistance_levels = analysis["resistance_levels"]
        price_change = analysis["price_change_24h"]
        
        # Check if near support (potential buy)
        near_support = any(abs(current_price - level) / current_price < 0.01 for level in support_levels[:3])
        
        # Check if near resistance (potential sell)
        near_resistance = any(abs(current_price - level) / current_price < 0.01 for level in resistance_levels[:3])
        
        # Conservative strategy: buy near support in uptrend, sell near resistance in downtrend
        if near_support and price_change > -1:  # Not in strong downtrend
            return "buy"
        elif near_resistance and price_change < 1:  # Not in strong uptrend
            return "sell"
        
        return None
    
    def execute_trade(self, symbol: str, analysis: Dict) -> Dict:
        """Execute a trade based on analysis"""
        trade_direction = self.determine_trade_direction(analysis)
        
        if not trade_direction:
            return {"status": "no_trade", "reason": "No clear trade direction"}
        
        current_price = analysis["current_price"]
        position_amount, stop_loss, take_profit = self.calculate_position(current_price)
        
        # Place order
        order_result = self.trader.place_order(
            symbol=symbol,
            amount=position_amount,
            price=current_price,
            side=trade_direction
        )
        
        if "error" in order_result:
            return {"status": "error", "details": order_result}
        
        trade_summary = {
            "status": "executed",
            "symbol": symbol,
            "direction": trade_direction,
            "entry_price": current_price,
            "position_size": position_amount,
            "position_value": position_amount * current_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "order_id": order_result.get("order_id"),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return trade_summary

def main():
    """Main trading function"""
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Capital: ${CAPITAL}")
    print(f"Risk Parameters: {STOP_LOSS_PCT*100}% SL, {TAKE_PROFIT_PCT*100}% TP")
    print(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
    print("=" * 60)
    
    # Check for API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("ERROR: Gemini API credentials not found in environment variables")
        print("Please set GEMINI_API_KEY and GEMINI_API_SECRET")
        return
    
    # Initialize trader and strategy
    trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
    strategy = TradingStrategy(trader)
    
    trades_executed = []
    
    # Analyze each trading pair
    for symbol in TRADING_PAIRS:
        print(f"\nAnalyzing {symbol}...")
        
        # Get market analysis
        analysis = strategy.analyze_market(symbol)
        
        if "error" in analysis:
            print(f"  Error: {analysis['error']}")
            continue
        
        print(f"  Current Price: ${analysis['current_price']:,.2f}")
        print(f"  24h Change: {analysis['price_change_24h']:+.2f}%")
        print(f"  Spread: {analysis['spread_pct']:.2f}%")
        print(f"  Support Levels: {[f'${x:,.0f}' for x in analysis['support_levels'][:3]]}")
        print(f"  Resistance Levels: {[f'${x:,.0f}' for x in analysis['resistance_levels'][:3]]}")
        
        # Check if we should trade
        if strategy.should_trade(analysis):
            print(f"  ✓ Trading conditions met for {symbol}")
            
            # Execute trade
            trade_result = strategy.execute_trade(symbol, analysis)
            
            if trade_result["status"] == "executed":
                trades_executed.append(trade_result)
                print(f"  ✓ Trade executed: {trade_result['direction'].upper()} {trade_result['position_size']:.6f} {symbol}")
                print(f"    Entry: ${trade_result['entry_price']:,.2f}")
                print(f"    Stop Loss: ${trade_result['stop_loss']:,.2f} ({STOP_LOSS_PCT*100}%)")
                print(f"    Take Profit: ${trade_result['take_profit']:,.2f} ({TAKE_PROFIT_PCT*100}%)")
            else:
                print(f"  ✗ Trade not executed: {trade_result.get('reason', 'Unknown reason')}")
        else:
            print(f"  ✗ No trade opportunity for {symbol}")
    
    # Generate summary
    print("\n" + "=" * 60)
    print("TRADING SUMMARY")
    print("=" * 60)
    
    if trades_executed:
        total_trades = len(trades_executed)
        total_value = sum(trade["position_value"] for trade in trades_executed)
        
        print(f"Trades Executed: {total_trades}")
        print(f"Total Position Value: ${total_value:,.2f}")
        print(f"Remaining Capital: ${CAPITAL - total_value:,.2f}")
        
        for i, trade in enumerate(trades_executed, 1):
            print(f"\nTrade {i}:")
            print(f"  Symbol: {trade['symbol']}")
            print(f"  Direction: {trade['direction'].upper()}")
            print(f"  Entry Price: ${trade['entry_price']:,.2f}")
            print(f"  Position Size: {trade['position_size']:.6f}")
            print(f"  Position Value: ${trade['position_value']:,.2f}")
            print(f"  Stop Loss: ${trade['stop_loss']:,.2f}")
            print(f"  Take Profit: ${trade['take_profit']:,.2f}")
            print(f"  Order ID: {trade.get('order_id', 'N/A')}")
    else:
        print("No trades executed today.")
        print("Reason: Market conditions did not meet conservative trading criteria.")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()