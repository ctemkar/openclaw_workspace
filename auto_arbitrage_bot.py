#!/usr/bin/env python3
"""
Auto Arbitrage Bot - Automatically executes arbitrage trades when spread > 0.5%
Real-time monitoring and execution across multiple cryptos
"""

import os
import sys
import json
import time
import ccxt
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'api_keys.json')

# Cryptos to monitor (liquid pairs on both exchanges)
# Expanded from 10 to 15 cryptos for more opportunities
CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'DOT', 'UNI', 'LINK', 'AVAX', 'DOGE', 'LTC', 'SHIB', 'BCH']

# Trading parameters
MIN_SPREAD_PERCENT = 0.5      # 0.5% minimum spread to trade
MIN_PROFIT_AMOUNT = 1.0       # Minimum $1 profit after fees
TRADE_SIZE_PERCENT = 0.04     # 4% of available capital per trade (INCREASED)
MAX_TRADE_SIZE = 150.0        # Maximum $150 per trade (INCREASED)

# Exchange fees (approximate)
GEMINI_FEE = 0.0010  # 0.10% taker fee
BINANCE_FEE = 0.0010  # 0.10% taker fee

class AutoArbitrageBot:
    def __init__(self):
        """Initialize exchanges and trading parameters"""
        self.exchanges = {}
        self.trade_history = []
        self.total_profit = 0.0
        self.trade_count = 0
        self.initialize_exchanges()
        
    def initialize_exchanges(self):
        """Initialize Gemini and Binance exchanges"""
        try:
            # Load API keys
            with open(CONFIG_FILE, 'r') as f:
                api_keys = json.load(f)
            
            # Initialize Gemini
            self.exchanges['gemini'] = ccxt.gemini({
                'apiKey': api_keys.get('gemini', {}).get('api_key', ''),
                'secret': api_keys.get('gemini', {}).get('api_secret', ''),
                'enableRateLimit': True,
                'options': {'adjustForTimeDifference': True}
            })
            logger.info("✅ Gemini exchange initialized for auto-trading")
            
            # Initialize Binance
            self.exchanges['binance'] = ccxt.binance({
                'apiKey': api_keys.get('binance', {}).get('api_key', ''),
                'secret': api_keys.get('binance', {}).get('api_secret', ''),
                'enableRateLimit': True,
            })
            logger.info("✅ Binance exchange initialized for auto-trading")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize exchanges: {e}")
            raise
    
    def fetch_prices(self, crypto: str) -> Tuple[float, float]:
        """Fetch current prices from both exchanges"""
        try:
            # Gemini price (DOT/USD)
            gemini_symbol = f"{crypto}/USD"
            gemini_ticker = self.exchanges['gemini'].fetch_ticker(gemini_symbol)
            gemini_price = gemini_ticker['last']
            
            # Binance price (DOT/USDT)
            binance_symbol = f"{crypto}/USDT"
            binance_ticker = self.exchanges['binance'].fetch_ticker(binance_symbol)
            binance_price = binance_ticker['last']
            
            return gemini_price, binance_price
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch prices for {crypto}: {e}")
            return 0.0, 0.0
    
    def calculate_arbitrage_opportunity(self, crypto: str) -> Optional[Dict]:
        """Calculate arbitrage opportunity for a crypto"""
        gemini_price, binance_price = self.fetch_prices(crypto)
        
        if gemini_price <= 0 or binance_price <= 0:
            return None
        
        # Calculate spread percentage
        if gemini_price > binance_price:
            # Gemini is more expensive - buy on Binance, sell on Gemini
            spread_percent = ((gemini_price - binance_price) / binance_price) * 100
            direction = "binance_to_gemini"
            buy_exchange = 'binance'
            sell_exchange = 'gemini'
            buy_price = binance_price
            sell_price = gemini_price
        else:
            # Binance is more expensive - buy on Gemini, sell on Binance
            spread_percent = ((binance_price - gemini_price) / gemini_price) * 100
            direction = "gemini_to_binance"
            buy_exchange = 'gemini'
            sell_exchange = 'binance'
            buy_price = gemini_price
            sell_price = binance_price
        
        # Check if spread meets minimum threshold
        if spread_percent < MIN_SPREAD_PERCENT:
            return None
        
        # DYNAMIC TRADE SIZING BASED ON SPREAD
        # Larger spreads = larger trades (more profit, less risk)
        if spread_percent >= 1.0:
            # 1.0%+ spread: Use larger trade size
            trade_multiplier = 1.5
            min_profit = 2.0  # Require $2 profit for larger trades
        elif spread_percent >= 0.75:
            # 0.75-1.0% spread: Medium trade size
            trade_multiplier = 1.2
            min_profit = 1.5
        else:
            # 0.5-0.75% spread: Standard trade size
            trade_multiplier = 1.0
            min_profit = MIN_PROFIT_AMOUNT
        
        # Estimate available capital
        available_capital = 100.0  # Increased from $50
        
        # Calculate trade size with dynamic scaling
        base_trade_size = available_capital * TRADE_SIZE_PERCENT
        trade_size = min(base_trade_size * trade_multiplier, MAX_TRADE_SIZE)
        
        if trade_size < 10.0:  # Minimum $10 trade
            return None
        
        # Calculate profit after fees
        crypto_amount = trade_size / buy_price
        sell_value = crypto_amount * sell_price
        
        # Apply fees
        buy_fee = trade_size * (GEMINI_FEE if buy_exchange == 'gemini' else BINANCE_FEE)
        sell_fee = sell_value * (BINANCE_FEE if sell_exchange == 'binance' else GEMINI_FEE)
        
        total_fees = buy_fee + sell_fee
        net_profit = sell_value - trade_size - total_fees
        
        # Check if profit meets dynamic minimum threshold
        if net_profit < min_profit:
            return None
        
        # Return arbitrage opportunity
        return {
            'crypto': crypto,
            'direction': direction,
            'buy_exchange': buy_exchange,
            'sell_exchange': sell_exchange,
            'spread_percent': round(spread_percent, 3),
            'buy_price': round(buy_price, 4),
            'sell_price': round(sell_price, 4),
            'trade_size': round(trade_size, 2),
            'crypto_amount': round(crypto_amount, 4),
            'net_profit': round(net_profit, 2),
            'profit_percent': round((net_profit / trade_size) * 100, 3),
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_arbitrage(self, opportunity: Dict) -> bool:
        """Execute an arbitrage trade"""
        crypto = opportunity['crypto']
        direction = opportunity['direction']
        
        logger.info(f"🚀 EXECUTING AUTO-ARBITRAGE: {crypto}")
        logger.info(f"   Spread: {opportunity['spread_percent']}%")
        logger.info(f"   Trade: ${opportunity['trade_size']}")
        logger.info(f"   Expected profit: ${opportunity['net_profit']}")
        
        try:
            if direction == "binance_to_gemini":
                # Buy on Binance, sell on Gemini
                # 1. Buy on Binance
                binance_symbol = f"{crypto}/USDT"
                binance_order = self.exchanges['binance'].create_order(
                    symbol=binance_symbol,
                    type='market',
                    side='buy',
                    amount=opportunity['crypto_amount']
                )
                logger.info(f"✅ Binance BUY order: {binance_order['id']}")
                
                # Small delay between exchanges
                time.sleep(1)
                
                # 2. Sell on Gemini
                gemini_symbol = f"{crypto}/USD"
                gemini_order = self.exchanges['gemini'].create_order(
                    symbol=gemini_symbol,
                    type='market',
                    side='sell',
                    amount=opportunity['crypto_amount']
                )
                logger.info(f"✅ Gemini SELL order: {gemini_order['id']}")
                
            else:  # gemini_to_binance
                # Buy on Gemini, sell on Binance
                # 1. Buy on Gemini
                gemini_symbol = f"{crypto}/USD"
                gemini_order = self.exchanges['gemini'].create_order(
                    symbol=gemini_symbol,
                    type='market',
                    side='buy',
                    amount=opportunity['crypto_amount']
                )
                logger.info(f"✅ Gemini BUY order: {gemini_order['id']}")
                
                # Small delay between exchanges
                time.sleep(1)
                
                # 2. Sell on Binance
                binance_symbol = f"{crypto}/USDT"
                binance_order = self.exchanges['binance'].create_order(
                    symbol=binance_symbol,
                    type='market',
                    side='sell',
                    amount=opportunity['crypto_amount']
                )
                logger.info(f"✅ Binance SELL order: {binance_order['id']}")
            
            # Record successful trade
            self.record_trade(opportunity, success=True)
            self.total_profit += opportunity['net_profit']
            self.trade_count += 1
            
            logger.info(f"🎉 ARBITRAGE COMPLETED: ${opportunity['net_profit']} profit")
            logger.info(f"💰 Total profit: ${self.total_profit:.2f} ({self.trade_count} trades)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Arbitrage execution failed: {e}")
            self.record_trade(opportunity, success=False, error=str(e))
            return False
    
    def record_trade(self, opportunity: Dict, success: bool, error: str = None):
        """Record trade in history"""
        trade_record = {
            **opportunity,
            'success': success,
            'error': error,
            'execution_time': datetime.now().isoformat()
        }
        
        self.trade_history.append(trade_record)
        
        # Save to file
        trades_file = os.path.join(BASE_DIR, 'trading_data', 'auto_arbitrage_trades.json')
        os.makedirs(os.path.dirname(trades_file), exist_ok=True)
        
        # Load existing trades
        trades = []
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                try:
                    trades = json.load(f)
                except:
                    trades = []
        
        # Add new trade
        trades.append(trade_record)
        
        # Save back
        with open(trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
        
        logger.info(f"📝 Trade recorded: {trade_record['crypto']} {'✅' if success else '❌'}")
    
    def monitor_and_trade(self):
        """Main monitoring and trading loop"""
        logger.info("=" * 70)
        logger.info("🤖 AUTO ARBITRAGE BOT STARTED")
        logger.info(f"Monitoring {len(CRYPTOS)} cryptos")
        logger.info(f"Min spread: {MIN_SPREAD_PERCENT}%")
        logger.info(f"Min profit: ${MIN_PROFIT_AMOUNT}")
        logger.info(f"Trade size: {TRADE_SIZE_PERCENT*100}% of capital")
        logger.info("=" * 70)
        
        cycle = 0
        
        while True:
            cycle += 1
            logger.info(f"\n🔄 AUTO-ARBITRAGE CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                # Find all arbitrage opportunities
                opportunities = []
                for crypto in CRYPTOS:
                    opportunity = self.calculate_arbitrage_opportunity(crypto)
                    if opportunity:
                        opportunities.append(opportunity)
                
                # Log current market status
                logger.info("📊 Market Status:")
                top_cryptos = ['BTC', 'ETH', 'DOT']  # Log top 3
                for crypto in top_cryptos:
                    gemini_price, binance_price = self.fetch_prices(crypto)
                    if gemini_price > 0 and binance_price > 0:
                        spread = abs(gemini_price - binance_price) / min(gemini_price, binance_price) * 100
                        logger.info(f"  {crypto}: G=${gemini_price:.2f}, B=${binance_price:.2f}, Spread={spread:.2f}%")
                
                # Execute best opportunity if found
                if opportunities:
                    # Sort by profit percentage (descending)
                    opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
                    best_opportunity = opportunities[0]
                    
                    logger.info(f"🎯 Found {len(opportunities)} arbitrage opportunities")
                    logger.info(f"Best: {best_opportunity['crypto']} - {best_opportunity['profit_percent']}% profit (${best_opportunity['net_profit']})")
                    
                    # Execute the best opportunity
                    self.execute_arbitrage(best_opportunity)
                else:
                    logger.info("⏳ No profitable arbitrage opportunities found")
                
                # Performance summary
                if self.trade_count > 0:
                    logger.info(f"\n💰 PERFORMANCE SUMMARY:")
                    logger.info(f"   Total trades: {self.trade_count}")
                    logger.info(f"   Total profit: ${self.total_profit:.2f}")
                    logger.info(f"   Avg profit/trade: ${self.total_profit/self.trade_count:.2f}")
                
                # Intelligent scanning based on time
                current_hour = datetime.now().hour
                
                # Adjust scan frequency based on market hours
                if 13 <= current_hour <= 21:  # US/EU overlap (high volume)
                    scan_delay = 20  # Scan more frequently
                    logger.info(f"🌍 High volume hours: Next scan in {scan_delay} seconds...")
                elif 22 <= current_hour or current_hour <= 4:  # Asia hours
                    scan_delay = 40  # Scan less frequently
                    logger.info(f"🌏 Asia hours: Next scan in {scan_delay} seconds...")
                else:
                    scan_delay = 30  # Standard
                    logger.info(f"💤 Next scan in {scan_delay} seconds...")
                
                time.sleep(scan_delay)
                
            except Exception as e:
                logger.error(f"❌ Error in arbitrage cycle: {e}")
                time.sleep(60)  # Wait longer on error

def main():
    """Main function"""
    bot = AutoArbitrageBot()
    
    try:
        bot.monitor_and_trade()
    except KeyboardInterrupt:
        logger.info("👋 Auto arbitrage bot stopped by user")
        logger.info(f"💰 Final profit: ${bot.total_profit:.2f} ({bot.trade_count} trades)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()