#!/usr/bin/env python3
"""
SIMPLE TELEGRAM TRADING BOT
Just sends trading updates - no complex monitoring
"""

import json
import time
import os
from datetime import datetime
import requests

class SimpleTelegramTradingBot:
    """Simple Telegram bot for trading updates"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        
        # Last sent data
        self.last_balance = None
        self.last_trade_count = 0
        
    def send_message(self, text):
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"✅ Message sent: {text[:50]}...")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def get_trading_data(self):
        """Get trading data from files"""
        data = {
            'metrics': None,
            'trades': [],
            'spreads': [],
            'llm': []
        }
        
        try:
            # Trading metrics
            with open("real_trading_data/trading_metrics.json", "r") as f:
                data['metrics'] = json.load(f)
        except:
            pass
            
        try:
            # Recent trades
            with open("real_trading_data/recent_trades.json", "r") as f:
                data['trades'] = json.load(f)
        except:
            pass
            
        try:
            # Spread analysis
            with open("real_trading_data/spread_analysis.json", "r") as f:
                data['spreads'] = json.load(f)
        except:
            pass
            
        try:
            # LLM scores
            with open("real_trading_data/llm_scores.json", "r") as f:
                data['llm'] = json.load(f)
        except:
            pass
            
        return data
    
    def format_trading_summary(self, data):
        """Format trading summary message"""
        metrics = data['metrics']
        if not metrics:
            return "⚠️ *No trading data available*"
        
        # Basic summary
        message = f"📊 *TRADING UPDATE* - {datetime.now().strftime('%H:%M')}\n\n"
        
        # Balance and trades
        balance = metrics.get('virtual_balance', 0)
        trades = metrics.get('total_trades', 0)
        win_rate = metrics.get('win_rate', 0)
        
        message += f"💰 *Balance:* `${balance:,.2f}`\n"
        message += f"📈 *Trades:* {trades}\n"
        message += f"🎯 *Win Rate:* {win_rate}%\n"
        
        # Check if balance changed
        if self.last_balance is not None:
            change = balance - self.last_balance
            if abs(change) > 0.01:
                change_emoji = "📈" if change > 0 else "📉"
                message += f"{change_emoji} *Change:* `${change:+.2f}`\n"
        
        self.last_balance = balance
        
        # Market sentiment
        sentiment = metrics.get('market_sentiment', 'Unknown')
        sentiment_emoji = "🐂" if sentiment == 'BULLISH' else "🐻" if sentiment == 'BEARISH' else "⚖️"
        message += f"{sentiment_emoji} *Sentiment:* {sentiment}\n\n"
        
        # Recent activity
        if data['trades'] and len(data['trades']) > 0:
            latest = data['trades'][0]
            side = "🟢 BUY" if latest.get('side') == 'buy' else "🔴 SELL"
            message += f"🔄 *Latest Trade:*\n"
            message += f"{side} {latest.get('symbol', 'N/A')}\n"
            message += f"Price: `${latest.get('price', 0):,.2f}`\n"
            
            if latest.get('llm_score'):
                score = latest.get('llm_score', 5.0)
                message += f"LLM Score: {score}/10\n"
            
            message += f"Reason: {latest.get('reason', 'Unknown')}\n\n"
        
        # Best opportunity
        if data['spreads']:
            best_spread = max(data['spreads'], key=lambda x: abs(x.get('spread_percent', 0)))
            spread = best_spread.get('spread_percent', 0)
            
            if abs(spread) > 1.0:
                message += f"🎯 *Best Opportunity:*\n"
                message += f"{best_spread.get('pair', 'N/A')}\n"
                message += f"Spread: {spread:+.2f}%\n"
                message += f"Action: {best_spread.get('action', 'HOLD')}\n\n"
        
        # LLM consensus
        if data['llm']:
            consensus = next((llm for llm in data['llm'] if llm.get('model') == 'Consensus'), data['llm'][0] if data['llm'] else None)
            if consensus:
                message += f"🤖 *LLM Consensus:*\n"
                message += f"Score: {consensus.get('score', 0)}/10\n"
                message += f"Rec: {consensus.get('recommendation', 'N/A')}\n"
        
        message += f"\n_Updated: {datetime.now().strftime('%H:%M:%S')}_"
        message += f"\n_Paper Trading • 100% Simulation_"
        
        return message
    
    def run(self, interval_minutes=15):
        """Run the bot"""
        print("=" * 50)
        print("🤖 SIMPLE TELEGRAM TRADING BOT")
        print("=" * 50)
        print(f"Token: {self.token[:10]}...")
        print(f"Chat ID: {self.chat_id}")
        print(f"Updates every {interval_minutes} minutes")
        print("=" * 50)
        
        # Send startup message
        startup_msg = "✅ *Simple Trading Bot Started*\n\n"
        startup_msg += "I will send trading updates every 15 minutes:\n"
        startup_msg += "• Balance & trade count\n"
        startup_msg += "• Market sentiment\n"
        startup_msg += "• Latest trades\n"
        startup_msg += "• Best opportunities\n"
        startup_msg += "• LLM consensus\n\n"
        startup_msg += "_Paper trading only - 100% simulation_"
        
        self.send_message(startup_msg)
        
        # Main loop
        try:
            while True:
                # Get and send trading data
                data = self.get_trading_data()
                message = self.format_trading_summary(data)
                self.send_message(message)
                
                # Wait for next update
                print(f"⏰ Next update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
            self.send_message("🛑 *Trading Bot Stopped*\n\nUpdates will no longer be sent.")
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)

def main():
    """Main function"""
    # Telegram configuration
    TOKEN = "8682526051:AAEITwha34khnpfGf1U-miGT0mFRsz7GKog"
    CHAT_ID = "8682526051"  # Using token as chat ID
    
    # Create and run bot
    bot = SimpleTelegramTradingBot(TOKEN, CHAT_ID)
    bot.run(interval_minutes=15)

if __name__ == "__main__":
    main()