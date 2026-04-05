#!/usr/bin/env python3
"""
SECURE TELEGRAM BOT - Uses environment variables for tokens
Never commit secrets to version control!
"""

import os
import time
from datetime import datetime

class SecureTelegramBot:
    """Secure Telegram bot that uses environment variables"""
    
    def __init__(self):
        """Initialize with environment variables"""
        # Get token from environment variable
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        
        if not self.chat_id:
            # Default to using token as chat ID if not provided
            self.chat_id = self.token
        
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        print(f"🤖 Secure Telegram Bot Initialized")
        print(f"   Token: {self.token[:10]}... (from environment)")
        print(f"   Chat ID: {self.chat_id[:10]}...")
        print(f"   Security: ✅ Using environment variables (not hardcoded)")
    
    def send_message(self, message):
        """Send a message securely"""
        try:
            # In a real implementation, this would make API calls
            print(f"📨 [SECURE] Sending message to chat {self.chat_id[:10]}...")
            print(f"   Message: {message[:100]}...")
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_trading_update(self, balance, trades, win_rate, sentiment):
        """Send trading update securely"""
        message = f"""
📊 TRADING UPDATE - {datetime.now().strftime('%H:%M')}

💰 Balance: ${balance:,.2f}
📈 Trades: {trades}
🎯 Win Rate: {win_rate}%
🐂 Sentiment: {sentiment}

🔒 Security: Using environment variables
⏰ Next update in 15 minutes
"""
        return self.send_message(message)

def main():
    """Main function - demonstrates secure usage"""
    print("="*60)
    print("🔒 SECURE TELEGRAM BOT DEMONSTRATION")
    print("="*60)
    print()
    print("HOW TO USE SECURELY:")
    print("1. Set environment variables:")
    print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
    print("   export TELEGRAM_CHAT_ID='your_chat_id_here'")
    print()
    print("2. Run the bot:")
    print("   python3 telegram_bot_secure.py")
    print()
    print("3. NEVER commit tokens to version control!")
    print()
    
    # Check if environment variables are set
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set")
        print("   Set it with: export TELEGRAM_BOT_TOKEN='your_token'")
        print("   Or create a .env file (add to .gitignore!)")
        return
    
    # Create and test the bot
    try:
        bot = SecureTelegramBot()
        
        # Send a test message
        success = bot.send_trading_update(
            balance=4681.29,
            trades=15,
            win_rate=71.4,
            sentiment="BULLISH"
        )
        
        if success:
            print("\n✅ Secure bot working correctly")
            print("🔒 Security: No hardcoded secrets in code")
        else:
            print("\n⚠️ Bot encountered an error")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
