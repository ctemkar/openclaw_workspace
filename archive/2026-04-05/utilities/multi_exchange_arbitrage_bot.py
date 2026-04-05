#!/usr/bin/env python3
"""
MULTI-EXCHANGE ARBITRAGE BOT
Trades across multiple exchanges for maximum arbitrage opportunities
"""

import ccxt
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_exchange_arbitrage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiExchangeArbitrageBot:
    def __init__(self, config_file: str = 'config/api_keys.json'):
        """Initialize bot with multiple exchanges"""
        self.exchanges = {}
        self.config_file = config_file
        self.min_spread_threshold = 0.5  # 0.5% minimum spread
        self.trade_size_usd = 50  # $50 per trade
        self.scan_interval = 30  # seconds
        self.max_restart_attempts = 3
        
        # Cryptos to monitor (prioritize liquid ones)
        self.cryptos_to_monitor = [
            'BTC', 'ETH', 'SOL', 'XRP', 'DOT', 
            'ADA', 'DOGE', 'LTC', 'SHIB', 'AVAX'
        ]
        
        # Exchange pairs to check (avoid geographic restrictions)
        self.exchange_pairs = [
            ('gemini', 'binance'),
            ('coinbase', 'kraken'),
            ('kucoin', 'bybit'),
            ('kraken', 'gemini'),
            ('coinbase', 'binance')
        ]
        
        self.load_exchanges()
        
    def load_exchanges(self):
        """Load all configured exchanges"""
        try:
            with open(self.config_file, 'r') as f:
                api_keys = json.load(f)
            
            logger.info("📊 Loading exchanges...")
            
            # Exchange configurations
            exchange_configs = {
                'binance': {
                    'class': ccxt.binance,
                    'requires_keys': True,
                    'symbol_format': '{crypto}/USDT'
                },
                'gemini': {
                    'class': ccxt.gemini,
                    'requires_keys': True,
                    'symbol_format': '{crypto}/USD'
                },
                'coinbase': {
                    'class': ccxt.coinbase,
                    'requires_keys': False,  # Can fetch prices without keys
                    'symbol_format': '{crypto}/USD'
                },
                'kraken': {
                    'class': ccxt.kraken,
                    'requires_keys': False,
                    'symbol_format': '{crypto}/USD'
                },
                'kucoin': {
                    'class': ccxt.kucoin,
                    'requires_keys': False,
                    'symbol_format': '{crypto}/USDT'
                },
                'bybit': {
                    'class': ccxt.bybit,
                    'requires_keys': False,
                    'symbol_format': '{crypto}/USDT'
                }
            }
            
            loaded_count = 0
            for exchange_id, config in exchange_configs.items():
                try:
                    if config['requires_keys']:
                        if exchange_id not in api_keys or not api_keys[exchange_id].get('api_key'):
                            logger.warning(f"⚠️  No API keys for {exchange_id}, using public mode")
                            # Initialize without keys for price checking only
                            exchange = config['class']()
                        else:
                            # Initialize with API keys
                            exchange = config['class']({
                                'apiKey': api_keys[exchange_id]['api_key'],
                                'secret': api_keys[exchange_id]['api_secret'],
                                'enableRateLimit': True
                            })
                    else:
                        # Initialize without keys (public data)
                        exchange = config['class']()
                    
                    # Test connection
                    exchange.load_markets()
                    self.exchanges[exchange_id] = {
                        'instance': exchange,
                        'config': config,
                        'has_trading': exchange_id in api_keys and api_keys[exchange_id].get('api_key')
                    }
                    loaded_count += 1
                    logger.info(f"✅ Loaded {exchange_id} ({'Trading enabled' if self.exchanges[exchange_id]['has_trading'] else 'Price checking only'})")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load {exchange_id}: {e}")
            
            logger.info(f"📊 Successfully loaded {loaded_count}/{len(exchange_configs)} exchanges")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            sys.exit(1)
    
    def get_price(self, exchange_id: str, crypto: str) -> Optional[float]:
        """Get current price for a crypto on an exchange"""
        try:
            exchange = self.exchanges[exchange_id]['instance']
            config = self.exchanges[exchange_id]['config']
            
            symbol = config['symbol_format'].format(crypto=crypto)
            ticker = exchange.fetch_ticker(symbol)
            return ticker['last']
            
        except Exception as e:
            logger.debug(f"Price fetch failed for {crypto} on {exchange_id}: {e}")
            return None
    
    def find_arbitrage_opportunities(self) -> List[Dict]:
        """Find arbitrage opportunities across all exchange pairs"""
        opportunities = []
        
        logger.info(f"🔍 Scanning {len(self.cryptos_to_monitor)} cryptos across {len(self.exchange_pairs)} exchange pairs...")
        
        for crypto in self.cryptos_to_monitor:
            for exchange1_id, exchange2_id in self.exchange_pairs:
                if exchange1_id not in self.exchanges or exchange2_id not in self.exchanges:
                    continue
                
                # Get prices
                price1 = self.get_price(exchange1_id, crypto)
                price2 = self.get_price(exchange2_id, crypto)
                
                if price1 is None or price2 is None:
                    continue
                
                # Calculate spread
                if price1 > price2:
                    spread_percent = ((price1 - price2) / price2) * 100
                    buy_exchange = exchange2_id
                    sell_exchange = exchange1_id
                    buy_price = price2
                    sell_price = price1
                else:
                    spread_percent = ((price2 - price1) / price1) * 100
                    buy_exchange = exchange1_id
                    sell_exchange = exchange2_id
                    buy_price = price1
                    sell_price = price2
                
                # Check if spread meets threshold
                if spread_percent >= self.min_spread_threshold:
                    # Calculate potential profit
                    crypto_amount = self.trade_size_usd / buy_price
                    sell_value = crypto_amount * sell_price
                    
                    # Estimate fees (0.2% per trade)
                    buy_fee = self.trade_size_usd * 0.002
                    sell_fee = sell_value * 0.002
                    net_profit = sell_value - self.trade_size_usd - buy_fee - sell_fee
                    
                    opportunity = {
                        'crypto': crypto,
                        'spread_percent': spread_percent,
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'trade_size_usd': self.trade_size_usd,
                        'estimated_profit': net_profit,
                        'timestamp': datetime.now().isoformat(),
                        'can_execute': (
                            self.exchanges[buy_exchange]['has_trading'] and 
                            self.exchanges[sell_exchange]['has_trading']
                        )
                    }
                    
                    opportunities.append(opportunity)
                    
                    logger.info(f"🎯 Found opportunity: {crypto} - {spread_percent:.3f}% spread")
                    logger.info(f"   Buy on {buy_exchange} at ${buy_price:.4f}")
                    logger.info(f"   Sell on {sell_exchange} at ${sell_price:.4f}")
                    logger.info(f"   Estimated profit: ${net_profit:.2f}")
        
        return opportunities
    
    def execute_trade(self, opportunity: Dict) -> bool:
        """Execute an arbitrage trade"""
        if not opportunity['can_execute']:
            logger.warning(f"⚠️  Cannot execute trade - missing trading permissions")
            return False
        
        crypto = opportunity['crypto']
        buy_exchange = opportunity['buy_exchange']
        sell_exchange = opportunity['sell_exchange']
        
        try:
            logger.info(f"🚀 Executing arbitrage trade for {crypto}...")
            
            # Get exchange instances
            buy_exchange_obj = self.exchanges[buy_exchange]['instance']
            sell_exchange_obj = self.exchanges[sell_exchange]['instance']
            
            # Calculate amount to buy
            crypto_amount = opportunity['trade_size_usd'] / opportunity['buy_price']
            
            # Execute buy order
            logger.info(f"📈 Buying {crypto_amount:.6f} {crypto} on {buy_exchange}...")
            # buy_order = buy_exchange_obj.create_market_buy_order(
            #     symbol=f"{crypto}/USDT" if buy_exchange != 'gemini' else f"{crypto}/USD",
            #     amount=crypto_amount
            # )
            # logger.info(f"✅ Buy order executed: {buy_order}")
            
            # Execute sell order
            logger.info(f"📉 Selling {crypto_amount:.6f} {crypto} on {sell_exchange}...")
            # sell_order = sell_exchange_obj.create_market_sell_order(
            #     symbol=f"{crypto}/USDT" if sell_exchange != 'gemini' else f"{crypto}/USD",
            #     amount=crypto_amount
            # )
            # logger.info(f"✅ Sell order executed: {sell_order}")
            
            # For now, just log (comment out actual trading for safety)
            logger.info(f"🛑 TRADE SIMULATION ONLY - Would execute real trade")
            logger.info(f"   Buy: {crypto_amount:.6f} {crypto} on {buy_exchange}")
            logger.info(f"   Sell: {crypto_amount:.6f} {crypto} on {sell_exchange}")
            logger.info(f"   Estimated profit: ${opportunity['estimated_profit']:.2f}")
            
            # Save trade record
            self.save_trade_record(opportunity, simulated=True)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            return False
    
    def save_trade_record(self, opportunity: Dict, simulated: bool = True):
        """Save trade record to file"""
        try:
            record = opportunity.copy()
            record['simulated'] = simulated
            record['executed_at'] = datetime.now().isoformat()
            
            # Load existing trades
            trades_file = 'trading_data/multi_exchange_trades.json'
            os.makedirs('trading_data', exist_ok=True)
            
            if os.path.exists(trades_file):
                with open(trades_file, 'r') as f:
                    trades = json.load(f)
            else:
                trades = []
            
            trades.append(record)
            
            # Keep only last 100 trades
            if len(trades) > 100:
                trades = trades[-100:]
            
            with open(trades_file, 'w') as f:
                json.dump(trades, f, indent=2)
            
            logger.info(f"💾 Trade record saved")
            
        except Exception as e:
            logger.error(f"❌ Failed to save trade record: {e}")
    
    def run(self):
        """Main bot loop"""
        logger.info("=" * 60)
        logger.info("🚀 MULTI-EXCHANGE ARBITRAGE BOT STARTED")
        logger.info("=" * 60)
        logger.info(f"📊 Monitoring {len(self.cryptos_to_monitor)} cryptos")
        logger.info(f"🎯 Minimum spread: {self.min_spread_threshold}%")
        logger.info(f"💰 Trade size: ${self.trade_size_usd}")
        logger.info(f"🔄 Scan interval: {self.scan_interval} seconds")
        logger.info("=" * 60)
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                logger.info(f"\n🔄 CYCLE {cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Find opportunities
                opportunities = self.find_arbitrage_opportunities()
                
                if opportunities:
                    logger.info(f"🎯 Found {len(opportunities)} arbitrage opportunities")
                    
                    # Sort by profit (highest first)
                    opportunities.sort(key=lambda x: x['estimated_profit'], reverse=True)
                    
                    # Execute the best opportunity
                    best_opportunity = opportunities[0]
                    
                    if best_opportunity['estimated_profit'] > 0.5:  # Minimum $0.50 profit
                        logger.info(f"💰 Best opportunity: {best_opportunity['crypto']} - ${best_opportunity['estimated_profit']:.2f} profit")
                        
                        # Execute trade (simulated for now)
                        self.execute_trade(best_opportunity)
                    else:
                        logger.info("⏳ Profits too small, waiting for better opportunity")
                else:
                    logger.info("⏳ No arbitrage opportunities found")
                
                # Save current market state
                self.save_market_state()
                
                logger.info(f"⏰ Next scan in {self.scan_interval} seconds...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                logger.info(f"⏰ Retrying in {self.scan_interval} seconds...")
                time.sleep(self.scan_interval)
    
    def save_market_state(self):
        """Save current market state for analysis"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'exchanges_loaded': list(self.exchanges.keys()),
                'cryptos_monitored': self.cryptos_to_monitor,
                'min_spread_threshold': self.min_spread_threshold,
                'trade_size_usd': self.trade_size_usd
            }
            
            with open('trading_data/multi_exchange_state.json', 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Could not save market state: {e}")

def main():
    """Main entry point"""
    bot = MultiExchangeArbitrageBot()
    bot.run()

if __name__ == "__main__":
    main()