#!/usr/bin/env python3
"""
ULTRA-AGGRESSIVE TRADER
- Trade size: $30 (uses your full $40)
- Min profit: $0.07 (lower threshold)
- Actually executes REAL trades NOW
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
        logging.FileHandler('ultra_aggressive_trades.log'),
        logging.StreamHandler()
    ]
)

class UltraAggressiveTrader:
    def __init__(self):
        logging.info("🚀 ULTRA-AGGRESSIVE TRADER STARTING")
        logging.info("💰 USING YOUR FULL $40 - MAXIMUM TRADING!")
        
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
        
        # ULTRA-AGGRESSIVE parameters
        self.min_spread = 0.4  # 0.4% minimum
        self.trade_size = 30.0  # $30 trades (ULTRA-AGGRESSIVE!)
        self.min_profit = 0.07  # $0.07 minimum (LOWER!)
        
        self.real_trades = 0
        self.real_profit = 0.0
        
        self.cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
        
        logging.info(f"📊 ULTRA-AGGRESSIVE Trading:")
        logging.info(f"   Min spread: {self.min_spread}%")
        logging.info(f"   Trade size: ${self.trade_size} (75% of your $40!)")
        logging.info(f"   Min profit: ${self.min_profit} (LOWER threshold)")
    
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
    
    def check_balance(self):
        """Check balance"""
        try:
            balance = self.binance.fetch_balance()
            usdt = balance.get('USDT', {}).get('free', 0)
            
            logging.info(f"💰 Balance: ${usdt:.2f} USDT")
            
            if usdt >= self.trade_size:
                logging.info(f"   ✅ READY for ${self.trade_size} trades!")
            else:
                logging.warning(f"   ⚠️ Need ${self.trade_size - usdt:.2f} more")
            
            return usdt
            
        except Exception as e:
            logging.error(f"❌ Balance error: {e}")
            return 0
    
    def find_opportunity(self):
        """Find ULTRA-AGGRESSIVE opportunity"""
        for crypto in self.cryptos:
            try:
                # Get prices
                gemini_price = self.gemini.fetch_ticker(f"{crypto}/USD")['last']
                binance_price = self.binance.fetch_ticker(f"{crypto}/USDT")['last']
                
                # Calculate spread
                spread = ((gemini_price - binance_price) / binance_price) * 100
                
                # Calculate ULTRA-AGGRESSIVE profit
                gross_profit = self.trade_size * (abs(spread) / 100)
                fees = self.trade_size * 0.002
                net_profit = gross_profit - fees
                
                # ULTRA-AGGRESSIVE check
                if abs(spread) >= self.min_spread and net_profit >= self.min_profit:
                    # Determine direction
                    if gemini_price > binance_price:
                        return {
                            'crypto': crypto,
                            'spread': abs(spread),
                            'profit': net_profit,
                            'buy_exchange': 'binance',
                            'sell_exchange': 'gemini',
                            'buy_price': binance_price,
                            'sell_price': gemini_price
                        }
                    else:
                        return {
                            'crypto': crypto,
                            'spread': abs(spread),
                            'profit': net_profit,
                            'buy_exchange': 'gemini',
                            'sell_exchange': 'binance',
                            'buy_price': gemini_price,
                            'sell_price': binance_price
                        }
                        
            except Exception as e:
                logging.debug(f"Can't check {crypto}: {e}")
        
        return None
    
    def execute_trade(self, opp):
        """Execute ULTRA-AGGRESSIVE REAL trade"""
        logging.info(f"🎯 EXECUTING ULTRA-AGGRESSIVE TRADE!")
        logging.info(f"   Crypto: {opp['crypto']}")
        logging.info(f"   Spread: {opp['spread']:.2f}%")
        logging.info(f"   Expected profit: ${opp['profit']:.2f}")
        logging.info(f"   Trade size: ${self.trade_size}")
        
        try:
            crypto = opp['crypto']
            
            # Calculate trade amount
            buy_amount = self.trade_size / opp['buy_price']
            
            # Step 1: REAL BUY
            logging.info(f"   📈 BUYING {buy_amount:.6f} {crypto}...")
            
            if opp['buy_exchange'] == 'gemini':
                buy_symbol = f"{crypto}/USD"
                buy_exchange = self.gemini
            else:
                buy_symbol = f"{crypto}/USDT"
                buy_exchange = self.binance
            
            # REAL buy order
            buy_order = buy_exchange.create_market_buy_order(buy_symbol, buy_amount)
            logging.info(f"   ✅ BOUGHT at ${opp['buy_price']:.2f}")
            
            # Wait
            time.sleep(3)
            
            # Step 2: REAL SELL
            logging.info(f"   📉 SELLING {buy_amount:.6f} {crypto}...")
            
            if opp['sell_exchange'] == 'gemini':
                sell_symbol = f"{crypto}/USD"
                sell_exchange = self.gemini
            else:
                sell_symbol = f"{crypto}/USDT"
                sell_exchange = self.binance
            
            # REAL sell order
            sell_order = sell_exchange.create_market_sell_order(sell_symbol, buy_amount)
            logging.info(f"   ✅ SOLD at ${opp['sell_price']:.2f}")
            
            # Calculate REAL profit
            actual_profit = sell_order['cost'] - buy_order['cost']
            
            # Update stats
            self.real_trades += 1
            self.real_profit += actual_profit
            
            logging.info(f"   🎉 ULTRA-AGGRESSIVE TRADE COMPLETE!")
            logging.info(f"   💰 REAL Profit: ${actual_profit:.2f}")
            logging.info(f"   📊 Total trades: {self.real_trades}")
            logging.info(f"   📈 Total profit: ${self.real_profit:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"   ❌ Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop"""
        logging.info("=" * 60)
        logging.info("🚀 ULTRA-AGGRESSIVE TRADING ACTIVATED")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Ultra Scan #{scan_count}")
                
                # Check balance
                balance = self.check_balance()
                
                # Find opportunity
                opp = self.find_opportunity()
                
                if opp:
                    logging.info(f"   🎯 Found: {opp['crypto']} - {opp['spread']:.2f}%")
                    logging.info(f"      Profit: ${opp['profit']:.2f}")
                    
                    if balance >= self.trade_size:
                        # EXECUTE REAL TRADE
                        self.execute_trade(opp)
                    else:
                        logging.warning(f"   ⚠️ Insufficient balance")
                else:
                    logging.info("   ⏳ No opportunities found")
                
                # Wait
                time.sleep(30)
                
            except KeyboardInterrupt:
                logging.info("🛑 Ultra trader stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    trader = UltraAggressiveTrader()
    trader.run()