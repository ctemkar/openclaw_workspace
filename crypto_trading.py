#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot for Gemini API
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Capital: $1,000
Pairs: BTC/USD and ETH/USD
"""

import os
import time
import json
import requests
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Configuration
CAPITAL = 1000.0
MAX_TRADES_PER_DAY = 2
STOP_LOSS_PERCENT = 5.0
TAKE_PROFIT_PERCENT = 10.0

# Gemini API configuration (using sandbox for safety)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.environ.get('GEMINI_API_SECRET', '')
GEMINI_SANDBOX = True  # Use sandbox for testing
BASE_URL = "https://api.sandbox.gemini.com" if GEMINI_SANDBOX else "https://api.gemini.com"

# Trading pairs to monitor
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
                    self.trades_today = data.get('trades', 0)
                    self.last_trade_date = today
        except FileNotFoundError:
            self.trades_today = 0
            self.last_trade_date = None
    
    def save_trade_history(self):
        """Save today's trade count to file"""
        today = datetime.now().date().isoformat()
        data = {
            'date': today,
            'trades': self.trades_today
        }
        with open('trade_history.json', 'w') as f:
            json.dump(data, f)
    
    def reset_daily_trades(self):
        """Reset trade count if it's a new day"""
        today = datetime.now().date().isoformat()
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
        
        payload['request'] = endpoint
        payload['nonce'] = str(int(time.time() * 1000))
        
        encoded_payload = json.dumps(payload).encode()
        b64_payload = base64.b64encode(encoded_payload)
        signature = self.generate_signature(b64_payload)
        
        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': b64_payload,
            'X-GEMINI-SIGNATURE': signature,
            'Cache-Control': "no-cache"
        }
        
        url = f"{BASE_URL}{endpoint}"
        
        if method == "POST":
            response = self.session.post(url, headers=headers)
        else:
            response = self.session.get(url, headers=headers)
        
        return response.json()
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker price"""
        endpoint = f"/v1/pubticker/{symbol}"
        url = f"{BASE_URL}{endpoint}"
        response = self.session.get(url)
        return response.json()
    
    def get_order_book(self, symbol: str) -> Dict:
        """Get current order book"""
        endpoint = f"/v1/book/{symbol}"
        url = f"{BASE_URL}{endpoint}"
        response = self.session.get(url)
        return response.json()
    
    def analyze_market(self, symbol: str) -> Dict:
        """Analyze market conditions for a symbol"""
        ticker = self.get_ticker(symbol)
        order_book = self.get_order_book(symbol)
        
        # Calculate basic metrics
        last_price = float(ticker['last'])
        bid = float(ticker['bid'])
        ask = float(ticker['ask'])
        volume = float(ticker['volume']['USD'])
        
        # Simple support/resistance from order book
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        support_level = float(bids[0]['price']) if bids else last_price * 0.99
        resistance_level = float(asks[0]['price']) if asks else last_price * 1.01
        
        # Calculate spread percentage
        spread_percent = ((ask - bid) / bid) * 100
        
        # Determine trend (simple)
        change_24h = float(ticker.get('percentChange24h', 0))
        
        return {
            'symbol': symbol,
            'price': last_price,
            'bid': bid,
            'ask': ask,
            'volume_usd': volume,
            'support': support_level,
            'resistance': resistance_level,
            'spread_percent': spread_percent,
            'change_24h': change_24h,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on capital and risk"""
        # Use 50% of capital per trade for conservative approach
        trade_capital = CAPITAL * 0.5
        position_size = trade_capital / price
        return round(position_size, 6)  # Round to 6 decimal places
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Place an order on Gemini"""
        if not self.can_trade():
            return {'error': 'Daily trade limit reached'}
        
        endpoint = "/v1/order/new"
        payload = {
            'symbol': symbol,
            'amount': str(amount),
            'side': side,
            'type': 'exchange limit'
        }
        
        if price:
            payload['price'] = str(price)
        
        result = self.make_request(endpoint, payload)
        
        if 'order_id' in result:
            self.trades_today += 1
            self.save_trade_history()
            
            # Calculate stop loss and take profit levels
            if side == 'buy':
                stop_price = price * (1 - STOP_LOSS_PERCENT / 100)
                take_profit_price = price * (1 + TAKE_PROFIT_PERCENT / 100)
            else:  # sell
                stop_price = price * (1 + STOP_LOSS_PERCENT / 100)
                take_profit_price = price * (1 - TAKE_PROFIT_PERCENT / 100)
            
            # Store order details with risk management
            order_details = {
                'order_id': result['order_id'],
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'stop_loss': round(stop_price, 2),
                'take_profit': round(take_profit_price, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save order details
            self.save_order_details(order_details)
            
            result['risk_management'] = {
                'stop_loss': stop_price,
                'take_profit': take_profit_price
            }
        
        return result
    
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
    
    def conservative_trading_strategy(self, market_data: Dict) -> Optional[Tuple[str, float]]:
        """
        Conservative trading strategy based on:
        1. Price near support/resistance
        2. Low spread
        3. Moderate volume
        4. Recent price movement
        """
        symbol = market_data['symbol']
        price = market_data['price']
        support = market_data['support']
        resistance = market_data['resistance']
        spread = market_data['spread_percent']
        volume = market_data['volume_usd']
        change_24h = market_data['change_24h']
        
        # Conservative conditions
        buy_conditions = [
            price <= support * 1.01,  # Price near support (within 1%)
            spread < 0.5,  # Low spread
            volume > 1000000,  # Good volume (> $1M)
            change_24h < -2,  # Recent dip (oversold)
        ]
        
        sell_conditions = [
            price >= resistance * 0.99,  # Price near resistance (within 1%)
            spread < 0.5,  # Low spread
            volume > 1000000,  # Good volume
            change_24h > 2,  # Recent gain (overbought)
        ]
        
        if all(buy_conditions):
            position_size = self.calculate_position_size(price)
            return ('buy', position_size)
        elif all(sell_conditions):
            position_size = self.calculate_position_size(price)
            return ('sell', position_size)
        
        return None

def main():
    print("=== Conservative Crypto Trading Bot ===")
    print(f"Capital: ${CAPITAL}")
    print(f"Risk Parameters: {STOP_LOSS_PERCENT}% stop-loss, {TAKE_PROFIT_PERCENT}% take-profit")
    print(f"Max trades per day: {MAX_TRADES_PER_DAY}")
    print(f"Trading pairs: {', '.join(TRADING_PAIRS)}")
    print(f"Current time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Check for API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("WARNING: Gemini API credentials not found in environment variables")
        print("Using simulated trading mode")
        simulate_trading = True
    else:
        simulate_trading = False
    
    # Initialize trader
    trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
    
    # Analyze markets
    print("\n=== Market Analysis ===")
    market_analysis = {}
    
    for symbol in TRADING_PAIRS:
        print(f"\nAnalyzing {symbol.upper()}...")
        try:
            analysis = trader.analyze_market(symbol)
            market_analysis[symbol] = analysis
            
            print(f"  Price: ${analysis['price']:,.2f}")
            print(f"  24h Change: {analysis['change_24h']:.2f}%")
            print(f"  Support: ${analysis['support']:,.2f}")
            print(f"  Resistance: ${analysis['resistance']:,.2f}")
            print(f"  Spread: {analysis['spread_percent']:.3f}%")
            print(f"  Volume (24h): ${analysis['volume_usd']:,.0f}")
            
        except Exception as e:
            print(f"  Error analyzing {symbol}: {e}")
            market_analysis[symbol] = None
    
    # Execute trades based on conservative strategy
    print("\n=== Trading Decisions ===")
    trades_executed = []
    
    for symbol, analysis in market_analysis.items():
        if analysis is None:
            continue
        
        if not trader.can_trade():
            print(f"Daily trade limit reached. Skipping {symbol}")
            continue
        
        decision = trader.conservative_trading_strategy(analysis)
        
        if decision:
            side, amount = decision
            price = analysis['price']
            
            print(f"\n{'-' * 40}")
            print(f"TRADE SIGNAL for {symbol.upper()}:")
            print(f"  Action: {side.upper()}")
            print(f"  Price: ${price:,.2f}")
            print(f"  Amount: {amount:.6f}")
            print(f"  Value: ${amount * price:,.2f}")
            
            if simulate_trading:
                print("  [SIMULATED] Trade would be executed")
                trade_result = {
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'simulated': True,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print("  Executing trade...")
                try:
                    trade_result = trader.place_order(symbol, side, amount, price)
                    if 'order_id' in trade_result:
                        print(f"  ✓ Order placed: {trade_result['order_id']}")
                        trade_result['symbol'] = symbol
                        trade_result['side'] = side
                        trade_result['amount'] = amount
                        trade_result['price'] = price
                        trade_result['simulated'] = False
                    else:
                        print(f"  ✗ Order failed: {trade_result}")
                        continue
                except Exception as e:
                    print(f"  ✗ Error executing trade: {e}")
                    continue
            
            trades_executed.append(trade_result)
            print(f"  Remaining trades today: {MAX_TRADES_PER_DAY - trader.trades_today}")
            print(f"{'-' * 40}")
    
    # Summary
    print("\n" + "=" * 50)
    print("=== TRADING SUMMARY ===")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Trades executed today: {trader.trades_today}/{MAX_TRADES_PER_DAY}")
    
    if trades_executed:
        print("\nExecuted trades:")
        for i, trade in enumerate(trades_executed, 1):
            print(f"{i}. {trade['symbol'].upper()} {trade['side'].upper()} "
                  f"{trade['amount']:.6f} @ ${trade['price']:,.2f} "
                  f"(Value: ${trade['amount'] * trade['price']:,.2f})")
            if trade.get('simulated'):
                print("   [SIMULATED TRADE]")
    else:
        print("\nNo trades executed - market conditions didn't meet conservative criteria")
    
    # Save summary to file
    summary = {
        'timestamp': datetime.now().isoformat(),
        'trades_executed': len(trades_executed),
        'trades_today': trader.trades_today,
        'max_trades_per_day': MAX_TRADES_PER_DAY,
        'capital': CAPITAL,
        'stop_loss_percent': STOP_LOSS_PERCENT,
        'take_profit_percent': TAKE_PROFIT_PERCENT,
        'trades': trades_executed,
        'market_analysis': market_analysis
    }
    
    with open('trading_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSummary saved to trading_summary.json")
    print("=" * 50)
    
    return summary

if __name__ == "__main__":
    main()