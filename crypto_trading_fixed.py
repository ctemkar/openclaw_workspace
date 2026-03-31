#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot
Risk parameters: 5% stop-loss, 10% take-profit, max 2 trades per day
Capital: $1,000
"""

import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import json
import os

class ConservativeCryptoTrader:
    def __init__(self, capital=1000):
        self.capital = capital
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.stop_loss = 0.05  # 5% stop loss
        self.take_profit = 0.10  # 10% take profit
        self.max_trades_per_day = 2
        self.today_trades = 0
        self.today_date = datetime.now().date()
        
        # Initialize exchange
        try:
            self.exchange = ccxt.binance({
                'enableRateLimit': True,
            })
            print("Exchange initialized successfully")
        except Exception as e:
            print(f"Error initializing exchange: {e}")
            self.exchange = None
    
    def check_market_conditions(self):
        """Check BTC/USD and ETH/USD prices and market sentiment"""
        if not self.exchange:
            return None
        
        try:
            # Fetch current prices
            btc_ticker = self.exchange.fetch_ticker('BTC/USDT')
            eth_ticker = self.exchange.fetch_ticker('ETH/USDT')
            
            # Fetch recent OHLCV data for analysis
            btc_ohlcv = self.exchange.fetch_ohlcv('BTC/USDT', '1h', limit=24)
            eth_ohlcv = self.exchange.fetch_ohlcv('ETH/USDT', '1h', limit=24)
            
            # Convert to DataFrames
            btc_df = pd.DataFrame(btc_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            eth_df = pd.DataFrame(eth_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate technical indicators
            btc_df['sma_20'] = btc_df['close'].rolling(window=20).mean()
            btc_df['rsi'] = self.calculate_rsi(btc_df['close'])
            
            eth_df['sma_20'] = eth_df['close'].rolling(window=20).mean()
            eth_df['rsi'] = self.calculate_rsi(eth_df['close'])
            
            # Calculate support and resistance levels
            btc_support, btc_resistance = self.calculate_support_resistance(btc_df)
            eth_support, eth_resistance = self.calculate_support_resistance(eth_df)
            
            # Market sentiment analysis
            btc_sentiment = self.analyze_sentiment(btc_df)
            eth_sentiment = self.analyze_sentiment(eth_df)
            
            market_data = {
                'btc': {
                    'price': btc_ticker['last'],
                    'change_24h': btc_ticker['percentage'],
                    'high_24h': btc_ticker['high'],
                    'low_24h': btc_ticker['low'],
                    'volume': btc_ticker['quoteVolume'],
                    'sma_20': btc_df['sma_20'].iloc[-1] if not pd.isna(btc_df['sma_20'].iloc[-1]) else None,
                    'rsi': btc_df['rsi'].iloc[-1] if not pd.isna(btc_df['rsi'].iloc[-1]) else None,
                    'support': btc_support,
                    'resistance': btc_resistance,
                    'sentiment': btc_sentiment
                },
                'eth': {
                    'price': eth_ticker['last'],
                    'change_24h': eth_ticker['percentage'],
                    'high_24h': eth_ticker['high'],
                    'low_24h': eth_ticker['low'],
                    'volume': eth_ticker['quoteVolume'],
                    'sma_20': eth_df['sma_20'].iloc[-1] if not pd.isna(eth_df['sma_20'].iloc[-1]) else None,
                    'rsi': eth_df['rsi'].iloc[-1] if not pd.isna(eth_df['rsi'].iloc[-1]) else None,
                    'support': eth_support,
                    'resistance': eth_resistance,
                    'sentiment': eth_sentiment
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_support_resistance(self, df, window=20):
        """Calculate support and resistance levels"""
        recent_data = df.tail(window)
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        return support, resistance
    
    def analyze_sentiment(self, df):
        """Analyze market sentiment based on price action"""
        recent_close = df['close'].iloc[-1]
        sma_20 = df['sma_20'].iloc[-1] if not pd.isna(df['sma_20'].iloc[-1]) else recent_close
        rsi = df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else 50
        
        sentiment = "NEUTRAL"
        
        if recent_close > sma_20 * 1.02:  # Price above SMA by 2%
            if rsi > 70:
                sentiment = "OVERBOUGHT"
            elif rsi > 55:
                sentiment = "BULLISH"
        elif recent_close < sma_20 * 0.98:  # Price below SMA by 2%
            if rsi < 30:
                sentiment = "OVERSOLD"
            elif rsi < 45:
                sentiment = "BEARISH"
        
        return sentiment
    
    def generate_trading_signals(self, market_data):
        """Generate conservative trading signals based on analysis"""
        if not market_data:
            return []
        
        signals = []
        
        # Check if we've reached daily trade limit
        if self.today_date != datetime.now().date():
            self.today_date = datetime.now().date()
            self.today_trades = 0
        
        if self.today_trades >= self.max_trades_per_day:
            print(f"Daily trade limit reached ({self.max_trades_per_day} trades)")
            return signals
        
        # Analyze BTC
        btc = market_data['btc']
        btc_price = btc['price']
        
        # Conservative BTC trading logic
        if btc['sentiment'] == "OVERSOLD" and btc['rsi'] and btc['rsi'] < 35:
            # Buy signal: oversold condition
            position_size = (self.capital * self.risk_per_trade) / btc_price
            stop_loss_price = btc_price * (1 - self.stop_loss)
            take_profit_price = btc_price * (1 + self.take_profit)
            
            signals.append({
                'symbol': 'BTC/USDT',
                'action': 'BUY',
                'price': btc_price,
                'size': position_size,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'reason': f"Oversold condition (RSI: {btc['rsi']:.2f}, Support: ${btc['support']:.2f})",
                'risk_score': 'LOW'
            })
        
        elif btc['sentiment'] == "OVERBOUGHT" and btc['rsi'] and btc['rsi'] > 75:
            # Sell signal: overbought condition
            position_size = (self.capital * self.risk_per_trade) / btc_price
            stop_loss_price = btc_price * (1 + self.stop_loss)
            take_profit_price = btc_price * (1 - self.take_profit)
            
            signals.append({
                'symbol': 'BTC/USDT',
                'action': 'SELL',
                'price': btc_price,
                'size': position_size,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'reason': f"Overbought condition (RSI: {btc['rsi']:.2f}, Resistance: ${btc['resistance']:.2f})",
                'risk_score': 'LOW'
            })
        
        # Analyze ETH
        eth = market_data['eth']
        eth_price = eth['price']
        
        # Conservative ETH trading logic
        if eth['sentiment'] == "OVERSOLD" and eth['rsi'] and eth['rsi'] < 35:
            position_size = (self.capital * self.risk_per_trade) / eth_price
            stop_loss_price = eth_price * (1 - self.stop_loss)
            take_profit_price = eth_price * (1 + self.take_profit)
            
            signals.append({
                'symbol': 'ETH/USDT',
                'action': 'BUY',
                'price': eth_price,
                'size': position_size,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'reason': f"Oversold condition (RSI: {eth['rsi']:.2f}, Support: ${eth['support']:.2f})",
                'risk_score': 'LOW'
            })
        
        elif eth['sentiment'] == "OVERBOUGHT" and eth['rsi'] and eth['rsi'] > 75:
            position_size = (self.capital * self.risk_per_trade) / eth_price
            stop_loss_price = eth_price * (1 + self.stop_loss)
            take_profit_price = eth_price * (1 - self.take_profit)
            
            signals.append({
                'symbol': 'ETH/USDT',
                'action': 'SELL',
                'price': eth_price,
                'size': position_size,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'reason': f"Overbought condition (RSI: {eth['rsi']:.2f}, Resistance: ${eth['resistance']:.2f})",
                'risk_score': 'LOW'
            })
        
        # Limit to one signal per execution to be conservative
        if signals:
            # Sort by risk score and take the best one
            signals.sort(key=lambda x: 0 if x['risk_score'] == 'LOW' else 1)
            signals = [signals[0]]
            self.today_trades += 1
        
        return signals
    
    def execute_trade(self, signal):
        """Execute a trade (simulated for demonstration)"""
        # Simulated execution for demonstration
        print(f"\n[SIMULATED TRADE EXECUTION]")
        print(f"Symbol: {signal['symbol']}")
        print(f"Action: {signal['action']}")
        print(f"Price: ${signal['price']:.2f}")
        print(f"Size: {signal['size']:.6f}")
        print(f"Stop Loss: ${signal['stop_loss']:.2f}")
        print(f"Take Profit: ${signal['take_profit']:.2f}")
        print(f"Reason: {signal['reason']}")
        print(f"Risk Score: {signal['risk_score']}")
        
        # Calculate position value
        position_value = signal['price'] * signal['size']
        
        # Simulate order ID
        simulated_order = {
            'id': f"SIM-{int(time.time())}",
            'symbol': signal['symbol'],
            'side': signal['action'].lower(),
            'price': signal['price'],
            'amount': signal['size'],
            'cost': position_value,
            'status': 'closed',
            'timestamp': datetime.now().isoformat()
        }
        
        return simulated_order
    
    def run_analysis(self):
        """Run complete trading analysis"""
        print("=" * 60)
        print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ${self.capital:,}")
        print(f"Risk Parameters: {self.stop_loss*100}% Stop Loss, {self.take_profit*100}% Take Profit")
        print(f"Max Trades/Day: {self.max_trades_per_day}")
        print("=" * 60)
        
        # Check market conditions
        print("\n1. MARKET ANALYSIS")
        market_data = self.check_market_conditions()
        
        if not market_data:
            print("Failed to fetch market data. Exiting.")
            return None
        
        # Display BTC analysis
        btc = market_data['btc']
        print(f"\nBTC/USDT Analysis:")
        print(f"  Current Price: ${btc['price']:,.2f}")
        print(f"  24h Change: {btc['change_24h']:.2f}%")
        print(f"  24h Range: ${btc['low_24h']:,.2f} - ${btc['high_24h']:,.2f}")
        print(f"  Volume: ${btc['volume']:,.0f}")
        if btc['sma_20']:
            print(f"  SMA(20): ${btc['sma_20']:,.2f}")
        if btc['rsi']:
            print(f"  RSI(14): {btc['rsi']:.2f}")
        print(f"  Support: ${btc['support']:,.2f}")
        print(f"  Resistance: ${btc['resistance']:,.2f}")
        print(f"  Sentiment: {btc['sentiment']}")
        
        # Display ETH analysis
        eth = market_data['eth']
        print(f"\nETH/USDT Analysis:")
        print(f"  Current Price: ${eth['price']:,.2f}")
        print(f"  24h Change: {eth['change_24h']:.2f}%")
        print(f"  24h Range: ${eth['low_24h']:,.2f} - ${eth['high_24h']:,.2f}")
        print(f"  Volume: ${eth['volume']:,.0f}")
        if eth['sma_20']:
            print(f"  SMA(20): ${eth['sma_20']:,.2f}")
        if eth['rsi']:
            print(f"  RSI(14): {eth['rsi']:.2f}")
        print(f"  Support: ${eth['support']:,.2f}")
        print(f"  Resistance: ${eth['resistance']:,.2f}")
        print(f"  Sentiment: {eth['sentiment']}")
        
        # Generate trading signals
        print("\n2. TRADING SIGNAL GENERATION")
        signals = self.generate_trading_signals(market_data)
        
        executed_trades = []
        
        if signals:
            print(f"\nGenerated {len(signals)} trading signal(s):")
            for i, signal in enumerate(signals, 1):
                print(f"\nSignal #{i}:")
                print(f"  Symbol: {signal['symbol']}")
                print(f"  Action: {signal['action']}")
                print(f"  Price: ${signal['price']:.2f}")
                print(f"  Size: {signal['size']:.6f}")
                print(f"  Stop Loss: ${signal['stop_loss']:.2f} ({self.stop_loss*100}% loss)")
                print(f"  Take Profit: ${signal['take_profit']:.2f} ({self.take_profit*100}% gain)")
                print(f"  Reason: {signal['reason']}")
                print(f"  Risk Score: {signal['risk_score']}")
                
                # Execute trade
                print(f"\n3. TRADE EXECUTION")
                order = self.execute_trade(signal)
                
                if order:
                    print(f"\nTrade executed successfully!")
                    print(f"  Order ID: {order.get('id', 'N/A')}")
                    print(f"  Status: {order.get('status', 'N/A')}")
                    print(f"  Cost: ${order.get('cost', 0):.2f}")
                    executed_trades.append(order)
                else:
                    print("Trade execution failed.")
        else:
            print("\nNo conservative trading signals generated at this time.")
            print("Reason: Market conditions don't meet conservative entry criteria.")
        
        # Summary
        print("\n" + "=" * 60)
        print("TRADING SUMMARY")
        print("=" * 60)
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ${self.capital:,}")
        print(f"Trades Executed Today: {self.today_trades}/{self.max_trades_per_day}")
        print(f"Total Trades Executed: {len(executed_trades)}")
        
        if executed_trades:
            total_cost = sum(trade.get('cost', 0) for trade in executed_trades)
            print(f"Total Position Value: ${total_cost:.2f}")
            print(f"Remaining Capital: ${self.capital - total_cost:.2f}")
        
        print("\nRECOMMENDATIONS:")
        if not signals:
            print("1. Maintain current positions (if any)")
            print("2. Wait for better entry points")
            print("3. Monitor support/resistance levels")
            print("4. Next analysis in 1-4 hours")
        
        return {
            'market_data': market_data,
            'signals': signals,
            'executed_trades': executed_trades,
            'summary': {
                'capital': self.capital,
                'trades_today': self.today_trades,
                'max_trades_per_day': self.max_trades_per_day,
                'total_trades': len(executed_trades)
            }
        }

def main():
    """Main function to run the trading analysis"""
    trader = ConservativeCryptoTrader(capital=1000)
    result = trader.run_analysis()
    return result

if __name__ == "__main__":
    main()