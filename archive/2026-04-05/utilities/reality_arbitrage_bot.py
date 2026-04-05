#!/usr/bin/env python3
"""
REALITY ARBITRAGE BOT - Works with what you ACTUALLY have
- Checks REAL balances
- Uses whatever money is available
- Actually executes trades with REAL money
"""

import ccxt
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reality_arbitrage_trades.log'),
        logging.StreamHandler()
    ]
)

class RealityArbitrageBot:
    def __init__(self):
        logging.info("🚀 REALITY ARBITRAGE BOT STARTING")
        logging.info("💰 Uses whatever money you ACTUALLY have!")
        
        # Load API keys
        self.keys = self.load_keys()
        
        # Initialize exchanges
        self.binance = ccxt.binance({
            'apiKey': self.keys.get('BINANCE_API_KEY', ''),
            'secret': self.keys.get('BINANCE_API_SECRET', ''),
            'enableRateLimit': True
        })
        
        # Gemini with VERY long delays
        self.gemini = ccxt.gemini({
            'apiKey': self.keys.get('GEMINI_API_KEY', ''),
            'secret': self.keys.get('GEMINI_API_SECRET', ''),
            'enableRateLimit': True,
            'nonce': lambda: int(time.time() * 1000) + 1000000  # Large offset
        })
        
        # REAL trading parameters
        self.min_spread = 0.8  # 0.8% minimum (higher threshold)
        self.min_profit = 0.20  # $0.20 minimum profit
        
        # Track REAL trades
        self.real_trades = 0
        self.real_profit = 0.0
        
        # Cryptos
        self.cryptos = ['MANA', 'ARB', 'GALA']
        
        logging.info(f"📊 REALITY Trading:")
        logging.info(f"   Min spread: {self.min_spread}%")
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
    
    def check_real_balances(self):
        """Check what you ACTUALLY have"""
        try:
            logging.info("💰 Checking REAL balances...")
            
            # Check Binance
            binance_balance = self.binance.fetch_balance()
            binance_usdt = binance_balance.get('USDT', {}).get('free', 0)
            
            # Check what cryptos you have on Binance
            binance_cryptos = {}
            for crypto in self.cryptos:
                amount = binance_balance.get(crypto, {}).get('free', 0)
                if amount > 0:
                    binance_cryptos[crypto] = amount
            
            logging.info(f"   Binance USDT: ${binance_usdt:.2f}")
            if binance_cryptos:
                for crypto, amount in binance_cryptos.items():
                    logging.info(f"   Binance {crypto}: {amount:.2f}")
            
            # Try Gemini (with error handling)
            gemini_usd = 0
            try:
                # VERY long delay for Gemini
                time.sleep(40)
                gemini_balance = self.gemini.fetch_balance()
                gemini_usd = gemini_balance.get('USD', {}).get('free', 0)
                logging.info(f"   Gemini USD: ${gemini_usd:.2f}")
            except Exception as e:
                logging.warning(f"   Gemini error: {e}")
                gemini_usd = 0
            
            return {
                'binance_usdt': binance_usdt,
                'binance_cryptos': binance_cryptos,
                'gemini_usd': gemini_usd
            }
            
        except Exception as e:
            logging.error(f"❌ Balance error: {e}")
            return {'binance_usdt': 0, 'binance_cryptos': {}, 'gemini_usd': 0}
    
    def find_reality_opportunity(self, balances):
        """Find opportunity with what you ACTUALLY have"""
        try:
            # Check MANA first (most likely)
            gemini_price = 0
            binance_price = 0
            
            # Get Binance price
            try:
                binance_ticker = self.binance.fetch_ticker('MANA/USDT')
                binance_price = binance_ticker['last']
            except:
                pass
            
            # Get Gemini price (with long delay)
            try:
                time.sleep(5)
                gemini_ticker = self.gemini.fetch_ticker('MANA/USD')
                gemini_price = gemini_ticker['last']
            except:
                pass
            
            if gemini_price > 0 and binance_price > 0:
                spread = ((gemini_price - binance_price) / binance_price) * 100
                
                # Determine what we can trade
                if gemini_price > binance_price and balances['binance_usdt'] >= 10:
                    # Buy on Binance, sell on Gemini
                    trade_size = min(balances['binance_usdt'], 20.0)
                    gross_profit = trade_size * (abs(spread) / 100)
                    fees = trade_size * 0.002
                    net_profit = gross_profit - fees
                    
                    if abs(spread) >= self.min_spread and net_profit >= self.min_profit:
                        return {
                            'crypto': 'MANA',
                            'spread': abs(spread),
                            'profit': net_profit,
                            'direction': 'BUY_BINANCE_SELL_GEMINI',
                            'trade_size': trade_size,
                            'buy_price': binance_price,
                            'sell_price': gemini_price
                        }
                
                elif binance_price > gemini_price and balances['gemini_usd'] >= 10:
                    # Buy on Gemini, sell on Binance
                    trade_size = min(balances['gemini_usd'], 20.0)
                    gross_profit = trade_size * (abs(spread) / 100)
                    fees = trade_size * 0.002
                    net_profit = gross_profit - fees
                    
                    if abs(spread) >= self.min_spread and net_profit >= self.min_profit:
                        return {
                            'crypto': 'MANA',
                            'spread': abs(spread),
                            'profit': net_profit,
                            'direction': 'BUY_GEMINI_SELL_BINANCE',
                            'trade_size': trade_size,
                            'buy_price': gemini_price,
                            'sell_price': binance_price
                        }
            
            return None
            
        except Exception as e:
            logging.error(f"Opportunity check error: {e}")
            return None
    
    def execute_reality_trade(self, opportunity):
        """Execute trade with what we ACTUALLY have"""
        logging.info(f"🎯 EXECUTING REALITY TRADE!")
        logging.info(f"   Crypto: {opportunity['crypto']}")
        logging.info(f"   Spread: {opportunity['spread']:.2f}%")
        logging.info(f"   Expected profit: ${opportunity['profit']:.2f}")
        
        try:
            crypto = opportunity['crypto']
            trade_amount = opportunity['trade_size'] / opportunity['buy_price']
            
            # Step 1: BUY
            logging.info(f"   📈 BUYING {trade_amount:.2f} {crypto}...")
            
            if opportunity['direction'] == 'BUY_BINANCE_SELL_GEMINI':
                # Buy on Binance
                buy_order = self.binance.create_market_buy_order('MANA/USDT', trade_amount)
                logging.info(f"   ✅ BOUGHT on Binance at ${opportunity['buy_price']:.4f}")
                
                # Wait
                time.sleep(3)
                
                # Try to sell on Gemini (might fail due to nonce)
                try:
                    time.sleep(30)  # Long delay for Gemini
                    sell_order = self.gemini.create_limit_sell_order('MANA/USD', trade_amount, opportunity['sell_price'] * 0.999)
                    logging.info(f"   ✅ SOLD on Gemini at ${opportunity['sell_price']:.4f}")
                    
                    # Calculate profit
                    actual_profit = float(sell_order.get('cost', 0)) - float(buy_order.get('cost', 0))
                    
                except Exception as e:
                    logging.warning(f"   Gemini sell failed: {e}")
                    # Sell back on Binance to avoid loss
                    sell_order = self.binance.create_market_sell_order('MANA/USDT', trade_amount)
                    actual_profit = float(sell_order.get('cost', 0)) - float(buy_order.get('cost', 0))
                    logging.info(f"   Sold back on Binance, P&L: ${actual_profit:.2f}")
            
            else:
                # Buy on Gemini (might fail)
                try:
                    time.sleep(30)
                    buy_order = self.gemini.create_limit_buy_order('MANA/USD', trade_amount, opportunity['buy_price'] * 1.001)
                    logging.info(f"   ✅ BOUGHT on Gemini at ${opportunity['buy_price']:.4f}")
                    
                    # Sell on Binance
                    time.sleep(3)
                    sell_order = self.binance.create_market_sell_order('MANA/USDT', trade_amount)
                    logging.info(f"   ✅ SOLD on Binance at ${opportunity['sell_price']:.4f}")
                    
                    actual_profit = float(sell_order.get('cost', 0)) - float(buy_order.get('cost', 0))
                    
                except Exception as e:
                    logging.error(f"   Gemini buy failed: {e}")
                    return False
            
            # Update stats
            self.real_trades += 1
            self.real_profit += actual_profit
            
            logging.info(f"   🎉 REALITY TRADE COMPLETE!")
            logging.info(f"   💰 Actual profit: ${actual_profit:.2f}")
            logging.info(f"   📊 Total trades: {self.real_trades}")
            
            # Log to file
            with open('reality_profits.log', 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {crypto} - Profit: ${actual_profit:.2f}\n")
            
            return True
            
        except Exception as e:
            logging.error(f"   ❌ Trade failed: {e}")
            return False
    
    def run(self):
        """Main loop - WORKS WITH REALITY"""
        logging.info("=" * 60)
        logging.info("🚀 REALITY ARBITRAGE BOT - USING WHAT YOU HAVE")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                logging.info(f"🔍 Reality Scan #{scan_count}")
                
                # Check REAL balances
                balances = self.check_real_balances()
                
                # Find opportunity with what we have
                opportunity = self.find_reality_opportunity(balances)
                
                if opportunity:
                    logging.info(f"   🎯 Found: {opportunity['crypto']} - {opportunity['spread']:.2f}%")
                    logging.info(f"      Profit: ${opportunity['profit']:.2f}")
                    
                    # EXECUTE REALITY TRADE
                    self.execute_reality_trade(opportunity)
                else:
                    logging.info("   ⏳ No reality opportunities")
                
                # Wait
                logging.info("   ⏳ Waiting 90 seconds...")
                time.sleep(90)
                
            except KeyboardInterrupt:
                logging.info("🛑 Reality bot stopped")
                break
            except Exception as e:
                logging.error(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = RealityArbitrageBot()
    bot.run()