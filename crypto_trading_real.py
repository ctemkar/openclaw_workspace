#!/usr/bin/env python3
"""
Conservative Crypto Trading Bot with Real Market Data
Uses public APIs for price data, simulates Gemini API trades
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
import hashlib
import hmac
import base64

# Configuration
CAPITAL = 1000.0  # $1,000
STOP_LOSS = 0.05  # 5%
TAKE_PROFIT = 0.10  # 10%
MAX_TRADES_PER_DAY = 2

# Public API endpoints for market data
COINGECKO_API = "https://api.coingecko.com/api/v3"
BINANCE_API = "https://api.binance.com/api/v3"

class ConservativeCryptoTrader:
    def __init__(self):
        self.capital = CAPITAL
        self.stop_loss = STOP_LOSS
        self.take_profit = TAKE_PROFIT
        self.max_trades_per_day = MAX_TRADES_PER_DAY
        self.trades_today = 0
        self.last_trade_date = None
        self.trade_history = []
        
    def reset_daily_counts(self):
        """Reset daily trade counts if it's a new day"""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.trades_today = 0
            self.last_trade_date = today
    
    def get_real_market_data(self, symbol):
        """Get real market data from public APIs"""
        try:
            if symbol == "BTCUSD":
                # Get Bitcoin price from CoinGecko
                response = requests.get(f"{COINGECKO_API}/simple/price", params={
                    'ids': 'bitcoin',
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    price = data['bitcoin']['usd']
                    change = data['bitcoin']['usd_24h_change']
                    
                    # Simulate bid/ask spread
                    return {
                        'price': price,
                        'volume': 1000000000,  # Placeholder
                        'bid': price * 0.999,
                        'ask': price * 1.001,
                        'change_24h': change
                    }
            
            elif symbol == "ETHUSD":
                # Get Ethereum price from CoinGecko
                response = requests.get(f"{COINGECKO_API}/simple/price", params={
                    'ids': 'ethereum',
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    price = data['ethereum']['usd']
                    change = data['ethereum']['usd_24h_change']
                    
                    return {
                        'price': price,
                        'volume': 500000000,  # Placeholder
                        'bid': price * 0.999,
                        'ask': price * 1.001,
                        'change_24h': change
                    }
            
            # Fallback to simulated data if API fails
            return self.get_simulated_market_data(symbol)
            
        except Exception as e:
            print(f"Error getting real market data: {e}")
            return self.get_simulated_market_data(symbol)
    
    def get_simulated_market_data(self, symbol):
        """Fallback simulated market data"""
        import random
        if symbol == "BTCUSD":
            base_price = 65000
            variation = random.uniform(-500, 500)
            change = random.uniform(-3, 3)
        else:  # ETHUSD
            base_price = 3500
            variation = random.uniform(-50, 50)
            change = random.uniform(-2, 2)
        
        price = base_price + variation
        return {
            'price': price,
            'volume': 1000.0,
            'bid': price * 0.999,
            'ask': price * 1.001,
            'change_24h': change
        }
    
    def analyze_market_sentiment(self, symbol):
        """Analyze market sentiment with real data"""
        market_data = self.get_real_market_data(symbol)
        if not market_data:
            return None
        
        price = market_data['price']
        change_24h = market_data['change_24h']
        
        # Conservative analysis based on real price movements
        analysis = {
            'symbol': symbol,
            'current_price': price,
            'signal': 'HOLD',
            'confidence': 0.0,
            'support_level': price * 0.95,
            'resistance_level': price * 1.05,
            'volume_trend': 'normal',
            'risk_level': 'medium',
            'change_24h': change_24h
        }
        
        # More realistic conservative trading logic
        if change_24h > 5.0:
            # Strong upward trend - cautious buy signal
            analysis['signal'] = 'BUY'
            analysis['confidence'] = 0.65
            analysis['risk_level'] = 'medium'
            analysis['notes'] = 'Strong upward momentum'
        
        elif change_24h > 2.0:
            # Moderate upward trend - weak buy signal
            analysis['signal'] = 'BUY'
            analysis['confidence'] = 0.55
            analysis['risk_level'] = 'low'
            analysis['notes'] = 'Moderate upward trend'
        
        elif change_24h < -5.0:
            # Strong downward trend - sell signal
            analysis['signal'] = 'SELL'
            analysis['confidence'] = 0.70
            analysis['risk_level'] = 'medium'
            analysis['notes'] = 'Strong downward pressure'
        
        elif change_24h < -2.0:
            # Moderate downward trend - weak sell signal
            analysis['signal'] = 'SELL'
            analysis['confidence'] = 0.60
            analysis['risk_level'] = 'low'
            analysis['notes'] = 'Moderate downward trend'
        
        else:
            # Sideways movement - hold
            analysis['signal'] = 'HOLD'
            analysis['confidence'] = 0.85
            analysis['risk_level'] = 'very low'
            analysis['notes'] = 'Market consolidating'
        
        return analysis
    
    def calculate_position_size(self, price, risk_per_trade=0.02):
        """Calculate conservative position size"""
        risk_amount = self.capital * risk_per_trade
        stop_loss_amount = price * self.stop_loss
        position_size = risk_amount / stop_loss_amount
        
        # Conservative: max 20% of capital per position
        max_position_value = self.capital * 0.20
        max_position_size = max_position_value / price
        
        return min(position_size, max_position_size)
    
    def execute_trade(self, symbol, signal, price, confidence):
        """Execute simulated trade"""
        self.reset_daily_counts()
        
        if self.trades_today >= self.max_trades_per_day:
            print(f"Max trades per day ({self.max_trades_per_day}) reached")
            return None
        
        # Conservative: require 55%+ confidence for BUY, 60%+ for SELL
        min_confidence = 0.55 if signal == 'BUY' else 0.60
        if confidence < min_confidence:
            print(f"Confidence {confidence:.2f} below minimum {min_confidence} for {signal}")
            return None
        
        position_size = self.calculate_position_size(price)
        trade_value = position_size * price
        
        # Ensure we don't exceed available capital
        if trade_value > self.capital * 0.8:
            position_size = (self.capital * 0.8) / price
            trade_value = position_size * price
        
        trade = {
            'id': f"trade_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': signal,
            'price': price,
            'quantity': position_size,
            'value': trade_value,
            'stop_loss': price * (1 - self.stop_loss) if signal == 'BUY' else price * (1 + self.stop_loss),
            'take_profit': price * (1 + self.take_profit) if signal == 'BUY' else price * (1 - self.take_profit),
            'confidence': confidence,
            'status': 'EXECUTED',
            'risk_per_trade': '2%',
            'max_capital_usage': '20%'
        }
        
        self.trades_today += 1
        self.trade_history.append(trade)
        
        print(f"\n✓ EXECUTED {signal} ORDER")
        print(f"  Symbol: {symbol}")
        print(f"  Price: ${price:.2f}")
        print(f"  Quantity: {position_size:.6f}")
        print(f"  Value: ${trade_value:.2f}")
        print(f"  Stop Loss: ${trade['stop_loss']:.2f}")
        print(f"  Take Profit: ${trade['take_profit']:.2f}")
        print(f"  Confidence: {confidence:.2f}")
        
        return trade
    
    def run_analysis(self):
        """Run complete trading analysis with real data"""
        print(f"\n{'='*70}")
        print(f"CONSERVATIVE CRYPTO TRADING ANALYSIS - REAL MARKET DATA")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Capital: ${self.capital:.2f}")
        print(f"Risk Parameters: {self.stop_loss*100}% SL, {self.take_profit*100}% TP")
        print(f"Max trades today: {self.max_trades_per_day}")
        print(f"Trades remaining: {self.max_trades_per_day - self.trades_today}")
        print(f"{'='*70}\n")
        
        executed_trades = []
        symbols = ["BTCUSD", "ETHUSD"]
        
        for symbol in symbols:
            print(f"\n🔍 ANALYZING {symbol}")
            print("-" * 50)
            
            analysis = self.analyze_market_sentiment(symbol)
            if not analysis:
                print(f"  ❌ Could not analyze {symbol}")
                continue
            
            print(f"  Current Price: ${analysis['current_price']:.2f}")
            print(f"  24h Change: {analysis['change_24h']:.2f}%")
            print(f"  Signal: {analysis['signal']}")
            print(f"  Confidence: {analysis['confidence']:.2f}")
            print(f"  Risk Level: {analysis['risk_level']}")
            print(f"  Notes: {analysis.get('notes', 'N/A')}")
            
            # Check if we should execute
            if analysis['signal'] in ['BUY', 'SELL']:
                print(f"\n  ⚡ TRADE SIGNAL DETECTED")
                print(f"  Minimum confidence required: {0.55 if analysis['signal'] == 'BUY' else 0.60}")
                print(f"  Actual confidence: {analysis['confidence']:.2f}")
                
                if analysis['confidence'] >= (0.55 if analysis['signal'] == 'BUY' else 0.60):
                    trade = self.execute_trade(
                        symbol, 
                        analysis['signal'], 
                        analysis['current_price'], 
                        analysis['confidence']
                    )
                    if trade:
                        executed_trades.append(trade)
                else:
                    print(f"  ⚠️  Confidence too low, skipping trade")
            else:
                print(f"  📊 HOLD signal - no trade execution")
            
            time.sleep(2)  # Respect API rate limits
        
        return executed_trades
    
    def generate_summary(self, executed_trades):
        """Generate plain text summary"""
        summary = []
        summary.append("=" * 70)
        summary.append("CONSERVATIVE CRYPTO TRADING - EXECUTION SUMMARY")
        summary.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        summary.append(f"Initial Capital: ${CAPITAL:.2f}")
        summary.append(f"Trades Executed: {len(executed_trades)}/{self.max_trades_per_day}")
        summary.append("=" * 70)
        
        if executed_trades:
            total_invested = sum(t['value'] for t in executed_trades)
            summary.append(f"\n💰 TOTAL INVESTED: ${total_invested:.2f}")
            summary.append(f"💰 CAPITAL REMAINING: ${self.capital - total_invested:.2f}")
            
            summary.append("\n📊 EXECUTED TRADES:")
            summary.append("-" * 50)
            
            for i, trade in enumerate(executed_trades, 1):
                summary.append(f"\nTrade #{i}:")
                summary.append(f"  ID: {trade['id']}")
                summary.append(f"  Symbol: {trade['symbol']}")
                summary.append(f"  Action: {trade['action']}")
                summary.append(f"  Executed: {trade['timestamp']}")
                summary.append(f"  Price: ${trade['price']:.2f}")
                summary.append(f"  Quantity: {trade['quantity']:.6f}")
                summary.append(f"  Value: ${trade['value']:.2f}")
                summary.append(f"  Stop Loss: ${trade['stop_loss']:.2f} ({self.stop_loss*100}%)")
                summary.append(f"  Take Profit: ${trade['take_profit']:.2f} ({self.take_profit*100}%)")
                summary.append(f"  Confidence: {trade['confidence']:.2f}")
                summary.append(f"  Risk per Trade: {trade['risk_per_trade']}")
                summary.append(f"  Max Capital Usage: {trade['max_capital_usage']}")
        else:
            summary.append("\n📊 NO TRADES EXECUTED")
            summary.append("-" * 50)
            summary.append("Conservative strategy active:")
            summary.append("  • Waiting for high-confidence signals (>55% for BUY, >60% for SELL)")
            summary.append("  • Market conditions not favorable for conservative trading")
            summary.append("  • Capital preservation prioritized over aggressive trading")
        
        summary.append("\n" + "=" * 70)
        summary.append("🔒 RISK MANAGEMENT PROTOCOL:")
        summary.append(f"  • Stop Loss: {self.stop_loss*100}% per trade")
        summary.append(f"  • Take Profit: {self.take_profit*100}% per trade")
        summary.append(f"  • Max Trades per Day: {self.max_trades_per_day}")
        summary.append(f"  • Max Position Size: 20% of capital")
        summary.append(f"  • Max Risk per Trade: 2% of capital")
        summary.append(f"  • Minimum Confidence: 55% BUY / 60% SELL")
        summary.append("=" * 70)
        summary.append("\n⚠️  DISCLAIMER: This is a simulated trading exercise.")
        summary.append("   Real trading requires actual API keys and carries risk.")
        summary.append("=" * 70)
        
        return "\n".join(summary)

def main():
    """Main function"""
    print("🚀 Starting Conservative Crypto Trading Analysis")
    print("📈 Using real market data from public APIs")
    print("⚖️  Conservative strategy with strict risk management")
    
    trader = ConservativeCryptoTrader()
    
    try:
        executed_trades = trader.run_analysis()
        summary = trader.generate_summary(executed_trades)
        
        print("\n" + summary)
        
        # Save to file
        with open('trading_summary_real.txt', 'w') as f:
            f.write(summary)
        
        return summary
        
    except Exception as e:
        error_msg = f"Error in trading analysis: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    main()