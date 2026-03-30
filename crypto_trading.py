#!/usr/bin/env python3
"""
Conservative Crypto Trading Script for Gemini API
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
MAX_DAILY_TRADES = 2
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.environ.get('GEMINI_API_SECRET', '')
GEMINI_API_URL = "https://api.gemini.com"

# Trading pairs to analyze
TRADING_PAIRS = ["btcusd", "ethusd"]

class GeminiTrader:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.trades_today = 0
        self.last_trade_date = None
        self.load_trade_history()
    
    def load_trade_history(self):
        """Load today's trade count from file"""
        try:
            with open('trade_history.json', 'r') as f:
                data = json.load(f)
                today = datetime.now().date().isoformat()
                if data.get('date') == today:
                    self.trades_today = data.get('trades_today', 0)
                    self.last_trade_date = today
        except FileNotFoundError:
            self.trades_today = 0
            self.last_trade_date = None
    
    def save_trade_history(self):
        """Save today's trade count to file"""
        data = {
            'date': datetime.now().date().isoformat(),
            'trades_today': self.trades_today
        }
        with open('trade_history.json', 'w') as f:
            json.dump(data, f)
    
    def reset_daily_trades_if_needed(self):
        """Reset trade count if it's a new day"""
        today = datetime.now().date().isoformat()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
            self.save_trade_history()
    
    def can_trade_today(self) -> bool:
        """Check if we can execute more trades today"""
        self.reset_daily_trades_if_needed()
        return self.trades_today < MAX_DAILY_TRADES
    
    def increment_trade_count(self):
        """Increment today's trade count"""
        self.trades_today += 1
        self.save_trade_history()
    
    def generate_signature(self, payload: str) -> str:
        """Generate Gemini API signature"""
        signature = hmac.new(
            self.api_secret.encode(),
            payload.encode(),
            hashlib.sha384
        ).hexdigest()
        return signature
    
    def make_request(self, endpoint: str, payload: Dict = None) -> Dict:
        """Make authenticated request to Gemini API"""
        if payload is None:
            payload = {}
        
        payload['request'] = endpoint
        payload['nonce'] = str(int(time.time() * 1000))
        
        encoded_payload = json.dumps(payload).encode()
        b64_payload = base64.b64encode(encoded_payload)
        signature = self.generate_signature(b64_payload)
        
        headers = {
            'Content-Type': 'text/plain',
            'Content-Length': '0',
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64_payload,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': 'no-cache'
        }
        
        url = f"{GEMINI_API_URL}{endpoint}"
        response = self.session.post(url, headers=headers)
        return response.json()
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price"""
        endpoint = f"/v1/pubticker/{symbol}"
        response = requests.get(f"{GEMINI_API_URL}{endpoint}")
        return response.json()
    
    def get_order_book(self, symbol: str) -> Dict:
        """Get current order book"""
        endpoint = f"/v1/book/{symbol}"
        response = requests.get(f"{GEMINI_API_URL}{endpoint}")
        return response.json()
    
    def get_market_sentiment(self, symbol: str) -> str:
        """Analyze market sentiment based on order book"""
        try:
            order_book = self.get_order_book(symbol)
            
            # Calculate bid/ask volume ratio
            bids = order_book.get('bids', [])
            asks = order_book.get('asks', [])
            
            bid_volume = sum(float(bid['amount']) for bid in bids[:10])
            ask_volume = sum(float(ask['amount']) for ask in asks[:10])
            
            if bid_volume > ask_volume * 1.2:
                return "bullish"
            elif ask_volume > bid_volume * 1.2:
                return "bearish"
            else:
                return "neutral"
        except:
            return "neutral"
    
    def calculate_support_resistance(self, symbol: str) -> Tuple[float, float]:
        """Calculate approximate support and resistance levels"""
        try:
            order_book = self.get_order_book(symbol)
            bids = order_book.get('bids', [])
            asks = order_book.get('asks', [])
            
            # Support: average of top 5 bids
            top_bids = bids[:5]
            support = sum(float(bid['price']) for bid in top_bids) / len(top_bids)
            
            # Resistance: average of top 5 asks
            top_asks = asks[:5]
            resistance = sum(float(ask['price']) for ask in top_asks) / len(top_asks)
            
            return support, resistance
        except:
            ticker = self.get_ticker(symbol)
            price = float(ticker['last'])
            return price * 0.98, price * 1.02
    
    def analyze_pair(self, symbol: str) -> Dict:
        """Perform comprehensive analysis of a trading pair"""
        ticker = self.get_ticker(symbol)
        current_price = float(ticker['last'])
        sentiment = self.get_market_sentiment(symbol)
        support, resistance = self.calculate_support_resistance(symbol)
        
        # Calculate price position between support and resistance
        price_position = (current_price - support) / (resistance - support) if resistance > support else 0.5
        
        # Determine trading signal
        signal = "HOLD"
        if sentiment == "bullish" and price_position < 0.3:
            signal = "BUY"
        elif sentiment == "bearish" and price_position > 0.7:
            signal = "SELL"
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'sentiment': sentiment,
            'support': support,
            'resistance': resistance,
            'price_position': price_position,
            'signal': signal,
            '24h_change': float(ticker.get('percentChange24h', 0))
        }
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Place an order on Gemini"""
        if not self.can_trade_today():
            return {'error': f'Daily trade limit reached ({MAX_DAILY_TRADES} trades)'}
        
        endpoint = "/v1/order/new"
        
        # Calculate order amount based on capital and risk
        ticker = self.get_ticker(symbol)
        current_price = float(ticker['last'])
        
        if price is None:
            price = current_price
        
        # Conservative position sizing: 25% of capital per trade
        position_size = CAPITAL * 0.25
        order_amount = position_size / price
        
        payload = {
            "symbol": symbol,
            "amount": str(round(order_amount, 6)),
            "price": str(round(price, 2)),
            "side": side,
            "type": "exchange limit",
            "options": ["maker-or-cancel"]
        }
        
        response = self.make_request(endpoint, payload)
        
        if 'order_id' in response:
            self.increment_trade_count()
            
            # Calculate stop loss and take profit levels
            if side == "buy":
                stop_loss = price * (1 - STOP_LOSS_PCT)
                take_profit = price * (1 + TAKE_PROFIT_PCT)
            else:
                stop_loss = price * (1 + STOP_LOSS_PCT)
                take_profit = price * (1 - TAKE_PROFIT_PCT)
            
            # Save order details
            order_details = {
                'order_id': response['order_id'],
                'symbol': symbol,
                'side': side,
                'price': price,
                'amount': order_amount,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': datetime.now().isoformat()
            }
            
            self.save_order_details(order_details)
        
        return response
    
    def save_order_details(self, order_details: Dict):
        """Save order details to file"""
        try:
            with open('orders.json', 'r') as f:
                orders = json.load(f)
        except FileNotFoundError:
            orders = []
        
        orders.append(order_details)
        
        with open('orders.json', 'w') as f:
            json.dump(orders, f, indent=2)
    
    def get_account_balance(self) -> Dict:
        """Get account balances"""
        endpoint = "/v1/balances"
        return self.make_request(endpoint)

def main():
    """Main trading function"""
    print("=" * 60)
    print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Capital: ${CAPITAL}")
    print(f"Risk Parameters: {STOP_LOSS_PCT*100}% stop-loss, {TAKE_PROFIT_PCT*100}% take-profit")
    print(f"Max Daily Trades: {MAX_DAILY_TRADES}")
    print("=" * 60)
    
    # Check for API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("ERROR: Gemini API credentials not found in environment variables")
        print("Please set GEMINI_API_KEY and GEMINI_API_SECRET environment variables")
        return
    
    # Initialize trader
    trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
    
    # Analyze each trading pair
    analyses = []
    for pair in TRADING_PAIRS:
        print(f"\nAnalyzing {pair.upper()}...")
        analysis = trader.analyze_pair(pair)
        analyses.append(analysis)
        
        print(f"  Current Price: ${analysis['current_price']:,.2f}")
        print(f"  24h Change: {analysis['24h_change']:+.2f}%")
        print(f"  Market Sentiment: {analysis['sentiment'].upper()}")
        print(f"  Support: ${analysis['support']:,.2f}")
        print(f"  Resistance: ${analysis['resistance']:,.2f}")
        print(f"  Price Position: {analysis['price_position']:.1%}")
        print(f"  Trading Signal: {analysis['signal']}")
    
    # Check if we can trade today
    if not trader.can_trade_today():
        print(f"\n⚠️  Daily trade limit reached ({MAX_DAILY_TRADES} trades)")
        print("No trades will be executed today.")
        return
    
    # Execute trades based on analysis
    trades_executed = []
    for analysis in analyses:
        if analysis['signal'] != "HOLD" and trader.can_trade_today():
            print(f"\nExecuting {analysis['signal']} order for {analysis['symbol'].upper()}...")
            
            side = "buy" if analysis['signal'] == "BUY" else "sell"
            
            # Place order
            result = trader.place_order(
                analysis['symbol'],
                side,
                CAPITAL * 0.25  # 25% of capital
            )
            
            if 'order_id' in result:
                trades_executed.append({
                    'symbol': analysis['symbol'],
                    'side': side,
                    'order_id': result['order_id'],
                    'price': analysis['current_price']
                })
                print(f"  ✅ Order placed successfully!")
                print(f"  Order ID: {result['order_id']}")
                print(f"  Price: ${analysis['current_price']:,.2f}")
            elif 'error' in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                print(f"  ❌ Order failed: {result}")
    
    # Get account balance
    print("\n" + "=" * 60)
    print("ACCOUNT SUMMARY")
    print("=" * 60)
    
    try:
        balances = trader.get_account_balance()
        print("\nCurrent Balances:")
        for balance in balances:
            if float(balance['amount']) > 0:
                print(f"  {balance['currency']}: {balance['amount']} (available: {balance['available']})")
    except Exception as e:
        print(f"  Could not fetch balances: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TRADING SUMMARY")
    print("=" * 60)
    
    if trades_executed:
        print(f"\nTrades Executed Today: {len(trades_executed)}")
        for trade in trades_executed:
            print(f"  • {trade['side'].upper()} {trade['symbol'].upper()} at ${trade['price']:,.2f}")
            print(f"    Order ID: {trade['order_id']}")
    else:
        print("\nNo trades executed.")
        print("Reasons:")
        print("  - Market conditions not favorable")
        print("  - Daily trade limit reached")
        print("  - No clear trading signals")
    
    print(f"\nRemaining Daily Trades: {MAX_DAILY_TRADES - trader.trades_today}")
    print(f"Total Trades Today: {trader.trades_today}")
    
    # Save analysis results
    results = {
        'timestamp': datetime.now().isoformat(),
        'analyses': analyses,
        'trades_executed': trades_executed,
        'trades_today': trader.trades_today
    }
    
    with open('trading_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nAnalysis complete. Results saved to trading_results.json")

if __name__ == "__main__":
    main()