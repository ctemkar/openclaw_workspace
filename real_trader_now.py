#!/usr/bin/env python3
"""
REAL TRADER NOW - No simulation, real trades only
- Actually executes trades with your money
- No bullshit, no simulation
- Real mode from the start
"""

import ccxt
import time
import logging
import os

# Configure logging - REAL TRADES ONLY
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_trades.log'),
        logging.StreamHandler()
    ]
)

class RealTraderNow:
    def __init__(self):
        logging.info("🚀 REAL TRADER NOW - STARTING")
        logging.info("💰 NO SIMULATION - REAL TRADES ONLY")
        
        # Load REAL API keys
        self.keys = self.load_real_keys()
        
        # Initialize exchanges with REAL keys
        self.gemini = ccxt.gemini({
            'apiKey': self.keys.get('GEMINI_API_KEY', ''),
            'secret': self.keys.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
            'nonce': lambda: int(time.time() * 1000)  # Proper nonce
        })
        
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        # REAL trading parameters
        self.min_spread = 0.4  # 0.4% minimum
        self.trade_size = 10.0  # Start with $10 REAL trades
        self.min_profit = 0.10  # $0.10 minimum profit
        
        # Track REAL trades
        self.real_trades = 0
        self.real_profit = 0.0
        
        # Cryptos to trade
        self.cryptos = ['MANA', 'ARB', 'GALA', 'BTC', 'ETH', 'SOL']
        
        logging.info(f"📊 REAL Trading: {len(self.cryptos)} cryptos")
        logging.info(f"   Min spread: {self.min_spread}%")
        logging.info(f"   Trade size: ${self.trade_size}")
        logging.info(f"   Min profit: ${self.min_profit}")
    
    def load_real_keys(self):
        """Load REAL API keys"""
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
            logging.error(f"❌ Error loading keys: {e}")
        return keys
    
    def check_real_balances(self):
        """Check REAL balances"""
        try:
            # Check Binance first (no nonce issues)
            binance_bal = self.binance.fetch_balance()
            binance_usdt = binance_bal.get('USDT', {}).get('free', 0)
            logging.info(f"💰 Binance REAL Balance: ${binance_usdt:.2f}")
            
            # Check Gemini with delay
            time.sleep(5)  # Wait 5 seconds for nonce
            gemini_bal = self.gemini.fetch_balance()
            gemini_usd = gemini_bal.get('USD', {}).get('free', 0)
            logging.info(f"💰 Gemini REAL Balance: ${gemini_usd:.2f}")
            
            return gemini_usd, binance_usdt
            
        except Exception as e:
            logging.error(f"❌ Balance check error: {e}")
            return 0, 0
    
    def find_real_opportunity(self):
        """Find REAL arbitrage opportunity"""
        for crypto in self.cryptos:
            try:
                # Get REAL prices
                time.sleep(1)  # Rate limiting
                gemini_ticker = self.gemini.fetch_ticker(f"{crypto}/USD")
                binance_ticker = self.binance.fetch_ticker(f"{crypto}/USDT")
                
                gemini_price = gemini_ticker['last']
                binance_price = binance_ticker['last']
                
                # Calculate REAL spread
                spread = ((gemini_price - binance_price) / binance_price) * 100
                
                # Calculate REAL profit
                profit = self.trade_size * (abs(spread) / 100) - (self.trade_size * 0.002)
                
                if abs(spread) >= self.min_spread and profit >= self.min_profit:
                    # Determine direction
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
    
    def execute_real_trade(self, opp):
        """Execute REAL trade with REAL money"""
        logging.info(f"🎯 EXECUTING REAL TRADE: {opp['crypto']}")
        logging.info(f"   Spread: {opp['spread']:.2f}%")
        logging.info(f"   Expected profit: ${opp['profit']:.2f}")
        logging.info(f"   Strategy: BUY {opp['buy_exchange']}, SELL {opp['sell_exchange']}")
        
        try:
            crypto = opp['crypto']
            
            # Calculate REAL trade amount
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
            
            # Update REAL stats
            self.real_trades += 1
            self.real_profit += actual_profit
            
            logging.info(f"   🎉 REAL TRADE COMPLETE!")
            logging.info(f"   💰 REAL Profit: ${actual_profit:.2f}")
            logging.info(f"   📊 Total REAL trades: {self.real_trades}")
            logging.info(f"   📈 Total REAL profit: ${self.real_profit:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"   ❌ REAL Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop - REAL trading only"""
        logging.info("=" * 60)
        logging.info("🚀 STARTING REAL TRADING - NO SIMULATION")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 REAL Scan #{scan_count}")
                
                # Check REAL balances
                gemini_bal, binance_bal = self.check_real_balances()
                
                # Find REAL opportunity
                opp = self.find_real_opportunity()
                
                if opp:
                    # Check if we have REAL money
                    if opp['buy_exchange'] == 'gemini' and gemini_bal >= self.trade_size:
                        self.execute_real_trade(opp)
                    elif opp['buy_exchange'] == 'binance' and binance_bal >= self.trade_size:
                        self.execute_real_trade(opp)
                    else:
                        logging.warning(f"   ⚠️ Not enough REAL money for trade")
                else:
                    logging.info("   ⏳ No REAL opportunities found")
                
                # Wait between REAL scans
                time.sleep(30)
                
            except KeyboardInterrupt:
                logging.info("🛑 REAL Trader stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    trader = RealTraderNow()
    trader.run()