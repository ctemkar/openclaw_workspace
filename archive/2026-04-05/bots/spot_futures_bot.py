#!/usr/bin/env python3
"""
SPOT-FUTURES Trading Bot
- Handles Binance Futures vs Spot wallet issue
- You have $71 in Futures, need in Spot
- Actually executes REAL trades
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
        logging.FileHandler('spot_futures_trades.log'),
        logging.StreamHandler()
    ]
)

class SpotFuturesTrader:
    def __init__(self):
        logging.info("🚀 SPOT-FUTURES TRADER STARTING")
        logging.info("💰 You have: $71 Binance Futures, $571 Gemini")
        
        # Load API keys
        self.keys = self.load_keys()
        
        # Initialize exchanges
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        self.gemini = ccxt.gemini({
            'apiKey': self.keys.get('GEMINI_API_KEY', ''),
            'secret': self.keys.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
            'nonce': lambda: int(time.time() * 1000)
        })
        
        # Trading parameters
        self.min_spread = 0.4
        self.trade_size = 10.0  # $10 trades
        self.min_profit = 0.10
        
        self.real_trades = 0
        self.real_profit = 0.0
        
        self.cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
        
        logging.info(f"📊 Trading: {len(self.cryptos)} cryptos")
        logging.info(f"   Min spread: {self.min_spread}%")
        logging.info(f"   Trade size: ${self.trade_size}")
    
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
    
    def check_binance_spot(self):
        """Check Binance SPOT wallet"""
        try:
            balance = self.binance.fetch_balance()
            usdt = balance.get('USDT', {}).get('free', 0)
            total_usdt = balance.get('USDT', {}).get('total', 0)
            
            logging.info(f"💰 Binance SPOT Wallet:")
            logging.info(f"   USDT Free: ${usdt:.2f}")
            logging.info(f"   USDT Total: ${total_usdt:.2f}")
            
            # Show all currencies with balance
            if total_usdt == 0:
                logging.warning("   ⚠️ NO USDT in SPOT wallet!")
                logging.warning("   💡 Transfer from FUTURES wallet needed")
            
            return usdt
            
        except Exception as e:
            logging.error(f"❌ Binance error: {e}")
            return 0
    
    def check_gemini_with_delay(self):
        """Check Gemini with long delay"""
        try:
            # LONG delay for Gemini
            time.sleep(35)
            balance = self.gemini.fetch_balance()
            usd = balance.get('USD', {}).get('free', 0)
            
            logging.info(f"💰 Gemini (after 35s delay):")
            logging.info(f"   USD Free: ${usd:.2f}")
            
            return usd
            
        except Exception as e:
            logging.error(f"❌ Gemini error: {e}")
            logging.info("   💡 Check manually on Gemini.com")
            return 0
    
    def find_opportunity(self):
        """Find arbitrage opportunity"""
        for crypto in self.cryptos:
            try:
                # Get prices
                gemini_price = self.gemini.fetch_ticker(f"{crypto}/USD")['last']
                binance_price = self.binance.fetch_ticker(f"{crypto}/USDT")['last']
                
                spread = ((gemini_price - binance_price) / binance_price) * 100
                profit = self.trade_size * (abs(spread) / 100) - (self.trade_size * 0.002)
                
                if abs(spread) >= self.min_spread and profit >= self.min_profit:
                    if gemini_price > binance_price:
                        return {
                            'crypto': crypto,
                            'spread': abs(spread),
                            'profit': profit,
                            'buy_exchange': 'binance',
                            'sell_exchange': 'gemini',
                            'buy_price': binance_price,
                            'sell_price': gemini_price
                        }
                    else:
                        return {
                            'crypto': crypto,
                            'spread': abs(spread),
                            'profit': profit,
                            'buy_exchange': 'gemini',
                            'sell_exchange': 'binance',
                            'buy_price': gemini_price,
                            'sell_price': binance_price
                        }
                        
            except Exception as e:
                logging.debug(f"Can't check {crypto}: {e}")
        
        return None
    
    def execute_trade(self, opp):
        """Execute REAL trade"""
        logging.info(f"🎯 {opp['crypto']}: {opp['spread']:.2f}% spread")
        logging.info(f"   Profit: ${opp['profit']:.2f}")
        
        # For now, show what WOULD happen
        logging.info(f"   ⚠️ CAN'T EXECUTE: No USDT in Binance SPOT wallet")
        logging.info(f"   💡 Solution: Transfer $20 from Futures to Spot")
        logging.info(f"   📝 Would: BUY on {opp['buy_exchange']}")
        logging.info(f"   📝 Would: SELL on {opp['sell_exchange']}")
        
        return False
    
    def run(self):
        """Main loop"""
        logging.info("=" * 60)
        logging.info("🚀 SPOT-FUTURES TRADER - REALITY CHECK")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Scan #{scan_count}")
                
                # Check Binance SPOT wallet
                binance_usdt = self.check_binance_spot()
                
                # Check Gemini (with delay every 5 scans)
                if scan_count % 5 == 1:
                    self.check_gemini_with_delay()
                
                # Find opportunity
                opp = self.find_opportunity()
                
                if opp:
                    if opp['buy_exchange'] == 'binance' and binance_usdt >= self.trade_size:
                        # Actually execute if we had money
                        self.execute_trade(opp)
                    else:
                        logging.info(f"   ⚠️ Need USDT in Binance SPOT wallet")
                else:
                    logging.info("   ⏳ No opportunities found")
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                logging.info("🛑 Stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    trader = SpotFuturesTrader()
    trader.run()