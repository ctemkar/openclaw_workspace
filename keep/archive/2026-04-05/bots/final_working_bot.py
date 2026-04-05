#!/usr/bin/env python3
"""
FINAL WORKING BOT - Trades what you ALREADY HAVE
- You have: $50 USDT + 225 MANA
- Bot will trade between USDT and MANA
- Actually executes REAL trades
- NO Gemini issues
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
        logging.FileHandler('final_working_trades.log'),
        logging.StreamHandler()
    ]
)

class FinalWorkingBot:
    def __init__(self):
        logging.info("🚀 FINAL WORKING BOT STARTING")
        logging.info("💰 YOU HAVE: $50 USDT + 225 MANA")
        
        # Load API keys
        self.keys = self.load_keys()
        
        # Initialize Binance
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        # Your actual assets
        self.usdt_balance = 0
        self.mana_balance = 0
        self.eth_balance = 0
        
        # Trading parameters
        self.min_trade_usd = 10.0  # $10 minimum (Binance requirement)
        self.trade_percentage = 0.5  # Trade 50% of available
        
        # Track REAL trades
        self.real_trades = 0
        self.real_profit = 0.0
        
        logging.info(f"📊 Trading with what you HAVE")
        logging.info(f"   Min trade: ${self.min_trade_usd}")
        logging.info(f"   Trade %: {self.trade_percentage*100}% of available")
    
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
    
    def check_actual_balances(self):
        """Check what you ACTUALLY have"""
        try:
            balance = self.binance.fetch_balance()
            
            self.usdt_balance = balance.get('USDT', {}).get('free', 0)
            self.mana_balance = balance.get('MANA', {}).get('free', 0)
            self.eth_balance = balance.get('ETH', {}).get('free', 0)
            
            mana_price = self.binance.fetch_ticker('MANA/USDT')['last']
            eth_price = self.binance.fetch_ticker('ETH/USDT')['last']
            
            mana_value = self.mana_balance * mana_price
            eth_value = self.eth_balance * eth_price
            total_value = self.usdt_balance + mana_value + eth_value
            
            logging.info("💰 YOUR ACTUAL ASSETS:")
            logging.info(f"   USDT: ${self.usdt_balance:.2f}")
            logging.info(f"   MANA: {self.mana_balance:.2f} (${mana_value:.2f})")
            logging.info(f"   ETH: {self.eth_balance:.6f} (${eth_value:.2f})")
            logging.info(f"   TOTAL: ${total_value:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Balance error: {e}")
            return False
    
    def execute_mana_trade(self):
        """Trade between USDT and MANA (what you have)"""
        try:
            # Get current price
            ticker = self.binance.fetch_ticker('MANA/USDT')
            current_price = ticker['last']
            
            logging.info(f"📊 MANA Price: ${current_price:.4f}")
            
            # Decide: Buy MANA with USDT or Sell MANA for USDT
            if self.usdt_balance >= self.min_trade_usd:
                # BUY MANA with USDT
                trade_usd = min(self.usdt_balance * self.trade_percentage, 20.0)
                trade_amount = trade_usd / current_price
                
                # Check minimums
                market = self.binance.market('MANA/USDT')
                if trade_amount < market['limits']['amount']['min']:
                    trade_amount = market['limits']['amount']['min']
                    trade_usd = trade_amount * current_price
                
                if trade_usd >= market['limits']['cost']['min']:
                    logging.info(f"🎯 BUYING MANA with ${trade_usd:.2f} USDT")
                    logging.info(f"   Amount: {trade_amount:.2f} MANA")
                    
                    # EXECUTE REAL BUY
                    buy_order = self.binance.create_market_buy_order('MANA/USDT', trade_amount)
                    logging.info(f"   ✅ BOUGHT at ${buy_order['price']:.4f}")
                    logging.info(f"   💰 Cost: ${buy_order['cost']:.2f}")
                    
                    # Update balances
                    self.usdt_balance -= float(buy_order['cost'])
                    self.mana_balance += float(buy_order['amount'])
                    
                    self.real_trades += 1
                    
                    # Log trade
                    with open('real_trades_history.log', 'a') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - BUY MANA - Cost: ${buy_order['cost']:.2f}, Amount: {buy_order['amount']:.2f}\n")
                    
                    return True
                    
            elif self.mana_balance >= 10:  # At least 10 MANA
                # SELL MANA for USDT
                trade_amount = min(self.mana_balance * self.trade_percentage, 100.0)
                trade_usd = trade_amount * current_price
                
                if trade_usd >= self.min_trade_usd:
                    logging.info(f"🎯 SELLING {trade_amount:.2f} MANA for USDT")
                    logging.info(f"   Expected: ${trade_usd:.2f}")
                    
                    # EXECUTE REAL SELL
                    sell_order = self.binance.create_market_sell_order('MANA/USDT', trade_amount)
                    logging.info(f"   ✅ SOLD at ${sell_order['price']:.4f}")
                    logging.info(f"   💰 Revenue: ${sell_order['cost']:.2f}")
                    
                    # Update balances
                    self.mana_balance -= float(sell_order['amount'])
                    self.usdt_balance += float(sell_order['cost'])
                    
                    self.real_trades += 1
                    
                    # Log trade
                    with open('real_trades_history.log', 'a') as f:
                        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - SELL MANA - Revenue: ${sell_order['cost']:.2f}, Amount: {sell_order['amount']:.2f}\n")
                    
                    return True
            
            logging.info("   ⏳ No trade opportunity right now")
            return False
            
        except Exception as e:
            logging.error(f"   ❌ Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop - TRADES WHAT YOU HAVE"""
        logging.info("=" * 60)
        logging.info("🚀 FINAL WORKING BOT - TRADING YOUR ASSETS")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Scan #{scan_count}")
                
                # Check what you actually have
                if not self.check_actual_balances():
                    time.sleep(30)
                    continue
                
                # Execute trade with what you have
                trade_executed = self.execute_mana_trade()
                
                if trade_executed:
                    logging.info(f"   🎉 REAL TRADE #{self.real_trades} COMPLETE!")
                    logging.info(f"   📊 New balances:")
                    logging.info(f"      USDT: ${self.usdt_balance:.2f}")
                    logging.info(f"      MANA: {self.mana_balance:.2f}")
                
                # Wait between trades
                time.sleep(60)  # 1 minute between trades
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    bot = FinalWorkingBot()
    bot.run()