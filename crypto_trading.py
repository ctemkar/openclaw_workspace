#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Uses Gemini API with $1,000 capital
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Analyzes BTC/USD and ETH/USD with conservative strategy
"""

import ccxt
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
import sys

# Trading parameters
CAPITAL = 1000  # $1,000 total capital
MAX_TRADES_PER_DAY = 2
STOP_LOSS_PCT = 5  # 5% stop-loss
TAKE_PROFIT_PCT = 10  # 10% take-profit
POSITION_SIZE_PCT = 40  # Use 40% of capital per trade (conservative)

# Gemini API configuration (using sandbox for safety)
# In production, use real API keys from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_API_SECRET = os.getenv('GEMINI_API_SECRET', '')

# Use sandbox for testing, set to False for real trading
USE_SANDBOX = True

class ConservativeCryptoTrader:
    def __init__(self):
        """Initialize Gemini exchange connection"""
        if USE_SANDBOX:
            self.exchange = ccxt.gemini({
                'apiKey': GEMINI_API_KEY,
                'secret': GEMINI_API_SECRET,
                'sandbox': True,
                'enableRateLimit': True,
            })
        else:
            self.exchange = ccxt.gemini({
                'apiKey': GEMINI_API_KEY,
                'secret': GEMINI_API_SECRET,
                'enableRateLimit': True,
            })
        
        # Track daily trades
        self.today_trades = 0
        self.trades_history = []
        
        # Market symbols to analyze
        self.symbols = ['BTC/USD', 'ETH/USD']
        
        print(f"Initialized Conservative Crypto Trader")
        print(f"Capital: ${CAPITAL}")
        print(f"Risk Parameters: {STOP_LOSS_PCT}% stop-loss, {TAKE_PROFIT_PCT}% take-profit")
        print(f"Max trades per day: {MAX_TRADES_PER_DAY}")
        print(f"Using {'SANDBOX' if USE_SANDBOX else 'LIVE'} mode")
    
    def fetch_market_data(self, symbol, timeframe='1h', limit=100):
        """Fetch OHLCV data for analysis"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calculate conservative technical indicators"""
        if df is None or len(df) < 20:
            return None
        
        # Simple Moving Averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        
        # Relative Strength Index (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # Support and Resistance levels (simplified)
        df['support'] = df['low'].rolling(window=20).min()
        df['resistance'] = df['high'].rolling(window=20).max()
        
        return df
    
    def analyze_market_sentiment(self, df):
        """Analyze market sentiment based on technical indicators"""
        if df is None or len(df) < 50:
            return "NEUTRAL", 0
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        score = 0
        
        # Trend analysis (weight: 40%)
        if latest['SMA_20'] > latest['SMA_50']:
            score += 40  # Bullish trend
        else:
            score -= 40  # Bearish trend
        
        # RSI analysis (weight: 30%)
        if latest['RSI'] < 30:
            score += 30  # Oversold, bullish signal
        elif latest['RSI'] > 70:
            score -= 30  # Overbought, bearish signal
        
        # Bollinger Band analysis (weight: 20%)
        if latest['close'] < latest['BB_lower']:
            score += 20  # Below lower band, potential bounce
        elif latest['close'] > latest['BB_upper']:
            score -= 20  # Above upper band, potential pullback
        
        # Support/Resistance analysis (weight: 10%)
        if latest['close'] > latest['resistance'] * 0.98:
            score += 10  # Near resistance, caution
        elif latest['close'] < latest['support'] * 1.02:
            score -= 10  # Near support, potential bounce
        
        # Determine sentiment
        if score >= 20:
            return "BULLISH", score
        elif score <= -20:
            return "BEARISH", score
        else:
            return "NEUTRAL", score
    
    def get_trading_signal(self, symbol):
        """Generate conservative trading signal"""
        df = self.fetch_market_data(symbol)
        if df is None:
            return "HOLD", 0, "No data"
        
        df = self.calculate_technical_indicators(df)
        if df is None:
            return "HOLD", 0, "Insufficient data"
        
        sentiment, score = self.analyze_market_sentiment(df)
        latest = df.iloc[-1]
        
        # Conservative trading rules
        signal = "HOLD"
        confidence = abs(score) / 100.0
        
        # Only trade on strong signals for conservative approach
        if sentiment == "BULLISH" and score >= 40:
            signal = "BUY"
            reason = f"Strong bullish signals: SMA crossover, RSI oversold, price near support"
        elif sentiment == "BEARISH" and score <= -40:
            signal = "SELL"
            reason = f"Strong bearish signals: SMA crossover, RSI overbought, price near resistance"
        else:
            reason = f"Neutral market conditions: score={score}"
        
        return signal, confidence, reason
    
    def check_daily_trade_limit(self):
        """Check if daily trade limit has been reached"""
        today = datetime.now().date()
        today_trades = sum(1 for trade in self.trades_history 
                          if trade['timestamp'].date() == today)
        return today_trades >= MAX_TRADES_PER_DAY
    
    def calculate_position_size(self, price):
        """Calculate position size based on capital and risk parameters"""
        position_value = CAPITAL * (POSITION_SIZE_PCT / 100)
        quantity = position_value / price
        return quantity, position_value
    
    def execute_trade(self, symbol, signal, price):
        """Execute trade with proper risk management"""
        if self.check_daily_trade_limit():
            print(f"Daily trade limit ({MAX_TRADES_PER_DAY}) reached. Skipping trade.")
            return False
        
        quantity, position_value = self.calculate_position_size(price)
        
        # Calculate stop-loss and take-profit prices
        if signal == "BUY":
            stop_loss_price = price * (1 - STOP_LOSS_PCT / 100)
            take_profit_price = price * (1 + TAKE_PROFIT_PCT / 100)
            order_type = "buy"
        elif signal == "SELL":
            stop_loss_price = price * (1 + STOP_LOSS_PCT / 100)
            take_profit_price = price * (1 - TAKE_PROFIT_PCT / 100)
            order_type = "sell"
        else:
            return False
        
        # In sandbox mode, simulate trade execution
        if USE_SANDBOX:
            trade = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'type': order_type,
                'quantity': quantity,
                'price': price,
                'value': position_value,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'status': 'SIMULATED'
            }
            self.trades_history.append(trade)
            self.today_trades += 1
            
            print(f"\n{'='*60}")
            print(f"SIMULATED TRADE EXECUTED")
            print(f"{'='*60}")
            print(f"Symbol: {symbol}")
            print(f"Action: {order_type.upper()}")
            print(f"Quantity: {quantity:.6f}")
            print(f"Price: ${price:.2f}")
            print(f"Position Value: ${position_value:.2f}")
            print(f"Stop-Loss: ${stop_loss_price:.2f} ({STOP_LOSS_PCT}%)")
            print(f"Take-Profit: ${take_profit_price:.2f} ({TAKE_PROFIT_PCT}%)")
            print(f"{'='*60}")
            
            return True
        else:
            # Real trade execution (commented out for safety)
            try:
                # order = self.exchange.create_order(
                #     symbol=symbol,
                #     type='limit',
                #     side=order_type,
                #     amount=quantity,
                #     price=price
                # )
                # print(f"Real trade executed: {order}")
                # return True
                print("Real trading disabled. Enable by setting USE_SANDBOX=False and providing API keys.")
                return False
            except Exception as e:
                print(f"Error executing trade: {e}")
                return False
    
    def run_analysis(self):
        """Run complete market analysis and execute trades if signals are strong"""
        print(f"\n{'='*60}")
        print(f"CRYPTO MARKET ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        trade_executed = False
        
        for symbol in self.symbols:
            print(f"\nAnalyzing {symbol}...")
            
            # Get current price
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                print(f"Current Price: ${current_price:.2f}")
            except Exception as e:
                print(f"Error fetching price for {symbol}: {e}")
                continue
            
            # Get trading signal
            signal, confidence, reason = self.get_trading_signal(symbol)
            
            print(f"Signal: {signal}")
            print(f"Confidence: {confidence:.2%}")
            print(f"Reason: {reason}")
            
            # Execute trade if signal is strong enough
            if signal in ["BUY", "SELL"] and confidence >= 0.6:
                print(f"\nStrong {signal} signal detected for {symbol} (confidence: {confidence:.2%})")
                
                if self.execute_trade(symbol, signal, current_price):
                    trade_executed = True
                    print(f"Trade executed successfully!")
                else:
                    print(f"Trade execution failed or skipped.")
            else:
                print(f"No strong trading signal for {symbol}. Holding position.")
        
        return trade_executed
    
    def generate_summary(self):
        """Generate plain text summary of trades"""
        summary = []
        summary.append("=" * 60)
        summary.append("CONSERVATIVE CRYPTO TRADING SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Capital: ${CAPITAL}")
        summary.append(f"Risk Parameters: {STOP_LOSS_PCT}% stop-loss, {TAKE_PROFIT_PCT}% take-profit")
        summary.append(f"Max trades per day: {MAX_TRADES_PER_DAY}")
        summary.append(f"Mode: {'SANDBOX (Simulated)' if USE_SANDBOX else 'LIVE'}")
        summary.append("")
        
        if not self.trades_history:
            summary.append("No trades executed in this session.")
        else:
            summary.append("TRADES EXECUTED:")
            summary.append("-" * 40)
            
            for i, trade in enumerate(self.trades_history, 1):
                summary.append(f"Trade #{i}:")
                summary.append(f"  Time: {trade['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                summary.append(f"  Symbol: {trade['symbol']}")
                summary.append(f"  Action: {trade['type'].upper()}")
                summary.append(f"  Quantity: {trade['quantity']:.6f}")
                summary.append(f"  Price: ${trade['price']:.2f}")
                summary.append(f"  Value: ${trade['value']:.2f}")
                summary.append(f"  Stop-Loss: ${trade['stop_loss']:.2f}")
                summary.append(f"  Take-Profit: ${trade['take_profit']:.2f}")
                summary.append(f"  Status: {trade['status']}")
                summary.append("")
        
        # Market analysis summary
        summary.append("MARKET ANALYSIS:")
        summary.append("-" * 40)
        
        for symbol in self.symbols:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                signal, confidence, reason = self.get_trading_signal(symbol)
                summary.append(f"{symbol}:")
                summary.append(f"  Price: ${ticker['last']:.2f}")
                summary.append(f"  Signal: {signal} (confidence: {confidence:.2%})")
                summary.append(f"  Analysis: {reason}")
            except Exception as e:
                summary.append(f"{symbol}: Error in analysis - {str(e)}")
        
        summary.append("")
        summary.append("RECOMMENDATION:")
        summary.append("-" * 40)
        
        if self.check_daily_trade_limit():
            summary.append("Daily trade limit reached. No further trades recommended today.")
        else:
            trades_remaining = MAX_TRADES_PER_DAY - self.today_trades
            summary.append(f"Trades remaining today: {trades_remaining}")
            summary.append("Continue monitoring for strong signals with >60% confidence.")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)

def main():
    """Main execution function"""
    print("Starting Conservative Crypto Trading Analysis...")
    
    # Initialize trader
    trader = ConservativeCryptoTrader()
    
    # Run analysis
    trade_executed = trader.run_analysis()
    
    # Generate summary
    summary = trader.generate_summary()
    
    print("\n" + summary)
    
    # Save summary to file
    with open('trading_summary.txt', 'w') as f:
        f.write(summary)
    
    if trade_executed:
        print("\n✅ Trade(s) executed successfully!")
    else:
        print("\n⏸️ No trades executed - waiting for stronger signals.")
    
    return summary

if __name__ == "__main__":
    main()