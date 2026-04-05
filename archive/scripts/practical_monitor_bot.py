#!/usr/bin/env python3
"""
PRACTICAL MONITOR BOT - Monitors opportunities and alerts
- Uses PUBLIC APIs only (no private keys needed)
- Monitors MANA spreads between Binance and Gemini
- Alerts when profitable opportunities exist
- Safe to run without API keys
"""

import ccxt
import time
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('practical_monitor.log'),
        logging.StreamHandler()
    ]
)

class PracticalMonitorBot:
    def __init__(self):
        logging.info("🚀 PRACTICAL MONITOR BOT STARTING")
        logging.info("💰 Monitors opportunities - No API keys needed!")
        
        # Initialize exchanges with PUBLIC access only
        self.binance = ccxt.binance({
            'enableRateLimit': True
        })
        
        self.gemini = ccxt.gemini({
            'enableRateLimit': True
        })
        
        # Monitoring parameters
        self.min_spread = 0.5  # Minimum 0.5% spread to alert
        
        logging.info(f"📊 Monitoring Setup:")
        logging.info(f"   Min spread: {self.min_spread}%")
        logging.info("============================================================")
        logging.info("🚀 PRACTICAL MONITOR - FINDING PROFITABLE OPPORTUNITIES")
        logging.info("============================================================")
        logging.info("💰 MONITORING:")
        logging.info("    • Binance PUBLIC API for prices")
        logging.info("    • Gemini PUBLIC API for prices")
        logging.info("    • MANA spreads for arbitrage")
        logging.info("============================================================")
    
    def check_spread(self):
        """Check MANA spread between exchanges"""
        try:
            # Get MANA prices from PUBLIC APIs
            binance_ticker = self.binance.fetch_ticker('MANA/USDT')
            binance_price = binance_ticker['last']
            
            gemini_ticker = self.gemini.fetch_ticker('MANA/USD')
            gemini_price = gemini_ticker['last']
            
            # Calculate spread (Gemini - Binance)
            spread = ((gemini_price - binance_price) / binance_price) * 100
            
            logging.info(f"📊 MARKET CHECK:")
            logging.info(f"    Binance MANA/USDT: ${binance_price:.4f}")
            logging.info(f"    Gemini MANA/USD: ${gemini_price:.4f}")
            logging.info(f"    Spread: {spread:.2f}%")
            
            # Calculate potential profit
            if abs(spread) >= self.min_spread:
                # Assuming $30 trade size
                trade_size = 30
                potential_profit = trade_size * (abs(spread)/100) - 0.06  # Approx fees
                
                if spread > 0:
                    logging.info(f"    🎯 PROFITABLE OPPORTUNITY!")
                    logging.info(f"    💰 Buy Binance ${binance_price:.4f}, Sell Gemini ${gemini_price:.4f}")
                    logging.info(f"    📈 Potential profit: ${potential_profit:.2f} per ${trade_size}")
                else:
                    logging.info(f"    ⚠️ REVERSE OPPORTUNITY (negative spread)")
                    logging.info(f"    💰 Buy Gemini ${gemini_price:.4f}, Sell Binance ${binance_price:.4f}")
                    logging.info(f"    📈 Potential profit: ${potential_profit:.2f} per ${trade_size}")
            else:
                logging.info(f"    ⏳ Spread too small ({spread:.2f}% < {self.min_spread}%)")
            
            return binance_price, gemini_price, spread
            
        except Exception as e:
            logging.error(f"❌ Spread check error: {e}")
            return 0, 0, 0
    
    def run(self):
        """Main monitoring loop"""
        scan_count = 0
        
        while True:
            scan_count += 1
            logging.info(f"🔍 Monitor Scan #{scan_count}")
            
            # Check spread
            binance_price, gemini_price, spread = self.check_spread()
            
            # Wait for next check
            wait_time = random.randint(30, 60)  # Check every 30-60 seconds
            logging.info(f"    ⏳ Next check in {wait_time} seconds...")
            logging.info("    " + "="*50)
            time.sleep(wait_time)

if __name__ == "__main__":
    bot = PracticalMonitorBot()
    bot.run()