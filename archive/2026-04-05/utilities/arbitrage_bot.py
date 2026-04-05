#!/usr/bin/env python3
"""
Arbitrage Bot - Finds price differences between Gemini and Binance
Real-time monitoring and execution of arbitrage opportunities
"""

import os
import sys
import json
import time
import ccxt
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'api_keys.json')

# Cryptos to monitor (common to both exchanges)
CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'UNI', 'LINK', 'MATIC', 'AVAX']

# Arbitrage thresholds
MIN_SPREAD_PERCENT = 0.5  # 0.5% minimum spread to consider arbitrage
MIN_PROFIT_AMOUNT = 1.0   # Minimum $1 profit after fees
MAX_POSITION_SIZE = 50.0  # Maximum $50 per arbitrage trade (due to low Binance balance)

# Exchange fees (approximate)
GEMINI_FEE = 0.0010  # 0.10% taker fee
BINANCE_FEE = 0.0010  # 0.10% taker fee

class ArbitrageBot:
    def __init__(self):
        """Initialize exchanges and load API keys"""
        self.exchanges = {}
        self.balances = {}
        self.last_prices = {}
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
                'options': {
                    'defaultType': 'spot',
                }
            })
            logger.info("✅ Gemini exchange initialized")
            
            # Initialize Binance
            self.exchanges['binance'] = ccxt.binance({
                'apiKey': api_keys.get('binance', {}).get('api_key', ''),
                'secret': api_keys.get('binance', {}).get('api_secret', ''),
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            logger.info("✅ Binance exchange initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize exchanges: {e}")
            raise
    
    async def fetch_prices(self, crypto: str) -> Dict[str, float]:
        """Fetch current prices from both exchanges for a crypto"""
        prices = {}
        symbol = f"{crypto}/USD"
        
        try:
            # Fetch Gemini price
            gemini_ticker = self.exchanges['gemini'].fetch_ticker(symbol)
            prices['gemini'] = gemini_ticker['last']
            
            # Fetch Binance price (USDT instead of USD)
            binance_symbol = f"{crypto}/USDT"
            binance_ticker = self.exchanges['binance'].fetch_ticker(binance_symbol)
            prices['binance'] = binance_ticker['last']
            
            # Store last prices
            self.last_prices[crypto] = prices
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch prices for {crypto}: {e}")
            prices = {'gemini': 0, 'binance': 0}
            
        return prices
    
    async def fetch_all_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch prices for all cryptos concurrently"""
        all_prices = {}
        
        # Create tasks for all cryptos
        tasks = []
        for crypto in CRYPTOS:
            tasks.append(self.fetch_prices(crypto))
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, crypto in enumerate(CRYPTOS):
            if isinstance(results[i], dict):
                all_prices[crypto] = results[i]
            else:
                logger.warning(f"⚠️ Failed to fetch prices for {crypto}: {results[i]}")
                all_prices[crypto] = {'gemini': 0, 'binance': 0}
        
        return all_prices
    
    def calculate_arbitrage_opportunity(self, crypto: str, prices: Dict[str, float]) -> Optional[Dict]:
        """Calculate if there's an arbitrage opportunity for a crypto"""
        gemini_price = prices.get('gemini', 0)
        binance_price = prices.get('binance', 0)
        
        if gemini_price <= 0 or binance_price <= 0:
            return None
        
        # Calculate spread percentage
        if gemini_price > binance_price:
            # Gemini is more expensive - buy on Binance, sell on Gemini
            spread_percent = ((gemini_price - binance_price) / binance_price) * 100
            direction = "binance_to_gemini"
            buy_price = binance_price
            sell_price = gemini_price
        else:
            # Binance is more expensive - buy on Gemini, sell on Binance
            spread_percent = ((binance_price - gemini_price) / gemini_price) * 100
            direction = "gemini_to_binance"
            buy_price = gemini_price
            sell_price = binance_price
        
        # Check if spread meets minimum threshold
        if spread_percent < MIN_SPREAD_PERCENT:
            return None
        
        # Calculate maximum position size based on available balance
        position_size = min(MAX_POSITION_SIZE, self.get_available_capital(direction))
        
        if position_size < 10:  # Minimum $10 for meaningful trade
            return None
        
        # Calculate profit after fees
        buy_amount = position_size / buy_price
        sell_value = buy_amount * sell_price
        
        # Apply fees
        buy_fee = position_size * (GEMINI_FEE if direction == "gemini_to_binance" else BINANCE_FEE)
        sell_fee = sell_value * (BINANCE_FEE if direction == "gemini_to_binance" else GEMINI_FEE)
        
        total_fees = buy_fee + sell_fee
        net_profit = sell_value - position_size - total_fees
        
        # Check if profit meets minimum threshold
        if net_profit < MIN_PROFIT_AMOUNT:
            return None
        
        # Return arbitrage opportunity
        return {
            'crypto': crypto,
            'direction': direction,
            'spread_percent': round(spread_percent, 3),
            'buy_price': round(buy_price, 2),
            'sell_price': round(sell_price, 2),
            'position_size': round(position_size, 2),
            'net_profit': round(net_profit, 2),
            'profit_percent': round((net_profit / position_size) * 100, 3),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_available_capital(self, direction: str) -> float:
        """Get available capital for arbitrage direction"""
        # In reality, we should fetch actual balances
        # For now, use configured amounts
        if direction == "gemini_to_binance":
            return 434.35  # Gemini balance
        else:
            return 36.70   # Binance balance
    
    async def execute_arbitrage(self, opportunity: Dict) -> bool:
        """Execute an arbitrage trade"""
        crypto = opportunity['crypto']
        direction = opportunity['direction']
        
        logger.info(f"🚀 EXECUTING ARBITRAGE: {crypto} {direction}")
        logger.info(f"   Spread: {opportunity['spread_percent']}%")
        logger.info(f"   Position: ${opportunity['position_size']}")
        logger.info(f"   Expected profit: ${opportunity['net_profit']} ({opportunity['profit_percent']}%)")
        
        try:
            if direction == "gemini_to_binance":
                # Buy on Gemini, sell on Binance
                # 1. Buy on Gemini
                gemini_symbol = f"{crypto}/USD"
                gemini_amount = opportunity['position_size'] / opportunity['buy_price']
                
                gemini_order = self.exchanges['gemini'].create_order(
                    symbol=gemini_symbol,
                    type='market',
                    side='buy',
                    amount=gemini_amount
                )
                logger.info(f"✅ Gemini BUY order: {gemini_order['id']}")
                
                # 2. Sell on Binance
                binance_symbol = f"{crypto}/USDT"
                binance_order = self.exchanges['binance'].create_order(
                    symbol=binance_symbol,
                    type='market',
                    side='sell',
                    amount=gemini_amount  # Same amount we bought
                )
                logger.info(f"✅ Binance SELL order: {binance_order['id']}")
                
            else:  # binance_to_gemini
                # Buy on Binance, sell on Gemini
                # 1. Buy on Binance
                binance_symbol = f"{crypto}/USDT"
                binance_amount = opportunity['position_size'] / opportunity['buy_price']
                
                binance_order = self.exchanges['binance'].create_order(
                    symbol=binance_symbol,
                    type='market',
                    side='buy',
                    amount=binance_amount
                )
                logger.info(f"✅ Binance BUY order: {binance_order['id']}")
                
                # 2. Sell on Gemini
                gemini_symbol = f"{crypto}/USD"
                gemini_order = self.exchanges['gemini'].create_order(
                    symbol=gemini_symbol,
                    type='market',
                    side='sell',
                    amount=binance_amount  # Same amount we bought
                )
                logger.info(f"✅ Gemini SELL order: {gemini_order['id']}")
            
            # Save trade record
            self.save_arbitrage_trade(opportunity, success=True)
            logger.info(f"🎉 ARBITRAGE COMPLETED: ${opportunity['net_profit']} profit")
            return True
            
        except Exception as e:
            logger.error(f"❌ Arbitrage execution failed: {e}")
            self.save_arbitrage_trade(opportunity, success=False, error=str(e))
            return False
    
    def save_arbitrage_trade(self, opportunity: Dict, success: bool, error: str = None):
        """Save arbitrage trade record"""
        trade_data = {
            **opportunity,
            'success': success,
            'error': error,
            'execution_time': datetime.now().isoformat()
        }
        
        # Save to file
        trades_file = os.path.join(BASE_DIR, 'trading_data', 'arbitrage_trades.json')
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
        trades.append(trade_data)
        
        # Save back
        with open(trades_file, 'w') as f:
            json.dump(trades, f, indent=2)
        
        logger.info(f"📝 Arbitrage trade saved: {trade_data['crypto']} {'✅' if success else '❌'}")
    
    async def monitor_arbitrage(self):
        """Main monitoring loop for arbitrage opportunities"""
        logger.info("=" * 60)
        logger.info("🔍 ARBITRAGE BOT STARTED")
        logger.info(f"Monitoring {len(CRYPTOS)} cryptos")
        logger.info(f"Min spread: {MIN_SPREAD_PERCENT}%")
        logger.info(f"Min profit: ${MIN_PROFIT_AMOUNT}")
        logger.info("=" * 60)
        
        cycle_count = 0
        
        while True:
            cycle_count += 1
            logger.info(f"\n🔄 ARBITRAGE CYCLE {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                # Fetch all prices
                all_prices = await self.fetch_all_prices()
                
                # Find arbitrage opportunities
                opportunities = []
                for crypto, prices in all_prices.items():
                    opportunity = self.calculate_arbitrage_opportunity(crypto, prices)
                    if opportunity:
                        opportunities.append(opportunity)
                
                # Log current prices
                logger.info("📊 Current Prices:")
                for crypto in ['BTC', 'ETH', 'SOL']:  # Log top 3
                    if crypto in all_prices:
                        prices = all_prices[crypto]
                        if prices['gemini'] > 0 and prices['binance'] > 0:
                            spread = abs(prices['gemini'] - prices['binance']) / min(prices['gemini'], prices['binance']) * 100
                            logger.info(f"  {crypto}: Gemini=${prices['gemini']:.2f}, Binance=${prices['binance']:.2f}, Spread={spread:.2f}%")
                
                # Execute best opportunity if found
                if opportunities:
                    # Sort by profit percentage (descending)
                    opportunities.sort(key=lambda x: x['profit_percent'], reverse=True)
                    best_opportunity = opportunities[0]
                    
                    logger.info(f"🎯 Found {len(opportunities)} arbitrage opportunities")
                    logger.info(f"Best: {best_opportunity['crypto']} - {best_opportunity['profit_percent']}% profit")
                    
                    # Execute the best opportunity
                    await self.execute_arbitrage(best_opportunity)
                else:
                    logger.info("⏳ No profitable arbitrage opportunities found")
                
                # Wait before next cycle
                logger.info(f"💤 Sleeping for 30 seconds...")
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in arbitrage cycle: {e}")
                await asyncio.sleep(60)  # Wait longer on error

async def main():
    """Main function"""
    bot = ArbitrageBot()
    await bot.monitor_arbitrage()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Arbitrage bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)