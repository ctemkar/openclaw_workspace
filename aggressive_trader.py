#!/usr/bin/env python3
"""
AGGRESSIVE TRADER - Uses your $40 Spot wallet
- Trade size: $20 (2x more)
- Actually executes REAL trades
- No more missing opportunities
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
        logging.FileHandler('aggressive_trades.log'),
        logging.StreamHandler()
    ]
)

class AggressiveTrader:
    def __init__(self):
        logging.info("🚀 AGGRESSIVE TRADER STARTING")
        logging.info("💰 You have $40 in Binance Spot - READY TO TRADE!")
        
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
        
        # AGGRESSIVE trading parameters
        self.min_spread = 0.4  # 0.4% minimum
        self.trade_size = 20.0  # $20 trades (AGGRESSIVE!)
        self.min_profit = 0.10  # $0.10 minimum
        
        self.real_trades = 0
        self.real_profit = 0.0
        
        self.cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
        
        logging.info(f"📊 AGGRESSIVE Trading:")
        logging.info(f"   Min spread: {self.min_spread}%")
        logging.info(f"   Trade size: ${self.trade_size} (2x!)")
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
    
    def check_balance(self):
        """Check Binance Spot wallet"""
        try:
            balance = self.binance.fetch_balance()
            usdt = balance.get('USDT', {}).get('free', 0)
            
            logging.info(f"💰 Binance Spot: ${usdt:.2f} USDT")
            
            if usdt >= self.trade_size:
                logging.info(f"   ✅ SUFFICIENT BALANCE for ${self.trade_size} trades")
            else:
                logging.warning(f"   ⚠️ Need ${self.trade_size - usdt:.2f} more")
            
            return usdt
            
        except Exception as e:
            logging.error(f"❌ Balance error: {e}")
            return 0
    
    def find_aggressive_opportunity(self):
        """Find opportunity with AGGRESSIVE parameters"""
        for crypto in self.cryptos:
            try:
                # Get prices
                gemini_price = self.gemini.fetch_ticker(f"{crypto}/USD")['last']
                binance_price = self.binance.fetch_ticker(f"{crypto}/USDT")['last']
                
                # Calculate spread
                spread = ((gemini_price - binance_price) / binance_price) * 100
                
                # Calculate AGGRESSIVE profit
                gross_profit = self.trade_size * (abs(spread) / 100)
                fees = self.trade_size * 0.002  # 0.2% total
                net_profit = gross_profit - fees
                
                # Check if profitable
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
    
    def execute_aggressive_trade(self, opp):
        """Execute AGGRESSIVE REAL trade"""
        logging.info(f"🎯 EXECUTING AGGRESSIVE TRADE: {opp['crypto']}")
        logging.info(f"   Spread: {opp['spread']:.2f}%")
        logging.info(f"   Expected profit: ${opp['profit']:.2f}")
        logging.info(f"   Trade size: ${self.trade_size}")
        
        try:
            crypto = opp['crypto']
            
            # Calculate trade amount
            buy_amount = self.trade_size / opp['buy_price']
            
            # Step 1: REAL BUY
            logging.info(f"   📈 BUYING {buy_amount:.6f} {crypto} on {opp['buy_exchange']}...")
            
            if opp['buy_exchange'] == 'gemini':
                buy_symbol = f"{crypto}/USD"
                buy_exchange = self.gemini
            else:
                buy_symbol = f"{crypto}/USDT"
                buy_exchange = self.binance
            
            # REAL buy order
            buy_order = buy_exchange.create_market_buy_order(buy_symbol, buy_amount)
            logging.info(f"   ✅ BOUGHT {buy_amount:.6f} {crypto} at ${opp['buy_price']:.2f}")
            
            # Wait for order to fill
            time.sleep(3)
            
            # Step 2: REAL SELL
            logging.info(f"   📉 SELLING {buy_amount:.6f} {crypto} on {opp['sell_exchange']}...")
            
            if opp['sell_exchange'] == 'gemini':
                sell_symbol = f"{crypto}/USD"
                sell_exchange = self.gemini
            else:
                sell_symbol = f"{crypto}/USDT"
                sell_exchange = self.binance
            
            # REAL sell order
            sell_order = sell_exchange.create_market_sell_order(sell_symbol, buy_amount)
            logging.info(f"   ✅ SOLD {buy_amount:.6f} {crypto} at ${opp['sell_price']:.2f}")
            
            # Calculate REAL profit
            buy_cost = buy_order['cost']
            sell_revenue = sell_order['cost']
            actual_profit = sell_revenue - buy_cost
            
            # Update stats
            self.real_trades += 1
            self.real_profit += actual_profit
            
            logging.info(f"   🎉 AGGRESSIVE TRADE COMPLETE!")
            logging.info(f"   💰 REAL Profit: ${actual_profit:.2f}")
            logging.info(f"   📊 Total trades: {self.real_trades}")
            logging.info(f"   📈 Total profit: ${self.real_profit:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"   ❌ Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop - AGGRESSIVE trading"""
        logging.info("=" * 60)
        logging.info("🚀 STARTING AGGRESSIVE TRADING")
        logging.info("💰 USING YOUR $40 SPOT WALLET")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 AGGRESSIVE Scan #{scan_count}")
                
                # Check balance
                balance = self.check_balance()
                
                # Find AGGRESSIVE opportunity
                opp = self.find_aggressive_opportunity()
                
                if opp:
                    logging.info(f"   🎯 Found: {opp['crypto']} - {opp['spread']:.2f}% spread")
                    logging.info(f"      Profit: ${opp['profit']:.2f}")
                    
                    if balance >= self.trade_size:
                        # EXECUTE REAL TRADE
                        self.execute_aggressive_trade(opp)
                    else:
                        logging.warning(f"   ⚠️ Insufficient balance: ${balance:.2f}")
                else:
                    logging.info("   ⏳ No AGGRESSIVE opportunities found")
                
                # Wait between scans
                time.sleep(30)
                
            except KeyboardInterrupt:
                logging.info("🛑 Aggressive trader stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    trader = AggressiveTrader()
    trader.run()