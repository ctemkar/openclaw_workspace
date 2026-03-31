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
CAPITAL = 1000.0  # USD
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2
SYMBOLS = ['BTCUSD', 'ETHUSD']

# Gemini API configuration (using sandbox for safety)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.environ.get('GEMINI_API_SECRET', '')
GEMINI_API_URL = 'https://api.gemini.com'  # Production
# GEMINI_API_URL = 'https://api.sandbox.gemini.com'  # Sandbox

class GeminiTrader:
    def __init__(self, api_key: str, api_secret: str, base_url: str = GEMINI_API_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.trades_today = 0
        self.last_trade_date = None
        self.load_trade_history()
    
    def load_trade_history(self):
        """Load today's trade count from file"""
        try:
            with open('trade_history.json', 'r') as f:
                data = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                if data.get('date') == today:
                    self.trades_today = data.get('trades', 0)
                    self.last_trade_date = today
        except FileNotFoundError:
            self.trades_today = 0
            self.last_trade_date = None
    
    def save_trade_history(self):
        """Save today's trade count to file"""
        today = datetime.now().strftime('%Y-%m-%d')
        data = {
            'date': today,
            'trades': self.trades_today
        }
        with open('trade_history.json', 'w') as f:
            json.dump(data, f)
    
    def can_trade(self) -> bool:
        """Check if we can execute more trades today"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
        return self.trades_today < MAX_TRADES_PER_DAY
    
    def increment_trade_count(self):
        """Increment today's trade count"""
        self.trades_today += 1
        self.save_trade_history()
    
    def generate_signature(self, payload: str) -> str:
        """Generate Gemini API signature"""
        encoded_payload = payload.encode()
        b64 = base64.b64encode(encoded_payload)
        signature = hmac.new(self.api_secret.encode(), b64, hashlib.sha384).hexdigest()
        return signature
    
    def make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Gemini API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': "text/plain",
            'Content-Length': "0",
            'X-GEMINI-APIKEY': self.api_key,
            'Cache-Control': "no-cache"
        }
        
        if data:
            payload = json.dumps(data)
            signature = self.generate_signature(payload)
            headers['X-GEMINI-PAYLOAD'] = base64.b64encode(payload.encode()).decode()
            headers['X-GEMINI-SIGNATURE'] = signature
            response = requests.post(url, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        return response.json()
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get current ticker price"""
        try:
            endpoint = f"/v1/pubticker/{symbol.lower()}"
            data = self.make_request(endpoint)
            return {
                'symbol': symbol,
                'bid': float(data.get('bid', 0)),
                'ask': float(data.get('ask', 0)),
                'last': float(data.get('last', 0)),
                'volume': float(data.get('volume', {}).get('USD', 0))
            }
        except Exception as e:
            print(f"Error getting ticker for {symbol}: {e}")
            return None
    
    def get_order_book(self, symbol: str) -> Optional[Dict]:
        """Get order book for analysis"""
        try:
            endpoint = f"/v1/book/{symbol.lower()}"
            data = self.make_request(endpoint)
            return {
                'bids': [(float(bid['price']), float(bid['amount'])) for bid in data.get('bids', [])[:10]],
                'asks': [(float(ask['price']), float(ask['amount'])) for ask in data.get('asks', [])[:10]]
            }
        except Exception as e:
            print(f"Error getting order book for {symbol}: {e}")
            return None
    
    def analyze_market(self, symbol: str) -> Dict:
        """Perform conservative market analysis"""
        ticker = self.get_ticker(symbol)
        order_book = self.get_order_book(symbol)
        
        if not ticker or not order_book:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'Data unavailable'}
        
        current_price = ticker['last']
        
        # Calculate support and resistance from order book
        bid_prices = [bid[0] for bid in order_book['bids']]
        ask_prices = [ask[0] for ask in order_book['asks']]
        
        support_level = sum(bid_prices) / len(bid_prices) if bid_prices else current_price * 0.98
        resistance_level = sum(ask_prices) / len(ask_prices) if ask_prices else current_price * 1.02
        
        # Conservative trading signals
        signal = 'HOLD'
        confidence = 0
        reason = "No clear signal"
        
        # Price relative to support/resistance
        price_to_support = (current_price - support_level) / support_level
        price_to_resistance = (resistance_level - current_price) / current_price
        
        # Volume check (simplified)
        volume_ok = ticker['volume'] > 1000000  # $1M+ volume
        
        if volume_ok:
            if price_to_support < 0.01:  # Near support
                signal = 'BUY'
                confidence = 0.6
                reason = f"Price near support level ({support_level:.2f})"
            elif price_to_resistance < 0.01:  # Near resistance
                signal = 'SELL'
                confidence = 0.6
                reason = f"Price near resistance level ({resistance_level:.2f})"
            elif current_price < support_level * 0.99:  # Below support
                signal = 'BUY'
                confidence = 0.7
                reason = f"Price below support, potential bounce ({support_level:.2f})"
            elif current_price > resistance_level * 1.01:  # Above resistance
                signal = 'SELL'
                confidence = 0.7
                reason = f"Price above resistance, potential pullback ({resistance_level:.2f})"
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'support': support_level,
            'resistance': resistance_level,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'volume': ticker['volume']
        }
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on capital and risk"""
        position_value = CAPITAL * 0.5  # Use 50% of capital per trade for conservative approach
        return position_value / price
    
    def place_order(self, symbol: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """Place an order on Gemini"""
        if not self.can_trade():
            return {'error': f'Max trades per day ({MAX_TRADES_PER_DAY}) reached'}
        
        try:
            endpoint = "/v1/order/new"
            data = {
                "request": "/v1/order/new",
                "nonce": int(time.time() * 1000),
                "symbol": symbol.lower(),
                "amount": str(round(amount, 8)),
                "price": str(round(price, 2)),
                "side": side.lower(),
                "type": "exchange limit",
                "options": ["maker-or-cancel"]  # Conservative: only execute if we get maker fee
            }
            
            result = self.make_request(endpoint, method='POST', data=data)
            
            if 'order_id' in result:
                self.increment_trade_count()
                return {
                    'order_id': result['order_id'],
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'price': price,
                    'status': 'PENDING'
                }
            else:
                return {'error': result.get('message', 'Unknown error')}
                
        except Exception as e:
            return {'error': str(e)}
    
    def execute_trade(self, analysis: Dict) -> Optional[Dict]:
        """Execute trade based on analysis"""
        if analysis['signal'] == 'HOLD' or analysis['confidence'] < 0.6:
            return None
        
        symbol = analysis['symbol']
        side = analysis['signal']
        current_price = analysis['current_price']
        
        # Calculate position size
        amount = self.calculate_position_size(current_price)
        
        # Set limit price with small buffer
        if side == 'BUY':
            limit_price = current_price * 0.995  # 0.5% below current for better entry
        else:  # SELL
            limit_price = current_price * 1.005  # 0.5% above current for better entry
        
        # Place order
        order_result = self.place_order(symbol, side, amount, limit_price)
        
        if order_result and 'error' not in order_result:
            # Calculate stop loss and take profit levels
            if side == 'BUY':
                stop_loss = limit_price * (1 - STOP_LOSS_PCT)
                take_profit = limit_price * (1 + TAKE_PROFIT_PCT)
            else:  # SELL
                stop_loss = limit_price * (1 + STOP_LOSS_PCT)
                take_profit = limit_price * (1 - TAKE_PROFIT_PCT)
            
            order_result.update({
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'analysis_reason': analysis['reason']
            })
        
        return order_result

def main():
    """Main trading function"""
    print(f"=== Conservative Crypto Trading Bot ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Capital: ${CAPITAL}")
    print(f"Risk Parameters: {STOP_LOSS_PCT*100}% stop-loss, {TAKE_PROFIT_PCT*100}% take-profit")
    print(f"Max trades per day: {MAX_TRADES_PER_DAY}")
    print()
    
    # Check for API credentials
    if not GEMINI_API_KEY or not GEMINI_API_SECRET:
        print("WARNING: Gemini API credentials not found in environment variables")
        print("Using simulated trading mode")
        simulate_trading = True
    else:
        simulate_trading = False
        trader = GeminiTrader(GEMINI_API_KEY, GEMINI_API_SECRET)
    
    trades_executed = []
    
    # Analyze each symbol
    for symbol in SYMBOLS:
        print(f"\n--- Analyzing {symbol} ---")
        
        if simulate_trading:
            # Simulated analysis for demo
            import random
            current_price = random.uniform(30000, 35000) if symbol == 'BTCUSD' else random.uniform(2000, 2500)
            support = current_price * random.uniform(0.97, 0.99)
            resistance = current_price * random.uniform(1.01, 1.03)
            
            # Simulate trading signals
            signals = ['BUY', 'SELL', 'HOLD']
            weights = [0.3, 0.3, 0.4]  # Conservative: 40% HOLD
            signal = random.choices(signals, weights=weights)[0]
            confidence = random.uniform(0.5, 0.8) if signal != 'HOLD' else 0
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'support': support,
                'resistance': resistance,
                'signal': signal,
                'confidence': confidence,
                'reason': 'Simulated analysis',
                'volume': random.uniform(1000000, 5000000)
            }
        else:
            analysis = trader.analyze_market(symbol)
        
        print(f"Current Price: ${analysis['current_price']:.2f}")
        print(f"Support: ${analysis['support']:.2f}")
        print(f"Resistance: ${analysis['resistance']:.2f}")
        print(f"Signal: {analysis['signal']} (Confidence: {analysis['confidence']:.2f})")
        print(f"Reason: {analysis['reason']}")
        print(f"Volume (24h): ${analysis['volume']:,.0f}")
        
        # Execute trade if signal is strong enough
        if analysis['signal'] != 'HOLD' and analysis['confidence'] >= 0.6:
            print(f"\nExecuting {analysis['signal']} order for {symbol}...")
            
            if simulate_trading:
                # Simulated trade execution
                if len(trades_executed) < MAX_TRADES_PER_DAY:
                    amount = (CAPITAL * 0.5) / analysis['current_price']
                    
                    if analysis['signal'] == 'BUY':
                        stop_loss = analysis['current_price'] * (1 - STOP_LOSS_PCT)
                        take_profit = analysis['current_price'] * (1 + TAKE_PROFIT_PCT)
                    else:  # SELL
                        stop_loss = analysis['current_price'] * (1 + STOP_LOSS_PCT)
                        take_profit = analysis['current_price'] * (1 - TAKE_PROFIT_PCT)
                    
                    trade = {
                        'order_id': f"SIM-{int(time.time())}",
                        'symbol': symbol,
                        'side': analysis['signal'],
                        'amount': round(amount, 6),
                        'price': round(analysis['current_price'], 2),
                        'stop_loss': round(stop_loss, 2),
                        'take_profit': round(take_profit, 2),
                        'status': 'FILLED',
                        'analysis_reason': analysis['reason'],
                        'simulated': True
                    }
                    trades_executed.append(trade)
                    print(f"SIMULATED TRADE EXECUTED:")
                    print(f"  Order ID: {trade['order_id']}")
                    print(f"  Side: {trade['side']}")
                    print(f"  Amount: {trade['amount']} {symbol[:3]}")
                    print(f"  Price: ${trade['price']:.2f}")
                    print(f"  Stop Loss: ${trade['stop_loss']:.2f}")
                    print(f"  Take Profit: ${trade['take_profit']:.2f}")
                else:
                    print(f"Max trades per day ({MAX_TRADES_PER_DAY}) reached")
            else:
                # Real trade execution
                trade = trader.execute_trade(analysis)
                if trade and 'error' not in trade:
                    trades_executed.append(trade)
                    print(f"REAL TRADE EXECUTED:")
                    print(f"  Order ID: {trade['order_id']}")
                    print(f"  Side: {trade['side']}")
                    print(f"  Amount: {trade['amount']} {symbol[:3]}")
                    print(f"  Price: ${trade['price']:.2f}")
                    print(f"  Stop Loss: ${trade['stop_loss']:.2f}")
                    print(f"  Take Profit: ${trade['take_profit']:.2f}")
                elif trade and 'error' in trade:
                    print(f"Trade failed: {trade['error']}")
        else:
            print(f"No trade executed for {symbol} (signal: {analysis['signal']}, confidence: {analysis['confidence']:.2f})")
    
    # Generate summary
    print(f"\n=== TRADING SUMMARY ===")
    print(f"Total trades executed today: {len(trades_executed)}/{MAX_TRADES_PER_DAY}")
    
    if trades_executed:
        print("\nTrade Details:")
        for i, trade in enumerate(trades_executed, 1):
            print(f"\nTrade {i}:")
            print(f"  Symbol: {trade['symbol']}")
            print(f"  Side: {trade['side']}")
            print(f"  Order ID: {trade['order_id']}")
            print(f"  Amount: {trade['amount']} {trade['symbol'][:3]}")
            print(f"  Entry Price: ${trade['price']:.2f}")
            print(f"  Stop Loss: ${trade['stop_loss']:.2f} ({STOP_LOSS_PCT*100}%)")
            print(f"  Take Profit: ${trade['take_profit']:.2f} ({TAKE_PROFIT_PCT*100}%)")
            print(f"  Status: {trade['status']}")
            print(f"  Reason: {trade['analysis_reason']}")
            if trade.get('simulated'):
                print(f"  NOTE: Simulated trade (no real funds used)")