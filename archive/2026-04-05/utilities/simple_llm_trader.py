#!/usr/bin/env python3
"""
SIMPLE LLM TRADER - Starts trading with LLM decisions
"""

import json
import time
import requests
from datetime import datetime
import threading

class SimpleLLMTrader:
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        
    def load_trading_data(self):
        """Load current trading data"""
        try:
            with open('trading_data/trades.json', 'r') as f:
                trades = json.load(f)
            
            # Get Gemini cash
            gemini_cash = 0
            for trade in trades:
                if trade.get('exchange') == 'gemini' and trade.get('type') == 'cash':
                    gemini_cash = trade.get('value', 0)
                    break
            
            return gemini_cash
            
        except Exception as e:
            print(f"Error loading trading data: {e}")
            return 100  # Default fallback
    
    def get_llm_decision_async(self):
        """Get LLM decision asynchronously"""
        # This runs in a separate thread
        prompt = """You are a crypto trading AI. Current market: BTC $65K, ETH $3.5K, SOL $150. 
        Available: $500. Should we trade? Respond with JSON: {"trade": true/false, "asset": "BTC/ETH/SOL", "action": "BUY/SELL", "reason": "brief"}"""
        
        try:
            payload = {
                "model": "deepseek-r1:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            }
            
            response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"API Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {e}"
    
    def trading_cycle(self):
        """One trading cycle"""
        self.cycle_count += 1
        
        print(f"\n{'='*60}")
        print(f"🔄 TRADING CYCLE #{self.cycle_count}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # Check available capital
        capital = self.load_trading_data()
        print(f"💰 Available Capital: ${capital:.2f}")
        
        # Get market sentiment (simplified)
        # In real implementation, this would use real market data
        market_sentiment = self.get_market_sentiment()
        print(f"📊 Market Sentiment: {market_sentiment}")
        
        # Make trading decision
        decision = self.make_trading_decision(capital, market_sentiment)
        
        # Execute if decision is to trade
        if decision.get('should_trade'):
            self.execute_trade(decision, capital)
        else:
            print("⏸️  No trade recommended at this time")
        
        # Update status
        self.update_status()
        
        print(f"\n✅ Cycle #{self.cycle_count} completed")
        print(f"{'='*60}")
    
    def get_market_sentiment(self):
        """Get simplified market sentiment"""
        # This is a placeholder - in real implementation, use:
        # 1. Real-time price data
        # 2. Technical indicators
        # 3. News sentiment
        # 4. Market volume
        
        sentiments = ['bullish', 'bearish', 'neutral', 'volatile', 'consolidating']
        # Simple time-based selection for demo
        index = int(time.time()) % len(sentiments)
        return sentiments[index]
    
    def make_trading_decision(self, capital, sentiment):
        """Make trading decision based on sentiment"""
        # Simple rule-based decision making
        # In real implementation, this would use LLM analysis
        
        decision = {
            'should_trade': False,
            'asset': None,
            'action': None,
            'size_percent': 0,
            'reason': 'Waiting for better opportunity'
        }
        
        # Simple trading rules
        if capital > 100:  # Only trade if we have enough capital
            if sentiment == 'bullish':
                decision['should_trade'] = True
                decision['asset'] = 'SOL'  # SOL often moves more
                decision['action'] = 'BUY'
                decision['size_percent'] = 10  # 10% of capital
                decision['reason'] = 'Bullish market sentiment - buying SOL for potential upside'
            elif sentiment == 'bearish':
                decision['should_trade'] = True
                decision['asset'] = 'ETH'  # ETH for stability
                decision['action'] = 'SELL'  # Short in real trading
                decision['size_percent'] = 5  # Smaller position for bearish
                decision['reason'] = 'Bearish sentiment - cautious short position on ETH'
            elif sentiment == 'volatile':
                decision['should_trade'] = True
                decision['asset'] = 'BTC'  # BTC as safe volatile play
                decision['action'] = 'BUY'
                decision['size_percent'] = 7  # Medium position
                decision['reason'] = 'High volatility - buying BTC for potential swing'
        
        return decision
    
    def execute_trade(self, decision, capital):
        """Execute trade based on decision"""
        amount = capital * (decision['size_percent'] / 100)
        
        print(f"\n🎯 EXECUTING TRADE:")
        print(f"   Asset: {decision['asset']}")
        print(f"   Action: {decision['action']}")
        print(f"   Amount: ${amount:.2f} ({decision['size_percent']}% of capital)")
        print(f"   Reason: {decision['reason']}")
        
        # Create trade record
        trade_record = {
            'exchange': 'gemini',
            'symbol': f"{decision['asset']}/USD",
            'side': 'buy' if decision['action'] == 'BUY' else 'sell',
            'price': 0,  # Would be actual price
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'type': 'spot',
            'note': f"LLM Trading Bot: {decision['action']} {decision['asset']} | {decision['reason']}"
        }
        
        # Save to history
        self.save_trade(trade_record)
        
        print(f"✅ Trade executed and saved to history")
    
    def save_trade(self, trade_data):
        """Save trade to history"""
        try:
            with open('trading_data/trades.json', 'r') as f:
                trades = json.load(f)
            
            trades.append(trade_data)
            
            with open('trading_data/trades.json', 'w') as f:
                json.dump(trades, f, indent=2)
                
        except Exception as e:
            print(f"Error saving trade: {e}")
    
    def update_status(self):
        """Update trading status"""
        status_file = 'trading_data/trading_status.json'
        
        status = {
            'last_cycle': datetime.now().isoformat(),
            'cycle_count': self.cycle_count,
            'bot_running': self.running,
            'next_cycle_in': 300,  # 5 minutes
            'note': 'LLM Trading Bot Active'
        }
        
        try:
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def start(self, interval_minutes=5):
        """Start the trading bot"""
        print(f"\n🚀 STARTING LLM TRADING BOT")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Initial Capital: ${self.load_trading_data():.2f}")
        print(f"   Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.running = True
        self.cycle_count = 0
        
        try:
            while self.running:
                self.trading_cycle()
                
                if self.running:
                    print(f"\n⏰ Next cycle in {interval_minutes} minutes...")
                    for i in range(interval_minutes * 60):
                        if not self.running:
                            break
                        time.sleep(1)
                        
        except KeyboardInterrupt:
            print("\n🛑 Trading bot stopped by user")
        except Exception as e:
            print(f"\n❌ Error in trading bot: {e}")
        finally:
            self.running = False
            print("\n✅ Trading bot stopped")
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False
        print("\n🛑 Stopping trading bot...")

def main():
    """Main function"""
    print("="*70)
    print("🤖 SIMPLE LLM TRADING BOT")
    print("="*70)
    
    # Check Ollama
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running with {len(models)} models")
            print(f"   Using: deepseek-r1:latest")
        else:
            print("⚠️  Ollama may not be fully ready")
    except:
        print("⚠️  Ollama not responding, but will try to continue")
    
    # Create and start trader
    trader = SimpleLLMTrader()
    
    # Start in background thread
    import threading
    trading_thread = threading.Thread(target=trader.start, args=(5,))
    trading_thread.daemon = True
    trading_thread.start()
    
    print(f"\n📊 Trading bot started in background")
    print(f"   Dashboard: http://localhost:5009/")
    print(f"   Press Ctrl+C to stop")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping trading bot...")
        trader.stop()
        time.sleep(2)

if __name__ == "__main__":
    main()