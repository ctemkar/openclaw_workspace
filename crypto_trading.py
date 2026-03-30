#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Uses Gemini API with $1,000 capital
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Analyzes BTC/USD and ETH/USD
"""

import os
import time
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional, Tuple

# Configuration
CAPITAL = 1000.0  # USD
MAX_DAILY_TRADES = 2
STOP_LOSS_PCT = 0.05  # 5%
TAKE_PROFIT_PCT = 0.10  # 10%
SYMBOLS = ['BTCUSD', 'ETHUSD']

# Gemini API configuration (would need actual API keys in production)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.getenv('GEMINI_API_SECRET', '')

class ConservativeCryptoTrader:
    def __init__(self):
        self.capital = CAPITAL
        self.positions = {}
        self.daily_trades = 0
        self.trade_history = []
        
    def get_market_data(self, symbol: str) -> Dict:
        """Get current market data for a symbol"""
        try:
            # For demo purposes, using CoinGecko API (free)
            if symbol == 'BTCUSD':
                url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true'
                response = requests.get(url, timeout=10)
                data = response.json()
                return {
                    'price': data['bitcoin']['usd'],
                    'change_24h': data['bitcoin']['usd_24h_change'],
                    'volume': data['bitcoin']['usd_24h_vol'],
                    'market_cap': data['bitcoin']['usd_market_cap']
                }
            elif symbol == 'ETHUSD':
                url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true'
                response = requests.get(url, timeout=10)
                data = response.json()
                return {
                    'price': data['ethereum']['usd'],
                    'change_24h': data['ethereum']['usd_24h_change'],
                    'volume': data['ethereum']['usd_24h_vol'],
                    'market_cap': data['ethereum']['usd_market_cap']
                }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def analyze_market_sentiment(self, symbol: str) -> Dict:
        """Analyze market sentiment and technical indicators"""
        market_data = self.get_market_data(symbol)
        if not market_data:
            return {'sentiment': 'neutral', 'signal': 'hold'}
        
        price = market_data['price']
        change_24h = market_data['change_24h']
        volume = market_data['volume']
        
        # Simple sentiment analysis
        sentiment = 'neutral'
        if change_24h > 3:
            sentiment = 'bullish'
        elif change_24h < -3:
            sentiment = 'bearish'
        
        # Volume analysis
        volume_signal = 'normal'
        if volume > 10000000000:  # 10B+ volume
            volume_signal = 'high'
        
        # Determine trading signal (conservative approach)
        signal = 'hold'
        if sentiment == 'bullish' and volume_signal == 'high':
            signal = 'buy'
        elif sentiment == 'bearish' and volume_signal == 'high':
            signal = 'sell'
        
        return {
            'symbol': symbol,
            'price': price,
            'change_24h': change_24h,
            'volume': volume,
            'sentiment': sentiment,
            'volume_signal': volume_signal,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on capital and risk parameters"""
        # Conservative: Use 20% of capital per trade
        position_value = self.capital * 0.2
        quantity = position_value / price
        return round(quantity, 6)
    
    def execute_trade(self, symbol: str, signal: str, price: float) -> Optional[Dict]:
        """Execute a trade (simulated for demo)"""
        if self.daily_trades >= MAX_DAILY_TRADES:
            print(f"Max daily trades ({MAX_DAILY_TRADES}) reached")
            return None
        
        quantity = self.calculate_position_size(price)
        if quantity * price > self.capital * 0.25:  # Safety check
            quantity = (self.capital * 0.2) / price
        
        trade_value = quantity * price
        
        # Simulate trade execution
        trade_id = f"{symbol}_{int(time.time())}"
        trade = {
            'trade_id': trade_id,
            'symbol': symbol,
            'action': signal,
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'stop_loss': price * (1 - STOP_LOSS_PCT) if signal == 'buy' else price * (1 + STOP_LOSS_PCT),
            'take_profit': price * (1 + TAKE_PROFIT_PCT) if signal == 'buy' else price * (1 - TAKE_PROFIT_PCT),
            'timestamp': datetime.now().isoformat(),
            'status': 'executed'
        }
        
        self.trade_history.append(trade)
        self.daily_trades += 1
        
        # Update capital (simulated)
        if signal == 'buy':
            self.capital -= trade_value
            self.positions[symbol] = trade
        elif signal == 'sell':
            self.capital += trade_value
            if symbol in self.positions:
                del self.positions[symbol]
        
        return trade
    
    def check_open_positions(self):
        """Check stop-loss and take-profit levels for open positions"""
        for symbol, position in list(self.positions.items()):
            current_data = self.get_market_data(symbol)
            if not current_data:
                continue
            
            current_price = current_data['price']
            
            # Check stop-loss
            if position['action'] == 'buy':
                if current_price <= position['stop_loss']:
                    print(f"Stop-loss triggered for {symbol} at ${current_price}")
                    # Execute sell to close position
                    self.execute_trade(symbol, 'sell', current_price)
                elif current_price >= position['take_profit']:
                    print(f"Take-profit triggered for {symbol} at ${current_price}")
                    self.execute_trade(symbol, 'sell', current_price)
    
    def run_analysis(self):
        """Run complete trading analysis"""
        print(f"\n{'='*60}")
        print(f"CONSERVATIVE CRYPTO TRADING ANALYSIS")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ${self.capital:.2f}")
        print(f"Daily Trades: {self.daily_trades}/{MAX_DAILY_TRADES}")
        print(f"{'='*60}\n")
        
        analysis_results = []
        
        for symbol in SYMBOLS:
            print(f"\nAnalyzing {symbol}...")
            analysis = self.analyze_market_sentiment(symbol)
            analysis_results.append(analysis)
            
            print(f"  Current Price: ${analysis['price']:,.2f}")
            print(f"  24h Change: {analysis['change_24h']:.2f}%")
            print(f"  Volume: ${analysis['volume']:,.0f}")
            print(f"  Sentiment: {analysis['sentiment']}")
            print(f"  Volume Signal: {analysis['volume_signal']}")
            print(f"  Trading Signal: {analysis['signal']}")
            
            # Execute trade if signal is strong and we have capacity
            if analysis['signal'] in ['buy', 'sell'] and self.daily_trades < MAX_DAILY_TRADES:
                print(f"\n  Executing {analysis['signal']} order for {symbol}...")
                trade = self.execute_trade(symbol, analysis['signal'], analysis['price'])
                if trade:
                    print(f"  Trade Executed:")
                    print(f"    Quantity: {trade['quantity']}")
                    print(f"    Value: ${trade['value']:.2f}")
                    print(f"    Stop-Loss: ${trade['stop_loss']:.2f}")
                    print(f"    Take-Profit: ${trade['take_profit']:.2f}")
        
        # Check existing positions
        if self.positions:
            print(f"\nChecking open positions...")
            self.check_open_positions()
        
        return analysis_results
    
    def generate_summary(self) -> str:
        """Generate plain text summary of trading activity"""
        summary = []
        summary.append("=" * 60)
        summary.append("CRYPTO TRADING SUMMARY")
        summary.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        summary.append(f"Capital: ${self.capital:.2f}")
        summary.append(f"Daily Trades Used: {self.daily_trades}/{MAX_DAILY_TRADES}")
        summary.append("=" * 60)
        
        if self.trade_history:
            summary.append("\nRECENT TRADES:")
            for trade in self.trade_history[-5:]:  # Last 5 trades
                summary.append(f"- {trade['timestamp'][:19]} | {trade['symbol']} | "
                             f"{trade['action'].upper()} | Qty: {trade['quantity']} | "
                             f"Price: ${trade['price']:.2f} | Value: ${trade['value']:.2f}")
        else:
            summary.append("\nNo trades executed in this session.")
        
        summary.append("\nOPEN POSITIONS:")
        if self.positions:
            for symbol, position in self.positions.items():
                summary.append(f"- {symbol}: {position['quantity']} @ ${position['price']:.2f} | "
                             f"SL: ${position['stop_loss']:.2f} | TP: ${position['take_profit']:.2f}")
        else:
            summary.append("- None")
        
        summary.append("\nMARKET OVERVIEW:")
        for symbol in SYMBOLS:
            data = self.get_market_data(symbol)
            if data:
                summary.append(f"- {symbol}: ${data['price']:,.2f} | "
                             f"24h: {data['change_24h']:+.2f}% | "
                             f"Vol: ${data['volume']/1e9:.1f}B")
        
        summary.append("\nRISK PARAMETERS:")
        summary.append(f"- Max Daily Trades: {MAX_DAILY_TRADES}")
        summary.append(f"- Stop-Loss: {STOP_LOSS_PCT*100}%")
        summary.append(f"- Take-Profit: {TAKE_PROFIT_PCT*100}%")
        summary.append(f"- Position Size: 20% of capital")
        
        summary.append("\n" + "=" * 60)
        return "\n".join(summary)

def main():
    """Main trading function"""
    trader = ConservativeCryptoTrader()
    
    print("Starting conservative crypto trading analysis...")
    print(f"Initial Capital: ${trader.capital:.2f}")
    print(f"Risk Parameters: {STOP_LOSS_PCT*100}% SL, {TAKE_PROFIT_PCT*100}% TP")
    print(f"Max Daily Trades: {MAX_DAILY_TRADES}")
    
    # Run analysis
    analysis_results = trader.run_analysis()
    
    # Generate summary
    summary = trader.generate_summary()
    print(summary)
    
    # Save summary to file
    with open('trading_summary.txt', 'w') as f:
        f.write(summary)
    
    return summary

if __name__ == "__main__":
    main()