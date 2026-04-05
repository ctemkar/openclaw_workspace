#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot - Version 2
Uses public APIs for market data with simulated trading
$1,000 capital with strict risk management
"""

import os
import json
import time
import requests
import datetime
from typing import Dict, List, Optional, Tuple
import math

# Configuration
CAPITAL = 1000.0  # $1,000 capital
STOP_LOSS = 0.05  # 5% stop-loss
TAKE_PROFIT = 0.10  # 10% take-profit
MAX_TRADES_PER_DAY = 2
SYMBOLS = ['BTC-USD', 'ETH-USD']

class ConservativeCryptoTrader:
    def __init__(self):
        self.trades_today = 0
        self.today_date = datetime.date.today().isoformat()
        self.load_trade_history()
        
    def load_trade_history(self):
        """Load today's trade history from file"""
        try:
            with open('trade_history.json', 'r') as f:
                history = json.load(f)
                today = datetime.date.today().isoformat()
                if history.get('date') == today:
                    self.trades_today = history.get('trades_today', 0)
        except FileNotFoundError:
            self.trades_today = 0
            
    def save_trade_history(self):
        """Save today's trade history to file"""
        history = {
            'date': datetime.date.today().isoformat(),
            'trades_today': self.trades_today,
            'last_updated': datetime.datetime.now().isoformat()
        }
        with open('trade_history.json', 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_market_data_from_coingecko(self) -> Dict:
        """Get market data from CoinGecko API"""
        try:
            # Using CoinGecko public API
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Get additional data for highs/lows (using 24h range approximation)
                btc_price = data.get('bitcoin', {}).get('usd', 67000)
                btc_change = data.get('bitcoin', {}).get('usd_24h_change', 0)
                btc_volume = data.get('bitcoin', {}).get('usd_24h_vol', 30000000000)
                
                eth_price = data.get('ethereum', {}).get('usd', 2000)
                eth_change = data.get('ethereum', {}).get('usd_24h_change', 0)
                eth_volume = data.get('ethereum', {}).get('usd_24h_vol', 10000000000)
                
                # Calculate approximate highs/lows based on price and change
                btc_high = btc_price * (1 + abs(btc_change/100) * 0.5)
                btc_low = btc_price * (1 - abs(btc_change/100) * 0.5)
                
                eth_high = eth_price * (1 + abs(eth_change/100) * 0.5)
                eth_low = eth_price * (1 - abs(eth_change/100) * 0.5)
                
                return {
                    'BTC-USD': {
                        'last': btc_price,
                        'percentChange24h': btc_change,
                        'volume': {'USD': btc_volume},
                        'high': btc_high,
                        'low': btc_low
                    },
                    'ETH-USD': {
                        'last': eth_price,
                        'percentChange24h': eth_change,
                        'volume': {'USD': eth_volume},
                        'high': eth_high,
                        'low': eth_low
                    }
                }
        except Exception as e:
            print(f"Error fetching from CoinGecko: {e}")
            
        # Fallback to simulated data if API fails
        return self.get_simulated_market_data()
    
    def get_simulated_market_data(self) -> Dict:
        """Generate realistic simulated market data"""
        import random
        
        # Base prices (approximate current market)
        btc_base = 67000 + random.uniform(-500, 500)
        eth_base = 2000 + random.uniform(-50, 50)
        
        # Simulate some market movement
        btc_change = random.uniform(-3, 3)
        eth_change = random.uniform(-4, 4)
        
        btc_price = btc_base * (1 + btc_change/100)
        eth_price = eth_base * (1 + eth_change/100)
        
        # Calculate highs/lows
        btc_high = btc_price * (1 + abs(btc_change/100) * 0.6)
        btc_low = btc_price * (1 - abs(btc_change/100) * 0.6)
        
        eth_high = eth_price * (1 + abs(eth_change/100) * 0.6)
        eth_low = eth_price * (1 - abs(eth_change/100) * 0.6)
        
        return {
            'BTC-USD': {
                'last': round(btc_price, 2),
                'percentChange24h': round(btc_change, 2),
                'volume': {'USD': random.uniform(25000000000, 40000000000)},
                'high': round(btc_high, 2),
                'low': round(btc_low, 2)
            },
            'ETH-USD': {
                'last': round(eth_price, 2),
                'percentChange24h': round(eth_change, 2),
                'volume': {'USD': random.uniform(8000000000, 15000000000)},
                'high': round(eth_high, 2),
                'low': round(eth_low, 2)
            }
        }
    
    def analyze_market_sentiment(self, market_data: Dict) -> Dict:
        """Analyze market sentiment based on price action"""
        sentiment = {
            'btc_trend': 'neutral',
            'eth_trend': 'neutral',
            'overall_sentiment': 'neutral',
            'recommendation': 'hold',
            'confidence': 'low'
        }
        
        btc_data = market_data.get('BTC-USD', {})
        eth_data = market_data.get('ETH-USD', {})
        
        if btc_data and eth_data:
            btc_change = btc_data.get('percentChange24h', 0)
            eth_change = eth_data.get('percentChange24h', 0)
            
            # Trend analysis
            if btc_change > 2.0:
                sentiment['btc_trend'] = 'bullish'
                sentiment['confidence'] = 'medium'
            elif btc_change < -2.0:
                sentiment['btc_trend'] = 'bearish'
                sentiment['confidence'] = 'medium'
                
            if eth_change > 2.0:
                sentiment['eth_trend'] = 'bullish'
                sentiment['confidence'] = 'medium'
            elif eth_change < -2.0:
                sentiment['eth_trend'] = 'bearish'
                sentiment['confidence'] = 'medium'
            
            # Volume analysis (simplified)
            btc_volume = btc_data.get('volume', {}).get('USD', 0)
            eth_volume = eth_data.get('volume', {}).get('USD', 0)
            
            if btc_volume > 35000000000 or eth_volume > 12000000000:
                sentiment['confidence'] = 'high'
            
            # Overall sentiment
            bullish_count = sum([1 for trend in [sentiment['btc_trend'], sentiment['eth_trend']] if trend == 'bullish'])
            bearish_count = sum([1 for trend in [sentiment['btc_trend'], sentiment['eth_trend']] if trend == 'bearish'])
            
            if bullish_count >= 2 and sentiment['confidence'] in ['medium', 'high']:
                sentiment['overall_sentiment'] = 'bullish'
                sentiment['recommendation'] = 'consider_buy'
            elif bearish_count >= 2 and sentiment['confidence'] in ['medium', 'high']:
                sentiment['overall_sentiment'] = 'bearish'
                sentiment['recommendation'] = 'consider_sell'
        
        return sentiment
    
    def calculate_support_resistance(self, symbol: str, market_data: Dict) -> Dict:
        """Calculate support and resistance levels"""
        data = market_data.get(symbol, {})
        if not data:
            return {'support': 0, 'resistance': 0, 'current_position': 'middle'}
        
        high = data.get('high', 0)
        low = data.get('low', 0)
        current = data.get('last', 0)
        
        if high <= low:
            # If data is invalid, use simple percentage bands
            high = current * 1.05
            low = current * 0.95
        
        # Fibonacci-based support/resistance levels (conservative)
        range_size = high - low
        support = low + (range_size * 0.382)  # 38.2% Fibonacci level
        resistance = high - (range_size * 0.382)  # 61.8% from bottom
        
        # Adjust for current price
        position = 'middle'
        if current < support * 1.01:  # Within 1% of support
            position = 'near_support'
        elif current > resistance * 0.99:  # Within 1% of resistance
            position = 'near_resistance'
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current_position': position,
            'distance_to_support': round(((current - support) / current) * 100, 2) if current > 0 else 0,
            'distance_to_resistance': round(((resistance - current) / current) * 100, 2) if current > 0 else 0
        }
    
    def should_trade(self, symbol: str, sentiment: Dict, levels: Dict, market_data: Dict) -> Tuple[bool, str, float]:
        """Determine if we should trade based on conservative strategy"""
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return False, "max_trades_reached", 0.0
        
        data = market_data.get(symbol, {})
        current_price = data.get('last', 0)
        daily_change = data.get('percentChange24h', 0)
        
        if current_price <= 0:
            return False, "invalid_price", 0.0
        
        # Conservative position sizing
        position_size = CAPITAL * 0.1  # 10% of capital per trade = $100
        crypto_amount = position_size / current_price
        
        # Very conservative trading rules
        trade_conditions = []
        
        # Condition 1: Strong trend with confirmation
        if sentiment['overall_sentiment'] == 'bullish' and sentiment['confidence'] == 'high':
            trade_conditions.append(('bullish_trend', 3))
        
        # Condition 2: Price near key level with volume
        if levels['current_position'] == 'near_support' and abs(daily_change) < 1.5:
            trade_conditions.append(('near_support', 2))
        
        if levels['current_position'] == 'near_resistance' and abs(daily_change) < 1.5:
            trade_conditions.append(('near_resistance', 2))
        
        # Condition 3: Low volatility opportunity
        if abs(daily_change) < 1.0 and levels['distance_to_support'] < 5:
            trade_conditions.append(('low_volatility', 1))
        
        # Score the conditions
        total_score = sum(score for _, score in trade_conditions)
        
        if total_score >= 3:  # Need strong confirmation
            if sentiment['overall_sentiment'] == 'bullish':
                return True, "buy", position_size
            elif sentiment['overall_sentiment'] == 'bearish':
                return True, "sell", position_size
        
        return False, f"insufficient_conditions (score: {total_score})", 0.0
    
    def execute_trade(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Execute a simulated trade with risk management"""
        if self.trades_today >= MAX_TRADES_PER_DAY:
            return {'error': 'Maximum trades per day reached', 'status': 'rejected'}
        
        trade_id = f"{symbol.replace('-', '')}_{side}_{int(time.time())}"
        trade_value = amount
        
        # Calculate stop-loss and take-profit prices
        if side == "buy":
            stop_price = price * (1 - STOP_LOSS)
            take_profit_price = price * (1 + TAKE_PROFIT)
            position = "long"
        else:  # sell/short
            stop_price = price * (1 + STOP_LOSS)
            take_profit_price = price * (1 - TAKE_PROFIT)
            position = "short"
        
        crypto_amount = amount / price
        
        trade = {
            'trade_id': trade_id,
            'symbol': symbol,
            'side': side,
            'position': position,
            'crypto_amount': round(crypto_amount, 6),
            'usd_amount': round(amount, 2),
            'entry_price': round(price, 2),
            'current_value': round(amount, 2),
            'stop_loss': round(stop_price, 2),
            'take_profit': round(take_profit_price, 2),
            'risk_reward_ratio': round(TAKE_PROFIT / STOP_LOSS, 2),
            'max_loss': round(amount * STOP_LOSS, 2),
            'potential_gain': round(amount * TAKE_PROFIT, 2),
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'executed',
            'risk_level': 'conservative'
        }
        
        self.trades_today += 1
        self.save_trade_history()
        
        # Save trade to history file
        self.save_trade_to_history(trade)
        
        return trade
    
    def save_trade_to_history(self, trade: Dict):
        """Save individual trade to history file"""
        try:
            # Load existing trades
            try:
                with open('trades_executed.json', 'r') as f:
                    all_trades = json.load(f)
            except FileNotFoundError:
                all_trades = []
            
            # Add new trade
            all_trades.append(trade)
            
            # Keep only last 100 trades
            if len(all_trades) > 100:
                all_trades = all_trades[-100:]
            
            # Save back
            with open('trades_executed.json', 'w') as f:
                json.dump(all_trades, f, indent=2)
                
        except Exception as e:
            print(f"Error saving trade history: {e}")
    
    def run_analysis(self) -> Dict:
        """Run complete trading analysis"""
        print(f"\n{'='*60}")
        print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
        print(f"{'='*60}")
        print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Date: {self.today_date}")
        print(f"Capital: ${CAPITAL:,.2f}")
        print(f"Risk Parameters: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
        print(f"Max Trades/Day: {MAX_TRADES_PER_DAY}")
        print(f"Trades executed today: {self.trades_today}/{MAX_TRADES_PER_DAY}")
        print(f"{'='*60}")
        
        # Get market data
        print("\n📊 FETCHING MARKET DATA...")
        market_data = self.get_market_data_from_coingecko()
        
        analysis_results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'date': self.today_date,
            'capital': CAPITAL,
            'trades_today': self.trades_today,
            'max_trades_per_day': MAX_TRADES_PER_DAY,
            'risk_parameters': {
                'stop_loss_pct': STOP_LOSS * 100,
                'take_profit_pct': TAKE_PROFIT * 100,
                'max_trades_per_day': MAX_TRADES_PER_DAY
            },
            'market_data': {},
            'technical_analysis': {},
            'sentiment_analysis': {},
            'trades_executed': []
        }
        
        # Display market data
        print("\n📈 CURRENT MARKET PRICES:")
        for symbol in SYMBOLS:
            data = market_data.get(symbol, {})
            if data:
                price = data.get('last', 0)
                change = data.get('percentChange24h', 0)
                volume = data.get('volume', {}).get('USD', 0)
                
                analysis_results['market_data'][symbol] = {
                    'price': price,
                    '24h_change': change,
                    '24h_volume': volume,
                    'high': data.get('high', 0),
                    'low': data.get('low', 0)
                }
                
                change_icon = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                print(f"  {symbol}:")
                print(f"    Price: ${price:,.2f}")
                print(f"    24h