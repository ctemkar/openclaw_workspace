#!/usr/bin/env python3
"""
Conservative Crypto Trading Simulation
Simulates trading with $1,000 capital using conservative strategy
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import random

# Trading parameters
CAPITAL = 1000  # $1,000 capital
STOP_LOSS = 0.05  # 5% stop-loss
TAKE_PROFIT = 0.10  # 10% take-profit
MAX_TRADES_PER_DAY = 2
SYMBOLS = ['BTC/USD', 'ETH/USD']

class ConservativeCryptoTrader:
    def __init__(self):
        """Initialize the trader"""
        # Load trade history
        self.trade_history_file = 'trade_history.json'
        self.trade_history = self.load_trade_history()
        
        # Today's trade count
        self.today = datetime.utcnow().date()
        self.today_trades = self.count_today_trades()
        
        # Simulated market data
        self.market_data = {
            'BTC/USD': {
                'price': 66245.23,
                'change_24h': 1.5,
                'high_24h': 66500.00,
                'low_24h': 65800.00,
                'volume': 25000000,
                'trend': 'bullish',
                'rsi': 58.5,
                'support': 65500.00,
                'resistance': 66800.00
            },
            'ETH/USD': {
                'price': 3520.45,
                'change_24h': 2.1,
                'high_24h': 3550.00,
                'low_24h': 3480.00,
                'volume': 12000000,
                'trend': 'bullish',
                'rsi': 62.3,
                'support': 3450.00,
                'resistance': 3580.00
            }
        }
        
        print(f"Initialized Conservative Crypto Trader")
        print(f"Capital: ${CAPITAL}")
        print(f"Risk Parameters: {STOP_LOSS*100}% stop-loss, {TAKE_PROFIT*100}% take-profit")
        print(f"Max trades per day: {MAX_TRADES_PER_DAY}")
        print(f"Today's trades so far: {self.today_trades}")
        print("-" * 50)
    
    def load_trade_history(self):
        """Load trade history from file"""
        try:
            if os.path.exists(self.trade_history_file):
                with open(self.trade_history_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_trade_history(self):
        """Save trade history to file"""
        with open(self.trade_history_file, 'w') as f:
            json.dump(self.trade_history, f, indent=2)
    
    def count_today_trades(self):
        """Count trades executed today"""
        today_str = self.today.isoformat()
        count = 0
        for trade in self.trade_history:
            if isinstance(trade, dict):
                trade_date = trade.get('date', '')
                if isinstance(trade_date, str) and trade_date.startswith(today_str):
                    count += 1
        return count
    
    def analyze_market_sentiment(self, symbol):
        """Analyze market sentiment for a symbol"""
        data = self.market_data[symbol]
        
        # Conservative scoring system (0-100)
        score = 50  # Neutral starting point
        
        # RSI analysis (30-70 range for conservative trading)
        rsi = data['rsi']
        if 30 < rsi < 70:
            score += 10  # Neutral RSI is good for conservative trading
        elif rsi < 30:
            score += 15  # Oversold - potential buying opportunity
        elif rsi > 70:
            score -= 10  # Overbought - be cautious
        
        # Trend analysis
        if data['trend'] == 'bullish':
            score += 10
        else:
            score -= 5
        
        # Price position relative to support/resistance
        price = data['price']
        support = data['support']
        resistance = data['resistance']
        
        distance_to_support = ((price - support) / support * 100)
        distance_to_resistance = ((resistance - price) / price * 100)
        
        if distance_to_support < 3:
            score += 10  # Near support - potential bounce
        if distance_to_resistance < 3:
            score -= 10  # Near resistance - potential pullback
        
        # Volume confirmation
        if data['volume'] > 10000000:
            if data['trend'] == 'bullish':
                score += 5
        
        # Determine action based on score
        if score >= 70:
            action = 'BUY'
            confidence = 'HIGH'
        elif score >= 60:
            action = 'BUY'
            confidence = 'MEDIUM'
        elif score <= 30:
            action = 'SELL'
            confidence = 'HIGH'
        elif score <= 40:
            action = 'SELL'
            confidence = 'MEDIUM'
        else:
            action = 'HOLD'
            confidence = 'NEUTRAL'
        
        return {
            'symbol': symbol,
            'price': data['price'],
            'score': score,
            'action': action,
            'confidence': confidence,
            'rsi': rsi,
            'trend': data['trend'],
            'support': support,
            'resistance': resistance,
            'change_24h': data['change_24h']
        }
    
    def calculate_position_size(self, price, action):
        """Calculate position size based on capital and risk"""
        # For conservative trading, use 20% of capital per trade
        position_percentage = 0.20
        position_value = CAPITAL * position_percentage
        
        # Calculate quantity
        quantity = position_value / price
        
        # Round to appropriate decimal places
        if 'BTC' in self.current_symbol:
            quantity = round(quantity, 6)  # BTC precision
        elif 'ETH' in self.current_symbol:
            quantity = round(quantity, 4)  # ETH precision
        
        return quantity, position_value
    
    def execute_trade(self, symbol, action, analysis):
        """Execute a trade based on analysis"""
        if self.today_trades >= MAX_TRADES_PER_DAY:
            print(f"Max trades per day ({MAX_TRADES_PER_DAY}) reached. Skipping trade.")
            return None
        
        try:
            self.current_symbol = symbol
            price = analysis['price']
            quantity, position_value = self.calculate_position_size(price, action)
            
            print(f"\nPreparing to execute {action} order:")
            print(f"Symbol: {symbol}")
            print(f"Price: ${price:,.2f}")
            print(f"Quantity: {quantity}")
            print(f"Position Value: ${position_value:,.2f}")
            print(f"Analysis Score: {analysis['score']:.1f}")
            print(f"Confidence: {analysis['confidence']}")
            
            # Create a mock trade
            trade_id = f"TRADE_{int(datetime.utcnow().timestamp())}"
            
            # Calculate stop-loss and take-profit prices
            if action == 'BUY':
                stop_loss_price = price * (1 - STOP_LOSS)
                take_profit_price = price * (1 + TAKE_PROFIT)
            else:  # SELL (short)
                stop_loss_price = price * (1 + STOP_LOSS)
                take_profit_price = price * (1 - TAKE_PROFIT)
            
            trade = {
                'id': trade_id,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'entry_price': price,
                'position_value': position_value,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'date': datetime.utcnow().isoformat(),
                'status': 'OPEN',
                'analysis_score': analysis['score'],
                'confidence': analysis['confidence']
            }
            
            # Add to trade history
            self.trade_history.append(trade)
            self.today_trades += 1
            self.save_trade_history()
            
            print(f"\n✅ Trade executed successfully!")
            print(f"Trade ID: {trade_id}")
            print(f"Stop-loss: ${stop_loss_price:,.2f} ({STOP_LOSS*100}%)")
            print(f"Take-profit: ${take_profit_price:,.2f} ({TAKE_PROFIT*100}%)")
            
            return trade
            
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None
    
    def check_open_trades(self):
        """Check status of open trades (simulated)"""
        open_trades = [t for t in self.trade_history if t.get('status') == 'OPEN']
        
        if not open_trades:
            print("No open trades.")
            return
        
        print(f"\nChecking {len(open_trades)} open trades:")
        for trade in open_trades:
            symbol = trade['symbol']
            current_price = self.market_data[symbol]['price']
            entry_price = trade['entry_price']
            
            if trade['action'] == 'BUY':
                pnl_pct = ((current_price - entry_price) / entry_price * 100)
            else:  # SELL
                pnl_pct = ((entry_price - current_price) / entry_price * 100)
            
            print(f"\nTrade {trade['id']}:")
            print(f"  {trade['action']} {trade['quantity']} {symbol}")
            print(f"  Entry: ${entry_price:,.2f}, Current: ${current_price:,.2f}")
            print(f"  P&L: {pnl_pct:+.2f}%")
            print(f"  Stop-loss: ${trade['stop_loss']:,.2f}")
            print(f"  Take-profit: ${trade['take_profit']:,.2f}")
            
            # Simulate price movement for demo
            price_move = random.uniform(-0.02, 0.03)  # -2% to +3%
            simulated_price = current_price * (1 + price_move)
            
            # Check if stop-loss or take-profit hit
            if trade['action'] == 'BUY':
                if simulated_price <= trade['stop_loss']:
                    trade['status'] = 'CLOSED_STOP_LOSS'
                    trade['exit_price'] = simulated_price
                    trade['exit_date'] = datetime.utcnow().isoformat()
                    print(f"  ⚠️  STOP-LOSS HIT! Trade closed at ${simulated_price:,.2f} (loss)")
                elif simulated_price >= trade['take_profit']:
                    trade['status'] = 'CLOSED_TAKE_PROFIT'
                    trade['exit_price'] = simulated_price
                    trade['exit_date'] = datetime.utcnow().isoformat()
                    print(f"  ✅ TAKE-PROFIT HIT! Trade closed at ${simulated_price:,.2f} (profit)")
            else:  # SELL
                if simulated_price >= trade['stop_loss']:
                    trade['status'] = 'CLOSED_STOP_LOSS'
                    trade['exit_price'] = simulated_price
                    trade['exit_date'] = datetime.utcnow().isoformat()
                    print(f"  ⚠️  STOP-LOSS HIT! Trade closed at ${simulated_price:,.2f} (loss)")
                elif simulated_price <= trade['take_profit']:
                    trade['status'] = 'CLOSED_TAKE_PROFIT'
                    trade['exit_price'] = simulated_price
                    trade['exit_date'] = datetime.utcnow().isoformat()
                    print(f"  ✅ TAKE-PROFIT HIT! Trade closed at ${simulated_price:,.2f} (profit)")
        
        self.save_trade_history()
    
    def generate_summary(self):
        """Generate trading summary"""
        total_trades = len(self.trade_history)
        open_trades = len([t for t in self.trade_history if t.get('status') == 'OPEN'])
        closed_trades = total_trades - open_trades
        
        # Calculate performance
        profitable_trades = 0
        total_pnl = 0
        
        for trade in self.trade_history:
            if trade.get('status', '').startswith('CLOSED'):
                entry = trade['entry_price']
                exit_price = trade.get('exit_price', entry)
                position_value = trade['position_value']
                
                if trade['action'] == 'BUY':
                    pnl = (exit_price - entry) / entry * position_value
                else:  # SELL
                    pnl = (entry - exit_price) / entry * position_value
                
                total_pnl += pnl
                if pnl > 0:
                    profitable_trades += 1
        
        win_rate = (profitable_trades / closed_trades * 100) if closed_trades > 0 else 0
        
        summary = f"""
CONSERVATIVE CRYPTO TRADING SUMMARY
====================================
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Capital: ${CAPITAL:,.2f}

TRADE STATISTICS:
• Total Trades: {total_trades}
• Open Trades: {open_trades}
• Closed Trades: {closed_trades}
• Profitable Trades: {profitable_trades}
• Win Rate: {win_rate:.1f}%
• Total P&L: ${total_pnl:,.2f}
• Today's Trades: {self.today_trades}/{MAX_TRADES_PER_DAY}

RISK PARAMETERS:
• Stop-loss: {STOP_LOSS*100}%
• Take-profit: {TAKE_PROFIT*100}%
• Max trades/day: {MAX_TRADES_PER_DAY}

RECOMMENDATION: {'Continue conservative trading' if win_rate >= 50 else 'Review strategy'}
"""
        return summary
    
    def run_analysis(self):
        """Run complete trading analysis"""
        print("\n" + "="*60)
        print("CONSERVATIVE CRYPTO TRADING ANALYSIS")
        print("="*60)
        
        all_analyses = []
        
        for symbol in SYMBOLS:
            print(f"\nAnalyzing {symbol}...")
            
            # Analyze sentiment
            analysis = self.analyze_market_sentiment(symbol)
            all_analyses.append(analysis)
            
            print(f"  Current Price: ${analysis['price']:,.2f}")
            print(f"  24h Change: {analysis['change_24h']:+.2f}%")
            print(f"  RSI: {analysis['rsi']:.1f}")
            print(f"  Trend: {analysis['trend']}")
            print(f"  Support: ${analysis['support']:,.2f}")
            print(f"  Resistance: ${analysis['resistance']:,.2f}")
            print(f"  Analysis Score: {analysis['score']:.1f}/100")
            print(f"  Recommendation: {analysis['action']} ({analysis['confidence']})")
            
            # Check if we should execute a trade
            if analysis['action'] in ['BUY', 'SELL'] and analysis['confidence'] in ['HIGH', 'MEDIUM']:
                if self.today_trades < MAX_TRADES_PER_DAY:
                    print(f"\n  ⚡ Strong signal detected! Executing {analysis['action']} order...")
                    self.execute_trade(symbol, analysis['action'], analysis)
                else:
                    print(f"\n  ⚡ Strong signal detected but max trades per day reached.")
        
        # Check open trades
        self.check_open_trades()
        
        # Generate and return summary
        summary = self.generate_summary()
        
        # Add current analyses to summary
        summary += "\nCURRENT MARKET ANALYSIS:\n"
        for analysis in all_analyses:
            summary += f"\n{analysis['symbol']}:\n"
            summary += f"  Price: ${analysis['price']:,.2f}\n"
            summary += f"  24h Change: {analysis['change_24h']:+.2f}%\n"
            summary += f"  RSI: {analysis['rsi']:.1f}\n"
            summary += f"  Trend: {analysis['trend']}\n"
            summary += f"  Score: {analysis['score']:.1f}/100\n"
            summary += f"  Action: {analysis['action']} ({analysis['confidence']})\n"
        
        return summary

def main():
    """Main function"""
    print("Starting Conservative Crypto Trading Analysis...")
    print(f"Current time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    trader = ConservativeCryptoTrader()
    summary = trader.run_analysis()
    
    print("\n" + "="*60)
    print("FINAL TRADING SUMMARY")
    print("="*60)
    print(summary)
    
    # Save summary to file
    with open('trading_summary.txt', 'w') as f:
        f.write(summary)
    
    print("\nSummary saved to 'trading_summary.txt'")
    return summary

if __name__ == "__main__":
    main()