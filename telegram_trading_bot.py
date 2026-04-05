#!/usr/bin/env python3
"""
TELEGRAM TRADING BOT
Sends trading updates to Telegram - only the trading part
No system status, no progress monitor wrong data
"""

import asyncio
import json
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

class TelegramTradingBot:
    """Telegram bot for trading updates only"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
        
        # Trading data directory
        self.data_dir = "real_trading_data"
        
        # Last sent trade ID to avoid duplicates
        self.last_trade_id = None
        
    async def send_message(self, text):
        """Send message to Telegram"""
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode='Markdown')
            print(f"✅ Message sent to Telegram")
            return True
        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def get_trading_metrics(self):
        """Get current trading metrics"""
        try:
            with open(os.path.join(self.data_dir, "trading_metrics.json"), "r") as f:
                return json.load(f)
        except:
            return None
    
    def get_recent_trades(self, limit=3):
        """Get recent trades"""
        try:
            with open(os.path.join(self.data_dir, "recent_trades.json"), "r") as f:
                trades = json.load(f)
                return trades[:limit]
        except:
            return []
    
    def get_spread_analysis(self):
        """Get spread analysis"""
        try:
            with open(os.path.join(self.data_dir, "spread_analysis.json"), "r") as f:
                spreads = json.load(f)
                # Find best spread opportunity
                best_spread = max(spreads, key=lambda x: abs(x.get('spread_percent', 0)))
                return best_spread
        except:
            return None
    
    def get_llm_consensus(self):
        """Get LLM consensus score"""
        try:
            with open(os.path.join(self.data_dir, "llm_scores.json"), "r") as f:
                scores = json.load(f)
                # Find consensus model
                for score in scores:
                    if score.get('model') == 'Consensus':
                        return score
                return scores[0] if scores else None
        except:
            return None
    
    async def send_trading_summary(self):
        """Send trading summary to Telegram"""
        metrics = self.get_trading_metrics()
        if not metrics:
            return await self.send_message("⚠️ *No trading data available*\nStart the data generator first.")
        
        # Format message
        message = f"📊 *TRADING SUMMARY* - {datetime.now().strftime('%H:%M')}\n\n"
        
        # Trading metrics
        message += f"💰 *Virtual Balance:* ${metrics.get('virtual_balance', 0):,.2f}\n"
        message += f"📈 *Total Trades:* {metrics.get('total_trades', 0)}\n"
        message += f"🎯 *Win Rate:* {metrics.get('win_rate', 0)}%\n"
        message += f"📊 *Avg P&L:* ${metrics.get('avg_pnl', 0):+.2f}\n"
        message += f"🌡️ *Market Sentiment:* {metrics.get('market_sentiment', 'Unknown')}\n\n"
        
        # Recent trades
        recent_trades = self.get_recent_trades(2)
        if recent_trades:
            message += "🔄 *Recent Trades:*\n"
            for trade in recent_trades:
                side_emoji = "🟢" if trade.get('side') == 'buy' else "🔴"
                message += f"{side_emoji} {trade.get('symbol', 'N/A')} @ ${trade.get('price', 0):,.2f}\n"
            message += "\n"
        
        # Best spread opportunity
        best_spread = self.get_spread_analysis()
        if best_spread:
            spread = best_spread.get('spread_percent', 0)
            if abs(spread) > 1.0:
                message += f"🎯 *Best Opportunity:* {best_spread.get('pair', 'N/A')}\n"
                message += f"   Spread: {spread:+.2f}%\n"
                message += f"   Action: {best_spread.get('action', 'HOLD')}\n\n"
        
        # LLM consensus
        llm = self.get_llm_consensus()
        if llm:
            message += f"🤖 *LLM Consensus:* {llm.get('score', 0)}/10\n"
            message += f"   Recommendation: {llm.get('recommendation', 'N/A')}\n"
        
        message += f"\n_Updated: {datetime.now().strftime('%H:%M:%S')}_"
        
        return await self.send_message(message)
    
    async def send_trade_alert(self, trade):
        """Send individual trade alert"""
        side_emoji = "🟢 BUY" if trade.get('side') == 'buy' else "🔴 SELL"
        
        message = f"{side_emoji} *TRADE EXECUTED*\n\n"
        message += f"*Symbol:* {trade.get('symbol', 'N/A')}\n"
        message += f"*Price:* ${trade.get('price', 0):,.2f}\n"
        message += f"*Amount:* {trade.get('amount', 0):.4f}\n"
        message += f"*Reason:* {trade.get('reason', 'Unknown')}\n"
        
        if trade.get('llm_score'):
            score = trade.get('llm_score', 5.0)
            score_text = "HIGH" if score >= 8 else "MEDIUM" if score >= 6 else "LOW"
            message += f"*LLM Score:* {score}/10 ({score_text})\n"
        
        message += f"\n_Time: {trade.get('time', '00:00:00')}_"
        
        return await self.send_message(message)
    
    async def monitor_new_trades(self):
        """Monitor for new trades and send alerts"""
        print("🔍 Monitoring for new trades...")
        
        while True:
            try:
                # Get current trades
                current_trades = self.get_recent_trades(5)
                if current_trades and len(current_trades) > 0:
                    latest_trade = current_trades[0]
                    latest_trade_id = f"{latest_trade.get('time')}_{latest_trade.get('symbol')}"
                    
                    # Check if this is a new trade
                    if latest_trade_id != self.last_trade_id:
                        print(f"📨 New trade detected: {latest_trade_id}")
                        await self.send_trade_alert(latest_trade)
                        self.last_trade_id = latest_trade_id
                
                # Wait before checking again
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"❌ Error monitoring trades: {e}")
                await asyncio.sleep(60)
    
    async def run_periodic_updates(self, interval_minutes=15):
        """Send periodic trading updates"""
        print(f"⏰ Setting up periodic updates every {interval_minutes} minutes")
        
        while True:
            try:
                await self.send_trading_summary()
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                print(f"❌ Error sending periodic update: {e}")
                await asyncio.sleep(60)
    
    async def start(self):
        """Start the Telegram bot"""
        print("=" * 50)
        print("🤖 TELEGRAM TRADING BOT")
        print("=" * 50)
        print(f"Token: {self.token[:10]}...")
        print(f"Chat ID: {self.chat_id}")
        print("=" * 50)
        
        # Send startup message
        startup_msg = "✅ *Telegram Trading Bot Started*\n\n"
        startup_msg += "I will send:\n"
        startup_msg += "• Trading summaries every 15 minutes\n"
        startup_msg += "• Real-time trade alerts\n"
        startup_msg += "• Market opportunities\n"
        startup_msg += "• LLM consensus scores\n\n"
        startup_msg += "_Paper trading only - 100% simulation_"
        
        await self.send_message(startup_msg)
        
        # Start monitoring tasks
        monitor_task = asyncio.create_task(self.monitor_new_trades())
        update_task = asyncio.create_task(self.run_periodic_updates(15))
        
        # Keep running
        try:
            await asyncio.gather(monitor_task, update_task)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Telegram bot...")
            await self.send_message("🛑 *Trading Bot Stopped*\n\nUpdates will no longer be sent.")

def main():
    """Main function"""
    # Telegram configuration
    TOKEN = "8682526051:AAEITwha34khnpfGf1U-miGT0mFRsz7GKog"
    CHAT_ID = "8682526051"  # Using the token as chat ID for now
    
    # Create and run bot
    bot = TelegramTradingBot(TOKEN, CHAT_ID)
    
    # Run async bot
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n✅ Telegram bot stopped")

if __name__ == "__main__":
    main()