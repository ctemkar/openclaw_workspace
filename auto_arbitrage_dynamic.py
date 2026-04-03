#!/usr/bin/env python3
"""
Dynamic Arbitrage Bot
- Checks exchange support dynamically
- Only monitors cryptos on BOTH Gemini and Binance
- Expands to maximum possible coverage
"""

import ccxt
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_dynamic.log'),
        logging.StreamHandler()
    ]
)

class DynamicArbitrageBot:
    def __init__(self):
        self.exchanges = {
            'gemini': ccxt.gemini({
                'apiKey': '',
                'secret': '',
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }),
            'binance': ccxt.binance({
                'apiKey': '',
                'secret': '',
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        }
        
        # Start with a comprehensive list
        self.potential_cryptos = [
            # Major Layer 1
            'BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOT', 'TRX', 'ALGO', 'NEAR', 'ATOM',
            # DeFi
            'LINK', 'UNI', 'AAVE', 'COMP', 'YFI', 'SNX', 'CRV', 'SUSHI', 'MKR', '1INCH',
            # Memecoins
            'DOGE', 'SHIB', 'PEPE', 'WIF', 'BONK', 'FLOKI', 'MEME',
            # Layer 2
            'MATIC', 'ARB', 'OP', 'IMX', 'METIS',
            # AI/Web3
            'RNDR', 'FET', 'AGIX', 'OCEAN', 'FIL',
            # Gaming/NFT
            'SAND', 'MANA', 'AXS', 'GALA', 'ENJ',
            # Exchange tokens
            'BNB', 'FTT', 'LEO', 'CRO',
            # Others
            'LTC', 'BCH', 'XLM', 'VET', 'EOS', 'XTZ', 'ETC', 'THETA', 'ZEC', 'XMR',
            # Stablecoins (for spreads)
            'USDC', 'DAI', 'BUSD'
        ]
        
        self.supported_cryptos = []
        self.min_spread = 0.4  # 0.4%
        self.min_profit_amount = 0.15  # $0.15 minimum profit
        self.trade_size_percent = 0.08  # 8% of capital
        self.max_trade_size = 200.0  # $200 max
        
    def check_exchange_support(self, crypto):
        """Check if crypto is supported on both exchanges"""
        try:
            # Check Gemini (uses /USD)
            gemini_symbol = f"{crypto}/USD"
            gemini_ticker = self.exchanges['gemini'].fetch_ticker(gemini_symbol)
            
            # Check Binance (uses /USDT)
            binance_symbol = f"{crypto}/USDT"
            binance_ticker = self.exchanges['binance'].fetch_ticker(binance_symbol)
            
            # If we get here, both exchanges support it
            return True
        except Exception as e:
            # One or both exchanges don't support this crypto
            return False
    
    def discover_supported_cryptos(self):
        """Dynamically discover which cryptos are supported on both exchanges"""
        logging.info("🔍 Discovering cryptos supported on BOTH Gemini and Binance...")
        
        supported = []
        for crypto in self.potential_cryptos:
            if self.check_exchange_support(crypto):
                supported.append(crypto)
                logging.info(f"   ✅ {crypto}: Supported on both exchanges")
            else:
                logging.info(f"   ❌ {crypto}: Not supported on both exchanges")
        
        self.supported_cryptos = supported
        logging.info(f"🎯 Found {len(supported)} cryptos supported on both exchanges")
        logging.info(f"📊 Supported cryptos: {', '.join(supported)}")
        return supported
    
    def calculate_spread(self, gemini_price, binance_price):
        """Calculate spread percentage"""
        if gemini_price > 0 and binance_price > 0:
            spread = ((gemini_price - binance_price) / binance_price) * 100
            return spread
        return 0
    
    def calculate_profit(self, spread_percent, trade_size):
        """Calculate potential profit after fees"""
        gross_profit = trade_size * (spread_percent / 100)
        fees = trade_size * 0.002  # 0.1% each side
        net_profit = gross_profit - fees
        return net_profit
    
    def scan_arbitrage_opportunities(self):
        """Scan all supported cryptos for arbitrage opportunities"""
        logging.info(f"📊 Scanning {len(self.supported_cryptos)} cryptos for arbitrage...")
        
        opportunities = []
        for crypto in self.supported_cryptos:
            try:
                # Get prices
                gemini_ticker = self.exchanges['gemini'].fetch_ticker(f"{crypto}/USD")
                binance_ticker = self.exchanges['binance'].fetch_ticker(f"{crypto}/USDT")
                
                gemini_price = gemini_ticker['last']
                binance_price = binance_ticker['last']
                
                # Calculate spread
                spread = self.calculate_spread(gemini_price, binance_price)
                
                # Calculate potential profit
                trade_size = min(1000.0 * self.trade_size_percent, self.max_trade_size)  # Assume $1000 capital
                profit = self.calculate_profit(spread, trade_size)
                
                if spread >= self.min_spread and profit >= self.min_profit_amount:
                    opportunities.append({
                        'crypto': crypto,
                        'spread': spread,
                        'profit': profit,
                        'gemini_price': gemini_price,
                        'binance_price': binance_price
                    })
                    logging.info(f"   🎯 {crypto}: Spread={spread:.2f}%, Profit=${profit:.2f}")
                else:
                    logging.debug(f"   {crypto}: Spread={spread:.2f}% (below {self.min_spread}% or profit ${profit:.2f} < ${self.min_profit_amount})")
                    
            except Exception as e:
                logging.warning(f"   ⚠️ Error fetching {crypto}: {e}")
        
        return opportunities
    
    def run(self):
        """Main bot loop"""
        logging.info("🚀 Starting Dynamic Arbitrage Bot")
        logging.info("=" * 50)
        
        # First, discover supported cryptos
        self.discover_supported_cryptos()
        
        if not self.supported_cryptos:
            logging.error("❌ No cryptos supported on both exchanges!")
            return
        
        logging.info(f"🎯 Monitoring {len(self.supported_cryptos)} cryptos")
        logging.info(f"📈 Minimum spread: {self.min_spread}%")
        logging.info(f"💰 Minimum profit: ${self.min_profit_amount}")
        logging.info("=" * 50)
        
        # Main loop
        while True:
            try:
                opportunities = self.scan_arbitrage_opportunities()
                
                if opportunities:
                    logging.info(f"🎯 Found {len(opportunities)} arbitrage opportunities!")
                    for opp in opportunities:
                        logging.info(f"   💰 {opp['crypto']}: {opp['spread']:.2f}% spread, ${opp['profit']:.2f} profit")
                else:
                    logging.info("⏳ No profitable arbitrage opportunities found")
                
                # Wait before next scan
                time.sleep(30)  # Scan every 30 seconds
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    bot = DynamicArbitrageBot()
    bot.run()
