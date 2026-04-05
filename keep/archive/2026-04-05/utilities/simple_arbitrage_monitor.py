#!/usr/bin/env python3
"""
Simple Arbitrage Monitor - Monitors price differences without trading
Useful for testing and monitoring while multi-LLM bot runs
"""

import os
import sys
import json
import time
import ccxt
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'api_keys.json')

# Cryptos to monitor
CRYPTOS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'UNI']

class ArbitrageMonitor:
    def __init__(self):
        """Initialize exchanges"""
        self.exchanges = {}
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
            })
            logger.info("✅ Gemini exchange initialized")
            
            # Initialize Binance
            self.exchanges['binance'] = ccxt.binance({
                'apiKey': api_keys.get('binance', {}).get('api_key', ''),
                'secret': api_keys.get('binance', {}).get('api_secret', ''),
                'enableRateLimit': True,
            })
            logger.info("✅ Binance exchange initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize exchanges: {e}")
            # Continue in monitoring-only mode
            self.exchanges = {}
    
    def fetch_price(self, exchange_name: str, crypto: str) -> float:
        """Fetch price from an exchange"""
        if exchange_name not in self.exchanges:
            return 0.0
            
        try:
            if exchange_name == 'gemini':
                symbol = f"{crypto}/USD"
            else:  # binance
                symbol = f"{crypto}/USDT"
                
            ticker = self.exchanges[exchange_name].fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.debug(f"⚠️ Could not fetch {crypto} price from {exchange_name}: {e}")
            return 0.0
    
    def calculate_spread(self, gemini_price: float, binance_price: float) -> dict:
        """Calculate spread between exchanges"""
        if gemini_price <= 0 or binance_price <= 0:
            return None
            
        spread_abs = abs(gemini_price - binance_price)
        spread_percent = (spread_abs / min(gemini_price, binance_price)) * 100
        
        if gemini_price > binance_price:
            direction = "Buy Binance → Sell Gemini"
            profit_potential = gemini_price - binance_price
        else:
            direction = "Buy Gemini → Sell Binance"
            profit_potential = binance_price - gemini_price
            
        return {
            'spread_abs': round(spread_abs, 2),
            'spread_percent': round(spread_percent, 3),
            'direction': direction,
            'profit_potential': round(profit_potential, 2)
        }
    
    def monitor_prices(self):
        """Main monitoring loop"""
        logger.info("=" * 70)
        logger.info("🔍 SIMPLE ARBITRAGE MONITOR")
        logger.info("Monitoring price differences between Gemini and Binance")
        logger.info("=" * 70)
        
        cycle = 0
        
        while True:
            cycle += 1
            logger.info(f"\n📊 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            all_spreads = []
            
            for crypto in CRYPTOS:
                # Fetch prices
                gemini_price = self.fetch_price('gemini', crypto)
                binance_price = self.fetch_price('binance', crypto)
                
                if gemini_price > 0 and binance_price > 0:
                    # Calculate spread
                    spread_info = self.calculate_spread(gemini_price, binance_price)
                    
                    if spread_info:
                        all_spreads.append({
                            'crypto': crypto,
                            'gemini_price': round(gemini_price, 2),
                            'binance_price': round(binance_price, 2),
                            **spread_info
                        })
            
            # Display results
            if all_spreads:
                # Sort by spread percentage (descending)
                all_spreads.sort(key=lambda x: x['spread_percent'], reverse=True)
                
                logger.info("💰 PRICE COMPARISON:")
                for item in all_spreads[:5]:  # Show top 5
                    if item['spread_percent'] > 0.1:  # Only show meaningful spreads
                        logger.info(f"  {item['crypto']}:")
                        logger.info(f"    Gemini: ${item['gemini_price']:,}")
                        logger.info(f"    Binance: ${item['binance_price']:,}")
                        logger.info(f"    Spread: ${item['spread_abs']} ({item['spread_percent']}%)")
                        logger.info(f"    Opportunity: {item['direction']}")
                
                # Log best opportunity
                best = all_spreads[0]
                logger.info(f"🎯 BEST OPPORTUNITY: {best['crypto']} - {best['spread_percent']}% spread")
                
                # Save to file for dashboard
                self.save_monitor_data(all_spreads)
            else:
                logger.info("⏳ No price data available")
            
            # Wait for next cycle
            logger.info(f"⏰ Next update in 60 seconds...")
            time.sleep(60)
    
    def save_monitor_data(self, spreads: list):
        """Save monitoring data to file"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'spreads': spreads
            }
            
            # Save to file
            data_file = os.path.join(BASE_DIR, 'trading_data', 'arbitrage_monitor.json')
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.debug(f"⚠️ Could not save monitor data: {e}")

def main():
    """Main function"""
    monitor = ArbitrageMonitor()
    
    try:
        monitor.monitor_prices()
    except KeyboardInterrupt:
        logger.info("👋 Arbitrage monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()