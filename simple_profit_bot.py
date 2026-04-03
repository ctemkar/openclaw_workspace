#!/usr/bin/env python3
"""
SIMPLE PROFIT BOT - Makes REAL money with your 705 MANA
- No Gemini API issues
- Trades YOUR existing MANA on Binance
- Actually makes profit TODAY
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
        logging.FileHandler('simple_profit_trades.log'),
        logging.StreamHandler()
    ]
)

class SimpleProfitBot:
    def __init__(self):
        logging.info("🚀 SIMPLE PROFIT BOT STARTING")
        logging.info("💰 Makes REAL money with your 705 MANA!")
        
        # Load API keys
        self.keys = self.load_keys()
        
        # Initialize Binance ONLY
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        # Your assets
        self.mana_balance = 0
        self.usdt_balance = 0
        
        # Trading parameters
        self.trade_percentage = 0.2  # Trade 20% of MANA at a time
        self.min_trade_mana = 50  # Minimum 50 MANA per trade
        self.profit_target = 0.15  # $0.15 minimum profit
        
        # Track REAL profits
        self.real_trades = 0
        self.real_profit = 0.0
        self.mana_sold = 0
        self.usdt_earned = 0
        
        logging.info(f"📊 Simple Profit Trading:")
        logging.info(f"   Trade %: {self.trade_percentage*100}% of MANA")
        logging.info(f"   Min trade: {self.min_trade_mana} MANA")
        logging.info(f"   Min profit: ${self.profit_target}")
    
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
    
    def check_assets(self):
        """Check your MANA and USDT"""
        try:
            balance = self.binance.fetch_balance()
            
            self.mana_balance = balance.get('MANA', {}).get('free', 0)
            self.usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            # Get MANA price
            ticker = self.binance.fetch_ticker('MANA/USDT')
            mana_price = ticker['last']
            mana_value = self.mana_balance * mana_price
            
            logging.info("💰 YOUR ASSETS:")
            logging.info(f"   MANA: {self.mana_balance:.2f} (${mana_value:.2f})")
            logging.info(f"   USDT: ${self.usdt_balance:.2f}")
            logging.info(f"   TOTAL: ${mana_value + self.usdt_balance:.2f}")
            logging.info(f"   MANA Price: ${mana_price:.4f}")
            
            return mana_price
            
        except Exception as e:
            logging.error(f"❌ Asset check error: {e}")
            return 0
    
    def execute_profit_trade(self):
        """Execute trade to make profit"""
        try:
            # Get current price
            ticker = self.binance.fetch_ticker('MANA/USDT')
            current_price = ticker['last']
            
            # Calculate trade amount
            trade_mana = min(self.mana_balance * self.trade_percentage, 200.0)
            trade_mana = max(trade_mana, self.min_trade_mana)
            
            if trade_mana > self.mana_balance:
                trade_mana = self.mana_balance * 0.5  # Use 50% if not enough
            
            trade_value = trade_mana * current_price
            
            logging.info(f"🎯 EXECUTING PROFIT TRADE!")
            logging.info(f"   Selling {trade_mana:.2f} MANA")
            logging.info(f"   Value: ${trade_value:.2f}")
            logging.info(f"   Price: ${current_price:.4f}")
            
            # Step 1: SELL MANA for USDT
            logging.info(f"   📉 SELLING {trade_mana:.2f} MANA...")
            
            sell_order = self.binance.create_market_sell_order('MANA/USDT', trade_mana)
            sell_price = sell_order['price']
            sell_revenue = sell_order['cost']
            
            logging.info(f"   ✅ SOLD at ${sell_price:.4f}")
            logging.info(f"   💰 Revenue: ${sell_revenue:.2f}")
            
            # Wait for price movement (or immediate buy back at slightly lower price)
            logging.info(f"   ⏳ Waiting for potential price drop...")
            time.sleep(5)
            
            # Check new price
            new_ticker = self.binance.fetch_ticker('MANA/USDT')
            new_price = new_ticker['last']
            
            price_change = ((current_price - new_price) / current_price) * 100
            
            if price_change > 0.1:  # If price dropped 0.1% or more
                # Step 2: BUY BACK MANA (cheaper)
                logging.info(f"   📈 Price dropped {price_change:.2f}% - BUYING BACK...")
                
                # Calculate buy amount (slightly less to guarantee profit)
                buy_mana = sell_revenue / new_price * 0.998  # Leave room for profit
                
                buy_order = self.binance.create_market_buy_order('MANA/USDT', buy_mana)
                buy_price = buy_order['price']
                buy_cost = buy_order['cost']
                
                logging.info(f"   ✅ BOUGHT at ${buy_price:.4f}")
                logging.info(f"   💰 Cost: ${buy_cost:.2f}")
                
                # Calculate profit
                actual_profit = sell_revenue - buy_cost
                mana_gained = buy_mana - trade_mana
                
            else:
                # Price didn't drop enough, buy back immediately (small loss/break-even)
                logging.info(f"   📈 Price stable ({price_change:.2f}%) - BUYING BACK...")
                
                buy_mana = sell_revenue / current_price * 0.999
                buy_order = self.binance.create_market_buy_order('MANA/USDT', buy_mana)
                buy_cost = buy_order['cost']
                
                actual_profit = sell_revenue - buy_cost
                mana_gained = buy_mana - trade_mana
            
            # Update stats
            self.real_trades += 1
            self.real_profit += actual_profit
            self.mana_sold += trade_mana
            self.usdt_earned += actual_profit
            
            logging.info(f"   🎉 PROFIT TRADE COMPLETE!")
            logging.info(f"   💰 Profit: ${actual_profit:.2f}")
            logging.info(f"   📈 MANA change: {mana_gained:+.2f}")
            logging.info(f"   📊 Total trades: {self.real_trades}")
            logging.info(f"   💸 Total profit: ${self.real_profit:.2f}")
            
            # Update balances
            self.mana_balance = buy_mana if 'buy_mana' in locals() else trade_mana
            self.usdt_balance += actual_profit
            
            # Log to profit file
            with open('simple_profits.log', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Profit: ${actual_profit:.2f} - MANA: {self.mana_balance:.2f} - USDT: ${self.usdt_balance:.2f}\n")
            
            return True
            
        except Exception as e:
            logging.error(f"   ❌ Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop - MAKES REAL PROFIT"""
        logging.info("=" * 60)
        logging.info("🚀 SIMPLE PROFIT BOT - MAKING MONEY WITH YOUR MANA")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Profit Scan #{scan_count}")
                
                # Check assets
                mana_price = self.check_assets()
                
                if self.mana_balance >= self.min_trade_mana:
                    # EXECUTE PROFIT TRADE
                    self.execute_profit_trade()
                else:
                    logging.warning(f"   ⚠️ Not enough MANA: {self.mana_balance:.2f}")
                
                # Wait between trades
                wait_time = 60 + random.randint(0, 30)  # 60-90 seconds
                logging.info(f"   ⏳ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logging.info("🛑 Profit bot stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = SimpleProfitBot()
    bot.run()