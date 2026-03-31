#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Capital: $1,000
"""

import os
import json
import time
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_SECRET = os.environ.get("GEMINI_API_SECRET", "")
GEMINI_SANDBOX = False  # Using real trading

if GEMINI_SANDBOX:
    BASE_URL = "https://api.sandbox.gemini.com"
else:
    BASE_URL = "https://api.gemini.com"

# Trading Parameters
CAPITAL = 1000.0  # $1,000
MAX_TRADES_PER_DAY = 2
STOP_LOSS_PERCENT = 5.0  # 5%
TAKE_PROFIT_PERCENT = 10.0  # 10%
MAX_POSITION_SIZE = CAPITAL * 0.5  # Max 50% per trade

# Track daily trades
DAILY_TRADES_FILE = "daily_trades.json"

class GeminiTrader:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
    def _generate_payload(self, payload: Dict) -> str:
        """Generate payload for Gemini API"""
        payload_nonce = str(int(time.time() * 1000))
        payload["nonce"] = payload_nonce
        payload["request"] = "/v1/" + payload.get("request", "")
        return json.dumps(payload)
    
    def _sign_payload(self, payload: str) -> str:
        """Sign payload with API secret"""
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
        
        payload["request"] = endpoint
        payload_str = self._generate_payload(payload)
        signature = self._sign_payload(payload_str)
        
        headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "X-GEMINI-APIKEY": self.api_key,
            "X-GEMINI-PAYLOAD": base64.b64encode(payload_str.encode()).decode(),
            "X-GEMINI-SIGNATURE": signature,
            "Cache-Control": "no-cache"
        }
        
        url = f"{BASE_URL}/v1/{endpoint}"
        
        try:
            if method == "POST":
                response = self.session.post(url, headers=headers)
            else:
                response = self.session.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return {"error": str(e)}
    
    def get_ticker(self, symbol: str = "btcusd") -> Dict:
        """Get current market price"""
        try:
            response = requests.get(f"{BASE_URL}/v1/pubticker/{symbol}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ticker Error: {e}")
            return {"last": "0", "bid": "0", "ask": "0", "volume": {}}
    
    def get_order_book(self, symbol: str = "btcusd") -> Dict:
        """Get order book for market analysis"""
        try:
            response = requests.get(f"{BASE_URL}/v1/book/{symbol}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Order Book Error: {e}")
            return {"bids": [], "asks": []}
    
    def get_account_balance(self) -> Dict:
        """Get account balances"""
        return self._make_request("balances")
    
    def place_order(self, symbol: str, amount: float, price: float, 
                   side: str, order_type: str = "exchange limit") -> Dict:
        """Place a new order"""
        payload = {
            "symbol": symbol,
            "amount": str(amount),
            "price": str(price),
            "side": side,
            "type": order_type,
            "options": ["maker-or-cancel"]  # Avoid taker fees
        }
        return self._make_request("order/new", payload)
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an existing order"""
        payload = {"order_id": order_id}
        return self._make_request("order/cancel", payload)
    
    def get_active_orders(self) -> List[Dict]:
        """Get all active orders"""
        result = self._make_request("orders")
        return result if isinstance(result, list) else []

class TradingAnalyzer:
    def __init__(self):
        self.trader = None
        
    def analyze_market(self, symbol: str = "btcusd") -> Dict:
        """Analyze market conditions for trading decision"""
        ticker = self.trader.get_ticker(symbol)
        order_book = self.trader.get_order_book(symbol)
        
        if "error" in ticker or "error" in order_book:
            return {"error": "Failed to fetch market data"}
        
        try:
            last_price = float(ticker.get("last", "0"))
            bid = float(ticker.get("bid", "0"))
            ask = float(ticker.get("ask", "0"))
            
            # Calculate spread
            spread = ((ask - bid) / bid) * 100 if bid > 0 else 0
            
            # Analyze order book depth
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            
            # Calculate support/resistance levels
            support_levels = self._calculate_support_resistance(bids, asks)
            
            # Market sentiment based on order book imbalance
            total_bid_volume = sum(float(bid[1]) for bid in bids[:10])
            total_ask_volume = sum(float(ask[1]) for ask in asks[:10])
            order_book_imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume) * 100
            
            # Volume analysis
            volume_data = ticker.get("volume", {})
            volume_24h = float(volume_data.get(symbol.upper(), "0")) if isinstance(volume_data, dict) else 0
            
            return {
                "symbol": symbol,
                "last_price": last_price,
                "bid": bid,
                "ask": ask,
                "spread_percent": spread,
                "support_levels": support_levels[:3],  # Top 3 support levels
                "resistance_levels": support_levels[-3:],  # Top 3 resistance levels
                "order_book_imbalance_percent": order_book_imbalance,
                "volume_24h": volume_24h,
                "market_sentiment": "BULLISH" if order_book_imbalance > 5 else "BEARISH" if order_book_imbalance < -5 else "NEUTRAL",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": f"Analysis error: {e}"}
    
    def _calculate_support_resistance(self, bids: List, asks: List) -> List[float]:
        """Calculate support and resistance levels from order book"""
        levels = []
        
        # Use bid prices as potential support
        for bid in bids[:20]:  # Top 20 bids
            try:
                levels.append(float(bid[0]))
            except:
                pass
        
        # Use ask prices as potential resistance  
        for ask in asks[:20]:  # Top 20 asks
            try:
                levels.append(float(ask[0]))
            except:
                pass
        
        # Sort and deduplicate
        levels = sorted(set(levels))
        return levels
    
    def calculate_position_size(self, price: float, risk_percent: float = 2.0) -> float:
        """Calculate position size based on risk parameters"""
        risk_amount = CAPITAL * (risk_percent / 100)
        position_value = min(risk_amount * 10, MAX_POSITION_SIZE)  # 10:1 risk:reward ratio
        position_size = position_value / price if price > 0 else 0
        return round(position_size, 6)
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side == "buy":
            return entry_price * (1 - STOP_LOSS_PERCENT / 100)
        else:  # sell/short
            return entry_price * (1 + STOP_LOSS_PERCENT / 100)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate take profit price"""
        if side == "buy":
            return entry_price * (1 + TAKE_PROFIT_PERCENT / 100)
        else:  # sell/short
            return entry_price * (1 - TAKE_PROFIT_PERCENT / 100)

class TradeExecutor:
    def __init__(self):
        self.analyzer = TradingAnalyzer()
        self.daily_trades = self._load_daily_trades()
        
    def _load_daily_trades(self) -> Dict:
        """Load today's trade count"""
        try:
            if os.path.exists(DAILY_TRADES_FILE):
                with open(DAILY_TRADES_FILE, "r") as f:
                    data = json.load(f)
                    # Check if data is from today
                    today = datetime.now().strftime("%Y-%m-%d")
                    if data.get("date") == today:
                        return data
        except:
            pass
        
        # Return fresh data for today
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "trade_count": 0,
            "trades": []
        }
    
    def _save_daily_trades(self):
        """Save daily trades to file"""
        try:
            with open(DAILY_TRADES_FILE, "w") as f:
                json.dump(self.daily_trades, f, indent=2)
        except Exception as e:
            print(f"Error saving daily trades: {e}")
    
    def can_trade_today(self) -> bool:
        """Check if we can execute more trades today"""
        return self.daily_trades["trade_count"] < MAX_TRADES_PER_DAY
    
    def record_trade(self, trade_details: Dict):
        """Record a trade execution"""
        self.daily_trades["trade_count"] += 1
        self.daily_trades["trades"].append({
            **trade_details,
            "timestamp": datetime.now().isoformat()
        })
        self._save_daily_trades()
    
    def execute_trade(self, symbol: str, analysis: Dict) -> Dict:
        """Execute a trade based on analysis"""
        if not self.can_trade_today():
            return {"error": f"Daily trade limit reached ({MAX_TRADES_PER_DAY} trades)"}
        
        last_price = analysis.get("last_price", 0)
        if last_price <= 0:
            return {"error": "Invalid price data"}
        
        # Conservative trading logic
        sentiment = analysis.get("market_sentiment", "NEUTRAL")
        order_book_imbalance = analysis.get("order_book_imbalance_percent", 0)
        
        # Only trade with strong signals
        if abs(order_book_imbalance) < 8:  # Require strong imbalance
            return {"error": "Market conditions too neutral for conservative trading"}
        
        # Determine trade direction
        if sentiment == "BULLISH" and order_book_imbalance > 8:
            side = "buy"
            entry_price = analysis.get("ask", last_price)
        elif sentiment == "BEARISH" and order_book_imbalance < -8:
            side = "sell"
            entry_price = analysis.get("bid", last_price)
        else:
            return {"error": "No clear trading signal"}
        
        # Calculate position size
        position_size = self.analyzer.calculate_position_size(entry_price)
        if position_size <= 0:
            return {"error": "Position size too small"}
        
        # Calculate stop loss and take profit
        stop_loss = self.analyzer.calculate_stop_loss(entry_price, side)
        take_profit = self.analyzer.calculate_take_profit(entry_price, side)
        
        # Prepare trade details
        trade_details = {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "position_size": position_size,
            "position_value": position_size * entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_percent": STOP_LOSS_PERCENT,
            "reward_percent": TAKE_PROFIT_PERCENT,
            "risk_reward_ratio": TAKE_PROFIT_PERCENT / STOP_LOSS_PERCENT,
            "market_sentiment": sentiment,
            "order_book_imbalance": order_book_imbalance
        }
        
        # Check if we have API credentials
        if not GEMINI_API_KEY or not GEMINI_API_SECRET:
            print("WARNING: No Gemini API credentials found. Running in simulation mode.")
            print(f"Simulated trade: {trade_details}")
            self.record_trade(trade_details)
            return {"simulation": True, **trade_details}
        
        # Execute real trade
        try:
            self.analyzer.trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
            
            # Place order
            order_result = self.analyzer.trader.place_order(
                symbol=symbol,
                amount=position_size,
                price=entry_price,
                side=side
            )
            
            if "error" in order_result:
                return {"error": f"Order failed: {order_result.get('error', 'Unknown error')}"}
            
            trade_details["order_id"] = order_result.get("order_id")
            trade_details["order_status"] = order_result.get("status", "unknown")
            
            self.record_trade(trade_details)
            return {"success": True, **trade_details}
            
        except Exception as e:
            return {"error": f"Trade execution failed: {e}"}

def main():
    """Main trading execution"""
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING BOT")
    print(f"Capital: ${CAPITAL:,}")
    print(f"Risk Parameters: {STOP_LOSS_PERCENT}% Stop-Loss, {TAKE_PROFIT_PERCENT}% Take-Profit")
    print(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    executor = TradeExecutor()
    analyzer = TradingAnalyzer()
    
    # Check API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("\n⚠️  WARNING: Gemini API credentials not found in environment variables")
        print("Set GEMINI_API_KEY and GEMINI_API_SECRET environment variables")
        print("Running in SIMULATION MODE only")
    
    # Analyze BTC/USD
    print("\n📊 ANALYZING BTC/USD MARKET...")
    btc_analysis = analyzer.analyze_market("btcusd")
    
    if "error" in btc_analysis:
        print(f"BTC Analysis Error: {btc_analysis['error']}")
    else:
        print(f"BTC Price: ${btc_analysis['last_price']:,.2f}")
        print(f"Market Sentiment: {btc_analysis['market_sentiment']}")
        print(f"Order Book Imbalance: {btc_analysis['order_book_imbalance_percent']:.2f}%")
        print(f"24h Volume: {btc_analysis['volume_24h']:,.2f} BTC")
        print(f"Spread: {btc_analysis['spread_percent']:.4f}%")
        
        # Check for trading opportunity
        if executor.can_trade_today():
            print(f"\n✅ Can trade today ({executor.daily_trades['trade_count']}/{MAX_TRADES_PER_DAY} trades used)")
            btc_trade = executor.execute_trade("btcusd", btc_analysis)
            
            if "error" in btc_trade:
                print(f"BTC Trade Decision: {btc_trade['error']}")
            elif "simulation" in btc_trade:
                print(f"\n📈 SIMULATED BTC TRADE:")
                print(f"  Side: {btc_trade['side'].upper()}")
                print(f"  Entry: ${btc_trade['entry_price']:,.2f}")
                print(f"  Size: {btc_trade['position_size']:.6f} BTC")
                print(f"  Value: ${btc_trade['position_value']:,.2f}")
                print(f"  Stop Loss: ${btc_trade['stop_loss']:,.2f}")
                print(f"  Take Profit: ${btc_trade['take_profit']:,.2f}")
                print(f"  Risk/Reward: 1:{btc_trade['risk_reward_ratio']:.1f}")
            else:
                print(f"\n✅ REAL BTC TRADE EXECUTED:")
                print(f"  Order ID: {btc_trade.get('order_id', 'N/A')}")
                print(f"  Side: {btc_trade['side'].upper()}")
                print(f"  Entry: ${btc_trade['entry_price']