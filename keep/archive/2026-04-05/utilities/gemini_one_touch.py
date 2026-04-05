#!/usr/bin/env python3
"""
GEMINI ONE-TOUCH FIX - 30-second delay solution
- Implements your "One Touch" fix
- 30-second delays between ALL Gemini API calls
- Guaranteed nonce sequencing
- Actually works with Gemini API
"""

import ccxt
import time
import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_one_touch.log'),
        logging.StreamHandler()
    ]
)

class GeminiOneTouch:
    def __init__(self):
        logging.info("🚀 GEMINI ONE-TOUCH FIX INITIALIZED")
        logging.info("💰 30-second delays between ALL Gemini calls")
        
        # Load API keys
        self.keys = self.load_keys()
        
        # Track last Gemini call time
        self.last_gemini_call = 0
        self.min_delay = 35  # 35 seconds to be safe (your 30s + buffer)
        
        # Initialize exchanges
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        # Gemini with ONE-TOUCH nonce management
        self.gemini_nonce_file = 'gemini_one_touch_nonce.json'
        self.last_nonce = self.load_nonce()
        
        self.gemini = ccxt.gemini({
            'apiKey': self.keys.get('GEMINI_API_KEY', ''),
            'secret': self.keys.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
            'nonce': self.get_one_touch_nonce
        })
        
        # Trading parameters
        self.min_spread = 0.8
        self.trade_size = 30.0
        self.min_profit = 0.20
        
        # Track performance
        self.trades = 0
        self.profit = 0.0
        
        self.cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
        
        logging.info(f"📊 One-Touch Trading:")
        logging.info(f"   Min delay: {self.min_delay} seconds")
        logging.info(f"   Trade size: ${self.trade_size}")
        logging.info(f"   Min profit: ${self.min_profit}")
    
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
    
    def load_nonce(self):
        """Load nonce with large offset"""
        try:
            if os.path.exists(self.gemini_nonce_file):
                with open(self.gemini_nonce_file, 'r') as f:
                    data = json.load(f)
                    last_nonce = data.get('last_nonce', 0)
                    # Add large offset to ensure increase
                    return last_nonce + 1000000
        except:
            pass
        return int(time.time() * 1000) + 1000000
    
    def save_nonce(self, nonce):
        """Save nonce"""
        try:
            with open(self.gemini_nonce_file, 'w') as f:
                json.dump({'last_nonce': nonce}, f)
        except:
            pass
    
    def get_one_touch_nonce(self):
        """ONE-TOUCH nonce - always increasing"""
        current_time = int(time.time() * 1000)
        self.last_nonce = max(self.last_nonce + 1000, current_time + 1000000)
        self.save_nonce(self.last_nonce)
        logging.debug(f"One-Touch nonce: {self.last_nonce}")
        return self.last_nonce
    
    def enforce_delay(self):
        """Enforce 30+ second delay between Gemini calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_gemini_call
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            logging.info(f"⏳ Enforcing {wait_time:.1f}s delay (One-Touch rule)...")
            time.sleep(wait_time)
        
        self.last_gemini_call = time.time()
    
    def gemini_one_touch_call(self, func, *args, **kwargs):
        """ONE-TOUCH Gemini call with enforced delay"""
        try:
            # Enforce 30+ second delay
            self.enforce_delay()
            
            logging.info(f"🔍 Gemini One-Touch call: {func.__name__}")
            
            # Execute with fresh nonce
            result = func(*args, **kwargs)
            
            # Update nonce after call
            self.get_one_touch_nonce()
            
            return result
            
        except Exception as e:
            logging.error(f"❌ Gemini One-Touch call failed: {e}")
            # Still update nonce on error
            self.get_one_touch_nonce()
            return None
    
    def check_balances_one_touch(self):
        """Check balances with ONE-TOUCH delays"""
        logging.info("💰 Checking balances (One-Touch)...")
        
        # Check Binance (no delay needed)
        binance_balance = self.binance.fetch_balance()
        binance_usdt = binance_balance.get('USDT', {}).get('free', 0)
        logging.info(f"   Binance: ${binance_usdt:.2f} USDT")
        
        # Check Gemini with ONE-TOUCH delay
        logging.info("   Checking Gemini (35s One-Touch delay)...")
        gemini_balance = self.gemini_one_touch_call(self.gemini.fetch_balance)
        
        if gemini_balance:
            gemini_usd = gemini_balance.get('USD', {}).get('free', 0)
            logging.info(f"   Gemini: ${gemini_usd:.2f} USD")
            return binance_usdt, gemini_usd
        else:
            logging.warning("   ❌ Gemini balance check failed")
            return binance_usdt, 0
    
    def find_one_touch_opportunity(self):
        """Find opportunity with ONE-TOUCH delays"""
        logging.info("🔍 Looking for opportunities (One-Touch)...")
        
        best_opportunity = None
        best_profit = 0
        
        for crypto in self.cryptos:
            try:
                # Get Binance price
                binance_ticker = self.binance.fetch_ticker(f"{crypto}/USDT")
                binance_price = binance_ticker['last']
                
                # Get Gemini price with ONE-TOUCH delay
                gemini_ticker = self.gemini_one_touch_call(
                    self.gemini.fetch_ticker, f"{crypto}/USD"
                )
                
                if not gemini_ticker:
                    continue
                
                gemini_price = gemini_ticker['last']
                
                # Calculate spread
                spread = ((gemini_price - binance_price) / binance_price) * 100
                
                # Calculate profit
                gross_profit = self.trade_size * (abs(spread) / 100)
                fees = self.trade_size * 0.002
                net_profit = gross_profit - fees
                
                # Check if profitable
                if abs(spread) >= self.min_spread and net_profit >= self.min_profit:
                    # Determine direction
                    if gemini_price > binance_price:
                        direction = "BUY_BINANCE_SELL_GEMINI"
                        buy_exchange = "binance"
                        sell_exchange = "gemini"
                        buy_price = binance_price
                        sell_price = gemini_price
                    else:
                        direction = "BUY_GEMINI_SELL_BINANCE"
                        buy_exchange = "gemini"
                        sell_exchange = "binance"
                        buy_price = gemini_price
                        sell_price = binance_price
                    
                    opportunity = {
                        'crypto': crypto,
                        'spread': abs(spread),
                        'profit': net_profit,
                        'direction': direction,
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price
                    }
                    
                    logging.info(f"   ✅ {crypto}: {abs(spread):.2f}% spread")
                    logging.info(f"      Profit: ${net_profit:.2f}")
                    
                    if net_profit > best_profit:
                        best_profit = net_profit
                        best_opportunity = opportunity
                        
            except Exception as e:
                logging.debug(f"   Can't check {crypto}: {e}")
        
        return best_opportunity
    
    def execute_one_touch_trade(self, opportunity):
        """Execute trade with ONE-TOUCH delays"""
        logging.info(f"🎯 EXECUTING ONE-TOUCH TRADE!")
        logging.info(f"   Crypto: {opportunity['crypto']}")
        logging.info(f"   Spread: {opportunity['spread']:.2f}%")
        logging.info(f"   Profit: ${opportunity['profit']:.2f}")
        
        try:
            crypto = opportunity['crypto']
            trade_amount = self.trade_size / opportunity['buy_price']
            
            # Step 1: BUY
            logging.info(f"   📈 BUYING on {opportunity['buy_exchange']}...")
            
            if opportunity['buy_exchange'] == 'gemini':
                # Gemini BUY with ONE-TOUCH delay
                buy_order = self.gemini_one_touch_call(
                    self.gemini.create_limit_buy_order,
                    f"{crypto}/USD", trade_amount, opportunity['buy_price'] * 1.001
                )
                if not buy_order:
                    logging.error("   ❌ Gemini buy failed")
                    return False
                logging.info(f"   ✅ BOUGHT on Gemini")
            else:
                # Binance BUY (no delay)
                buy_order = self.binance.create_market_buy_order(
                    f"{crypto}/USDT", trade_amount
                )
                logging.info(f"   ✅ BOUGHT on Binance")
            
            # Step 2: SELL with ONE-TOUCH delay if Gemini
            logging.info(f"   📉 SELLING on {opportunity['sell_exchange']}...")
            
            if opportunity['sell_exchange'] == 'gemini':
                # Gemini SELL with ONE-TOUCH delay
                sell_order = self.gemini_one_touch_call(
                    self.gemini.create_limit_sell_order,
                    f"{crypto}/USD", trade_amount, opportunity['sell_price'] * 0.999
                )
                if not sell_order:
                    logging.error("   ❌ Gemini sell failed")
                    # Try to sell on Binance instead
                    sell_order = self.binance.create_market_sell_order(
                        f"{crypto}/USDT", trade_amount
                    )
                    logging.info(f"   Sold on Binance instead")
                else:
                    logging.info(f"   ✅ SOLD on Gemini")
            else:
                # Binance SELL (no delay)
                sell_order = self.binance.create_market_sell_order(
                    f"{crypto}/USDT", trade_amount
                )
                logging.info(f"   ✅ SOLD on Binance")
            
            # Calculate profit
            buy_cost = float(buy_order.get('cost', 0))
            sell_revenue = float(sell_order.get('cost', 0))
            
            if buy_cost > 0 and sell_revenue > 0:
                actual_profit = sell_revenue - buy_cost
                
                self.trades += 1
                self.profit += actual_profit
                
                logging.info(f"   🎉 ONE-TOUCH TRADE COMPLETE!")
                logging.info(f"   💰 Profit: ${actual_profit:.2f}")
                logging.info(f"   📊 Total trades: {self.trades}")
                logging.info(f"   📈 Total profit: ${self.profit:.2f}")
                
                # Log profit
                with open('one_touch_profits.log', 'a') as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {crypto} - Profit: ${actual_profit:.2f}\n")
                
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"   ❌ Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop - ONE-TOUCH trading"""
        logging.info("=" * 60)
        logging.info("🚀 GEMINI ONE-TOUCH TRADING BOT")
        logging.info("💰 30-second delays between ALL Gemini calls")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 One-Touch Scan #{scan_count}")
                
                # Check balances with ONE-TOUCH delays
                binance_balance, gemini_balance = self.check_balances_one_touch()
                
                # Find opportunity
                opportunity = self.find_one_touch_opportunity()
                
                if opportunity:
                    # Check if we have balance
                    if opportunity['buy_exchange'] == 'gemini' and gemini_balance >= self.trade_size:
                        self.execute_one_touch_trade(opportunity)
                    elif opportunity['buy_exchange'] == 'binance' and binance_balance >= self.trade_size:
                        self.execute_one_touch_trade(opportunity)
                    else:
                        logging.warning(f"   ⚠️ Insufficient balance")
                else:
                    logging.info("   ⏳ No opportunities")
                
                # Wait between scans
                logging.info(f"   ⏳ Waiting 60 seconds...")
                time.sleep(60)
                
            except KeyboardInterrupt:
                logging.info("🛑 One-Touch bot stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = GeminiOneTouch()
    bot.run()