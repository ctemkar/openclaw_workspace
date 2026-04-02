#!/usr/bin/env python3
"""
LLM-POWERED TRADING BOT
Uses Ollama LLMs for trading decisions
"""

import json
import time
import requests
from datetime import datetime
import subprocess
import os

class LLMTradingBot:
    def __init__(self, exchange='gemini', model='deepseek-r1:latest'):
        self.exchange = exchange
        self.model = model
        self.base_url = 'http://localhost:11434/api/generate'
        
        # Trading parameters
        self.position_size_percent = 10  # 10% of capital per trade
        self.stop_loss_percent = 2.0     # 2% stop loss
        self.take_profit_percent = 3.0   # 3% take profit
        
        # Load trading data
        self.load_trading_data()
    
    def load_trading_data(self):
        """Load current trading data"""
        try:
            with open('trading_data/trades.json', 'r') as f:
                self.trades = json.load(f)
            
            # Get Gemini cash
            gemini_cash = 0
            for trade in self.trades:
                if trade.get('exchange') == 'gemini' and trade.get('type') == 'cash':
                    gemini_cash = trade.get('value', 0)
                    break
            
            self.available_capital = gemini_cash
            print(f"💰 Available capital: ${self.available_capital:.2f}")
            
        except Exception as e:
            print(f"Error loading trading data: {e}")
            self.available_capital = 100  # Default fallback
            self.trades = []
    
    def query_llm(self, prompt):
        """Query Ollama LLM for trading decision"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent decisions
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(self.base_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"LLM API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error querying LLM: {e}")
            return None
    
    def get_market_data(self):
        """Get current market data for analysis"""
        # For now, use simple mock data
        # In production, this would fetch real-time data from exchanges
        market_data = {
            'btc_price': 65000,  # Mock BTC price
            'eth_price': 3500,    # Mock ETH price
            'sol_price': 150,     # Mock SOL price
            'market_trend': 'neutral',  # bullish/bearish/neutral
            'volume_trend': 'increasing',
            'volatility': 'medium'
        }
        
        # TODO: Integrate with real exchange APIs
        # For Gemini: gemini_api.get_price('BTCUSD')
        # For Binance: binance_api.get_price('BTCUSDT')
        
        return market_data
    
    def analyze_market_with_llm(self, market_data):
        """Use LLM to analyze market and make trading decision"""
        prompt = f"""You are a professional cryptocurrency trading AI. Analyze the current market conditions and make a trading decision.

MARKET DATA:
- BTC Price: ${market_data['btc_price']:,}
- ETH Price: ${market_data['eth_price']:,}
- SOL Price: ${market_data['sol_price']:,}
- Market Trend: {market_data['market_trend']}
- Volume Trend: {market_data['volume_trend']}
- Volatility: {market_data['volatility']}

AVAILABLE CAPITAL: ${self.available_capital:.2f}
EXCHANGE: {self.exchange.upper()}

TRADING PARAMETERS:
- Position Size: {self.position_size_percent}% of capital
- Stop Loss: {self.stop_loss_percent}%
- Take Profit: {self.take_profit_percent}%

ANALYSIS REQUIREMENTS:
1. Analyze the market conditions
2. Determine if it's a good time to enter a trade
3. If yes, recommend which asset to trade (BTC, ETH, or SOL)
4. Recommend direction (LONG or SHORT)
5. Provide reasoning for your decision

OUTPUT FORMAT (JSON only):
{{
    "decision": "ENTER_TRADE" or "WAIT",
    "asset": "BTC" or "ETH" or "SOL" or null,
    "direction": "LONG" or "SHORT" or null,
    "reasoning": "Brief explanation of your analysis",
    "confidence": 0.0 to 1.0
}}

Respond with ONLY the JSON object, no other text."""

        print(f"\n🤖 Querying {self.model} for trading decision...")
        response = self.query_llm(prompt)
        
        if response:
            try:
                # Extract JSON from response
                # Sometimes LLMs add extra text
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    decision = json.loads(json_str)
                    return decision
                else:
                    print(f"Could not parse JSON from response: {response}")
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                print(f"Raw response: {response}")
        
        return None
    
    def execute_trade(self, decision):
        """Execute trade based on LLM decision"""
        if not decision or decision.get('decision') != 'ENTER_TRADE':
            print("⏸️  LLM recommends waiting, no trade executed")
            return False
        
        asset = decision.get('asset')
        direction = decision.get('direction')
        
        if not asset or not direction:
            print("❌ Invalid trade decision from LLM")
            return False
        
        # Calculate position size
        position_amount = self.available_capital * (self.position_size_percent / 100)
        
        print(f"\n🎯 EXECUTING TRADE BASED ON LLM DECISION:")
        print(f"   Asset: {asset}")
        print(f"   Direction: {direction}")
        print(f"   Amount: ${position_amount:.2f}")
        print(f"   Reasoning: {decision.get('reasoning', 'No reasoning provided')}")
        print(f"   Confidence: {decision.get('confidence', 0) * 100:.1f}%")
        
        # TODO: Implement actual trade execution
        # For Gemini: gemini_api.place_order(asset, direction, position_amount)
        # For Binance: binance_api.place_order(asset, direction, position_amount)
        
        # For now, simulate trade
        trade_data = {
            'exchange': self.exchange,
            'symbol': f'{asset}/USD',
            'side': 'buy' if direction == 'LONG' else 'sell',
            'price': 0,  # Would be actual execution price
            'amount': position_amount,
            'timestamp': datetime.now().isoformat(),
            'type': 'spot',
            'note': f'LLM-powered trade: {direction} {asset} | Confidence: {decision.get("confidence", 0)*100:.1f}%'
        }
        
        # Save trade to history
        self.save_trade(trade_data)
        
        return True
    
    def save_trade(self, trade_data):
        """Save trade to history"""
        try:
            # Load current trades
            with open('trading_data/trades.json', 'r') as f:
                trades = json.load(f)
            
            # Add new trade
            trades.append(trade_data)
            
            # Save updated trades
            with open('trading_data/trades.json', 'w') as f:
                json.dump(trades, f, indent=2)
            
            print(f"✅ Trade saved to history")
            
        except Exception as e:
            print(f"Error saving trade: {e}")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        print(f"\n{'='*60}")
        print(f"🔄 LLM TRADING CYCLE STARTED")
        print(f"   Exchange: {self.exchange.upper()}")
        print(f"   LLM Model: {self.model}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Step 1: Get market data
        market_data = self.get_market_data()
        print(f"\n📊 MARKET DATA:")
        for key, value in market_data.items():
            print(f"   {key}: {value}")
        
        # Step 2: Analyze with LLM
        decision = self.analyze_market_with_llm(market_data)
        
        if decision:
            print(f"\n🤖 LLM DECISION:")
            for key, value in decision.items():
                print(f"   {key}: {value}")
            
            # Step 3: Execute trade if recommended
            if decision.get('decision') == 'ENTER_TRADE':
                self.execute_trade(decision)
            else:
                print("⏸️  LLM recommends waiting for better opportunity")
        else:
            print("❌ Failed to get LLM decision")
        
        # Step 4: Update dashboard
        self.update_dashboard()
        
        print(f"\n✅ Trading cycle completed")
        print(f"{'='*60}")
    
    def update_dashboard(self):
        """Update trading dashboard"""
        # This would trigger dashboard refresh
        # For now, just log
        print("📊 Dashboard would be updated here")
    
    def run_continuous(self, interval_minutes=5):
        """Run trading bot continuously"""
        print(f"\n🚀 STARTING LLM TRADING BOT")
        print(f"   Model: {self.model}")
        print(f"   Exchange: {self.exchange}")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Available Capital: ${self.available_capital:.2f}")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n📈 CYCLE #{cycle_count}")
                
                self.run_trading_cycle()
                
                print(f"\n⏰ Waiting {interval_minutes} minutes for next cycle...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Trading bot stopped by user")
        except Exception as e:
            print(f"\n❌ Error in trading bot: {e}")

def test_llm_connection():
    """Test connection to Ollama"""
    print("🔍 Testing Ollama connection...")
    
    try:
        # List models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is running")
            print(f"Available models:\n{result.stdout}")
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed or not in PATH")
        return False

def main():
    """Main function"""
    print("="*70)
    print("🤖 LLM-POWERED TRADING BOT")
    print("="*70)
    
    # Test Ollama connection
    if not test_llm_connection():
        print("❌ Cannot start trading bot without Ollama")
        return
    
    # Choose LLM model
    models = [
        'deepseek-r1:latest',
        'mistral:latest',
        'qwen3:latest',
        'llama3.1:latest',
        'glm-4.7-flash:latest'
    ]
    
    print(f"\n📋 AVAILABLE LLM MODELS:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    # For now, use DeepSeek R1 (most capable)
    selected_model = 'deepseek-r1:latest'
    print(f"\n🎯 SELECTED MODEL: {selected_model}")
    
    # Create and run trading bot
    bot = LLMTradingBot(exchange='gemini', model=selected_model)
    
    # Run one test cycle
    print(f"\n🧪 RUNNING TEST CYCLE...")
    bot.run_trading_cycle()
    
    # Ask if user wants to run continuously
    print(f"\n❓ Run trading bot continuously? (y/n): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        print(f"\n🔄 Starting continuous trading...")
        bot.run_continuous(interval_minutes=5)
    else:
        print(f"\n✅ Test completed. Ready for manual trading cycles.")

if __name__ == "__main__":
    main()