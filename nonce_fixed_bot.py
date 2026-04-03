#!/usr/bin/env python3
"""
NONCE-FIXED Trading Bot
- Proper nonce handling for Gemini
- Uses your $572 Gemini + $72 Binance
"""

import ccxt
import time
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nonce_fixed_trading.log'),
        logging.StreamHandler()
    ]
)

class NonceFixedBot:
    def __init__(self):
        self.keys = self.load_keys()
        
        # Initialize with proper nonce
        self.gemini = ccxt.gemini({
            'apiKey': self.keys.get('GEMINI_API_KEY', ''),
            'secret': self.keys.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
            'nonce': lambda: int(time.time() * 1000)
        })
        
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        self.gemini_balance = 0
        self.binance_balance = 0
        self.total_profit = 0.0
        self.trade_count = 0
        
        logging.info("🚀 NONCE-FIXED BOT STARTED")
        logging.info("💰 YOU HAVE: $572 Gemini + $72 Binance")
    
    def load_keys(self):
        keys = {}
        try:
            with open('.env', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            keys[key.strip()] = value.strip()
        except Exception as e:
            logging.error(f"Error: {e}")
        return keys
    
    def safe_gemini_call(self, func, *args):
        """Safe Gemini call with delay"""
        time.sleep(2)  # Delay to avoid nonce issues
        try:
            return func(*args)
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            return None
    
    def check_balances(self):
        """Check balances with safe calls"""
        try:
            # Check Gemini with delay
            gemini_bal = self.safe_gemini_call(self.gemini.fetch_balance)
            if gemini_bal:
                self.gemini_balance = gemini_bal.get('USD', {}).get('free', 0)
                logging.info(f"💰 Gemini: ${self.gemini_balance:.2f}")
            
            # Check Binance
            binance_bal = self.binance.fetch_balance()
            self.binance_balance = binance_bal.get('USDT', {}).get('free', 0)
            logging.info(f"💰 Binance: ${self.binance_balance:.2f}")
            
        except Exception as e:
            logging.error(f"Balance error: {e}")
    
    def find_opportunity(self, crypto):
        """Find arbitrage opportunity"""
        try:
            # Get prices with delays
            time.sleep(1)
            gemini_ticker = self.safe_gemini_call(self.gemini.fetch_ticker, f"{crypto}/USD")
            if not gemini_ticker:
                return None
            
            binance_ticker = self.binance.fetch_ticker(f"{crypto}/USDT")
            
            gemini_price = gemini_ticker['last']
            binance_price = binance_ticker['last']
            
            # Calculate spread
            spread = ((gemini_price - binance_price) / binance_price) * 100
            
            # Determine trade
            if gemini_price > binance_price and self.binance_balance >= 20:
                # Buy Binance, Sell Gemini
                return {
                    'crypto': crypto,
                    'spread': abs(spread),
                    'buy_exchange': 'binance',
                    'sell_exchange': 'gemini',
                    'buy_price': binance_price,
                    'sell_price': gemini_price,
                    'trade_size': 20.0
                }
            elif binance_price > gemini_price and self.gemini_balance >= 50:
                # Buy Gemini, Sell Binance
                return {
                    'crypto': crypto,
                    'spread': abs(spread),
                    'buy_exchange': 'gemini',
                    'sell_exchange': 'binance',
                    'buy_price': gemini_price,
                    'sell_price': binance_price,
                    'trade_size': 50.0
                }
            
        except Exception as e:
            logging.debug(f"Can't check {crypto}: {e}")
        
        return None
    
    def execute_trade(self, opp):
        """Execute trade"""
        logging.info(f"🎯 {opp['crypto']}: {opp['spread']:.2f}% spread")
        
        # Calculate profit
        profit = opp['trade_size'] * (opp['spread'] / 100) - (opp['trade_size'] * 0.002)
        
        if profit < 0.15:  # Min profit
            logging.info(f"   Profit too low: ${profit:.2f}")
            return False
        
        logging.info(f"   Expected profit: ${profit:.2f}")
        
        # For now, simulate
        logging.info(f"   ⚠️ SAFETY: Simulating trade")
        logging.info(f"   Would buy on {opp['buy_exchange']} at ${opp['buy_price']:.2f}")
        logging.info(f"   Would sell on {opp['sell_exchange']} at ${opp['sell_price']:.2f}")
        
        # Simulate success
        self.trade_count += 1
        self.total_profit += profit
        
        logging.info(f"   💰 Simulated profit: ${profit:.2f}")
        logging.info(f"   📊 Total trades: {self.trade_count}")
        logging.info(f"   📈 Total profit: ${self.total_profit:.2f}")
        
        return True
    
    def run(self):
        """Main loop"""
        cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
        
        scan_num = 0
        while True:
            try:
                scan_num += 1
                logging.info(f"🔍 Scan #{scan_num}")
                
                # Check balances
                self.check_balances()
                
                # Find opportunities
                for crypto in cryptos:
                    opp = self.find_opportunity(crypto)
                    if opp and opp['spread'] >= 0.4:
                        self.execute_trade(opp)
                        time.sleep(5)  # Wait after trade
                
                # Wait between scans
                time.sleep(30)
                
            except KeyboardInterrupt:
                logging.info("🛑 Stopped")
                break
            except Exception as e:
                logging.error(f"Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = NonceFixedBot()
    bot.run()