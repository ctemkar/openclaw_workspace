#!/usr/bin/env python3
"""
PROPER Trading Bot - Uses EXACT .env variable names
- GEMINI_API_KEY, GEMINI_API_SECRET
- BINANCE_API_KEY, BINANCE_API_SECRET
- Actually executes trades when spread > 0.4%
"""

import ccxt
import time
import logging
import json
from datetime import datetime
from typing import Dict, Optional
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('proper_trading.log'),
        logging.StreamHandler()
    ]
)

class ProperTradingBot:
    def __init__(self):
        # Load API keys from .env file
        self.api_keys = self.load_api_keys_from_env()
        
        # Initialize exchanges with API keys
        self.exchanges = {
            'gemini': ccxt.gemini({
                'apiKey': self.api_keys.get('gemini_api_key', ''),
                'secret': self.api_keys.get('gemini_secret', ''),
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }),
            'binance': ccxt.binance({
                'apiKey': self.api_keys.get('binance_api_key', ''),
                'secret': self.api_keys.get('binance_secret', ''),
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        }
        
        # Trading parameters
        self.min_spread = 0.4  # 0.4% minimum spread
        self.trade_size_usd = 50.0  # Start small: $50 per trade
        self.max_position_usd = 200.0  # Max $200 total exposure
        self.min_profit_usd = 0.10  # $0.10 minimum profit after fees
        
        # Track trades
        self.trades_executed = 0
        self.total_profit = 0.0
        self.current_positions = {}
        
        # Cryptos that have shown opportunities
        self.supported_cryptos = ['ARB', 'GALA', 'XTZ', 'MANA', 'BTC', 'ETH', 'SOL', 'XRP']
        
        logging.info("🚀 PROPER Trading Bot Initialized")
        logging.info(f"📊 Trading parameters:")
        logging.info(f"   Min spread: {self.min_spread}%")
        logging.info(f"   Trade size: ${self.trade_size_usd}")
        logging.info(f"   Min profit: ${self.min_profit_usd}")
        
        # Check API keys
        if self.has_valid_api_keys():
            logging.info("✅ API KEYS LOADED - READY FOR REAL TRADING!")
        else:
            logging.warning("⚠️ API keys issue - will run in SIMULATION mode")
    
    def load_api_keys_from_env(self) -> Dict:
        """Load API keys directly from .env file"""
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
            logging.error(f"Error reading .env: {e}")
        
        # Map to expected format
        return {
            'gemini_api_key': keys.get('GEMINI_API_KEY', ''),
            'gemini_secret': keys.get('GEMINI_API_SECRET', ''),
            'binance_api_key': keys.get('BINANCE_API_KEY', ''),
            'binance_secret': keys.get('BINANCE_API_SECRET', '')
        }
    
    def has_valid_api_keys(self) -> bool:
        """Check if we have valid API keys"""
        return all([
            self.api_keys.get('gemini_api_key'),
            self.api_keys.get('gemini_secret'),
            self.api_keys.get('binance_api_key'),
            self.api_keys.get('binance_secret')
        ])
    
    def check_balances(self) -> Dict:
        """Check available balances on exchanges"""
        balances = {}
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                balance = exchange.fetch_balance()
                if exchange_name == 'gemini':
                    usd_balance = balance.get('USD', {}).get('free', 0)
                    logging.info(f"   GEMINI: ${usd_balance:.2f} USD available")
                else:  # binance
                    usd_balance = balance.get('USDT', {}).get('free', 0)
                    logging.info(f"   BINANCE: ${usd_balance:.2f} USDT available")
                
                balances[exchange_name] = {
                    'usd': usd_balance,
                    'total': balance.get('total', {})
                }
            except Exception as e:
                logging.error(f"   ❌ Error checking {exchange_name} balance: {e}")
                balances[exchange_name] = {'usd': 0, 'total': {}}
        
        return balances
    
    def get_price(self, exchange_name: str, crypto: str) -> Optional[float]:
        """Get current price from exchange"""
        try:
            exchange = self.exchanges[exchange_name]
            
            if exchange_name == 'gemini':
                symbol = f"{crypto}/USD"
            else:  # binance
                symbol = f"{crypto}/USDT"
            
            ticker = exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logging.debug(f"   Can't get {crypto} price from {exchange_name}: {e}")
            return None
    
    def calculate_arbitrage(self, crypto: str) -> Optional[Dict]:
        """Calculate arbitrage opportunity for a crypto"""
        gemini_price = self.get_price('gemini', crypto)
        binance_price = self.get_price('binance', crypto)
        
        if not gemini_price or not binance_price:
            return None
        
        # Calculate spread
        spread = ((gemini_price - binance_price) / binance_price) * 100
        
        # Calculate profit
        gross_profit = self.trade_size_usd * (abs(spread) / 100)
        fees = self.trade_size_usd * 0.002  # 0.1% each side
        net_profit = gross_profit - fees
        
        # Determine direction
        if gemini_price > binance_price:
            direction = "BUY Binance, SELL Gemini"
            buy_exchange = 'binance'
            sell_exchange = 'gemini'
            buy_price = binance_price
            sell_price = gemini_price
        else:
            direction = "BUY Gemini, SELL Binance"
            buy_exchange = 'gemini'
            sell_exchange = 'binance'
            buy_price = gemini_price
            sell_price = binance_price
        
        if abs(spread) >= self.min_spread and net_profit >= self.min_profit_usd:
            return {
                'crypto': crypto,
                'spread': abs(spread),
                'net_profit': net_profit,
                'direction': direction,
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'trade_size': self.trade_size_usd,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
        
        return None
    
    def execute_trade(self, opportunity: Dict) -> bool:
        """Execute an arbitrage trade"""
        logging.info(f"🎯 EXECUTING TRADE: {opportunity['crypto']}")
        logging.info(f"   Spread: {opportunity['spread']:.2f}%")
        logging.info(f"   Expected profit: ${opportunity['net_profit']:.2f}")
        logging.info(f"   Strategy: {opportunity['direction']}")
        
        # Check if we have valid API keys
        if not self.has_valid_api_keys():
            logging.warning("   ⚠️ SIMULATION MODE: No valid API keys, skipping execution")
            logging.info(f"   📝 Would execute: Buy {opportunity['crypto']} on {opportunity['buy_exchange']}")
            logging.info(f"   📝 Would execute: Sell {opportunity['crypto']} on {opportunity['sell_exchange']}")
            logging.info(f"   💰 Simulated profit: ${opportunity['net_profit']:.2f}")
            return True  # Return True for simulation
        
        try:
            # Get exchanges
            buy_exchange = self.exchanges[opportunity['buy_exchange']]
            sell_exchange = self.exchanges[opportunity['sell_exchange']]
            
            crypto = opportunity['crypto']
            
            # Calculate trade amount
            if opportunity['buy_exchange'] == 'gemini':
                # Buy on Gemini (USD)
                buy_symbol = f"{crypto}/USD"
                buy_amount = opportunity['trade_size'] / opportunity['buy_price']
            else:
                # Buy on Binance (USDT)
                buy_symbol = f"{crypto}/USDT"
                buy_amount = opportunity['trade_size'] / opportunity['buy_price']
            
            # Execute BUY order
            logging.info(f"   📈 Placing BUY order on {opportunity['buy_exchange']}...")
            buy_order = buy_exchange.create_market_buy_order(buy_symbol, buy_amount)
            logging.info(f"   ✅ Bought {buy_amount:.6f} {crypto} at ${opportunity['buy_price']:.2f}")
            
            # Small delay between orders
            time.sleep(1)
            
            # Execute SELL order
            logging.info(f"   📉 Placing SELL order on {opportunity['sell_exchange']}...")
            if opportunity['sell_exchange'] == 'gemini':
                sell_symbol = f"{crypto}/USD"
            else:
                sell_symbol = f"{crypto}/USDT"
            
            sell_order = sell_exchange.create_market_sell_order(sell_symbol, buy_amount)
            logging.info(f"   ✅ Sold {buy_amount:.6f} {crypto} at ${opportunity['sell_price']:.2f}")
            
            # Calculate actual profit
            buy_cost = buy_order['cost']
            sell_revenue = sell_order['cost']
            actual_profit = sell_revenue - buy_cost
            
            # Update stats
            self.trades_executed += 1
            self.total_profit += actual_profit
            
            logging.info(f"   🎉 TRADE COMPLETE!")
            logging.info(f"   💰 Actual profit: ${actual_profit:.2f}")
            logging.info(f"   📊 Total trades: {self.trades_executed}")
            logging.info(f"   📈 Total profit: ${self.total_profit:.2f}")
            
            return True
            
        except Exception as e:
            logging.error(f"   ❌ Trade execution failed: {e}")
            return False
    
    def run_scan(self):
        """Run a single scan and execute trades if profitable"""
        logging.info(f"🔍 Scan #{self.trades_executed + 1}: Checking {len(self.supported_cryptos)} cryptos")
        
        # Check balances
        balances = self.check_balances()
        
        # Scan each crypto
        opportunities_found = 0
        for crypto in self.supported_cryptos:
            opportunity = self.calculate_arbitrage(crypto)
            
            if opportunity:
                opportunities_found += 1
                logging.info(f"   🎯 Found opportunity: {crypto} - {opportunity['spread']:.2f}% spread")
                logging.info(f"      Profit: ${opportunity['net_profit']:.2f}")
                logging.info(f"      Strategy: {opportunity['direction']}")
                
                # Check if we have enough balance
                buy_exchange_balance = balances[opportunity['buy_exchange']]['usd']
                if buy_exchange_balance >= opportunity['trade_size']:
                    # Execute trade
                    success = self.execute_trade(opportunity)
                    if success:
                        # Wait a bit after successful trade
                        time.sleep(5)
                else:
                    logging.warning(f"   ⚠️ Insufficient balance on {opportunity['buy_exchange']}")
                    logging.warning(f"      Need: ${opportunity['trade_size']:.2f}, Have: ${buy_exchange_balance:.2f}")
            else:
                logging.debug(f"   ⏳ {crypto}: No profitable opportunity")
        
        if opportunities_found == 0:
            logging.info("   ⏳ No profitable opportunities found this scan")
    
    def run(self):
        """Main bot loop"""
        logging.info("=" * 60)
        logging.info("🚀 STARTING PROPER TRADING BOT")
        logging.info("=" * 60)
        logging.info("📊 Uses EXACT .env variable names:")
        logging.info("   • GEMINI_API_KEY, GEMINI_API_SECRET")
        logging.info("   • BINANCE_API_KEY, BINANCE_API_SECRET")
        logging.info("=" * 60)
        
        scan_count = 0
        while True:
            try:
                scan_count += 1
                self.run_scan()
                
                # Show summary every 10 scans
                if scan_count % 10 == 0:
                    logging.info(f"📊 SUMMARY: {scan_count} scans, {self.trades_executed} trades")
                    logging.info(f"💰 Total profit: ${self.total_profit:.2f}")
                
                # Wait between scans
                time.sleep(30)  # Scan every 30 seconds
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = ProperTradingBot()
    bot.run()